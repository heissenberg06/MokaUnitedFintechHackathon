#!/usr/bin/env python3
"""Moka United — İtiraz (chargeback) sayfası backend'i.
Sıfır bağımlılık: yalnız Python stdlib. itiraz.html/itiraz-durum.html ile aynı origin'den servis EDİLMEZ
(ana site statik http.server ile ayrı porttan sunulur); bu sunucu yalnız /api/itiraz/* uçlarını sağlar
ve CORS ile ana siteden çağrılabilir.

Sağladığı güvenlik/iş kuralları:
  1) IP bazlı rate limit — sorgu (brute force) ve itiraz oluşturma (spam) için ayrı sayaçlar.
  2) İtiraz oluşturma: multipart/form-data ile dosya yükleme (kanıt belgesi), tür/boyut kısıtlı.
  3) Aynı işlem (ref) için zaten AÇIK bir itiraz varsa yeni itiraz oluşturulmaz; mevcut caseId
     döndürülür ve istemci durum sorgulama sayfasına yönlendirilir.

Tüm veri KURGUDUR (mock işlem verisi assets/data/dispute-txns.js'den bağımsızdır).
Çalıştır: python3 itiraz_server.py  ->  http://localhost:8757
"""
import cgi
import html
import io
import json
import os
import re
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'itiraz.json')
UPLOAD_DIR = os.path.join(DATA_DIR, 'uploads')
PORT = 8757

LOCK = threading.Lock()

# ----------------------------------------------------------------------------
# Rate limit ayarları (IP başına, kayan pencere)
# ----------------------------------------------------------------------------
QUERY_WINDOW_S = 15 * 60      # sorgu (brute force) penceresi
QUERY_MAX = 5                 # bu pencerede izinli deneme sayısı
CREATE_WINDOW_S = 60 * 60     # itiraz oluşturma (spam) penceresi
CREATE_MAX = 3

_QUERY_HITS = {}   # ip -> [timestamps]
_CREATE_HITS = {}  # ip -> [timestamps]

# ----------------------------------------------------------------------------
# Dosya yükleme kısıtları
# ----------------------------------------------------------------------------
ALLOWED_EXT = {'.pdf', '.jpg', '.jpeg', '.png', '.heic'}
ALLOWED_CTYPE = {
    'application/pdf', 'image/jpeg', 'image/png', 'image/heic', 'image/heif',
}
MAX_FILE_SIZE = 5 * 1024 * 1024      # dosya başı 5MB
MAX_TOTAL_SIZE = 15 * 1024 * 1024    # toplam 15MB
MAX_FILES = 5

# Sonuçlanmış (kapalı) itiraz aşaması — bu aşamadaki bir işlem için yeni itiraz açılabilir.
CLOSED_STAGE = 4
OPEN_STAGES = (1, 2, 3)

# ----------------------------------------------------------------------------
# Yardımcılar
# ----------------------------------------------------------------------------
def now_iso():
    return datetime.now().replace(microsecond=0).isoformat()

def clean(s, maxlen=4000):
    return html.escape(str(s or '').strip())[:maxlen]

def client_ip(handler):
    # X-Forwarded-For yalnızca güvenilir bir proxy arkasında kullanılmalı; burada demo/localhost
    # senaryosu olduğu için doğrudan soket adresini esas alıyoruz (sahte header ile atlatılamaz).
    return handler.client_address[0]

def rate_check(bucket, ip, window_s, max_hits):
    now = time.time()
    with LOCK:
        hits = [t for t in bucket.get(ip, []) if now - t < window_s]
        if len(hits) >= max_hits:
            bucket[ip] = hits
            retry_after = int(window_s - (now - hits[0]))
            return False, max(1, retry_after)
        hits.append(now)
        bucket[ip] = hits
        return True, 0

# ----------------------------------------------------------------------------
# Kalıcılık
# ----------------------------------------------------------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        data = {"cases": {}}
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

def find_open_case_by_ref(data, ref):
    for c in data['cases'].values():
        if c.get('ref') == ref and c.get('stage', 1) in OPEN_STAGES:
            return c
    return None

# ----------------------------------------------------------------------------
# Doğrulama
# ----------------------------------------------------------------------------
PHONE_RE = re.compile(r'^0?5\d{9}$')

def v_required(s, lo, hi, label):
    s = (s or '').strip()
    if not (lo <= len(s) <= hi):
        return f"{label} {lo}-{hi} karakter olmalı."
    return None

# ----------------------------------------------------------------------------
# HTTP Handler
# ----------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "ItirazAPI/1.0"

    def log_message(self, fmt, *args):
        pass

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self._cors()
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    # --- GET ---
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        m = re.fullmatch(r'/api/itiraz/status/([A-Za-z0-9\-]+)', path)
        if m:
            return self._get_status(m.group(1))
        return self._json({"error": "not_found"}, 404)

    def _get_status(self, case_id):
        case_id = case_id.strip().upper()
        with LOCK:
            data = load_data()
            c = data['cases'].get(case_id)
        if not c:
            return self._json({"error": "not_found"}, 404)
        return self._json(c)

    # --- POST ---
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        ip = client_ip(self)

        if path == '/api/itiraz/attempt':
            return self._attempt(ip)
        if path == '/api/itiraz/create':
            return self._create(ip)
        m = re.fullmatch(r'/api/itiraz/([A-Za-z0-9\-]+)/advance', path)
        if m:
            return self._advance(m.group(1))
        return self._json({"error": "not_found"}, 404)

    def _advance(self, case_id):
        """Demo amaçlı: 'Durumu Yenile' ile süreci bir sonraki aşamaya taşır (gerçek bankacılık
        entegrasyonu değildir; yalnızca takip ekranı deneyimini göstermek içindir)."""
        case_id = case_id.strip().upper()
        with LOCK:
            data = load_data()
            c = data['cases'].get(case_id)
            if not c:
                return self._json({"error": "not_found"}, 404)
            if c['stage'] < CLOSED_STAGE:
                c['stage'] += 1
                _write(data)
        return self._json(c)

    def _attempt(self, ip):
        """Sorgu denemesi öncesi rate-limit kontrolü (brute force koruması)."""
        ok, retry_after = rate_check(_QUERY_HITS, ip, QUERY_WINDOW_S, QUERY_MAX)
        # istek gövdesini oku (varsa) — kullanılmıyor ama bağlantıyı temiz kapatmak için tüket
        length = int(self.headers.get('Content-Length', 0) or 0)
        if length:
            self.rfile.read(min(length, 4096))
        if not ok:
            return self._json({
                "allowed": False,
                "error": "rate_limited",
                "message": "Çok fazla deneme yapıldı. Lütfen bir süre sonra tekrar deneyin.",
                "retryAfter": retry_after,
            }, 429)
        with LOCK:
            remaining = QUERY_MAX - len(_QUERY_HITS.get(ip, []))
        return self._json({"allowed": True, "remaining": max(0, remaining)})

    def _create(self, ip):
        ctype = self.headers.get('Content-Type', '')
        if not ctype.startswith('multipart/form-data'):
            return self._json({"error": "invalid_content_type"}, 400)

        ok, retry_after = rate_check(_CREATE_HITS, ip, CREATE_WINDOW_S, CREATE_MAX)
        if not ok:
            length = int(self.headers.get('Content-Length', 0) or 0)
            if length:
                self.rfile.read(min(length, 1024))
            return self._json({
                "error": "rate_limited",
                "message": "Bu saatte çok fazla itiraz talebi oluşturuldu. Lütfen daha sonra tekrar deneyin.",
                "retryAfter": retry_after,
            }, 429)

        length = int(self.headers.get('Content-Length', 0) or 0)
        if length > MAX_TOTAL_SIZE + 64 * 1024:  # form alanları için küçük pay
            self.rfile.read(0)
            return self._json({"error": "too_large",
                              "message": "Yüklenen dosyaların toplam boyutu çok büyük (maks 15MB)."}, 413)

        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ctype,
                        'CONTENT_LENGTH': str(length)},
                keep_blank_values=True,
            )
        except Exception:
            return self._json({"error": "invalid_form"}, 400)

        def field(name, default=''):
            v = form.getvalue(name, default)
            return v if isinstance(v, str) else default

        reason = field('Reason')
        txn_type = field('TxnType')
        ref = field('Ref')
        merchant = field('Merchant')
        amount = field('Amount')
        note = field('Note')
        phone = field('Phone')
        email = field('Email')

        for chk in (
            v_required(reason, 3, 200, 'İtiraz sebebi'),
            v_required(txn_type, 2, 40, 'İşlem tipi'),
            v_required(ref, 3, 40, 'İşlem referansı'),
            v_required(note, 15, 2000, 'Açıklama'),
        ):
            if chk:
                return self._json({"error": chk, "field": "form"}, 400)
        phone_norm = re.sub(r'\D', '', phone)
        if not PHONE_RE.match(phone_norm):
            return self._json({"error": "Geçerli bir cep telefonu girin.", "field": "Phone"}, 400)
        if email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            return self._json({"error": "Geçerli bir e-posta girin.", "field": "Email"}, 400)

        with LOCK:
            data = load_data()
            existing = find_open_case_by_ref(data, ref)
            if existing:
                return self._json({
                    "error": "already_open",
                    "message": "Bu işlem için zaten devam eden bir itiraz talebiniz var. "
                              "Yeni bir talep oluşturmak yerine mevcut kaydınızın durumunu "
                              "sorgulayabilirsiniz.",
                    "caseId": existing['caseId'],
                }, 409)

            case_id = 'MU-ITZ-' + str(datetime.now().year) + '-' + str(uuid.uuid4().int)[:6]
            while case_id in data['cases']:
                case_id = 'MU-ITZ-' + str(datetime.now().year) + '-' + str(uuid.uuid4().int)[:6]

            # --- dosya yükleme ---
            saved_files = []
            file_fields = form['Evidence'] if 'Evidence' in form else None
            if isinstance(file_fields, list):
                items = file_fields
            elif file_fields is not None:
                items = [file_fields]
            else:
                items = []
            total_size = 0
            case_dir = os.path.join(UPLOAD_DIR, case_id)
            for item in items:
                if item is None or not getattr(item, 'filename', None):
                    continue
                if len(saved_files) >= MAX_FILES:
                    return self._json({"error": f"En fazla {MAX_FILES} dosya yükleyebilirsiniz."}, 400)
                raw = item.file.read(MAX_FILE_SIZE + 1)
                if len(raw) > MAX_FILE_SIZE:
                    return self._json({
                        "error": f"'{item.filename}' 5MB sınırını aşıyor."}, 400)
                total_size += len(raw)
                if total_size > MAX_TOTAL_SIZE:
                    return self._json({"error": "Toplam dosya boyutu 15MB'ı aşıyor."}, 400)
                orig_name = os.path.basename(item.filename)
                ext = os.path.splitext(orig_name)[1].lower()
                if ext not in ALLOWED_EXT:
                    return self._json({
                        "error": f"'{orig_name}': yalnızca PDF, JPG, PNG, HEIC dosyaları kabul edilir."}, 400)
                ctype_item = getattr(item, 'type', '') or ''
                if ctype_item and ctype_item not in ALLOWED_CTYPE:
                    return self._json({
                        "error": f"'{orig_name}': desteklenmeyen dosya türü."}, 400)
                if not raw:
                    continue
                safe_name = f"{uuid.uuid4().hex}{ext}"
                os.makedirs(case_dir, exist_ok=True)
                with open(os.path.join(case_dir, safe_name), 'wb') as out:
                    out.write(raw)
                saved_files.append({"name": clean(orig_name, 200), "storedAs": safe_name,
                                   "size": len(raw)})

            phone_mask = (phone_norm[:4] + ' *** ** ' + phone_norm[-2:]) if len(phone_norm) >= 8 else phone_norm
            rec = {
                "caseId": case_id,
                "createdAt": now_iso(),
                "stage": 1,
                "reason": clean(reason),
                "txnType": clean(txn_type),
                "ref": clean(ref, 60),
                "merchant": clean(merchant, 200),
                "amount": clean(amount, 30),
                "note": clean(note),
                "phone": phone_mask,
                "email": clean(email, 200),
                "files": saved_files,
                "ip_hash": str(hash(ip))[-8:],  # ham IP saklanmaz
            }
            data['cases'][case_id] = rec
            _write(data)

        return self._json(rec, 201)


def main():
    load_data()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    server = ThreadingHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"İtiraz API çalışıyor:  http://localhost:{PORT}")
    print(f"Veri dosyası: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
        server.shutdown()


if __name__ == '__main__':
    main()
