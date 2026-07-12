# Moka United — AI Destekli İşlem İtirazı & Müşteri Geri Bildirim Zekâsı

> **Moka United AI Ideathon & Hackathon — "Hack the Idea"** kapsamında geliştirilmiştir.
> Tüm marka, kişi, şikayet ve işlem verileri **kurgudur**; gerçek Moka United / Şikayetvar içeriğiyle bağlantısı yoktur. Eğitim/demo amaçlıdır.

## 1. Problem

Kart hamilleri ekstrelerinde tanımadıkları bir işlem gördüklerinde — çoğunlukla işlemi unuttukları için (*friendly fraud*) — doğrudan bankalarına itiraz açıyor. Bu durum:

- Üye işyeri için gereksiz **chargeback maliyeti**,
- Ödeme kuruluşu için gereksiz **operasyonel yük**,
- Müşteri hizmetlerinde tekrarlayan, kalıp cevaplarla çözülebilecek **şikayet trafiği**

yaratıyor. Uluslararası ekosistemde bu sorun, işlem bilgisinin kart hamiline zamanında ve **güvenli şekilde** sunulmasıyla (Visa Verifi Order Insight, Mastercard Ethoca Consumer Clarity) kaynağında önleniyor. Bu proje, aynı fikri Moka United'ın kendi verisi üzerinde, iki farklı temas noktasında (canlı chat + şikayet platformu) hayata geçiriyor.

## 2. Çözüm — İki Modül

| Modül | Ne yapıyor | Kullanılan AI |
|---|---|---|
| **A) İtiraz / İşlem Sorgulama** | Kart hamili, ekstresindeki işlemi kendi kendine sorgular; asgari bilgiyle ("Beymen – Akasya AVM, ₺7.650, 23 Haziran") harcamasını hatırlar. Hatırlamazsa resmi itiraz talebi (kanıt belgesi yükleyerek) açar ve MU-ITZ-XXXX numarasıyla durumunu takip eder. | BERTurk tabanlı niyet sınıflandırıcı (chatbot) |
| **B) Şikayetvar Klonu + Otomatik Yanıt + Yönetici Zekâ Paneli** | Şikayetvar'a gelen her şikayet otomatik sınıflandırılıp anında "Marka Yanıtı" olarak cevaplanıyor; insan incelemesi gereken hassas konular (dolandırıcılık şüphesi, cüzdan sorunu) otomatik kapatılmıyor. Ayrıca yönetim için gerçek zamanlı bir **müşteri zekâ paneli** (kategori/duygu/segment analizi, sahtekarlık ağı tespiti, trend, AI yönetici özeti) üretiyor. | BERTurk tabanlı 7 sınıflı şikayet sınıflandırıcı + stdlib istatistiksel analiz motoru + opsiyonel yerel LLM (Ollama) |

Her iki modül de aynı köke bağlanıyor: **kullanıcıyı insan müdahalesi gerekmeden doğru bilgiye/yönlendirmeye ulaştırmak, gerçekten insan gerektiren durumları ise otomatik olarak ayıklayıp öne çıkarmak.**

## 3. Mimari

```
┌─────────────────────────┐        ┌──────────────────────────┐
│   Moka United (statik)   │        │   Şikayetvar Klonu        │
│   Moko_United/*.html     │        │   Moko_United/sikayetvar/ │
│                          │        │                           │
│  ┌────────────────────┐  │        │  index.html (şikayet akışı)│
│  │ Chatbot ("yarim")   │──┼──chat──▶ main_classifier.py (8000) │
│  └────────────────────┘  │        │   → moka-intent-model      │
│                          │        │                           │
│  ┌────────────────────┐  │        │  admin.html (AI paneli)    │
│  │ itiraz.html         │──┼─rate───▶ itiraz_server.py (8757)   │
│  │ itiraz-durum.html   │  │ limit/ │   → data/itiraz.json      │
│  └────────────────────┘  │ create │                           │
└─────────────────────────┘        └──────────┬────────────────┘
                                               │
                                    server.py (8756)
                                     → data/complaints.json
                                     → analysis.py (Müşteri Zekâ Motoru)
                                               │
                                       ┌───────┴────────┐
                                       │ sikayet_api.py  │ (8020)
                                       │ → moka-sikayet- │
                                       │   model          │
                                       └────────┬────────┘
                                                │ opsiyonel
                                        Ollama (qwen2.5:3b, 11434)
```

### Servisler

| Servis | Port | Komut | Görevi |
|---|---|---|---|
| Moka United statik site | 8080 | `python3 -m http.server 8080` (çalıştırılan dizin: `Moko_United/`) | Kurumsal site, itiraz.html, itiraz-durum.html, chatbot widget'ı |
| Chatbot sınıflandırıcı | 8000 | `uvicorn main_classifier:app --port 8000` (repo kökünde) | Kullanıcı mesajını `itiraz / belirsiz / diger` sınıflarına ayırır, itiraz.html'e yönlendirir |
| İtiraz backend | 8757 | `python3 itiraz_server.py` (çalıştırılan dizin: `Moko_United/`) | IP bazlı rate-limit, kanıt belgesi yükleme, mükerrer itiraz engelleme, durum takibi |
| Şikayetvar klonu + admin paneli | 8756 | `python3 server.py` (çalıştırılan dizin: `Moko_United/sikayetvar/`) | Şikayet/yorum/destek API'si, statik arayüz, `/admin.html` yönetici zekâ paneli |
| Şikayet sınıflandırıcı | 8020 | `uvicorn sikayet_api:app --port 8020` (repo kökünde) | Gelen şikayeti 7 sınıfa ayırıp sabit şablon cevap üretir |
| (Opsiyonel) Ollama | 11434 | `ollama serve` + `ollama pull qwen2.5:3b` | Admin panelindeki "Yönetici Özeti" cümlesini doğal dilde üretir; kapalıysa şablon özete düşer |

Tüm backend'ler **sıfır harici bağımlılık** felsefesiyle yazılmıştır (yalnızca `http.server`/Python stdlib); yalnızca FastAPI tabanlı iki sınıflandırma servisi (`main_classifier.py`, `sikayet_api.py`) `fastapi`, `uvicorn`, `torch`, `transformers` gerektirir (bkz. `venv/`).

## 4. Modül A — İtiraz / İşlem Sorgulama

### Akış
1. **Sorgu** — Kullanıcı işlem tarihi, tutarı, işyeri adı ("Kurum Adı" — kısa/kısmi ad yeterli, ör. "Beymen") ve cüzdan ID'sini girer.
2. **Eşleştirme** — `assets/data/dispute-txns.js`'deki mock işlem havuzunda; işyeri adı **içerir** eşleşmesi + cüzdan ID tam eşleşmesi + tutar (toplam **veya** taksit tutarı) + tarih (±1 gün tolerans) ile aranır.
3. **Hatırlatma** — Eşleşme bulunursa yalnızca asgari bilgi gösterilir: işyeri adı, ilçe/şehir, kategori, tek işlem satırı. Kartın diğer işlemleri veya tam veri **gösterilmez**.
4. **Talep** (hatırlamıyorsa) — İtiraz sebebi, işlem tipi, açıklama, telefon ve opsiyonel kanıt belgesi (PDF/JPG/PNG/HEIC, dosya başı 5MB/toplam 15MB/en fazla 5 dosya) ile resmi itiraz talebi oluşturulur.
5. **Takip** — `MU-ITZ-YYYY-XXXXXX` numarasıyla `itiraz-durum.html`'den 4 aşamalı süreç (Talep Alındı → İnceleniyor → Bankaya/İşyerine İletildi → Sonuçlandırıldı) takip edilir.

### Güvenlik/iş kuralları (`itiraz_server.py`)
- IP bazlı rate-limit: sorgu için 15 dk'da 5 deneme, itiraz oluşturma için saatte 3 deneme (kayan pencere, `threading.Lock` korumalı).
- Aynı işlem referansı için açık bir itiraz varsa yenisi oluşturulmaz, mevcut kayda yönlendirilir.
- Dosya yükleme tip/boyut sunucu tarafında da doğrulanır; kayıtlar `data/itiraz.json` + `data/uploads/<caseId>/` altında tutulur.
- IP adresi ham saklanmaz (hash'lenir), telefon numarası maskelenir.

### Chatbot (`main_classifier.py` + `moka-intent-model`)
- `dbmdz/bert-base-turkish-cased` üzerine fine-tune edilmiş 3 sınıflı model (`itiraz / belirsiz / diger`), `train_classifier.py` ile `moka_intent_dataset.csv`'den eğitildi.
- Sitenin sağ altındaki **"yarim"** butonu chatbot panelini açar; "itiraz" niyeti algılanınca kullanıcıyı `itiraz.html`'e yönlendiren bir kart gösterir.

## 5. Modül B — Şikayetvar Klonu + Otomatik Yanıt + Yönetici Zekâ Paneli

### Otomatik sınıflandırma/cevap (`sikayet_api.py` + `moka-sikayet-model`)
- `dbmdz/bert-base-turkish-cased` üzerine fine-tune edilmiş **7 sınıflı** model (`train_sikayet.py`, `moka_sikayet_dataset.csv`): `tanimadigi_islem_kart`, `dolandiricilik_suphesi`, `abonelik_tekrarlayan`, `iade_gecikmesi`, `urun_hizmet_sorunu`, `cuzdan_hesap_sorunu`, `zaten_cozuldu_diger`.
- Her sınıf için sabit şablon cevap (`sablonlar.py`, **generation yok** — bilinçli tasarım, halüsinasyon riski taşımaz), itiraz sayfasına yönlendiren bir cümleyle biter.
- `sikayetvar/server.py`, her yeni şikayette bu servisi çağırır ve sonucu **`isBrand: true`** yorumu olarak (marka rozetli) anında ekler. `dolandiricilik_suphesi` ve `cuzdan_hesap_sorunu` sınıflarında durum otomatik **"çözüldü"** yapılmaz — insan incelemesine bırakılır. Sınıflandırma servisi kapalıysa akış bozulmaz, şikayet yorumsuz kaydedilir (*fail-safe*).

### Yönetici Zekâ Paneli (`analysis.py` + `admin.html`, `GET /api/admin/insights`)
İki katmanlı **Moka Müşteri Zeka Motoru**:

1. **Deterministik çekirdek** (yalnız stdlib, ağ gerektirmez, her zaman çalışır):
   - 12 kategoriye anahtar-kelime tabanlı otomatik sınıflandırma
   - Aciliyet skoru (1–10), duygu analizi (öfkeli/olumsuz/nötr/olumlu), müşteri segmenti tahmini (esnaf/bireysel/kurumsal)
   - TF-IDF ile **benzer şikayet kümeleme** (tekrar eden sorun / sahtekarlık ağı tespiti — aynı işyerinde kısa sürede biriken "yetkisiz işlem" şikayetlerini otomatik işaretler)
   - Haftalık trend, kurgusal rakip benchmark'ı, kategoriye özel yönetici aksiyon önerisi
2. **Opsiyonel yerel LLM katmanı**: Ollama (`qwen2.5:3b`) ile 3–4 cümlelik Türkçe yönetici özeti üretir; arka planda thread'de hesaplanıp önbelleğe yazılır (endpoint asla bloklanmaz), Ollama kapalıysa deterministik şablon özete düşer.

## 6. Kurulum ve Çalıştırma

```bash
# 1) Python bağımlılıkları (yalnızca chatbot + şikayet sınıflandırıcı için gerekli)
cd moka
python3 -m venv venv && source venv/bin/activate
pip install fastapi "uvicorn[standard]" transformers torch

# 2) Beş servisi ayrı terminallerde başlat
cd Moko_United && python3 -m http.server 8080                 # statik site
cd Moko_United && python3 itiraz_server.py                    # itiraz backend
cd Moko_United/sikayetvar && python3 server.py                # şikayetvar + admin
source venv/bin/activate && uvicorn sikayet_api:app --port 8020        # şikayet sınıflandırıcı
source venv/bin/activate && uvicorn main_classifier:app --port 8000   # chatbot
```

Sonra tarayıcıda:

- Kurumsal site: `http://localhost:8080/index.html`
- İtiraz sorgulama: `http://localhost:8080/itiraz.html`
- İtiraz durum takibi: `http://localhost:8080/itiraz-durum.html`
- Şikayetvar klonu: `http://localhost:8756/`
- Yönetici Zekâ Paneli: `http://localhost:8756/admin.html`

Modelleri yeniden eğitmek için: `python3 train_classifier.py` (chatbot) / `python3 train_sikayet.py` (şikayet sınıflandırıcı) — çıktılar sırasıyla `moka-intent-model/` ve `moka-sikayet-model/` altına yazılır.

## 7. Proje Yapısı

```
moka/
├── main_classifier.py        # chatbot backend (FastAPI, /chat)
├── train_classifier.py       # chatbot modeli eğitimi
├── moka_intent_dataset.csv
├── moka-intent-model/        # eğitilmiş chatbot modeli (BERTurk, 3 sınıf)
├── sikayet_api.py            # şikayet sınıflandırma/cevap servisi (FastAPI, /cevapla)
├── sablonlar.py              # sınıf başına sabit cevap şablonları
├── train_sikayet.py          # şikayet sınıflandırıcı eğitimi
├── moka_sikayet_dataset.csv
├── moka-sikayet-model/       # eğitilmiş şikayet sınıflandırıcı (BERTurk, 7 sınıf)
├── moka_uyum_raporu.docx     # KVKK/TCMB/PCI-DSS uyum analiz raporu
└── Moko_United/
    ├── build_pages.py        # 24 statik sayfanın jeneratörü
    ├── *.html                # üretilen sayfalar (hakkimizda, urunler, iletisim, ...)
    ├── itiraz.html            # işlem sorgulama + itiraz sihirbazı (elle bakımlı)
    ├── itiraz-durum.html      # itiraz durum takibi
    ├── itiraz_server.py       # itiraz backend (stdlib, rate-limit + dosya yükleme)
    ├── assets/
    │   ├── css/style.css
    │   ├── js/{components,main,moka-chat-widget}.js
    │   └── data/dispute-txns.js   # mock işlem veri seti (100 kayıt)
    └── sikayetvar/            # Şikayetvar klonu (alt proje)
        ├── server.py          # stdlib backend (şikayet/yorum/destek API'si)
        ├── analysis.py        # Müşteri Zeka Motoru (deterministik + opsiyonel LLM)
        ├── index.html / admin.html
        └── data/complaints.json
```

## 8. Güvenlik ve Mevzuat Uyumu

`moka_uyum_raporu.docx`, sistemin KVKK (6698 s. Kanun), TCMB'nin ödeme kuruluşlarına yönelik ikincil düzenlemeleri ve PCI DSS v4.0.1 ile uyumu üzerine hazırlanmış ayrı bir teknik/hukuki analiz raporudur. Öne çıkan tasarım ilkeleri:

- **Asgari ifşa**: sorgu sonucunda yalnızca işyeri adı, ilçe/şehir, kategori ve tek işlem satırı gösterilir; tam adres, kartın diğer işlemleri veya tam kart verisi gösterilmez.
- **Enumeration önleme**: eşleşme bulunamadığında hangi alanın tutup tutmadığına dair ipucu verilmez, jenerik "bulunamadı" mesajı gösterilir.
- **BDDK kapsam dışı**: Moka United bir banka değil ödeme kuruluşu olduğundan denetim TCMB/MASAK kapsamındadır; rapor bu ayrımı esas alır.

**Bilinen sınırlamalar (demo kapsamında, üretime taşınmadan önce ele alınmalı):**
- İşlem eşleştirmesi istemci tarafında (tarayıcıda) çalışır; `dispute-txns.js` şu an tüm mock veri setini içerir. Üretimde bu sorgu sunucu tarafına taşınmalı, istemciye yalnızca eşleşen kayıt gönderilmelidir.
- Asgari bilgi gösterilmeden önce ek bir kart hamili doğrulama adımı (OTP / bilgi tabanlı soru) bulunmuyor; KVKK'nın 2026/266 sayılı ilke kararı ve TCMB'nin güçlü kimlik doğrulama gerekliliği doğrultusunda üretim öncesi eklenmesi önerilir.

## 9. Kullanılan Teknolojiler

- **Backend**: Python stdlib (`http.server`), FastAPI + Uvicorn (yalnızca 2 sınıflandırma servisi)
- **ML**: `dbmdz/bert-base-turkish-cased` (BERTurk) fine-tuning, HuggingFace `transformers` + `datasets` + PyTorch
- **Opsiyonel LLM**: Ollama (`qwen2.5:3b`, tamamen yerel, veri dışarı çıkmaz)
- **Frontend**: Vanilla HTML/CSS/JS (framework yok), tasarım tokenleri ile CSS değişken sistemi
- **Veri kalıcılığı**: Atomik JSON dosya yazımı (`.tmp` → `os.replace`) + `threading.Lock`

## 10. Ekip

Coderspace **Moka United AI Ideathon & Hackathon** kapsamında 2 kişilik takım tarafından, git üzerinden (branch: `vedat`, PR akışıyla `master`'a merge) geliştirilmiştir.
