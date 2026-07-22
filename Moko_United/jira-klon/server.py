#!/usr/bin/env python3
"""Moka Akış — Jira (iş/talep yönetimi) klonu (bkz. JIRA_KLON_ANALIZ.md).
Sıfır bağımlılık: yalnız Python stdlib. Statik dosyalar + JSON API aynı porttan.
Veri kalıcılığı: jira-klon/data/issues.json (atomic write + Lock).
Bu sürümde AI (sikayetvar/analysis.py) <-> issue bağlantısı YOKTUR (kasıtlı,
bkz. JIRA_KLON_ANALIZ.md §5/§10). Seed veri ve tüm içerik KURGUDUR.
Çalıştır: python3 jira-klon/server.py  ->  http://localhost:8780
"""
import json
import os
import re
import threading
import time
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'issues.json')
PORT = 8780
MAX_BODY = 16 * 1024
PROJECT_KEY = "MOKA"

LOCK = threading.Lock()
_RATE = {}

# ----------------------------------------------------------------------------
# Taksonomi (sikayetvar/analysis.py ile hizalı — ileride AI köprüsü bu değerleri
# doğrudan üretecek; bkz. JIRA_KLON_ANALIZ.md §5)
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

# kategori -> varsayılan issue türü (bkz. JIRA_KLON_ANALIZ.md §5)
CATEGORY_ISSUETYPE = {
    "Yetkisiz İşlem": "bug", "Para İadesi": "bug", "Komisyon & Ücret": "bug",
    "POS & Teslimat": "task", "Sanal POS & Başvuru": "task",
    "Müşteri Hizmetleri": "bug", "Uygulama & Teknik": "bug",
    "Ödeme Linki": "bug", "Dijital Cüzdan": "bug",
    "Hesap & Doğrulama": "task", "Mutabakat & Rapor": "bug",
    "Sözleşme & İptal": "task",
}

ISSUE_TYPES = ["bug", "task", "story", "epic", "subtask"]
ISSUE_TYPE_LABEL = {
    "bug": "Arıza/Şikayet", "task": "Görev", "story": "Talep",
    "epic": "Konu", "subtask": "Alt Görev",
}
ISSUE_TYPE_COLOR = {"bug": "red", "task": "blue", "story": "green", "epic": "purple", "subtask": "blue"}

PRIORITIES = ["dusuk", "orta", "yuksek", "kritik"]
PRIORITY_LABEL = {"dusuk": "Düşük", "orta": "Orta", "yuksek": "Yüksek", "kritik": "Kritik"}
# öncelik -> toplam akış SLA penceresi (saat)
SLA_HOURS = {"kritik": 4, "yuksek": 24, "orta": 72, "dusuk": 120}

STATUSES = ["yeni", "siniflandirildi", "atandi", "islemde", "beklemede",
            "cozuldu", "kapandi", "yeniden-acildi"]
STATUS_LABEL = {
    "yeni": "Yeni", "siniflandirildi": "Sınıflandırıldı", "atandi": "Atandı",
    "islemde": "Devam Ediyor", "beklemede": "Beklemede", "cozuldu": "Bitti",
    "kapandi": "Kapandı", "yeniden-acildi": "Yeniden Açıldı",
}
OPEN_STATUSES = {"yeni", "siniflandirildi", "atandi", "islemde", "beklemede", "yeniden-acildi"}
# durum -> lozenge renk kategorisi (bkz. JIRA_KLON_ANALIZ.md §3.1)
STATUS_CATEGORY = {
    "yeni": "new", "siniflandirildi": "default", "atandi": "default",
    "islemde": "inprogress", "beklemede": "moved",
    "cozuldu": "success", "kapandi": "success", "yeniden-acildi": "removed",
}
SOURCES = ["ai", "self-service", "email", "chat", "whatsapp"]
SOURCE_LABEL = {"ai": "Yapay Zeka", "self-service": "Self-Servis", "email": "E-posta",
                "chat": "Canlı Destek", "whatsapp": "WhatsApp"}
SENTIMENTS = ["ofkeli", "olumsuz", "notr", "olumlu"]
SENTIMENT_LABEL = {"ofkeli": "Öfkeli", "olumsuz": "Olumsuz", "notr": "Nötr", "olumlu": "Olumlu"}

# durum makinesi: her durumdan hangi durumlara geçilebilir. Aynı duruma "geçiş" her zaman izinlidir (no-op).
ALLOWED_TRANSITIONS = {
    "yeni": {"siniflandirildi", "kapandi"},
    "siniflandirildi": {"yeni", "atandi", "kapandi"},
    "atandi": {"siniflandirildi", "islemde", "beklemede"},
    "islemde": {"atandi", "beklemede", "cozuldu"},
    "beklemede": {"atandi", "islemde"},
    "cozuldu": {"kapandi", "yeniden-acildi"},
    "kapandi": {"yeniden-acildi"},
    "yeniden-acildi": {"atandi", "islemde"},
}

TR_LETTERS = "A-Za-zÇĞİıÖŞÜçğıöşü"
NAME_RE = re.compile(f"^[{TR_LETTERS} .'-]+$")
LABEL_RE = re.compile(r"^[a-z0-9\-]{2,30}$")

# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------
def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()

def clean(s):
    """Girdiyi yalnızca kırpar (strip); HTML-escape burada YAPILMAZ.
    Tek escape noktası istemcidir (assets/js/components.js MokaUI.esc, render sırasında).
    Burada da escape edilirse çift-escape oluşur (bkz. JIRA_KLON_ANALIZ.md §11.1 F1)."""
    return str(s).strip()

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

def sla_state_of(issue, now=None):
    """ok | risk | breach — kapanmış/çözülmüş taleplerde her zaman 'ok'."""
    now = now or datetime.now()
    if issue['status'] in ('cozuldu', 'kapandi'):
        return 'ok'
    due = _parse_dt(issue.get('sla_due_at', ''))
    created = _parse_dt(issue.get('createdAt', ''))
    if not due or not created:
        return 'ok'
    if now >= due:
        return 'breach'
    total = (due - created).total_seconds()
    remaining = (due - now).total_seconds()
    if total > 0 and remaining / total <= 0.2:
        return 'risk'
    return 'ok'

def sla_remaining_label(issue, now=None):
    now = now or datetime.now()
    due = _parse_dt(issue.get('sla_due_at', ''))
    if not due:
        return '—'
    if issue['status'] in ('cozuldu', 'kapandi'):
        return 'tamamlandı'
    delta = due - now
    hours = delta.total_seconds() / 3600
    if hours < 0:
        return f"{abs(hours):.0f} sa. gecikti"
    if hours < 1:
        return f"{int(delta.total_seconds() / 60)} dk. kaldı"
    return f"{hours:.0f} sa. kaldı"

def _auto_labels(category, merchant):
    """Basit, deterministik otomatik etiketleme: aynı işyerinden gelen yetkisiz işlem
    şikayetleri olası bir dolandırıcılık halkasını işaret eder (demo senaryosu)."""
    labels = []
    if category == "Yetkisiz İşlem" and merchant:
        labels.append("olasi-fraud-ring")
    return labels

# ----------------------------------------------------------------------------
# Seed (tamamen kurgu içerik)
# ----------------------------------------------------------------------------
# (isim, özet, açıklama, kategori, öncelik, durum, kaç_saat_önce, işyeri, kaynak, duygu)
SEED_ISSUES = [
    ("Zeynep Kaya", "Kartımdan onayım olmadan tahsilat yapıldı",
     "Hızlı Ödeme Bayii'nde benim başlatmadığım bir işlem gerçekleşmiş, itiraz ediyorum.",
     "Yetkisiz İşlem", "kritik", "yeni", 6, "Hızlı Ödeme Bayii", "ai", "ofkeli"),
    ("Emre Aydın", "Yetkisiz işlem: kartımdan habersiz tahsilat",
     "Hızlı Ödeme Bayii üzerinden hesabımdan izinsiz bir çekim yapılmış.",
     "Yetkisiz İşlem", "kritik", "islemde", 20, "Hızlı Ödeme Bayii", "ai", "ofkeli"),
    ("Mehmet Yıldız", "Para iadem 10 gündür yapılmadı",
     "İptal ettiğim işlemin iadesi onaylandı görünüyor ama kartıma yansımadı.",
     "Para İadesi", "yuksek", "islemde", 22, None, "self-service", "olumsuz"),
    ("Elif Su", "Müşteri hizmetlerine bir türlü ulaşamıyorum",
     "Çağrı merkezini defalarca aradım, hat düşüyor, canlı destek de yanıt vermiyor.",
     "Müşteri Hizmetleri", "orta", "beklemede", 30, None, "chat", "olumsuz"),
    ("Can Turan", "Link ile ödeme sayfası açılmıyor",
     "Müşterilerime gönderdiğim ödeme linki bazı cihazlarda hata veriyor.",
     "Ödeme Linki", "yuksek", "atandi", 10, None, "email", "olumsuz"),
    ("Selin Arda", "Hesap doğrulama süreci çok uzadı",
     "Gerekli tüm evrakları yükledim ancak hesabım hâlâ onaylanmadı.",
     "Hesap & Doğrulama", "orta", "islemde", 48, None, "self-service", "olumsuz"),
    ("Burak Öz", "Dijital cüzdan bakiyem aktarılmadı",
     "Cüzdanımdaki bakiyeyi banka hesabıma aktarmak istedim, işlem askıda kaldı.",
     "Dijital Cüzdan", "yuksek", "yeni", 3, None, "whatsapp", "olumsuz"),
    ("Deniz Kara", "Uygulama sürekli hata veriyor",
     "Son güncellemeden sonra uygulamaya giriş yapamıyorum, ödeme alırken kapanıyor.",
     "Uygulama & Teknik", "orta", "atandi", 14, None, "ai", "olumsuz"),
    ("Gökhan Ma", "Sanal POS başvurum haftalardır sonuçlanmadı",
     "Başvuru yaptığımda 3 iş günü içinde dönüş yapılacağı belirtilmişti, üç hafta oldu.",
     "Sanal POS & Başvuru", "orta", "cozuldu", 96, None, "email", "notr"),
    ("Aylin Rüz", "Gün sonu mutabakatı tutmuyor",
     "Panelde görünen işlem tutarları ile hesabıma geçen tutarlar farklı.",
     "Mutabakat & Rapor", "yuksek", "islemde", 26, None, "self-service", "olumsuz"),
    ("Kerem Bal", "Sözleşmeyi iptal etmek istiyorum ama edemiyorum",
     "Hizmeti kullanmayı bırakmak istiyorum fakat panelde iptal seçeneği yok.",
     "Sözleşme & İptal", "dusuk", "beklemede", 60, None, "chat", "notr"),
    ("Merve İl", "İşlem ücreti hakkında bilgilendirilmedim",
     "Hesabımdan adını bilmediğim bir işlem ücreti kesilmiş.",
     "Komisyon & Ücret", "orta", "cozuldu", 80, None, "self-service", "notr"),
    ("Okan Ba", "Bilgim dışında hesabımdan üyelik ücreti çekilmiş",
     "Onaylamadığım bir üyelik için hesabımdan aylık ücret kesilmeye başlanmış.",
     "Yetkisiz İşlem", "kritik", "siniflandirildi", 2, "Yıldız Elektronik", "ai", "ofkeli"),
    ("Sibel Ak", "Kartımdan onayım olmadan tahsilat yapıldı",
     "Kartımdan başlatmadığım bir işlem için tahsilat gerçekleştirilmiş.",
     "Yetkisiz İşlem", "kritik", "cozuldu", 130, "Yıldız Elektronik", "ai", "olumlu"),
    ("Tolga En", "POS cihazım hâlâ teslim edilmedi",
     "Sanal POS onayının ardından fiziki POS cihazının 3 iş günü içinde teslim edileceği söylendi.",
     "POS & Teslimat", "dusuk", "kapandi", 200, None, "email", "olumlu"),
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
    issues = []
    seq = 0
    for name, summary, description, category, priority, status, hours_ago, merchant, source, sentiment in SEED_ISSUES:
        seq += 1
        created = datetime.now() - timedelta(hours=hours_ago)
        team = TEAM_ROUTING[category]
        resolved_at = None
        if status in ("cozuldu", "kapandi"):
            resolved_at = (created + timedelta(hours=hours_ago * 0.6)).replace(microsecond=0).isoformat()
        issues.append({
            "id": seq,
            "issuetype": CATEGORY_ISSUETYPE[category],
            "createdAt": created.replace(microsecond=0).isoformat(),
            "source": source,
            "reporter_name": mask_name(name),
            "reporter_initials": initials(name),
            "summary": clean(summary),
            "description": clean(description),
            "category": category,
            "labels": _auto_labels(category, merchant),
            "priority": priority,
            "status": status,
            "assignee_team": team,
            "assignee_user": None,
            "story_points": None,
            "sla_due_at": _sla_due(created, priority).replace(microsecond=0).isoformat(),
            "resolved_at": resolved_at,
            "sentiment": sentiment,
            "merchant": merchant,
            "attachments": [],
            "tasks": _make_tasks(status),
            "approvals": _make_approvals(priority, status),
            "timeline": _make_timeline(name, created, status, source),
            "audit": [{"at": created.replace(microsecond=0).isoformat(), "actor": "sistem",
                      "action": "issue_created"}],
        })
    return {"seq": seq, "issues": issues}

# ----------------------------------------------------------------------------
# Kalıcılık
# ----------------------------------------------------------------------------
_CACHE = None  # bellek-içi önbellek — her istekte disk okumayı önler

def load_data():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not os.path.exists(DATA_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        data = build_seed()
        _write(data)
        return data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        _CACHE = json.load(f)
    return _CACHE

def _write(data):
    global _CACHE
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)
    _CACHE = data

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

def v_labels(labels):
    if not isinstance(labels, list):
        return "Etiketler bir liste olmalı."
    if len(labels) > 5:
        return "En fazla 5 etiket eklenebilir."
    for l in labels:
        if not isinstance(l, str) or not LABEL_RE.match(l):
            return "Etiketler yalnızca küçük harf/rakam/tire içerebilir (2-30 karakter)."
    return None

# ----------------------------------------------------------------------------
# Sunum katmanı yardımcıları
# ----------------------------------------------------------------------------
def _decorate(t):
    """Ham kayda türetilmiş (computed) alanları ekler: key, status_category, sla, label'lar."""
    now = datetime.now()
    out = dict(t)
    out["key"] = f"{PROJECT_KEY}-{t['id']}"
    out["sla_state"] = sla_state_of(t, now)
    out["sla_remaining"] = sla_remaining_label(t, now)
    out["status_label"] = STATUS_LABEL.get(t["status"], t["status"])
    out["status_category"] = STATUS_CATEGORY.get(t["status"], "default")
    out["priority_label"] = PRIORITY_LABEL.get(t["priority"], t["priority"])
    out["issuetype_label"] = ISSUE_TYPE_LABEL.get(t.get("issuetype"), t.get("issuetype"))
    out["source_label"] = SOURCE_LABEL.get(t.get("source"), t.get("source"))
    return out

def compute_dashboard(issues):
    """KPI + dağılım verisi (dashboard.html için)."""
    total = len(issues)
    now = datetime.now()
    decorated = [_decorate(t) for t in issues]
    open_count = sum(1 for t in decorated if t['status'] in OPEN_STATUSES)
    closed_count = total - open_count
    breach_count = sum(1 for t in decorated if t['sla_state'] == 'breach')
    risk_count = sum(1 for t in decorated if t['sla_state'] == 'risk')

    by_status = {s: 0 for s in STATUSES}
    for t in decorated:
        by_status[t['status']] += 1
    status_dist = [{"status": s, "label": STATUS_LABEL[s], "category": STATUS_CATEGORY[s], "count": by_status[s]}
                   for s in STATUSES if by_status[s]]

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

    by_issuetype = {it: 0 for it in ISSUE_TYPES}
    for t in decorated:
        by_issuetype[t.get('issuetype', 'task')] += 1
    issuetype_dist = [{"issuetype": it, "label": ISSUE_TYPE_LABEL[it], "count": by_issuetype[it]}
                       for it in ISSUE_TYPES if by_issuetype[it]]

    open_ages = [(now - _parse_dt(t['createdAt'])).total_seconds() / 3600
                 for t in decorated if t['status'] in OPEN_STATUSES and _parse_dt(t['createdAt'])]
    avg_open_age_hours = round(sum(open_ages) / len(open_ages), 1) if open_ages else None

    resolution_times = []
    for t in decorated:
        if t.get('resolved_at'):
            c, r = _parse_dt(t['createdAt']), _parse_dt(t['resolved_at'])
            if c and r:
                resolution_times.append((r - c).total_seconds() / 3600)
    avg_resolution_hours = round(sum(resolution_times) / len(resolution_times), 1) if resolution_times else None

    by_sentiment = {s: 0 for s in SENTIMENTS}
    for t in decorated:
        by_sentiment[t.get('sentiment', 'notr')] += 1
    sentiment_dist = [{"sentiment": s, "label": SENTIMENT_LABEL[s], "count": by_sentiment[s]} for s in SENTIMENTS if by_sentiment[s]]

    return {
        "generated_at": now.replace(microsecond=0).isoformat(),
        "kpis": {
            "total": total, "open": open_count, "closed": closed_count,
            "sla_breach": breach_count, "sla_risk": risk_count,
            "avg_open_age_hours": avg_open_age_hours,
            "avg_resolution_hours": avg_resolution_hours,
        },
        "status_dist": status_dist,
        "team_load": team_load,
        "priority_dist": priority_dist,
        "category_dist": category_dist,
        "issuetype_dist": issuetype_dist,
        "sentiment_dist": sentiment_dist,
    }

PAGE_SIZE = 10

# ----------------------------------------------------------------------------
# HTTP Handler
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "JiraKlon/1.0"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
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
            for other_ip in list(_RATE.keys()):
                if other_ip == ip:
                    continue
                pruned = [t for t in _RATE[other_ip] if now - t < 60]
                if pruned:
                    _RATE[other_ip] = pruned
                else:
                    del _RATE[other_ip]
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
                "project_key": PROJECT_KEY,
                "categories": CATEGORIES, "teams": TEAMS, "priorities": PRIORITIES,
                "priority_label": PRIORITY_LABEL, "statuses": STATUSES,
                "status_label": STATUS_LABEL, "status_category": STATUS_CATEGORY,
                "sources": SOURCES, "source_label": SOURCE_LABEL,
                "allowed_transitions": {k: sorted(v) for k, v in ALLOWED_TRANSITIONS.items()},
                "sentiment_label": SENTIMENT_LABEL,
                "issue_types": ISSUE_TYPES, "issuetype_label": ISSUE_TYPE_LABEL,
                "issuetype_color": ISSUE_TYPE_COLOR,
                "category_issuetype": CATEGORY_ISSUETYPE,
                "category_team": TEAM_ROUTING,
            })
        if path == '/api/dashboard':
            with LOCK:
                data = load_data()
            return self._json(compute_dashboard(data['issues']))
        if path == '/api/issues':
            return self._list_issues(qs)
        m = re.fullmatch(r'/api/issues/(\d+)', path)
        if m:
            return self._get_issue(int(m.group(1)))
        return self._json({"error": "not_found"}, 404)

    def _list_issues(self, qs):
        def q1(key, default=''):
            return (qs.get(key, [default])[0] or '').strip()
        status = q1('status')
        category = q1('category')
        team = q1('team')
        source = q1('source')
        sla = q1('sla')
        issuetype = q1('issuetype')
        priority = q1('priority')
        search = q1('q')
        page = max(1, int(q1('page', '1') or 1))
        page_size = min(200, max(1, int(q1('pageSize', str(PAGE_SIZE)) or PAGE_SIZE)))

        with LOCK:
            data = load_data()
            items = list(reversed(data['issues']))
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
        if issuetype:
            items = [t for t in items if t['issuetype'] == issuetype]
        if priority:
            items = [t for t in items if t['priority'] == priority]
        if search:
            nq = tr_lower(search)
            items = [t for t in items if nq in tr_lower(t['summary']) or nq in tr_lower(t['description'])
                     or nq in tr_lower(t['key'])]

        total = len(items)
        start = (page - 1) * page_size
        page_items = items[start:start + page_size]
        return self._json({
            "total": total, "page": page, "pageSize": page_size,
            "totalPages": max(1, (total + page_size - 1) // page_size),
            "items": page_items,
        })

    def _get_issue(self, tid):
        with LOCK:
            data = load_data()
            t = next((x for x in data['issues'] if x['id'] == tid), None)
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

        if method == 'POST' and path == '/api/issues':
            return self._create_issue(body)
        m = re.fullmatch(r'/api/issues/(\d+)', path)
        if method == 'PATCH' and m:
            return self._update_issue(int(m.group(1)), body)
        m = re.fullmatch(r'/api/issues/(\d+)/tasks/(\d+)', path)
        if method == 'PATCH' and m:
            return self._toggle_task(int(m.group(1)), int(m.group(2)), body)
        m = re.fullmatch(r'/api/issues/(\d+)/notes', path)
        if method == 'POST' and m:
            return self._add_note(int(m.group(1)), body)
        m = re.fullmatch(r'/api/issues/(\d+)/approvals/(\d+)', path)
        if method == 'PATCH' and m:
            return self._update_approval(int(m.group(1)), int(m.group(2)), body)
        m = re.fullmatch(r'/api/issues/(\d+)/attachments', path)
        if method == 'POST' and m:
            return self._add_attachment(int(m.group(1)), body)
        return self._json({"error": "not_found"}, 404)

    def _create_issue(self, body):
        name = str(body.get('reporter', ''))
        summary = str(body.get('summary', ''))
        description = str(body.get('description', ''))
        category = str(body.get('category', ''))
        priority = str(body.get('priority', 'orta'))
        source = str(body.get('source', 'self-service'))
        merchant = str(body.get('merchant', '')).strip()
        issuetype = str(body.get('issuetype', '')) or CATEGORY_ISSUETYPE.get(category, 'task')
        labels = body.get('labels', [])
        # Normalde her issue "yeni" ile başlar; entegrasyonlar (ör. itiraz sistemi) doğrudan
        # belirli bir durumla (ör. "beklemede") oluşturabilsin diye opsiyonel override.
        initial_status = str(body.get('status', 'yeni'))
        if initial_status not in STATUSES:
            initial_status = 'yeni'

        for chk, field in ((v_name(name), 'reporter'),
                           (v_len(summary, 10, 120, 'Özet'), 'summary'),
                           (v_len(description, 20, 2000, 'Açıklama'), 'description'),
                           (v_choice(category, CATEGORIES, 'Kategori'), 'category'),
                           (v_choice(priority, PRIORITIES, 'Öncelik'), 'priority'),
                           (v_choice(source, SOURCES, 'Kaynak'), 'source'),
                           (v_choice(issuetype, ISSUE_TYPES, 'Issue türü'), 'issuetype'),
                           (v_labels(labels), 'labels')):
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
                "issuetype": issuetype,
                "createdAt": created.replace(microsecond=0).isoformat(),
                "source": source,
                "reporter_name": mask_name(name),
                "reporter_initials": initials(name),
                "summary": clean(summary),
                "description": clean(description),
                "category": category,
                "labels": list(labels) + _auto_labels(category, merchant),
                "priority": priority,
                "status": initial_status,
                "assignee_team": team,
                "assignee_user": None,
                "story_points": None,
                "sla_due_at": _sla_due(created, priority).replace(microsecond=0).isoformat(),
                "resolved_at": None,
                "sentiment": "notr",
                "merchant": clean(merchant) if merchant else None,
                "attachments": [],
                "tasks": _make_tasks(initial_status),
                "approvals": _make_approvals(priority, initial_status),
                "timeline": _make_timeline(name, created, initial_status, source),
                "audit": [{"at": now_iso(), "actor": "kullanici", "action": "issue_created"}],
            }
            data['issues'].append(rec)
            _write(data)
        return self._json(_decorate(rec), 201)

    def _update_issue(self, tid, body):
        with LOCK:
            data = load_data()
            t = next((x for x in data['issues'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)

            if 'summary' in body:
                new_summary = str(body['summary'])
                chk = v_len(new_summary, 10, 120, 'Özet')
                if chk:
                    return self._json({"error": chk, "field": "summary"}, 400)
                old_summary = t['summary']
                new_summary = clean(new_summary)
                if new_summary != old_summary:
                    t['summary'] = new_summary
                    t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "ozet_degisti",
                                          "note": "Özet güncellendi."})
                    t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": "summary_updated"})

            if 'description' in body:
                new_desc = str(body['description'])
                chk = v_len(new_desc, 20, 2000, 'Açıklama')
                if chk:
                    return self._json({"error": chk, "field": "description"}, 400)
                old_desc = t['description']
                new_desc = clean(new_desc)
                if new_desc != old_desc:
                    t['description'] = new_desc
                    t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "aciklama_degisti",
                                          "note": "Açıklama güncellendi."})
                    t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": "description_updated"})

            if 'status' in body:
                new_status = str(body['status'])
                if new_status not in STATUSES:
                    return self._json({"error": "Geçersiz durum.", "field": "status"}, 400)
                old_status = t['status']
                if new_status != old_status:
                    if new_status not in ALLOWED_TRANSITIONS.get(old_status, set()):
                        return self._json({
                            "error": f"'{STATUS_LABEL.get(old_status, old_status)}' durumundan "
                                     f"'{STATUS_LABEL.get(new_status, new_status)}' durumuna geçiş yapılamaz.",
                            "field": "status",
                        }, 400)
                    t['status'] = new_status
                    t['timeline'].append({
                        "at": now_iso(), "actor": "yonetici", "type": "durum_degisti",
                        "note": f"Durum '{STATUS_LABEL.get(old_status, old_status)}' -> "
                                f"'{STATUS_LABEL.get(new_status, new_status)}' olarak güncellendi.",
                    })
                    t['audit'].append({"at": now_iso(), "actor": "yonetici",
                                       "action": f"status:{old_status}->{new_status}"})
                    if new_status in ("cozuldu", "kapandi"):
                        t['resolved_at'] = now_iso()
                    elif old_status in ("cozuldu", "kapandi"):
                        t['resolved_at'] = None

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
                raw = str(body['assignee_user']).strip()
                if len(raw) > 60:
                    return self._json({"error": "Atanan kişi adı en fazla 60 karakter olmalı.", "field": "assignee_user"}, 400)
                old_user = t.get('assignee_user')
                new_user = clean(raw) if raw else None
                if new_user != old_user:
                    t['assignee_user'] = new_user
                    t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "kisi_degisti",
                                          "note": f"Atanan kişi '{old_user or '—'}' -> '{new_user or '—'}' olarak güncellendi."})
                    t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": f"assignee_user:{old_user}->{new_user}"})

            if 'labels' in body:
                chk = v_labels(body['labels'])
                if chk:
                    return self._json({"error": chk, "field": "labels"}, 400)
                old_labels = t.get('labels', [])
                new_labels = list(body['labels'])
                if new_labels != old_labels:
                    t['labels'] = new_labels
                    t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": "labels_updated"})

            if 'story_points' in body:
                raw_sp = body['story_points']
                if raw_sp is not None:
                    try:
                        raw_sp = int(raw_sp)
                        if not (0 <= raw_sp <= 100):
                            raise ValueError
                    except (TypeError, ValueError):
                        return self._json({"error": "Puan 0-100 arası bir sayı olmalı.", "field": "story_points"}, 400)
                t['story_points'] = raw_sp

            _write(data)
        return self._json(_decorate(t))

    def _update_approval(self, tid, idx, body):
        new_state = str(body.get('state', ''))
        if new_state not in ('onaylandi', 'reddedildi', 'bekliyor'):
            return self._json({"error": "Geçersiz onay durumu.", "field": "state"}, 400)
        with LOCK:
            data = load_data()
            t = next((x for x in data['issues'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)
            if not (0 <= idx < len(t['approvals'])):
                return self._json({"error": "not_found"}, 404)
            old_state = t['approvals'][idx]['state']
            role = t['approvals'][idx]['role']
            t['approvals'][idx]['state'] = new_state
            label = {"onaylandi": "onaylandı", "reddedildi": "reddedildi", "bekliyor": "bekliyor"}[new_state]
            t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "onay_degisti",
                                  "note": f"{role} onayı '{label}' olarak güncellendi."})
            t['audit'].append({"at": now_iso(), "actor": "yonetici",
                               "action": f"approval[{idx}]:{old_state}->{new_state}"})
            _write(data)
        return self._json(_decorate(t))

    def _toggle_task(self, tid, task_idx, body):
        with LOCK:
            data = load_data()
            t = next((x for x in data['issues'] if x['id'] == tid), None)
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
            t = next((x for x in data['issues'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)
            t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "not", "note": clean(text)})
            _write(data)
        return self._json(_decorate(t), 201)

    def _add_attachment(self, tid, body):
        """Minimal ek listesi: yalnızca ad/etiket kaydeder, gerçek dosya yükleme yoktur."""
        name = str(body.get('name', ''))
        chk = v_len(name, 2, 80, 'Ek adı')
        if chk:
            return self._json({"error": chk, "field": "name"}, 400)
        with LOCK:
            data = load_data()
            t = next((x for x in data['issues'] if x['id'] == tid), None)
            if not t:
                return self._json({"error": "not_found"}, 404)
            clean_name = clean(name)
            t.setdefault('attachments', []).append({"name": clean_name, "addedAt": now_iso()})
            t['timeline'].append({"at": now_iso(), "actor": "yonetici", "type": "ek_eklendi",
                                  "note": f"Ek eklendi: {clean_name}"})
            t['audit'].append({"at": now_iso(), "actor": "yonetici", "action": "attachment_added"})
            _write(data)
        return self._json(_decorate(t), 201)

    # --- statik dosyalar ---
    def _static(self, path):
        if path == '/' or path == '':
            path = '/board.html'
        rel = unquote(path).lstrip('/')
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT + os.sep) and full != os.path.join(ROOT, 'board.html'):
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
        self.send_header('X-Content-Type-Options', 'nosniff')
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
            '.woff2': 'font/woff2',
            '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon',
        }.get(ext, 'application/octet-stream')


def main():
    load_data()
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    print(f"Moka Akış (Jira klonu) çalışıyor:  http://localhost:{PORT}")
    print(f"Pano:                              http://localhost:{PORT}/board.html")
    print(f"Liste:                             http://localhost:{PORT}/list.html")
    print(f"Kontrol paneli:                    http://localhost:{PORT}/dashboard.html")
    print(f"Veri dosyası: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
        server.shutdown()


if __name__ == '__main__':
    main()
