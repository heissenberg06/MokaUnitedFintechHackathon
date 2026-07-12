# Moko United Klon Projesi — Genel Özet

> Bu belge projenin **ne olduğunu, neyi nasıl yaptığımızı** ve teknik yapıyı özetler.
> Tamamı eğitim/demo amaçlıdır; gerçek Moka United / Şikayetvar ile bağlantısı yoktur.

---

## 1. Proje Nedir?

İki web sitesinin **statik + hafif backend klonu**:

1. **Moka United kurumsal sitesi** (`mokaunited.com/tr`) — tamamen statik HTML/CSS/JS klonu (24 sayfa).
2. **Şikayetvar "Moka United" şikayet sayfası** (`sikayetvar.com/moka-united`) — statik arayüz + **sıfır bağımlılıklı Python backend** ile şikayet ve yorumların kalıcı olarak eklenip görüntülenebildiği bir klon.

Amaç: gerçek bir markanın web varlığını taklit eden, çalışır durumda, ekipçe geliştirilen bir demo üretmek.

---

## 2. Klasör Yapısı

```
~/Downloads/moko-repo/            ← git deposu (GitHub: heissenberg06/...)
└── Moko_United/
    ├── index.html                ← elle yönetilen tek sayfa
    ├── build_pages.py            ← 24 sayfayı üreten Python jeneratörü
    ├── MOKA_UNITED_FRONTEND_ANALIZ.md   ← analiz + görev listeleri
    ├── PROJE_OZETI.md            ← (bu dosya)
    ├── *.html                    ← build_pages.py'nin ürettiği sayfalar
    │   (hakkimizda, urunler, pos-cozumleri, iletisim, itiraz, itiraz-durum, ...)
    ├── assets/
    │   ├── css/style.css         ← tasarım tokenları + tüm stiller
    │   ├── js/components.js       ← header/CTA/footer bileşen enjeksiyonu
    │   ├── js/main.js             ← etkileşimler (reveal, sayaç, modal, arama...)
    │   └── images/*.svg           ← tüm görseller (SVG olarak elde üretildi)
    ├── .claude/launch.json        ← önizleme sunucusu (moka-static, port 8755)
    └── sikayetvar/                ← ALT PROJE (Şikayetvar klonu)
        ├── index.html
        ├── server.py             ← Python stdlib backend (port 8756)
        ├── SIKAYETVAR_KLON_ANALIZ.md
        ├── assets/css/sv.css
        ├── assets/js/sv.js
        ├── assets/img/favicon.svg
        └── data/complaints.json   ← kalıcı veri (JSON)
```

---

## 3. Nasıl Çalışıyoruz? (İş Akışı)

Proje **iki modelli** bir akışla ilerledi:

| Rol | Model | Görevi |
|-----|-------|--------|
| **Analist** | Fable | Canlı siteyle klonu sayfa sayfa karşılaştırır, eksikleri `.md` dosyalarına yazar. **Kod yazmaz.** |
| **Geliştirici** | Opus | `.md` dosyasındaki görev bölümlerini sırayla uygular, kodlar, tarayıcıda doğrular. |

**Kurallar:**
- İçerik değişiklikleri `build_pages.py` üzerinden yapılır → `python3 build_pages.py` çalıştırılınca 24 sayfa yeniden üretilir. **Sadece `index.html` elle düzenlenir.**
- Metinler telif nedeniyle **bilinçli parafraze** edilir, birebir kopyalanmaz.
- Şikayet metinleri ve kullanıcı adları **kurgudur** (telif + KVKK).

---

## 4. Moka United Sitesi — Teknik Detay

- **Statik yapı:** Framework yok. Saf HTML/CSS/JS.
- **Bileşen enjeksiyonu:** `components.js`, ortak header/CTA/footer parçalarını `#header-mount`, `#cta-mount`, `#footer-mount` noktalarına yerleştirir; aktif menü `data-active` ile işaretlenir.
- **Etkileşimler (`main.js`):** IntersectionObserver ile scroll-reveal + sayı sayaçları, akordeonlar, kayan şerit (marquee), modaller, çerez bandı, arama katmanı.
- **Tasarım sistemi:** CSS değişkenleri (design tokens), Poppins fontu, tema sınıfları (`theme-blue`, `theme-green-dark` vb.).
- **Görseller:** Tüm illüstrasyon ve ürün görselleri elde **SVG** olarak üretildi (hero, kart, cüzdan, kiosk, güvenlik, şehir vb.).
- **Klona özgü eklemeler:** `basvuru.html` (başvuru formu) ve `panel-giris.html` (panel girişi) bilinçli olarak eklendi.
- **Ekip eklentileri:** `itiraz.html` ve `itiraz-durum.html` (işlem numarasıyla itiraz durumu sorgulama) — takım arkadaşları ekledi.

**Durum:** 4 geliştirme turu tamamlandı, tarayıcıda doğrulandı, bilinen görsel eksik yok.

---

## 5. Şikayetvar Klonu — Teknik Detay

En teknik kısım burası: **statik arayüz + gerçek çalışan backend.**

### Backend (`server.py`)
- **Sıfır bağımlılık:** Sadece Python standart kütüphanesi (`http.server`, `ThreadingHTTPServer`). `pip install` yok.
- **Port:** 8756. Statik dosyaları ve JSON API'yi **aynı origin'den** sunar.
- **Kalıcılık:** Veriler `data/complaints.json`'da tutulur. Yazma **atomik** (`.tmp` dosyasına yaz → `os.replace`) ve `threading.Lock` ile korunur → bozulma/çakışma olmaz.
- **API uç noktaları:**
  - `GET/POST /api/complaints` — şikayet listele / ekle
  - `GET /api/complaints/{id}` — tekil şikayet
  - `POST /api/complaints/{id}/comments` — yorum ekle
  - `POST /api/complaints/{id}/support` — destekle
  - `POST /api/complaints/{id}/view` — görüntülenme

### Güvenlik
- **XSS koruması:** Sunucu tarafında `html.escape` ile tüm kullanıcı girdisi kaçışlanır; istemci güvenle gösterir (varlık kodları çalışmaz, düz metin olarak görünür).
- **Path traversal koruması:** `../`, `%2e%2e/` gibi denemelerde **403** döner.
- **Kullanıcı adı maskeleme:** "Ahmet Kaya" → "A** K**".
- **Doğrulama:** Ad/başlık/metin uzunluk ve zorunluluk kontrolleri.

### Arayüz (`index.html` + `sv.css` + `sv.js`)
- Marka bloğu, yıldız puanı, memnuniyet skoru halkası (conic-gradient), etiket bulutu, şikayet listesi, sayfalama.
- "Şikayet Yaz" modalı, yorum ve destek butonları.
- **Türkçe-duyarlı arama** (`tr_lower` — büyük/küçük harf İ/ı sorununu çözer).
- Footer'da zorunlu **"eğitim/demo klon"** açıklaması.
- Seed veri: yetkisiz işlem temalı **kurgu** şikayetler (gerçek değil).

**Renk paleti (orijinalden çıkarıldı):** mor `#695de9` (primary), yeşil `#3ad08f` (secondary), koyu `#272635`, açık `#f4f5f9`, beyaz header.

### Önizleme Notu
Önizleme aracı sikayetvar sunucusunu otomatik başlatamadı (launch.json'u başka klasörden okuyordu); çözüm: `python3 sikayetvar/server.py` elle arka planda çalıştırılıp tarayıcı `http://localhost:8756`'ya yönlendirildi.

---

## 6. Git / Ekip Çalışması

- **Depo:** `~/Downloads/moko-repo` — GitHub `heissenberg06/...`, `master` + `vedat` dalları.
- **Ekip:** Birden fazla geliştirici (vedat, berk...), PR akışı (#4, #5 merge edildi).
- **Standart push akışı:**
  ```bash
  git add -A
  git commit -m "mesaj"
  git pull --rebase origin vedat   # takımdakini al, çakışmayı önle
  git push origin vedat
  ```
- **`.DS_Store` ve `__pycache__`** gibi gereksiz dosyalar `.gitignore`'a alındı / alınmalı.
- **Not:** Ekip ortamı olduğu için `--force` / `reset --hard` yerine normal `pull --rebase` tercih edilir (takım commit'lerini silmemek için).

---

## 7. Kabul Kriterleri (Doğrulandı ✅)

**Moka United:**
- 24 sayfa üretiliyor, header/footer/CTA tutarlı, animasyonlar çalışıyor, görsel eksik yok.

**Şikayetvar:**
- Şikayet ekleme kalıcı (sunucu yeniden başlasa da kayıp yok).
- Yorum ekleme çalışıyor; destekleme tek tıkla.
- XSS düz metin olarak nötralize ediliyor.
- Türkçe-duyarlı arama çalışıyor.
- Path traversal 403 veriyor.
- Mobil/responsive uyumlu.

---

## 8. Özet Cümle

Gerçek bir fintech markasının (Moka United) hem **kurumsal sitesini** hem de onun hakkındaki **şikayet platformu sayfasını** klonladık; ikincisine sıfır bağımlılıklı, güvenli, kalıcı bir Python backend ekleyerek kullanıcıların gerçekten şikayet ve yorum bırakabildiği çalışır bir demo ürettik — tamamı ekipçe, git üzerinden, eğitim amaçlı.
