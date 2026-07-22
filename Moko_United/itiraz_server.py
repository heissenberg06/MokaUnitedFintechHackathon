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
import html
import io
import json
import os
import re
import smtplib
import threading
import time
import urllib.error
import urllib.request
import uuid
from collections import defaultdict
from datetime import datetime
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# Not: stdlib'deki `cgi` modülü Python 3.13'te kaldırıldı (PEP 594);
# bu yüzden multipart/form-data ayrıştırma elle yapılır (aşağıda).

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

# Mükerrer itiraz engeli yalnızca bu süre içinde geçerlidir (demo/test kolaylığı):
# aynı işlem için tekrar test edildiğinde "zaten açık itirazınız var" bloğuna takılmasın diye
# bu süreden eski açık itirazlar mükerrer kontrolünde yok sayılır.
DISPUTE_DEDUP_WINDOW_S = 60 * 60  # 1 saat

# ----------------------------------------------------------------------------
# E-posta bildirimi (opsiyonel, gerçek gönderim — stdlib smtplib)
# Ortam değişkenleri tanımlı değilse sessizce atlanır (demo akışı hiçbir zaman bloklanmaz).
# ----------------------------------------------------------------------------
SMTP_HOST = os.environ.get('MOKA_SMTP_HOST', '')
SMTP_PORT = int(os.environ.get('MOKA_SMTP_PORT', '465'))
SMTP_USER = os.environ.get('MOKA_SMTP_USER', '')
SMTP_PASS = os.environ.get('MOKA_SMTP_PASS', '')
SMTP_FROM = os.environ.get('MOKA_SMTP_FROM', SMTP_USER)

STAGE_LABELS = {1: 'Talep Alındı', 2: 'İnceleniyor', 3: 'Bankaya / İşyerine İletildi', 4: 'Sonuçlandırıldı'}

# ----------------------------------------------------------------------------
# jira-klon entegrasyonu — yeni itiraz açıldığında oraya "beklemede" bir kayıt düşer.
# Aynı VPS üzerinde çalışan ayrı bir servis (127.0.0.1:8780); erişilemezse itiraz akışı
# hiçbir şekilde bloklanmaz (sessizce loglanır).
# ----------------------------------------------------------------------------
JIRA_API_URL = "http://127.0.0.1:8780/api/issues"

def create_jira_issue_async(case_id, merchant, reason, note):
    def _send():
        payload = json.dumps({
            "reporter": "Kart Hamili",
            "summary": f"İtiraz talebi — {merchant} ({case_id})",
            "description": f"Moka United itiraz sayfasından otomatik açıldı.\n\n"
                            f"İşlem numarası: {case_id}\nİşyeri: {merchant}\n"
                            f"İtiraz sebebi: {reason}\n\nAçıklama: {note}",
            "category": "Yetkisiz İşlem",
            "priority": "yuksek",
            "source": "self-service",
            "status": "beklemede",
            "merchant": merchant,
        }).encode('utf-8')
        try:
            req = urllib.request.Request(
                JIRA_API_URL, data=payload,
                headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=8) as resp:
                resp.read()
            print(f"[jira] oluşturuldu -> {case_id}", flush=True)
        except Exception as e:
            print(f"[jira] oluşturulamadı -> {case_id}: {e}", flush=True)
    threading.Thread(target=_send, daemon=True).start()

def send_email(to_addr, subject, body):
    """Gerçek e-posta gönderir; SMTP yapılandırılmamışsa veya gönderim başarısız olursa
    sessizce loglar — itiraz akışını asla bloklamaz."""
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS and to_addr):
        print(f"[email] SMTP yapılandırılmamış, atlandı -> {to_addr}: {subject}", flush=True)
        return
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = f"Moka United <{SMTP_FROM}>"
        msg['To'] = to_addr
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_FROM, [to_addr], msg.as_string())
        print(f"[email] gönderildi -> {to_addr}: {subject}", flush=True)
    except Exception as e:
        print(f"[email] gönderilemedi -> {to_addr}: {e}", flush=True)

def send_email_async(to_addr, subject, body):
    if to_addr:
        threading.Thread(target=send_email, args=(to_addr, subject, body), daemon=True).start()

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
    now = time.time()
    for c in data['cases'].values():
        if c.get('ref') != ref or c.get('stage', 1) not in OPEN_STAGES:
            continue
        try:
            created_ts = datetime.fromisoformat(c['createdAt']).timestamp()
        except Exception:
            created_ts = 0
        if now - created_ts < DISPUTE_DEDUP_WINDOW_S:
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
# multipart/form-data ayrıştırma (cgi.FieldStorage yerine, stdlib-only)
# ----------------------------------------------------------------------------
class _UploadedFile:
    """cgi.FieldStorage'ın dosya alanlarıyla uyumlu minimal arayüz (.filename/.type/.file)."""
    def __init__(self, filename, ctype, data):
        self.filename = filename
        self.type = ctype
        self.file = io.BytesIO(data)

class MultipartForm:
    """cgi.FieldStorage'a yeterince benzeyen basit bir form nesnesi:
    form.getvalue(name), name in form, form['name'] (tek dosya ya da liste)."""
    def __init__(self, fields, files):
        self._fields = fields
        self._files = files

    def getvalue(self, name, default=''):
        return self._fields.get(name, default)

    def __contains__(self, name):
        return name in self._fields or name in self._files

    def __getitem__(self, name):
        if name in self._files:
            items = self._files[name]
            return items if len(items) > 1 else items[0]
        return self._fields.get(name)

_DISP_PARAM_RE = re.compile(r'(\w+)="([^"]*)"')

def parse_multipart(raw, content_type):
    m = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not m:
        raise ValueError("boundary bulunamadı")
    boundary = (m.group(1) or m.group(2)).strip()
    delim = ('--' + boundary).encode('utf-8')

    fields = {}
    files = defaultdict(list)
    for part in raw.split(delim):
        part = part.strip(b'\r\n')
        if not part or part == b'--':
            continue
        if b'\r\n\r\n' not in part:
            continue
        header_blob, body = part.split(b'\r\n\r\n', 1)
        body = body[:-2] if body.endswith(b'\r\n') else body  # kapanış CRLF'i at
        headers_text = header_blob.decode('utf-8', errors='replace')
        disp_m = re.search(r'Content-Disposition:\s*form-data;\s*(.+)', headers_text, re.I)
        if not disp_m:
            continue
        params = dict(_DISP_PARAM_RE.findall(disp_m.group(1)))
        name = params.get('name')
        if not name:
            continue
        if 'filename' in params:
            if not params['filename']:
                continue  # boş dosya alanı seçilmemiş
            ctype_m = re.search(r'Content-Type:\s*([^\r\n]+)', headers_text, re.I)
            ctype = ctype_m.group(1).strip() if ctype_m else 'application/octet-stream'
            files[name].append(_UploadedFile(params['filename'], ctype, body))
        else:
            fields[name] = body.decode('utf-8', errors='replace')
    return MultipartForm(fields, files)

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
        if c.get('email'):
            label = STAGE_LABELS.get(c['stage'], '')
            send_email_async(
                c['email'],
                f"İtiraz Durumu Güncellendi — {case_id}",
                "Merhaba,\n\n"
                f"{case_id} numaralı itiraz talebinizin durumu güncellendi: {label}.\n\n"
                f"Güncel durumu https://berkopasha.com/itiraz-durum.html?case={case_id} "
                "adresinden görüntüleyebilirsiniz.\n\nSaygılarımızla,\nMoka United"
            )
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
            raw_body = self.rfile.read(length)
            form = parse_multipart(raw_body, ctype)
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

        create_jira_issue_async(case_id, rec['merchant'], rec['reason'], rec['note'])

        if rec['email']:
            send_email_async(
                rec['email'],
                f"İtirazınız Alındı — {case_id}",
                "Merhaba,\n\n"
                f"{case_id} numaralı itiraz talebiniz sistemimize kaydedilmiştir.\n\n"
                f"İşyeri: {rec['merchant']}\n"
                f"İtiraz Sebebi: {rec['reason']}\n\n"
                "Süreç ilerledikçe (inceleme, bankaya/işyerine iletilme ve sonuçlanma "
                "aşamalarında) bu e-posta adresine bilgilendirme göndereceğiz. Talebinizin "
                f"güncel durumunu https://berkopasha.com/itiraz-durum.html?case={case_id} "
                "adresinden de takip edebilirsiniz.\n\n"
                "Saygılarımızla,\nMoka United"
            )

        return self._json(rec, 201)


def main():
    load_data()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Yalnızca localhost'a bağlan: dışarıdan doğrudan erişim yok, yalnızca aynı
    # makinedeki nginx reverse proxy üzerinden ulaşılabilir.
    server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    print(f"İtiraz API çalışıyor:  http://localhost:{PORT}")
    print(f"Veri dosyası: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu durduruldu.")
        server.shutdown()


if __name__ == '__main__':
    main()
