# Canlıya Alma Rehberi — berkopasha.com (Hostinger VPS)

VPS bilgileri: Ubuntu 22.04 LTS · 2 vCPU · 8GB RAM · IP `72.61.90.76` · kullanıcı `root`

Mimari: **dört alt alan adı**, tek VPS, tek nginx:

| Subdomain | İçerik | Yerel port(lar) |
|---|---|---|
| `berkopasha.com` / `www` | Moka United kurumsal site + chatbot + İtiraz sistemi | 8000 (chat), 8757 (itiraz) — statik dosyalar nginx'ten direkt |
| `sikayetvar.berkopasha.com` | Şikayetvar klonu + Yönetici AI paneli | 8756 |
| `next4biz.berkopasha.com` | next4biz-klon | 8770 |
| `jira.berkopasha.com` | jira-klon | 8780 |
| `juri.berkopasha.com` | Jüri değerlendirme merkezi (tek statik sayfa, `Moko_United/juri.html`) | yok — statik |

Her adımı sırayla, kendi terminalinizden VPS'e SSH ile bağlanarak çalıştırın:
```bash
ssh root@72.61.90.76
```

---

## Adım 0 — DNS (en başta yapın, yayılması zaman alır)

Domain panelinizden 5 A kaydı:

| Tip | Ad (Host) | Değer |
|---|---|---|
| A | `@` | `72.61.90.76` |
| A | `www` | `72.61.90.76` |
| A | `sikayetvar` | `72.61.90.76` |
| A | `next4biz` | `72.61.90.76` |
| A | `jira` | `72.61.90.76` |

Kontrol (kendi bilgisayarınızdan):
```bash
dig +short berkopasha.com sikayetvar.berkopasha.com next4biz.berkopasha.com jira.berkopasha.com
```
Hepsi `72.61.90.76` dönene kadar bekleyin (HTTPS adımından önce mutlaka yayılmış olmalı).

---

## Adım 1 — Sistem güncelleme + firewall

```bash
apt update && apt upgrade -y
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

```bash
id moka &>/dev/null || useradd --system --home /var/www/moka --shell /usr/sbin/nologin moka
rm -rf /var/www/moka
mkdir -p /var/www/moka
chown moka:moka /var/www/moka
```

---

## Adım 4 — Kodu GitHub'dan çek (master)

```bash
cd /var/www
git clone -b master https://github.com/heissenberg06/MokaUnitedFintechHackathon.git moka
chown -R moka:moka /var/www/moka
ls /var/www/moka/Moko_United
```
Çıktıda `jira-klon`, `next4biz-klon`, `sikayetvar`, `itiraz.html` gibi klasör/dosyaları görmelisiniz.

---

## Adım 5 — Python ortamı (chatbot + şikayet sınıflandırıcı için)

`itiraz_server.py`, `sikayetvar/server.py`, `next4biz-klon/server.py`, `jira-klon/server.py` saf stdlib'dir, venv gerekmez. Yalnızca 2 FastAPI servisi için:

```bash
cd /var/www/moka
sudo -u moka python3 -m venv venv
sudo -u moka ./venv/bin/pip install --upgrade pip
sudo -u moka ./venv/bin/pip install fastapi "uvicorn[standard]" transformers torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Adım 6 — Modelleri kendi Mac'inizden VPS'e taşıyın

**Kendi bilgisayarınızın terminalinde** (VPS'te değil):
```bash
cd /Users/berk/Desktop/moka
scp -r moka-intent-model moka-sikayet-model root@72.61.90.76:/var/www/moka/
```

VPS'e dönüp sahipliği düzeltin:
```bash
chown -R moka:moka /var/www/moka/moka-intent-model /var/www/moka/moka-sikayet-model
```

---

## Adım 7 — systemd servisleri (6 tane)

Her biri için dosya oluşturup içeriği yapıştıracaksınız: `nano /etc/systemd/system/<dosya-adı>` → yapıştır → `Ctrl+O`, `Enter`, `Ctrl+X`.

**`moka-chatbot.service`**
```ini
[Unit]
Description=Moka Chatbot Sınıflandırıcı (port 8000)
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

**`moka-sikayet-api.service`**
```ini
[Unit]
Description=Moka Şikayet Sınıflandırıcı (port 8020)
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

**`moka-itiraz.service`**
```ini
[Unit]
Description=Moka İtiraz Backend (port 8757)
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

**`moka-sikayetvar.service`**
```ini
[Unit]
Description=Şikayetvar Klonu + Admin Paneli (port 8756)
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

**`moka-next4biz.service`**
```ini
[Unit]
Description=next4biz-klon (port 8770)
After=network.target

[Service]
User=moka
WorkingDirectory=/var/www/moka/Moko_United/next4biz-klon
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**`moka-jira.service`**
```ini
[Unit]
Description=jira-klon (port 8780)
After=network.target

[Service]
User=moka
WorkingDirectory=/var/www/moka/Moko_United/jira-klon
ExecStart=/usr/bin/python3 server.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Hepsini etkinleştirip başlatın:
```bash
systemctl daemon-reload
systemctl enable --now moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar moka-next4biz moka-jira
systemctl status moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar moka-next4biz moka-jira --no-pager
```
Hepsi `active (running)` olmalı.

---

## Adım 8 — Nginx (4 site, HTTP)

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
        client_max_body_size 20M;
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

**`/etc/nginx/sites-available/next4biz.berkopasha.com`**
```nginx
server {
    listen 80;
    server_name next4biz.berkopasha.com;
    location / {
        proxy_pass http://127.0.0.1:8770;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**`/etc/nginx/sites-available/jira.berkopasha.com`**
```nginx
server {
    listen 80;
    server_name jira.berkopasha.com;
    location / {
        proxy_pass http://127.0.0.1:8780;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Oluşturup etkinleştirin:
```bash
nano /etc/nginx/sites-available/berkopasha.com
nano /etc/nginx/sites-available/sikayetvar.berkopasha.com
nano /etc/nginx/sites-available/next4biz.berkopasha.com
nano /etc/nginx/sites-available/jira.berkopasha.com

ln -s /etc/nginx/sites-available/berkopasha.com /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/sikayetvar.berkopasha.com /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/next4biz.berkopasha.com /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/jira.berkopasha.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx
```

Bu noktada (DNS yayılmışsa) 4 site de `http://` ile açılıyor olmalı.

---

## Adım 9 — HTTPS (Let's Encrypt)

```bash
certbot --nginx -d berkopasha.com -d www.berkopasha.com -d sikayetvar.berkopasha.com -d next4biz.berkopasha.com -d jira.berkopasha.com
```

---

## Adım 10 — Son kontrol listesi

- [ ] `https://berkopasha.com` → ana sayfa + chatbot ("yarim")
- [ ] `https://berkopasha.com/itiraz.html` → sorgu + talep oluşturma
- [ ] `https://berkopasha.com/itiraz-durum.html` → durum sorgulama
- [ ] `https://sikayetvar.berkopasha.com` + `/admin.html`
- [ ] `https://next4biz.berkopasha.com`
- [ ] `https://jira.berkopasha.com`

---

## Bakım

```bash
systemctl status moka-chatbot
journalctl -u moka-sikayetvar -f

cd /var/www/moka && sudo -u moka git pull origin master
systemctl restart moka-chatbot moka-sikayet-api moka-itiraz moka-sikayetvar moka-next4biz moka-jira

nginx -t && systemctl reload nginx
```
