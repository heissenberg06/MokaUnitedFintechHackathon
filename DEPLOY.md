# Canlıya Alma Rehberi — berkopasha.com (Hostinger VPS)

VPS bilgileri: Ubuntu 22.04 LTS · 2 vCPU · 8GB RAM · IP `72.61.90.76` · kullanıcı `root`

Mimari: **iki alt alan adı**
- `berkopasha.com` → Moka United kurumsal site + chatbot + İtiraz sistemi
- `sikayetvar.berkopasha.com` → Şikayetvar klonu + Yönetici AI paneli

Her adımı sırayla, kendi terminalinizden VPS'e SSH ile bağlanarak çalıştırın:
```bash
ssh root@72.61.90.76
```
(Aksi belirtilmedikçe tüm komutlar VPS içindedir.)

---

## Adım 0 — DNS (en başta yapın, yayılması 10 dk–birkaç saat sürebilir)

Domain sağlayıcınızın (berkopasha.com'u aldığınız yer) DNS panelinden:

| Tip | Ad (Host) | Değer |
|---|---|---|
| A | `@` | `72.61.90.76` |
| A | `www` | `72.61.90.76` |
| A | `sikayetvar` | `72.61.90.76` |

Yayılıp yayılmadığını kontrol etmek için (kendi bilgisayarınızdan):
```bash
dig +short berkopasha.com
dig +short sikayetvar.berkopasha.com
```
İkisi de `72.61.90.76` döndürene kadar sonraki adımlara geçebilirsiniz ama HTTPS (Adım 8) için mutlaka yayılmış olması gerekir.

---

## Adım 1 — VPS temel güncelleme + güvenlik

```bash
apt update && apt upgrade -y

# Basit firewall: yalnızca SSH, HTTP, HTTPS açık
apt install -y ufw
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
ufw status
```

---

## Adım 2 — Gerekli paketler

```bash
apt install -y python3 python3-venv python3-pip git nginx certbot python3-certbot-nginx
```

---

## Adım 3 — Uygulama kullanıcısı ve dizini

Servisleri root yerine ayrı, yetkisiz bir sistem kullanıcısıyla çalıştırıyoruz (güvenlik):

```bash
useradd --system --home /var/www/moka --shell /usr/sbin/nologin moka
mkdir -p /var/www/moka
chown moka:moka /var/www/moka
```

---

## Adım 4 — Kodu GitHub'dan çek

```bash
cd /var/www
git clone -b vedat https://github.com/heissenberg06/MokaUnitedFintechHackathon.git moka
chown -R moka:moka /var/www/moka
```

> Repo private ise bu komut şifre soracaktır — GitHub artık şifreyle push/clone'a izin vermiyor, bunun yerine bir **Personal Access Token** üretip (GitHub → Settings → Developer settings → Personal access tokens) şifre yerine onu girmeniz gerekir.

> Not: Modeller (`moka-intent-model/`, `moka-sikayet-model/`) `.gitignore`'da olduğu için bu klonda **gelmeyecek** — Adım 6'da ayrıca taşıyacağız.

---

## Adım 5 — Python ortamı (chatbot + şikayet sınıflandırıcı için)

`itiraz_server.py` ve `sikayetvar/server.py` saf stdlib'dir, venv gerekmez. Yalnızca FastAPI tabanlı iki servis (`main_classifier.py`, `sikayet_api.py`) için:

```bash
cd /var/www/moka
sudo -u moka python3 -m venv venv
sudo -u moka ./venv/bin/pip install --upgrade pip
sudo -u moka ./venv/bin/pip install fastapi "uvicorn[standard]" transformers torch --index-url https://download.pytorch.org/whl/cpu
```
(`--index-url .../cpu` CPU-only PyTorch indirir — VPS'te GPU olmadığı için hem çok daha küçük hem yeterli.)

---

## Adım 6 — Modelleri kendi Mac'inizden VPS'e taşıyın

Bu komutu VPS'te **değil**, kendi bilgisayarınızın terminalinde çalıştırın:

```bash
cd /Users/berk/Desktop/moka
scp -r moka-intent-model moka-sikayet-model root@72.61.90.76:/var/www/moka/
```

Sonra VPS'e dönüp sahipliği düzeltin:

```bash
chown -R moka:moka /var/www/moka/moka-intent-model /var/www/moka/moka-sikayet-model
```

---

## Adım 7 — systemd servisleri

Dört servis dosyası oluşturacağız. Her biri için:

**`/etc/systemd/system/moka-chatbot.service`**
```ini
[Unit]
Description=Moka Chatbot Sınıflandırıcı (main_classifier.py, port 8000)
After=network.target

[Service]
User=moka
WorkingDirectory=/var/www/moka
ExecStart=/var/www/moka/venv/bin/uvicorn main_classifier:app --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/moka-sikayet-api.service`**
```ini
[Unit]
Description=Moka Şikayet Sınıflandırıcı (sikayet_api.py, port 8020)
After=network.target

[Service]
User=moka
WorkingDirectory=/var/www/moka
ExecStart=/var/www/moka/venv/bin/uvicorn sikayet_api:app --host 127.0.0.1 --port 8020
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/moka-itiraz.service`**
```ini
[Unit]
Description=Moka İtiraz Backend (itiraz_server.py, port 8757)
After=network.target

[Service]
User=moka
WorkingDirectory=/var/www/moka/Moko_United
ExecStart=/usr/bin/python3 itiraz_server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**`/etc/systemd/system/moka-sikayetvar.service`**
```ini
[Unit]
Description=Şikayetvar Klonu + Admin Paneli (server.py, port 8756)
After=network.target moka-sikayet-api.service

[Service]
User=moka
WorkingDirectory=/var/www/moka/Moko_United/sikayetvar
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Bu 4 dosyayı oluşturmak için (her biri ayrı ayrı):
```bash
nano /etc/systemd/system/moka-chatbot.service        # içeriği yapıştır, Ctrl+O, Enter, Ctrl+X
nano /etc/systemd/system/moka-sikayet-api.service
nano /etc/systemd/system/moka-itiraz.service
nano /etc/systemd/system/moka-sikayetvar.service
```

Sonra hepsini etkinleştirip başlatın:
```bash
systemctl daemon-reload
systemctl enable --now moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar
systemctl status moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar --no-pager
```
Hepsi `active (running)` olmalı. Model yükleme (chatbot + sikayet-api) birkaç saniye sürebilir; `journalctl -u moka-chatbot -f` ile canlı log izleyebilirsiniz (çıkmak için `Ctrl+C`).

---

## Adım 8 — Nginx (HTTP, henüz HTTPS'siz)

**`/etc/nginx/sites-available/berkopasha.com`**
```nginx
server {
    listen 80;
    server_name berkopasha.com www.berkopasha.com;

    root /var/www/moka/Moko_United;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /chat {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/itiraz/ {
        proxy_pass http://127.0.0.1:8757;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 20M;   # kanıt belgesi yükleme (toplam 15MB + form payı)
    }
}
```

**`/etc/nginx/sites-available/sikayetvar.berkopasha.com`**
```nginx
server {
    listen 80;
    server_name sikayetvar.berkopasha.com;

    location / {
        proxy_pass http://127.0.0.1:8756;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Oluştur ve etkinleştir:
```bash
nano /etc/nginx/sites-available/berkopasha.com              # yukarıdaki ilk bloğu yapıştır
nano /etc/nginx/sites-available/sikayetvar.berkopasha.com    # ikinci bloğu yapıştır

ln -s /etc/nginx/sites-available/berkopasha.com /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/sikayetvar.berkopasha.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t          # syntax kontrolü — "syntax is ok" görmelisiniz
systemctl reload nginx
```

Bu noktada (DNS yayılmışsa) `http://berkopasha.com` ve `http://sikayetvar.berkopasha.com` açılıyor olmalı.

---

## Adım 9 — HTTPS (Let's Encrypt, ücretsiz)

```bash
certbot --nginx -d berkopasha.com -d www.berkopasha.com -d sikayetvar.berkopasha.com
```
Sorulan e-posta adresini girin, şartları kabul edin. Certbot nginx config'lerinizi otomatik günceller ve otomatik yenileme kurar (test etmek için: `certbot renew --dry-run`).

---

## Adım 10 — Son kontrol listesi

- [ ] `https://berkopasha.com` → ana sayfa açılıyor, sağ altta chatbot ("yarim") çalışıyor
- [ ] `https://berkopasha.com/itiraz.html` → sorgu yapılabiliyor, talep oluşturulabiliyor
- [ ] `https://berkopasha.com/itiraz-durum.html` → oluşturulan case ID ile durum sorgulanabiliyor
- [ ] `https://sikayetvar.berkopasha.com` → şikayet gönderilebiliyor, otomatik "Marka Yanıtı" geliyor
- [ ] `https://sikayetvar.berkopasha.com/admin.html` → AI paneli açılıyor

---

## Bakım / faydalı komutlar

```bash
# Servis durumu / loglar
systemctl status moka-chatbot
journalctl -u moka-sikayetvar -f

# Kod güncellemesi sonrası
cd /var/www/moka && sudo -u moka git pull origin vedat
systemctl restart moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar

# Nginx config değişikliği sonrası
nginx -t && systemctl reload nginx
```

## Bilinen sınırlamalar (canlıya çıkmadan önce hatırlatma)

`README.md`'de detaylandırıldığı gibi: işlem eşleştirmesi hâlâ istemci tarafında (tüm mock veri seti tarayıcıya gönderiliyor) ve kart hamili doğrulama adımı yok. Bu bir hackathon demosu için kabul edilebilir ama gerçek müşteri verisiyle çalışacak bir sürüm için üretime geçmeden ele alınmalı.
