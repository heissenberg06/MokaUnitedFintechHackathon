#!/usr/bin/env python3
"""Şikayetvar — Moka United şikayet sayfası klonu.
Sıfır bağımlılık: yalnız Python stdlib. Statik dosyalar + JSON API aynı porttan.
Veri kalıcılığı: sikayetvar/data/complaints.json (atomic write + Lock).
Seed ve tüm içerik KURGUDUR; gerçek şikayet metni/rumuz kullanılmaz.
Yeni şikayet gönderildiğinde sikayet_api'deki (port 8020) eğitilmiş sınıflandırıcı
çağrılır ve otomatik "Marka Yanıtı" yorumu olarak eklenir (bkz. get_auto_reply).
Çalıştır: python3 sikayetvar/server.py  ->  http://localhost:8756
"""
import json
import os
import html
import re
import time
import threading
import random
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

import analysis  # Moka Müşteri Zeka Motoru (deterministik + opsiyonel yerel LLM)

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'complaints.json')
PORT = 8756
MAX_BODY = 16 * 1024  # 16KB

# --- Otomatik sınıflandırma/cevap servisi (sikayet_api.py, ayrı süreç) ---
SIKAYET_API_URL = "http://localhost:8020/cevapla"
SIKAYET_API_TIMEOUT = 8  # saniye
# Bu sınıflarda sablonlar.py talebi ekibe yönlendirdiğini söylüyor -> otomatik kapatılmaz.
NEEDS_HUMAN_REVIEW = {"dolandiricilik_suphesi", "cuzdan_hesap_sorunu"}

LOCK = threading.Lock()
_RATE = {}  # ip -> [timestamps]

def get_auto_reply(text):
    """sikayet_api'yi çağırır; servis kapalıysa/hata verirse None döner (akış kesilmez)."""
    try:
        payload = json.dumps({"sikayet_metni": text}).encode('utf-8')
        req = urllib.request.Request(
            SIKAYET_API_URL, data=payload,
            headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=SIKAYET_API_TIMEOUT) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None

# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------
TR_LETTERS = "A-Za-zÇĞİıÖŞÜçğıöşü"
NAME_RE = re.compile(f"^[{TR_LETTERS} .'-]+$")

def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()

def mask_name(name):
    """'Ahmet Kaya' -> 'A** K**'  (Şikayetvar tarzı maskeleme; ham ad saklanmaz)."""
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

def clean(s):
    """Sunucu tarafı XSS savunması: her string girdi HTML-escape edilir."""
    return html.escape(str(s).strip())

# ----------------------------------------------------------------------------
# Seed (tamamen kurgu içerik)
# ----------------------------------------------------------------------------
SEED_COMPLAINTS = [
    ("Ahmet K.", "POS cihazım hâlâ teslim edilmedi",
     "Sanal POS başvurumun onaylanmasının ardından fiziki POS cihazımın 3 iş günü içinde teslim edileceği söylenmişti. Aradan iki hafta geçmesine rağmen cihaz elime ulaşmadı ve müşteri hizmetlerinden net bir tarih alamıyorum.",
     "cozuldu", True,
     "Merhaba, yaşadığınız gecikme için özür dileriz. Başvuru numaranızı özelden ilettiğinizde kargo sürecini hızlandıracağız."),
    ("Zeynep D.", "Komisyon oranı sözleşmedekinden yüksek kesildi",
     "İş yeri sözleşmemizde belirtilen komisyon oranı ile ay sonunda hesabımdan kesilen tutar birbirini tutmuyor. Aradaki farkın gerekçesini ve iadesini talep ediyorum.",
     "yanit-bekliyor", False, None),
    ("Mehmet Y.", "Para iadem 10 gündür yapılmadı",
     "İptal ettiğim bir işlemin iadesi ekranda onaylandı görünmesine rağmen kartıma hâlâ yansımadı. 10 gündür bekliyorum, bilgi alamıyorum.",
     "cozuldu", True,
     "İadeniz bankanız tarafından işleme alınmış olup 1-2 iş günü içinde kartınıza yansıyacaktır. İlginiz için teşekkürler."),
    ("Elif S.", "Müşteri hizmetlerine bir türlü ulaşamıyorum",
     "Çağrı merkezini defalarca aradım, uzun bekleme sürelerinden sonra hat düşüyor. Canlı destek de yanıt vermiyor. Acil bir sorunum var ve kimseye ulaşamıyorum.",
     "yanit-bekliyor", False, None),
    ("Can T.", "Link ile ödeme sayfası açılmıyor",
     "Müşterilerime gönderdiğim ödeme linki bazı cihazlarda hata veriyor ve ödeme alamıyorum. Bu durum satışlarımı doğrudan etkiliyor.",
     "yanit-bekliyor", False, None),
    ("Selin A.", "Hesap doğrulama süreci çok uzadı",
     "Gerekli tüm evrakları eksiksiz yükledim ancak hesabım hâlâ onaylanmadı. Her aradığımda 'inceleniyor' yanıtı alıyorum, süreç günlerdir ilerlemiyor.",
     "cozuldu", True,
     "Belgeleriniz kontrol edilip hesabınız aktifleştirilmiştir. Yaşattığımız gecikme için teşekkür ve özürlerimizi sunarız."),
    ("Burak Ö.", "Dijital cüzdan bakiyem aktarılmadı",
     "Cüzdanımdaki bakiyeyi banka hesabıma aktarmak istedim, tutar cüzdandan düştü ama hesabıma geçmedi. İşlem askıda kaldı.",
     "yanit-bekliyor", False, None),
    ("Deniz K.", "Uygulama sürekli hata veriyor",
     "Son güncellemeden sonra uygulamaya giriş yapamıyorum, işlem geçmişim görünmüyor ve ödeme alırken uygulama kapanıyor.",
     "yanit-bekliyor", False, None),
    ("Gökhan M.", "Sanal POS başvurum haftalardır sonuçlanmadı",
     "Başvuru yaptığımda 3 iş günü içinde dönüş yapılacağı belirtilmişti. Üç hafta oldu, başvurumun durumu hakkında hiçbir bilgi verilmiyor.",
     "cozuldu", True,
     "Başvurunuz onaylanmış olup panel giriş bilgileriniz e-posta adresinize iletilmiştir. İlginiz için teşekkür ederiz."),
    ("Aylin R.", "Gün sonu mutabakatı tutmuyor",
     "Panelde görünen işlem tutarları ile hesabıma geçen tutarlar farklı. Gün sonu raporlarında eksik işlemler var, mutabakat sağlayamıyorum.",
     "yanit-bekliyor", False, None),
    ("Kerem B.", "Sözleşmeyi iptal etmek istiyorum ama edemiyorum",
     "Hizmeti kullanmayı bırakmak ve sözleşmemi feshetmek istiyorum fakat panelde bir iptal seçeneği yok, destek ekibi de yönlendirme yapmıyor.",
     "yanit-bekliyor", False, None),
    ("Merve İ.", "İşlem ücreti hakkında bilgilendirilmedim",
     "Hesabımdan adını bilmediğim bir işlem ücreti kesilmiş. Sözleşmede böyle bir kalem göremedim, bu kesintinin ne olduğunu öğrenmek istiyorum.",
     "cozuldu", True,
     "Söz konusu ücret aylık hizmet bedeli olup sözleşmenizde yer almaktadır. Detaylı dökümü e-posta ile paylaştık, teşekkürler."),
    # --- "yetkisiz işlem" temalı KURGU şikayetler (2. tur, tamamen uydurma metin; en güncel) ---
    ("Okan B.", "Bilgim dışında hesabımdan üyelik ücreti çekilmiş",
     "Onayladığımı hatırlamadığım bir üyelik için hesabımdan aylık ücret kesilmeye başlanmış. Böyle bir hizmeti hiç talep etmedim; kesintinin durdurulmasını ve iadesini istiyorum.",
     "yanit-bekliyor", False, None),
    ("Sibel A.", "Kartımdan onayım olmadan tahsilat yapıldı",
     "Kartımdan, benim başlatmadığım bir işlem için tahsilat gerçekleştirilmiş. İşlemin kaynağını ve nasıl iptal edileceğini öğrenmek, tutarın iadesini talep etmek istiyorum.",
     "cozuldu", True,
     "Merhaba, bildirdiğiniz işlem incelenmiş olup itirazınız işleme alınmıştır. İlgili tutar en kısa sürede kartınıza iade edilecektir."),
    ("Tolga E.", "Tanımadığım bir işlem için hesabımdan kesinti yapıldı",
     "Ekstremde tanımadığım bir işlem gördüm; ne olduğuna dair hiçbir bilgilendirme almadım. Bu kesintinin ne olduğunun açıklanmasını ve yetkisiz ise iadesini istiyorum.",
     "yanit-bekliyor", False, None),
]

def build_seed():
    complaints = []
    seq = 0
    n = len(SEED_COMPLAINTS)
    for i, (name, title, body, status, has_reply, reply) in enumerate(SEED_COMPLAINTS):
        seq += 1
        # tarihleri son 30 güne yay; liste id-tersine gösterildiği için
        # son eklenen (yüksek index) EN GÜNCEL tarihi alır → üstteki kart en yeni görünür
        created = datetime.now() - timedelta(days=(n - 1 - i) * 2 + random.randint(0, 1),
                                             hours=random.randint(0, 23),
                                             minutes=random.randint(0, 59))
        comments = []
        if has_reply and reply:
            comments.append({
                "id": 1,
                "name": "Moka United",
                "isBrand": True,
                "body": clean(reply),
                "createdAt": (created + timedelta(hours=random.randint(2, 20))).replace(microsecond=0).isoformat(),
            })
        complaints.append({
            "id": seq,
            "name": mask_name(name),
            "initials": initials(name),
            "title": clean(title),
            "body": clean(body),
            "createdAt": created.replace(microsecond=0).isoformat(),
            "views": random.randint(20, 400),
            "supports": random.randint(0, 45),
            "status": status,
            "comments": comments,
        })
    return {"seq": seq, "complaints": complaints}

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
    """Atomic write: tmp'ye yaz -> os.replace."""
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)

# ----------------------------------------------------------------------------
# AI yönetici özeti — arka planda hesapla, önbellekten servis et
# (LLM yavaş olabilir; endpoint asla bloklanmaz. Hazır olana kadar deterministik
#  şablon özet gösterilir.)
# ----------------------------------------------------------------------------
_AI_LOCK = threading.Lock()
_AI_CACHE = {"summary": None, "count": -1, "at": None}
_AI_BUSY = threading.Event()

def _refresh_ai_summary():
    """İçgörüyü hesapla + LLM özeti üret, önbelleğe yaz. Ayrı thread'de çağrılır."""
    if _AI_BUSY.is_set():
        return
    _AI_BUSY.set()
    try:
        with LOCK:
            data = load_data()
            count = len(data.get('complaints', []))
        ins = analysis.analyze(data)
        summary = analysis.llm_summary(ins, timeout=240)
        with _AI_LOCK:
            _AI_CACHE.update({"summary": summary, "count": count,
                              "at": now_iso()})
    except Exception as e:
        with _AI_LOCK:
            _AI_CACHE["summary"] = {"text": f"AI özeti üretilemedi: {e}",
                                    "source": "error"}
    finally:
        _AI_BUSY.clear()

def _trigger_ai_refresh():
    threading.Thread(target=_refresh_ai_summary, daemon=True).start()

# ----------------------------------------------------------------------------
# TR-duyarlı arama yardımcısı
# ----------------------------------------------------------------------------
def tr_lower(s):
    return (s.replace('İ', 'i').replace('I', 'ı').replace('Ş', 'ş').replace('Ç', 'ç')
             .replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ö', 'ö').lower())

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

PAGE_SIZE = 10

# ----------------------------------------------------------------------------
# HTTP Handler
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "SVClone/1.0"

    def log_message(self, fmt, *args):
        pass  # sessiz

    # --- yardımcılar ---
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
            if len(hits) >= 15:
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
        if path == '/api/admin/insights':
            return self._admin_insights()
        m = re.fullmatch(r'/api/complaints/(\d+)', path)
        if path == '/api/complaints':
            page = max(1, int((qs.get('page', ['1'])[0]) or 1))
            q = (qs.get('q', [''])[0] or '').strip()
            with LOCK:
                data = load_data()
                items = list(reversed(data['complaints']))  # yeni -> eski
            if q:
                nq = tr_lower(q)
                items = [c for c in items if nq in tr_lower(c['title']) or nq in tr_lower(c['body'])]
            total = len(items)
            start = (page - 1) * PAGE_SIZE
            page_items = items[start:start + PAGE_SIZE]
            return self._json({
                "total": total, "page": page, "pageSize": PAGE_SIZE,
                "totalPages": max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE),
                "items": page_items,
            })
        if m:
            cid = int(m.group(1))
            with LOCK:
                data = load_data()
                c = next((x for x in data['complaints'] if x['id'] == cid), None)
            if not c:
                return self._json({"error": "not_found"}, 404)
            return self._json(c)
        return self._json({"error": "not_found"}, 404)

    # --- POST ---
    def do_POST(self):
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

        if path == '/api/complaints':
            return self._create_complaint(body)
        m = re.fullmatch(r'/api/complaints/(\d+)/comments', path)
        if m:
            return self._create_comment(int(m.group(1)), body)
        m = re.fullmatch(r'/api/complaints/(\d+)/support', path)
        if m:
            return self._counter(int(m.group(1)), 'supports')
        m = re.fullmatch(r'/api/complaints/(\d+)/view', path)
        if m:
            return self._counter(int(m.group(1)), 'views')
        return self._json({"error": "not_found"}, 404)

    def _create_complaint(self, body):
        name = str(body.get('name', ''))
        title = str(body.get('title', ''))
        text = str(body.get('body', ''))
        for chk, field in ((v_name(name), 'name'),
                           (v_len(title, 10, 100, 'Başlık'), 'title'),
                           (v_len(text, 30, 2000, 'Şikayet metni'), 'body')):
            if chk:
                return self._json({"error": chk, "field": field}, 400)

        # Otomatik sınıflandırma + marka yanıtı (model kapalıysa sessizce atlanır)
        auto = get_auto_reply(f"{title}. {text}")
        comments = []
        status = "yanit-bekliyor"
        if auto and auto.get('cevap'):
            comments.append({
                "id": 1,
                "name": "Moka United",
                "isBrand": True,
                "body": clean(auto['cevap']),
                "createdAt": now_iso(),
            })
            if auto.get('sinif') not in NEEDS_HUMAN_REVIEW:
                status = "cozuldu"

        with LOCK:
            data = load_data()
            data['seq'] += 1
            rec = {
                "id": data['seq'],
                "name": mask_name(name),
                "initials": initials(name),
                "title": clean(title),
                "body": clean(text),
                "createdAt": now_iso(),
                "views": 0,
                "supports": 0,
                "status": status,
                "comments": comments,
            }
            data['complaints'].append(rec)
            _write(data)
        _trigger_ai_refresh()  # yeni şikayet -> AI özetini tazele
        return self._json(rec, 201)

    def _create_comment(self, cid, body):
        name = str(body.get('name', ''))
        text = str(body.get('body', ''))
        for chk, field in ((v_name(name), 'name'),
                           (v_len(text, 5, 500, 'Yorum'), 'body')):
            if chk:
                return self._json({"error": chk, "field": field}, 400)
        with LOCK:
            data = load_data()
            c = next((x for x in data['complaints'] if x['id'] == cid), None)
            if not c:
                return self._json({"error": "not_found"}, 404)
            nid = (max((cm['id'] for cm in c['comments']), default=0)) + 1
            comment = {
                "id": nid,
                "name": mask_name(name),
                "initials": initials(name),
                "isBrand": False,
                "body": clean(text),
                "createdAt": now_iso(),
            }
            c['comments'].append(comment)
            _write(data)
        return self._json(comment, 201)

    def _counter(self, cid, field):
        with LOCK:
            data = load_data()
            c = next((x for x in data['complaints'] if x['id'] == cid), None)
            if not c:
                return self._json({"error": "not_found"}, 404)
            c[field] = int(c.get(field, 0)) + 1
            val = c[field]
            _write(data)
        return self._json({field: val})

    # --- admin: zeka paneli içgörüleri ---
    def _admin_insights(self):
        with LOCK:
            data = load_data()
            count = len(data.get('complaints', []))
        ins = analysis.analyze(data)  # deterministik: hızlı, her istekte taze
        with _AI_LOCK:
            cached = _AI_CACHE.get("summary")
            cached_count = _AI_CACHE.get("count")
            cached_at = _AI_CACHE.get("at")
        # önbellek yoksa ya da veri değiştiyse arka planda tazele
        if cached is None or cached_count != count:
            _trigger_ai_refresh()
        if cached is None:
            # ilk yükleme: anında deterministik şablon özeti ver
            ins["ai_summary"] = {"text": analysis._template_summary(ins),
                                 "source": "template", "pending": True}
        else:
            ai = dict(cached)
            ai["pending"] = (cached_count != count)
            ai["at"] = cached_at
            ins["ai_summary"] = ai
        return self._json(ins)

    # --- statik dosyalar ---
    def _static(self, path):
        if path == '/' or path == '':
            path = '/index.html'
        # path traversal koruması
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
    load_data()  # seed'i garantile
    _trigger_ai_refresh()  # AI özetini arka planda önceden hazırla (ısınma)
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"Şikayetvar klonu çalışıyor:  http://localhost:{PORT}")
    print(f"Yönetici paneli:            http://localhost:{PORT}/admin.html")
    print(f"Veri dosyası: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
        server.shutdown()


if __name__ == '__main__':
    main()
