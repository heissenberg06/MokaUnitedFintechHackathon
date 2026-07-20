#!/usr/bin/env python3
"""Moka Akış — next4biz BPM/CSM klonu (bkz. ANALIZ.md).
Sıfır bağımlılık: yalnız Python stdlib. Statik dosyalar + JSON API aynı porttan.
Veri kalıcılığı: next4biz-klon/data/tickets.json (atomic write + Lock).
Bu sürümde AI (sikayetvar/analysis.py) <-> ticket bağlantısı YOKTUR (kasıtlı,
bkz. ANALIZ.md Bölüm 6 Faz 4). Seed veri ve tüm içerik KURGUDUR.
Çalıştır: python3 next4biz-klon/server.py  ->  http://localhost:8770
"""
import html
import json
import os
import random
import re
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'tickets.json')
PORT = 8770
MAX_BODY = 16 * 1024

LOCK = threading.Lock()
_RATE = {}

# ----------------------------------------------------------------------------
# Taksonomi (sikayetvar/analysis.py ile hizalı — ileride AI köprüsü bu değerleri
# doğrudan üretecek; bkz. ANALIZ.md Bölüm 3.2)
# ----------------------------------------------------------------------------
CATEGORIES = [
    "Yetkisiz İşlem", "Para İadesi", "Komisyon & Ücret", "POS & Teslimat",
    "Sanal POS & Başvuru", "Müşteri Hizmetleri", "Uygulama & Teknik",
    "Ödeme Linki", "Dijital Cüzdan", "Hesap & Doğrulama",
    "Mutabakat & Rapor", "Sözleşme & İptal",
]

TEAM_ROUTING = {
    "Yetkisiz İşlem": "Güvenlik & Fraud Ekibi",
    "Para İadesi": "Finans & Ödemeler Ekibi",
    "Komisyon & Ücret": "Finans & Ödemeler Ekibi",
    "POS & Teslimat": "Operasyon & Lojistik Ekibi",
    "Sanal POS & Başvuru": "Satış & Onboarding Ekibi",
    "Müşteri Hizmetleri": "Müşteri Deneyimi Ekibi",
    "Uygulama & Teknik": "Ürün & Mühendislik Ekibi",
    "Ödeme Linki": "Ürün & Mühendislik Ekibi",
    "Dijital Cüzdan": "Finans & Ödemeler Ekibi",
    "Hesap & Doğrulama": "Uyum & Doğrulama (KYC) Ekibi",
    "Mutabakat & Rapor": "Finans & Ödemeler Ekibi",
    "Sözleşme & İptal": "Hukuk & Sözleşme Ekibi",
}
TEAMS = sorted(set(TEAM_ROUTING.values()))

PRIORITIES = ["dusuk", "orta", "yuksek", "kritik"]
PRIORITY_LABEL = {"dusuk": "Düşük", "orta": "Orta", "yuksek": "Yüksek", "kritik": "Kritik"}
# öncelik -> toplam akış SLA penceresi (saat) — bkz. ANALIZ.md Bölüm 3.4
SLA_HOURS = {"kritik": 4, "yuksek": 24, "orta": 72, "dusuk": 120}

STATUSES = ["yeni", "siniflandirildi", "atandi", "islemde", "beklemede",
            "cozuldu", "kapandi", "yeniden-acildi"]
STATUS_LABEL = {
    "yeni": "Yeni", "siniflandirildi": "Sınıflandırıldı", "atandi": "Atandı",
    "islemde": "İşlemde", "beklemede": "Beklemede", "cozuldu": "Çözüldü",
    "kapandi": "Kapandı", "yeniden-acildi": "Yeniden Açıldı",
}
OPEN_STATUSES = {"yeni", "siniflandirildi", "atandi", "islemde", "beklemede", "yeniden-acildi"}
SOURCES = ["ai", "self-service", "email", "chat", "whatsapp"]
SENTIMENTS = ["ofkeli", "olumsuz", "notr", "olumlu"]

TR_LETTERS = "A-Za-zÇĞİıÖŞÜçğıöşü"
NAME_RE = re.compile(f"^[{TR_LETTERS} .'-]+$")

# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------
def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()

def clean(s):
    """Sunucu tarafı XSS savunması: string girdi HTML-escape edilir."""
    return html.escape(str(s).strip())

def mask_name(name):
    parts = [p for p in name.strip().split() if p]
    out = []
    for p in parts[:3]:
        out.append(p[0].upper() + '**')
    return ' '.join(out) if out else 'A**'

def initials(name):
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def tr_lower(s):
    return (s.replace('İ', 'i').replace('I', 'ı').replace('Ş', 'ş').replace('Ç', 'ç')
             .replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ö', 'ö').lower())

def _parse_dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def sla_state_of(ticket, now=None):
    """ok | risk | breach — kapanmış/çözülmüş taleplerde her zaman 'ok'."""
    now = now or datetime.now()
    if ticket['status'] in ('cozuldu', 'kapandi'):
        return 'ok'
    due = _parse_dt(ticket.get('sla_due_at', ''))
    created = _parse_dt(ticket.get('createdAt', ''))
    if not due or not created:
        return 'ok'
    if now >= due:
        return 'breach'
    total = (due - created).total_seconds()
    remaining = (due - now).total_seconds()
    if total > 0 and remaining / total <= 0.2:
        return 'risk'
    return 'ok'

def sla_remaining_label(ticket, now=None):
    now = now or datetime.now()
    due = _parse_dt(ticket.get('sla_due_at', ''))
    if not due:
        return '—'
    if ticket['status'] in ('cozuldu', 'kapandi'):
        return 'tamamlandı'
    delta = due - now
    hours = delta.total_seconds() / 3600
    if hours < 0:
        return f"{abs(hours):.0f} sa. gecikti"
    if hours < 1:
        return f"{int(delta.total_seconds() / 60)} dk. kaldı"
    return f"{hours:.0f} sa. kaldı"

# ----------------------------------------------------------------------------
# Seed (tamamen kurgu içerik)
# ----------------------------------------------------------------------------
# (isim, başlık, gövde, kategori, öncelik, durum, ekip, kaç_saat_önce, işyeri, kaynak)
SEED_TICKETS = [
    ("Zeynep Kaya", "Kartımdan onayım olmadan tahsilat yapıldı",
     "Hızlı Ödeme Bayii'nde benim başlatmadığım bir işlem gerçekleşmiş, itiraz ediyorum.",
     "Yetkisiz İşlem", "kritik", "yeni", 6, "Hızlı Ödeme Bayii", "ai"),
    ("Emre Aydın", "Yetkisiz işlem: kartımdan habersiz tahsilat",
     "Hızlı Ödeme Bayii üzerinden hesabımdan izinsiz bir çekim yapılmış.",
     "Yetkisiz İşlem", "kritik", "islemde", 20, "Hızlı Ödeme Bayii", "ai"),
    ("Mehmet Yıldız", "Para iadem 10 gündür yapılmadı",
     "İptal ettiğim işlemin iadesi onaylandı görünüyor ama kartıma yansımadı.",
     "Para İadesi", "yuksek", "islemde", 22, None, "self-service"),
    ("Elif Su", "Müşteri hizmetlerine bir türlü ulaşamıyorum",
     "Çağrı merkezini defalarca aradım, hat düşüyor, canlı destek de yanıt vermiyor.",
     "Müşteri Hizmetleri", "orta", "beklemede", 30, None, "chat"),
    ("Can Turan", "Link ile ödeme sayfası açılmıyor",
     "Müşterilerime gönderdiğim ödeme linki bazı cihazlarda hata veriyor.",
     "Ödeme Linki", "yuksek", "atandi", 10, None, "email"),
    ("Selin Arda", "Hesap doğrulama süreci çok uzadı",
     "Gerekli tüm evrakları yükledim ancak hesabım hâlâ onaylanmadı.",
     "Hesap & Doğrulama", "orta", "islemde", 48, None, "self-service"),
    ("Burak Öz", "Dijital cüzdan bakiyem aktarılmadı",
     "Cüzdanımdaki bakiyeyi banka hesabıma aktarmak istedim, işlem askıda kaldı.",
     "Dijital Cüzdan", "yuksek", "yeni", 3, None, "whatsapp"),
    ("Deniz Kara", "Uygulama sürekli hata veriyor",
     "Son güncellemeden sonra uygulamaya giriş yapamıyorum, ödeme alırken kapanıyor.",
     "Uygulama & Teknik", "orta", "atandi", 14, None, "ai"),
    ("Gökhan Ma", "Sanal POS başvurum haftalardır sonuçlanmadı",
     "Başvuru yaptığımda 3 iş günü içinde dönüş yapılacağı belirtilmişti, üç hafta oldu.",
     "Sanal POS & Başvuru", "orta", "cozuldu", 96, None, "email"),
    ("Aylin Rüz", "Gün sonu mutabakatı tutmuyor",
     "Panelde görünen işlem tutarları ile hesabıma geçen tutarlar farklı.",
     "Mutabakat & Rapor", "yuksek", "islemde", 26, None, "self-service"),
    ("Kerem Bal", "Sözleşmeyi iptal etmek istiyorum ama edemiyorum",
     "Hizmeti kullanmayı bırakmak istiyorum fakat panelde iptal seçeneği yok.",
     "Sözleşme & İptal", "dusuk", "beklemede", 60, None, "chat"),
    ("Merve İl", "İşlem ücreti hakkında bilgilendirilmedim",
     "Hesabımdan adını bilmediğim bir işlem ücreti kesilmiş.",
     "Komisyon & Ücret", "orta", "cozuldu", 80, None, "self-service"),
    ("Okan Ba", "Bilgim dışında hesabımdan üyelik ücreti çekilmiş",
     "Onaylamadığım bir üyelik için hesabımdan aylık ücret kesilmeye başlanmış.",
     "Yetkisiz İşlem", "kritik", "siniflandirildi", 2, "Yıldız Elektronik", "ai"),
    ("Sibel Ak", "Kartımdan onayım olmadan tahsilat yapıldı",
     "Kartımdan başlatmadığım bir işlem için tahsilat gerçekleştirilmiş.",
     "Yetkisiz İşlem", "kritik", "cozuldu", 130, "Yıldız Elektronik", "ai"),
    ("Tolga En", "POS cihazım hâlâ teslim edilmedi",
     "Sanal POS onayının ardından fiziki POS cihazının 3 iş günü içinde teslim edileceği söylendi.",
     "POS & Teslimat", "dusuk", "kapandi", 200, None, "email"),
]

def _sla_due(created, priority):
    return created + timedelta(hours=SLA_HOURS[priority])

def _make_tasks(status):
    base = [
        {"title": "Talebi doğrula ve kategorilendir", "done": True},
        {"title": "İlgili ekibe ata", "done": status not in ("yeni",)},
        {"title": "Müşteriyle ilk temas kur", "done": status in ("islemde", "beklemede", "cozuldu", "kapandi")},
        {"title": "Çözümü uygula ve kapat", "done": status in ("cozuldu", "kapandi")},
    ]
    return base

def _make_approvals(priority, status):
    if priority not in ("kritik", "yuksek"):
        return []
    state = "onaylandi" if status in ("cozuldu", "kapandi", "islemde") else "bekliyor"
    return [{"role": "Ekip Lideri", "state": state}]

def _make_timeline(name, created, status, source):
    src_label = {"ai": "Yapay Zeka", "self-service": "Self-Servis", "email": "E-posta",
                 "chat": "Canlı Destek", "whatsapp": "WhatsApp"}.get(source, source)
    tl = [{"at": created.isoformat(), "actor": src_label, "type": "olusturuldu",
           "note": "Talep oluşturuldu."}]
    if status != "yeni":
        tl.append({"at": (created + timedelta(hours=1)).isoformat(), "actor": "Sistem",
                   "type": "siniflandirildi", "note": "Kategori otomatik belirlendi."})
    if status in ("atandi", "islemde", "beklemede", "cozuldu", "kapandi"):
        tl.append({"at": (created + timedelta(hours=2)).isoformat(), "actor": "Sistem",
                   "type": "atandi", "note": "İlgili ekibe yönlendirildi."})
    if status in ("islemde", "beklemede", "cozuldu", "kapandi"):
        tl.append({"at": (created + timedelta(hours=4)).isoformat(), "actor": "Ekip",
                   "type": "not", "note": "İşlem üzerinde çalışılmaya başlandı."})
    if status in ("cozuldu", "kapandi"):
        tl.append({"at": (created + timedelta(hours=8)).isoformat(), "actor": "Ekip",
                   "type": "cozuldu", "note": "Talep çözüldü olarak işaretlendi."})
    return tl

def build_seed():
    tickets = []
    seq = 0
    for name, title, body, category, priority, status, hours_ago, merchant, source in SEED_TICKETS:
        seq += 1
        created = datetime.now() - timedelta(hours=hours_ago)
        team = TEAM_ROUTING[category]
        tickets.append({
            "id": seq,
            "createdAt": created.replace(microsecond=0).isoformat(),
            "source": source,
            "requester_name": mask_name(name),
            "requester_initials": initials(name),
            "title": clean(title),
            "body": clean(body),
            "category": category,
            "priority": priority,
            "status": status,
            "assignee_team": team,
            "assignee_user": None,
            "sla_due_at": _sla_due(created, priority).replace(microsecond=0).isoformat(),
            "sentiment": random.choice(SENTIMENTS),
            "merchant": merchant,
            "tasks": _make_tasks(status),
            "approvals": _make_approvals(priority, status),
            "timeline": _make_timeline(name, created, status, source),
            "audit": [{"at": created.replace(microsecond=0).isoformat(), "actor": "sistem",
                      "action": "ticket_created"}],
        })
    return {"seq": seq, "tickets": tickets}

# ----------------------------------------------------------------------------
# Kalıcılık
# ----------------------------------------------------------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        data = build_seed()
        _write(data)
        return data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _write(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)

# ----------------------------------------------------------------------------
# Doğrulama
# ----------------------------------------------------------------------------
def v_name(s):
    s = s.strip()
    if not (2 <= len(s) <= 40):
        return "Ad Soyad 2-40 karakter olmalı."
    if not NAME_RE.match(s):
        return "Ad Soyad yalnızca harflerden oluşmalı."
    return None

def v_len(s, lo, hi, label):
    s = s.strip()
    if not (lo <= len(s) <= hi):
        return f"{label} {lo}-{hi} karakter olmalı."
    return None

def v_choice(val, choices, label):
    if val not in choices:
        return f"{label} geçersiz."
    return None

# ----------------------------------------------------------------------------
# Sunum katmanı yardımcıları
# ----------------------------------------------------------------------------
def _decorate(t):
    """Ham kayda türetilmiş (computed) alanları ekler: sla_state, sla_remaining, label'lar."""
    now = datetime.now()
    out = dict(t)
    out["sla_state"] = sla_state_of(t, now)
    out["sla_remaining"] = sla_remaining_label(t, now)
    out["status_label"] = STATUS_LABEL.get(t["status"], t["status"])
    out["priority_label"] = PRIORITY_LABEL.get(t["priority"], t["priority"])
    return out

def compute_dashboard(tickets):
    """KPI + dağılım verisi (dashboard.html için) — admin.html'deki dil ile tutarlı."""
    total = len(tickets)
    now = datetime.now()
    decorated = [_decorate(t) for t in tickets]
    open_count = sum(1 for t in decorated if t['status'] in OPEN_STATUSES)
    closed_count = total - open_count
    breach_count = sum(1 for t in decorated if t['sla_state'] == 'breach')
    risk_count = sum(1 for t in decorated if t['sla_state'] == 'risk')

    by_status = {s: 0 for s in STATUSES}
    for t in decorated:
        by_status[t['status']] += 1
    status_dist = [{"status": s, "label": STATUS_LABEL[s], "count": by_status[s]} for s in STATUSES if by_status[s]]

    by_team = {}
    for t in decorated:
        team = t['assignee_team']
        d = by_team.setdefault(team, {"team": team, "count": 0, "open": 0, "breach": 0, "risk": 0})
        d["count"] += 1
        if t['status'] in OPEN_STATUSES:
            d["open"] += 1
        if t['sla_state'] == 'breach':
            d["breach"] += 1
        elif t['sla_state'] == 'risk':
            d["risk"] += 1
    team_load = sorted(by_team.values(), key=lambda x: (x['breach'], x['risk'], x['open']), reverse=True)

    by_priority = {p: 0 for p in PRIORITIES}
    for t in decorated:
        by_priority[t['priority']] += 1
    priority_dist = [{"priority": p, "label": PRIORITY_LABEL[p], "count": by_priority[p]} for p in PRIORITIES]

    by_category = {}
    for t in decorated:
        by_category[t['category']] = by_category.get(t['category'], 0) + 1
    category_dist = sorted(
        [{"category": k, "count": v} for k, v in by_category.items()],
        key=lambda x: x['count'], reverse=True)

    avg_age_hours = None
    if total:
        ages = [(now - _parse_dt(t['createdAt'])).total_seconds() / 3600 for t in decorated if _parse_dt(t['createdAt'])]
        avg_age_hours = round(sum(ages) / len(ages), 1) if ages else None

    return {
        "generated_at": now.replace(microsecond=0).isoformat(),
        "kpis": {
            "total": total, "open": open_count, "closed": closed_count,
            "sla_breach": breach_count, "sla_risk": risk_count,
            "avg_age_hours": avg_age_hours,
        },
        "status_dist": status_dist,
        "team_load": team_load,
        "priority_dist": priority_dist,
        "category_dist": category_dist,
    }

PAGE_SIZE = 10

# ----------------------------------------------------------------------------
# HTTP Handler
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "N4BClone/1.0"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0) or 0)
        if length > MAX_BODY:
            return None, "too_large"
        raw = self.rfile.read(length) if length else b''
        if not raw:
            return {}, None
        try:
            return json.loads(raw.decode('utf-8')), None
        except Exception:
            return None, "invalid_json"

    def _rate_ok(self):
        ip = self.client_address[0]
        now = time.time()
        with LOCK:
            hits = [t for t in _RATE.get(ip, []) if now - t < 60]
            if len(hits) >= 30:
                _RATE[ip] = hits
                return False
            hits.append(now)
            _RATE[ip] = hits
        return True

    # --- GET ---
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith('/api/'):
            return self._api_get(path, parse_qs(parsed.query))
        return self._static(path)

    def _api_get(self, path, qs):
        if path == '/api/meta':
            return self._json({
                "categories": CATEGORIES, "teams": TEAMS, "priorities": PRIORITIES,
                "priority_label": PRIORITY_LABEL, "statuses": STATUSES,
                "status_label": STATUS_LABEL, "sources": SOURCES,
            })
        if path == '/api/dashboard':
            with LOCK:
                data = load_data()
            return self._json(compute_dashboard(data['tickets']))
        if path == '/api/tickets':
            return self._list_tickets(qs)
        m = re.fullmatch(r'/api/tickets/(\d+)', path)
        if m:
            return self._get_ticket(int(m.group(1)))
        return self._json({"error": "not_found"}, 404)

    def _list_tickets(self, qs):
        def q1(key, default=''):
            return (qs.get(key, [default])[0] or '').strip()
        status = q1('status')
        category = q1('category')
        team = q1('team')
        source = q1('source')
        sla = q1('sla')
        search = q1('q')
        page = max(1, int(q1('page', '1') or 1))

        with LOCK:
            data = load_data()
            items = list(reversed(data['tickets']))
        items = [_decorate(t) for t in items]

        if status:
            items = [t for t in items if t['status'] == status]
        if category:
            items = [t for t in items if t['category'] == category]
        if team:
            items = [t for t in items if t['assignee_team'] == team]
        if source:
            items = [t for t in items if t['source'] == source]
        if sla:
            items = [t for t in items if t['sla_state'] == sla]
        if search:
            nq = tr_lower(search)
            items = [t for t in items if nq in tr_lower(t['title']) or nq in tr_lower(t['body'])]

        total = len(items)
        start = (page - 1) * PAGE_SIZE
        page_items = items[start:start + PAGE_SIZE]
        return self._json({
            "total": total, "page": page, "pageSize": PAGE_SIZE,
            "totalPages": max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE),
            "items": page_items,
        })

    def _get_ticket(self, tid):
        with LOCK:
            data = load_data()
            t = next((x for x in data['tickets'] if x['id'] == tid), None)
        if not t:
            return self._json({"error": "not_found"}, 404)
        return self._json(_decorate(t))

    # --- POST / PATCH ---
    def do_POST(self):
        return self._mutate('POST')

    def do_PATCH(self):
        return self._mutate('PATCH')

    def _mutate(self, method):
        parsed = urlparse(self.path)
        path = parsed.path
        if not path.startswith('/api/'):
            return self._json({"error": "not_found"}, 404)
        if not self._rate_ok():
            return self._json({"error": "rate_limited"}, 429)
        body, err = self._read_body()
        if err == "too_large":
            return self._json({"error": "too_large"}, 413)
        if err == "invalid_json" or body is None:
            return self._json({"error": "invalid_json"}, 400)

        if method == 'POST' and path == '/api/tickets':
            return self._create_ticket(body)
        m = re.fullmatch(r'/api/tickets/(\d+)', path)
        if method == 'PATCH' and m:
            return self._update_ticket(int(m.group(1)), body)
        m = re.fullmatch(r'/api/tickets/(\d+)/tasks/(\d+)', path)
        if method == 'PATCH' and m:
            return self._toggle_task(int(m.group(1)), int(m.group(2)), body)
        m = re.fullmatch(r'/api/tickets/(\d+)/notes', path)
        if method == 'POST' and m:
            return self._add_note(int(m.group(1)), body)
        return self._json({"error": "not_found"}, 404)

    def _create_ticket(self, body):
        name = str(body.get('requester_name', ''))
        title = str(body.get('title', ''))
        text = str(body.get('body', ''))
        category = str(body.get('category', ''))
        priority = str(body.get('priority', 'orta'))
        source = str(body.get('source', 'self-service'))
        merchant = str(body.get('merchant', '')).strip()

        for chk, field in ((v_name(name), 'requester_name'),
                           (v_len(title, 10, 120, 'Başlık'), 'title'),
                           (v_len(text, 20, 2000, 'Açıklama'), 'body'),
                           (v_choice(category, CATEGORIES, 'Kategori'), 'category'),
                           (v_choice(priority, PRIORITIES, 'Öncelik'), 'priority'),
                           (v_choice(source, SOURCES, 'Kaynak'), 'source')):
            if chk:
                return self._json({"error": chk, "field": field}, 400)
        if merchant and len(merchant) > 80:
            return self._json({"error": "İşyeri adı en fazla 80 karakter olmalı.", "field": "merchant"}, 400)

        created = datetime.now()
        team = TEAM_ROUTING[category]
        with LOCK:
            data = load_data()
            data['seq'] += 1
            rec = {
                "id": data['seq'],
                "createdAt": created.replace(microsecond=0).isoformat(),
                "source": source,
                "requester_name": mask_name(name),
                "requester_initials": initials(name),
                "title": clean(title),
                "body": clean(text),
                "category": category,
                "priority": priority,
                "status": "yeni",
                "assignee_team": team,
                "assignee_user": None,
                "sla_due_at": _sla_due(created, priority).replace(microsecond=0).isoformat(),
                "sentiment": "notr",
                "merchant": clean(merchant) if merchant else None,
                "tasks": _make_tasks("yeni"),
                "approvals": _make_approvals(priority, "yeni"),
                "timeline": _make_timeline(name, created, "yeni", source),
                "audit": [{"at": now_iso(), "actor": "kullanici", "action": "ticket_created"}],
            }
            data['tickets'].append(rec)
            _write(data)
        return self._json(_decorate(rec), 201)

    def _update_ticket(self, tid, body):
        allowed_status = STATUSES
        with LOCK:
            data = load_data()
            t = next((x for x in data['tickets'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)

            if 'status' in body:
                new_status = str(body['status'])
                if new_status not in allowed_status:
                    return self._json({"error": "Geçersiz durum.", "field": "status"}, 400)
                old_status = t['status']
                t['status'] = new_status
                t['timeline'].append({
                    "at": now_iso(), "actor": "yonetici", "type": "durum_degisti",
                    "note": f"Durum '{STATUS_LABEL.get(old_status, old_status)}' -> "
                            f"'{STATUS_LABEL.get(new_status, new_status)}' olarak güncellendi.",
                })
                t['audit'].append({"at": now_iso(), "actor": "yonetici",
                                   "action": f"status:{old_status}->{new_status}"})

            if 'priority' in body:
                new_p = str(body['priority'])
                if new_p not in PRIORITIES:
                    return self._json({"error": "Geçersiz öncelik.", "field": "priority"}, 400)
                old_p = t['priority']
                t['priority'] = new_p
                created = _parse_dt(t['createdAt']) or datetime.now()
                t['sla_due_at'] = _sla_due(created, new_p).replace(microsecond=0).isoformat()
                t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "oncelik_degisti",
                                      "note": f"Öncelik '{PRIORITY_LABEL[old_p]}' -> '{PRIORITY_LABEL[new_p]}' olarak güncellendi."})
                t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": f"priority:{old_p}->{new_p}"})

            if 'assignee_team' in body:
                new_team = str(body['assignee_team'])
                if new_team not in TEAMS:
                    return self._json({"error": "Geçersiz ekip.", "field": "assignee_team"}, 400)
                old_team = t['assignee_team']
                t['assignee_team'] = new_team
                t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "ekip_degisti",
                                      "note": f"Ekip '{old_team}' -> '{new_team}' olarak yönlendirildi."})
                t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": f"team:{old_team}->{new_team}"})

            if 'assignee_user' in body:
                t['assignee_user'] = clean(str(body['assignee_user'])) if body['assignee_user'] else None

            _write(data)
        return self._json(_decorate(t))

    def _toggle_task(self, tid, task_idx, body):
        with LOCK:
            data = load_data()
            t = next((x for x in data['tickets'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)
            if not (0 <= task_idx < len(t['tasks'])):
                return self._json({"error": "not_found"}, 404)
            t['tasks'][task_idx]['done'] = bool(body.get('done', not t['tasks'][task_idx]['done']))
            t['audit'].append({"at": now_iso(), "actor": "yonetici",
                               "action": f"task[{task_idx}]:{t['tasks'][task_idx]['done']}"})
            _write(data)
        return self._json(_decorate(t))

    def _add_note(self, tid, body):
        text = str(body.get('note', ''))
        chk = v_len(text, 3, 500, 'Not')
        if chk:
            return self._json({"error": chk, "field": "note"}, 400)
        with LOCK:
            data = load_data()
            t = next((x for x in data['tickets'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)
            t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "not", "note": clean(text)})
            _write(data)
        return self._json(_decorate(t), 201)

    # --- statik dosyalar ---
    def _static(self, path):
        if path == '/' or path == '':
            path = '/index.html'
        rel = unquote(path).lstrip('/')
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT + os.sep) and full != os.path.join(ROOT, 'index.html'):
            return self._json({"error": "forbidden"}, 403)
        if not os.path.isfile(full):
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('404 Not Found'.encode('utf-8'))
            return
        ctype = self._ctype(full)
        try:
            with open(full, 'rb') as f:
                content = f.read()
        except OSError:
            return self._json({"error": "read_error"}, 500)
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    @staticmethod
    def _ctype(path):
        ext = os.path.splitext(path)[1].lower()
        return {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.svg': 'image/svg+xml',
            '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon',
        }.get(ext, 'application/octet-stream')


def main():
    load_data()
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Moka Akış klonu çalışıyor:  http://localhost:{PORT}")
    print(f"Talep listesi:              http://localhost:{PORT}/tickets.html")
    print(f"Kontrol paneli:              http://localhost:{PORT}/dashboard.html")
    print(f"Veri dosyası: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
        server.shutdown()


if __name__ == '__main__':
    main()
