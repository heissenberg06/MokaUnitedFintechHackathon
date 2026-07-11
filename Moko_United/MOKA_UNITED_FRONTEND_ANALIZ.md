# MOKA UNITED (mokaunited.com/tr) — Frontend Klon Spesifikasyonu

> Bu doküman, https://www.mokaunited.com/tr sitesinin frontend yapısının detaylı analizidir.
> Amaç: Bu dokümana bakarak sitenin birebir klonunu üretebilmek.
> Analiz tarihi: 2026-07-11. Sayfalar sunucu tarafında render ediliyor (statik HTML + JS animasyon katmanı).
> **GÜNCELLEME (2026-07-11, 2. tur):** Klonun mevcut durumu canlı site ile sayfa sayfa karşılaştırıldı; görev listesi Bölüm 12'ye yazıldı.
> **GÜNCELLEME (2026-07-11, 3. tur):** Bölüm 12'deki işlerin TAMAMI uygulandı ve tarayıcıda doğrulandı.
> Klon canlı siteyle yeniden karşılaştırıldı. Güncel durum ve KALAN işler için **Bölüm 13**'e bak. Kodlamaya oradan başla.
> Not: Uzun pazarlama paragrafları bu dokümanda özetlenmiştir; birebir metin gerekiyorsa canlı siteden alınmalı veya yeniden yazılmalıdır. Görseller `/medium/...` CMS yollarından servis edilir — klonda placeholder görsel kullanılabilir.

---

## 1. GENEL BAKIŞ VE TEKNOLOJİ YIĞINI

- **Site türü:** Kurumsal fintek tanıtım sitesi (POS, kart, cüzdan, para transferi, akıllı kasa, kiosk çözümleri).
- **Dil:** TR ana dil (`/tr`), EN (`/`), ayrıca harici domainlerde AZ/KA/UZ/RU sürümleri.
- **CSS framework:** Bootstrap 4 grid (col-12/col-lg-*, d-flex, d-none d-lg-* utility'leri) + özel tema (`style.min.css`, ~414KB).
- **Font:** Google Fonts **Poppins** (400, 500, 600, 700, 800, 900). `body{font-family:Poppins,sans-serif;font-size:14px;letter-spacing:-.011em}`.
- **JS kütüphaneleri:**
  - **GSAP** + **ScrollSmoother** + **ScrollTrigger** → yumuşak kaydırma ve scroll animasyonları
  - **Swiper** → referans logo slider'ları (3 sıra, sonsuz akış)
  - **two.js** ve **matter.js** → dekoratif canvas/fizik animasyonları
  - **lottie-player** (unpkg) → vektör animasyonlar
  - **intl-tel-input** → telefon input'u (iletişim formu)
  - **cookieconsent** → çerez bandı (özelleştirilmiş, dil algılamalı)
  - **instant.page** → link ön-yükleme
- **İkonlar/görseller:** SVG logolar `/_assets/images/`, içerik görselleri CMS'den `/medium/{Tip}/Image/{guid}`.
- **Favicon:** `/_assets/images/favicon2/` altında apple-icon + android-icon setleri, `manifest.json`.

### Sayfa listesi (TR sitemap)
```
/tr                                  → Ana sayfa
/tr/hakkimizda                       → Kart-grid yönlendirme sayfası
/tr/hakkimizda/hikayemiz             → Hikaye/zaman çizelgesi
/tr/hakkimizda/kurumsal-yonetim      → Yönetim kadrosu kartları
/tr/hakkimizda/kariyer               → Kariyer tanıtımı
/tr/hakkimizda/istirakler            → İştirakler (RUUT, Turan, Up Enerji, SmartUp)
/tr/urunler                          → Kart-grid yönlendirme sayfası
/tr/kart-cozumleri                   → Ürün detay (body: product-detail blue)
/tr/cuzdan-cozumleri                 → Ürün detay (body: product-detail green-medium orange)
/tr/para-transferi                   → Ürün detay (body: product-detail yellow-soft purple)
/tr/akilli-kasa                      → Ürün detay (body: product-detail yellow)
/tr/kiosk                            → Ürün detay (body: product-detail green-dark blue)
/tr/pos-cozumleri                    → Kart-grid yönlendirme sayfası
/tr/pos-cozumleri/sanal-pos          → İçerik + SSS sayfası
/tr/pos-cozumleri/fiziki-pos         → İçerik + SSS sayfası
/tr/pos-cozumleri/linkle-tahsilat    → İçerik + SSS sayfası
/tr/iletisim                         → Form + ofis sekmeleri (body: product-detail)
/tr/yasal-belgeler-ve-temsilcilikler → Kart-grid (20 belge kartı) + çok sayıda alt sayfa
/tr/gizlilik-politikasi, /tr/kisisel-verilerin-korunmasi, /tr/cerez-politikasi
```

---

## 2. TASARIM SİSTEMİ (DESIGN TOKENS)

### 2.1 Renk paleti (TR sürümünde geçerli olanlar)
| Kullanım | Renk |
|---|---|
| Ana marka mavisi (başlıklar, h1, buton metni) | `#0d3c94` |
| Neon yeşil — primary buton zemini | `#2bfb97` (hover katmanları `#33ffa3`, `#66ffba`) |
| Neon yeşil vurgu (gradyanlarda) | `#00ff8c` |
| Koyu metin | `#1b1c1a` / `#000` |
| Beyaz | `#fff` |
| Sarı bölüm zemini | `#f8f2a7` (oval çerçeve `#f4eb7b`) |
| Lila bölüm zemini | `#a89cec` (oval çerçeve `#b4a9ef`) |
| Turkuaz | `#50dcc8`, `#1cc8b6` |
| Açık gri kutu zemini | `#f8f8f8`, `#f3f3f3`, `#f0f0f0` |
| Footer menü zemini | `#f3f3f3` |
| Sayfa tema zeminleri (body class) | `blue:#4daac6`, `yellow:#ffff9c`, `yellow-soft:rgba(255,255,156,.75)`, `green-medium:#00ab92`, `green-dark:#064a45`, `gray:#d5d1cb`, `light-gray:#d9dcde`, `green:#85ebbd` |
| Renkli bölüm zeminleri (cp_item) | `bg-colorful-green:#2bfb97`, `bg-colorful-yellow:#fef593`, `bg-colorful-blue:#219cc3`, `bg-colorful-darkbeige:#cec7c0`, `bg-colorful-black:#000 (koyu)` |
| Bootstrap değişkenleri | `--primary:#DA291C` (eski marka kırmızısı, az kullanılır), `--secondary:#F0F0F0`, `--dark:#282a3c` |

**Kritik kural:** `html[lang=tr]` seçicisiyle tüm buton metinleri ve accordion başlıkları `#0d3c94` (koyu mavi) olur. Koyu zeminli bölümler TR'de `#0d3c94` arka plana zorlanır (`.fifth-section`, `.tenth-section-wrapper` → `background-color:#0d3c94!important`).

### 2.2 Gradyan başlık efekti (imza görsel öğe)
Alt sayfa H1'leri (`.content-parts-title.multicolors`) animasyonlu gradyan text-clip kullanır:
```css
background: linear-gradient(269.79deg, #50dcc8 21.04%, #faf19d 50.46%, #00ff8c 81.77%);
background-size: 150% auto;
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
animation: anime 10s infinite;   /* background-position kaydırma animasyonu */
```

### 2.3 Tipografi
| Öğe | Stil |
|---|---|
| h1 | `font-weight:800; font-size:clamp(42px,3vw,96px); color:#0d3c94; letter-spacing:-.04em` |
| h2 | `font-weight:800; font-size:clamp(35px,2.5vw,64px); letter-spacing:-.04em` |
| h3 | `font-weight:800; font-size:clamp(20px,1.5vw,40px)` |
| h4 | `font-weight:300; font-size:clamp(20px,1.5vw,40px)` (alt başlık/lead metin) |
| body | 14px, Poppins, `letter-spacing:-.011em` |
| Başlık kalıbı | Başlıklarda bir kısım normal, bir kısım `<strong>` (extra kalın/renk vurgusu). CMS `**bold**` ve `~alt-vurgu~` işaretlemesi kullanıyor. |

### 2.4 Butonlar
Ortak: `border-radius:40px; font-weight:800; display:inline-flex; align-items:center; justify-content:center; max-height:80px; padding ~ 1em 2em;` metin BÜYÜK HARF. Hover'da `:before/:after` katmanlarıyla soldan dolan renk animasyonu.
- **button-primary:** zemin `#2bfb97`, metin TR'de `#0d3c94`. Hover katmanları `#33ffa3` / `#66ffba`.
- **button-secondary:** şeffaf zemin + `2px solid #2bfb97` çerçeve; hover katmanları `#ebfff6` / `#ccffe8`.
- **button-third:** çerçevesiz ikon butonu (header'da arama/dil), `font-size:clamp(24px,1.4vw,32px)`.
- **button-icon:** ok ikonlu link buton varyantı.

### 2.5 Köşe yarıçapları ve kutular
- Kartlar/kutular: `border-radius:16px`
- Mega menü: `border-radius:24px`
- Hap şeklinde logo kutuları: `border-radius:188px`
- Sayaç kutuları: `border-radius:160px`
- Footer alt kavis: `border-radius:0 0 60vh 60vh` (dev yarım daire)

### 2.6 Breakpoint'ler (Bootstrap 4)
`sm:576px, md:768px, lg:992px, xl:1200px`. Masaüstü/mobil ayrımı `lg` üzerinden (`d-none d-lg-flex` vb.).

---

## 3. HEADER (tüm sayfalarda ortak)

Yapı: `header.header` — sol logo, ortada menü, sağda buton grubu. Sayfa açılışında `#overlay.overlay` (loader) var.

```
header.header
├── a.logo → iki logo img: mokaunited-logo.svg (koyu) + mokaunited-logo-light.svg (açık, koyu temada)
├── nav.main-menu (d-flex)
│   ├── (mobil) a.mobile-search-toggle "What are you looking for?"
│   ├── .menu-item → a "HAKKIMIZDA" + .mega-menu
│   │   └── mega-menu-item'lar: HİKAYEMİZ / KURUMSAL YÖNETİM / MOKA UNITED'TA KARİYER / İŞTİRAKLER
│   ├── .menu-item → a "ÜRÜNLER" + .mega-menu (görselli)
│   │   └── KART ÇÖZÜMLERİ / CÜZDAN ÇÖZÜMLERİ / PARA TRANSFERİ / AKILLI KASA / KİOSK (her biri + küçük görsel)
│   ├── .menu-item → a "POS ÇÖZÜMLERİ" + .mega-menu
│   │   └── SANAL POS / FİZİKİ POS / LİNKLE TAHSİLAT
│   └── (mobil) HEMEN BAŞVURUN + PANEL GİRİŞİ butonları
└── .buttons
    ├── a.button-secondary "HEMEN BAŞVURUN" → https://basvuru.mokaunited.com
    ├── a.button-primary "PANEL GİRİŞİ" → https://pos.mokaunited.com
    ├── button.button-third (arama ikonu, js-toggle-search)
    ├── .lang-wrapper → bayraklı dil dropdown: ENGLISH/TÜRKÇE/AZƏRBAYCAN/ქართული/O'ZBEK/РУССКИЙ
    ├── (mobil) a.button-primary "İLETİŞİM"
    └── (mobil) a.mobile-menu-button (hamburger: 52px siyah daire, 2 beyaz çizgi, aktifken X'e dönüşür)
```

**Mega menü davranışı:** hover'da açılır; `position:absolute; top:50%; padding:100px 16px 16px;` beyaz zemin `:before` katmanıyla `top:60px`'ten başlar, `border-radius:24px`. Menü öğeleri: `background:#fcfade` (krem), `font-weight:800; font-size:clamp(16px,1.5vw,30px); padding:2vw 3vw; border-radius:16px;` hover'da renk geçişi (0.5s).

**Arama:** `form.search-wrapper` tam ekran overlay, `input[name=q]` placeholder "Ne Aramıştınız?".

**Mobil:** menü tam ekran `.menu-overlay` ile açılır; sağ altta sabit `a.mobile-whatsapp-link` (WhatsApp ikonu).

---

## 4. FOOTER (tüm sayfalarda ortak)

### 4.1 Pre-footer CTA (`section#tenth.tenth-section`)
Her sayfanın sonunda dev CTA bloğu:
- `.tenth-section-wrapper`: zemin **#0d3c94**, `text-align:center`, `padding:20vh 10vh 80vh`, alt köşeler `border-radius:0 0 60vh 60vh` (dev kavis). 
- İçerik: gri renkte dev h2 satırı **"TANIŞALIM MI?"** + beyaz **"BİZ MOKA UNITED"** vurgu satırı (`font-size:clamp(30px,4vw,126px)`).
- `.links-wrapper`: WhatsApp kutusu (ikon + "Whatsapp Numarası" + `0850 252 22 22` linki + "İLETİŞİME GEÇ" butonu) ve `.social-links`: LinkedIn, Instagram, X, YouTube, Snapchat, TikTok ikonları (SVG, `/_assets/images/footer/`).

### 4.2 Ana footer
```
footer > .content-wrapper
├── section.row
│   ├── nav.footer-menu (zemin #f3f3f3, radius 16px, padding 40px)
│   │   ├── Sütun "HAKKIMIZDA": Hikayemiz / Kurumsal Yönetim / MOKA UNITED'TA KARİYER / İştirakler
│   │   ├── Sütun "ÜRÜNLER": Kart Çözümleri / Cüzdan Çözümleri / Para Transferi / Akıllı Kasa / Kiosk
│   │   ├── Sütun "POS ÇÖZÜMLERİ": Sanal POS / Fiziki Pos / Linkle Tahsilat
│   │   ├── Sütun "İLETİŞİM", Sütun "ÇEREZ POLİTİKASI"
│   │   └── .footer-logos: TCMB, BKM, TÖDEB, PCI DSS, Visa, Mastercard, Troy, MASAK logoları (dış linkli)
│   └── .footer-contact
│       ├── h5 "İLETİŞİM"
│       └── Ülke accordion'ları: Türkiye / Birleşik Krallık / Azerbaycan / Almanya / Gürcistan
│           └── Türkiye içinde nav-pills sekmeler: İstanbul Merkez | Ankara | İstanbul Teknopark | İstanbul Gayrettepe
│               Her sekme: adres + "YOL TARİFİ AL" (Google Maps) + Telefon/Faks/E-Posta/Mersis No satırları
├── Orta: mokaunited-logo.svg
└── nav.footer-sub-menu: Yasal Belgeler ve Temsilcilikler | Gizlilik Politikası | Kişisel Verilerin Korunması | Bilgi Toplumu Hizmetleri
```

Önemli iletişim verileri (footer'da geçen):
- İstanbul Merkez: "Levent Mah. Meltem Sk. İş Bankası Kuleleri No: 10 Kule: 2 PK. 34330 Beşiktaş/İstanbul", Tel `+908502522222`, Faks `0 (212) 241 59 59`, `info@mokaunited.com`, Mersis `0178071182100017`
- Londra: "1 King William St, London EC4N 7AF" — Bakü: Babek Plaza — Frankfurt: Maxi Digital GmbH, Taunustor 1 (`info@ruutapp.com`) — Tiflis: United Payment Georgia LTD (`info@unitedpayment.ge`)

---

## 5. ANA SAYFA (/tr) — BÖLÜM BÖLÜM

Body: `class="home-page"`, zemin beyaz. İçerik `main > .container-fluid > .content-parts.row` içinde `cp_item` sütunları olarak dizilir.

### 5.1 Hero (`section#first.first-section`)
- İki sütun: sol `col-lg-6` metin, sağ `col-lg-6` görsel.
- H1: **"TEK PLATFORM,"** + strong **"SINIRSIZ POTANSİYEL"** (koyu mavi, 800).
- Altında h4/paragraf bloğu (~5 paragraf): global altyapı, tek çatı altında Sanal POS/fiziki POS/SoftPOS/kart-cüzdan/akıllı kasa/kiosk, döviz POS - link ile ödeme - cross-border, AI destekli yönlendirme + fraud önleme + merkezi panel anlatımı ve başvuru çağrısı (özet — birebir metin canlı sayfadan).
- Butonlar: `HEMEN BAŞVURUN` → basvuru.mokaunited.com, `PANEL GİRİŞİ` → pos.mokaunited.com (ikisi de primary).
- Sağda büyük ürün görseli (`first-section-image`).
- Sol içerik `padding:80px 0 0 8vw` (TR'de `margin-bottom:100px`).

### 5.2 Koyu mavi büyüme bölümü (`section#fifth.fifth-section`)
- Zemin TR'de **#0d3c94**; arkada `.grow-bg`: 3 adet dev oval blok (`border:10vw solid #1d1d1d; border-radius:438px`, yükseklikleri %35/%70/%90 — "büyüyen barlar" görseli), sol içerik `margin:150px 0 150px 8vw; width:50%`.
- Beyaz h2: "İŞİNİZİ BİRLİKTE **BÜYÜTELİM**, **ÖDEME ALIN.**"
- 2 paragraf (Sanal+Fiziki POS tek panel; 7/24 fraud izleme — özet).
- Butonlar: HEMEN BAŞVURUN / PANEL GİRİŞİ (button-secondary, beyaz metin).

### 5.3 Kart & Cüzdan tanıtımı (iki sütunlu içerik bloğu)
- Sol `col-lg-4`: görsel (kart görseli). Sağ `col-lg-5`: h2 "**KART VE CÜZDAN ÇÖZÜMLERİMİZLE** FİNANSAL DENEYİMİNİZİ DÖNÜŞTÜRÜN." + h4 açıklama (bayi/satıcı/çalışan/müşteri ağını tek altyapıda birleştirme — özet) + `İLETİŞİME GEÇİN` butonu.
- (HTML'de ayrıca `d-none` gizli eski üçüncü bölüm var — klona gerek yok.)

### 5.4 Para transferi bloğu (ayna düzen)
- Sol `col-lg-5` metin: h2 "DÜNYANIN HER YERİNE **IŞIK HIZINDA** **PARA TRANSFERİ**" + h4 "Yurt İçi ve Yurt Dışı Para Transferi" + butonlar `İLETİŞİME GEÇİN`, `SEÇENEKLERİ KEŞFEDİN` → /tr/para-transferi.
- Sağ `col-lg-4` görsel.

### 5.4b Akıllı Kasa + Kiosk tanıtım blokları (2. tur tespiti — klonda YOK)
Para transferi bloğundan sonra orijinal ana sayfada iki tanıtım bölümü daha var (aynı iki sütunlu split kalıbı, dönüşümlü yerleşim):
- **Akıllı Kasa:** nakdin akıllı POS/kasa terminalleriyle dijitalleşmesi anlatımı + `SEÇENEKLERİ KEŞFEDİN` → /tr/akilli-kasa.
- **Kiosk:** 7/24 fatura ödeme, para çekme vb. self-servis vurgusu + link → /tr/kiosk.

### 5.5 Referanslar (`section#second.reference-section`)
- Başlık h2: "**DEĞER** KATTIKLARIMIZ".
- **3 adet Swiper marquee sırası** (`references-slider`, `-2`, `-3`), tam genişlik (`margin:0 -8vw`), sürekli akan logolar; her logo beyaz hap kutuda (`height:120px; border-radius:188px; padding:0 50px; shadow 0 4px 11px rgba(0,0,0,.04)`).
- Sıra 1: Samsung, Decathlon, Sahibinden, ENERJİSA, Yemeksepeti. Sıra 2: BTA, MARS, abb, Hektaş, poca. Sıra 3: tatilbudur, up enerji, DOA, TBBB, turan, vavacar, Yandex.

### 5.6 Sayılarla Moka United (`section#nineth.nineth-section`)
- Solda 2x2 `count-box` grid (siyah/koyu zemin, `border-radius:160px; padding:70px 3vw`, beyaz metin, üstte SVG ikon):
  - 6 Ülke (icon-global.svg) — 120 M+ İşlem Sayısı (icon-exchange.svg) — 250 + Çalışan (icon-people.svg) — 10 Milyar USD İşlem Hacmi (icon-money-send.svg)
  - Sayı stili: `font-size:clamp(40px,4vw,96px); font-weight:800` (scroll'da sayaç animasyonu).
- Sağda h2 "**SAYILARLA** ..." + 3 paragraf (6 ülkedeki ofisler; sunulan çözümler; güvenlik/regülasyon vurgusu — özet).

### 5.7 SSS Accordion
- Başlık: "MOKA UNITED HAKKINDA SIKÇA SORULAN SORULAR" (h2, ortalı).
- `.accordion > .accordion-item` listesi; başlıklar (`accordion-header`, `padding:24px 45px; font-size:clamp(14px,1.3vw,30px)`, TR'de mavi, sağda dönen ok ikonu):
  1. Moka United nedir?
  2. Moka United POS çözümleri neler?
  3. Kimler POS Çözümleri için başvurabilir?
  4. Başvurum kaç günde sonuçlanır?
  5. Komisyon oranları nelerdir?
  6. Hangi kartlar ile ödeme alabilirim?
  7. Moka United hangi ülkenin, hangi bankanın?
  8. Moka United hangi hizmetleri sunar?
  9. Moka United çözümleri hangi işletmeler için uygun?
  10. Moka United işletmelere ne gibi avantajlar sağlar?
  11. Moka United ile çalışmaya nasıl başlayabilirim?
  12. Moka United ödeme sistemlerinde güvenliği nasıl sağlıyor?
  13. Moka United ile uluslararası ödeme almak mümkün mü?
- Cevaplar 1-4 paragraf (özet içerik; örn. 3 iş günü sonuçlanma, PCI DSS v4.0.1 + ISO 27001 + 3D Secure 2.0, İş Bankası Moka + OYAK United Payment birleşimi).
- Altta `DAHA FAZLA GÖSTER` butonu (ilk N madde görünür, tıklayınca tümü açılır).

### 5.8 Kapanış: `#tenth` CTA + footer (bkz. Bölüm 4).

---

## 6. ORTAK ALT SAYFA ŞABLONLARI

### 6.0 Alt sayfa ortak iskeleti
- Breadcrumb: `Moka United / [Üst sayfa /] Sayfa adı` (üstte, küçük).
- `h1.content-parts-title.multicolors` — animasyonlu gradyan başlık, ortalı.
- İçerik `content-parts` grid'i: `cp_item col-12 col-lg-{n} offset-lg-{n}` kalıbıyla metin/görsel sütunları.
- Sayfa sonu: `#tenth` CTA + footer.

### 6.1 "Landing kart-grid" şablonu (hakkimizda, urunler, pos-cozumleri, yasal-belgeler)
`section.section.landing.about-us` içinde `card-component` grid'i:
- Her kart: `a.card` (tümü tıklanabilir), `background:rgba(194,198,201,.2); border-radius:16px; padding:40px; min-height:350px;` içinde `h2.card-title` + sağ altta görsel (`card-img`).
- **hakkimizda:** HİKAYEMİZ, KURUMSAL YÖNETİM, MOKA UNITED'TA KARİYER, İŞTİRAKLER (görselsiz)
- **urunler:** KART ÇÖZÜMLERİ, CÜZDAN ÇÖZÜMLERİ, PARA TRANSFERİ, AKILLI KASA, KİOSK (görselli)
- **pos-cozumleri:** SANAL POS, FİZİKİ POS, LİNKLE TAHSİLAT
- **yasal-belgeler:** 20 belge kartı (ÜRÜN VE ÜCRETLER, BAĞIMSIZ DENETİM BİLGİLERİ, ŞİKAYET POLİTİKASI, TEK SEFERLİK ÖDEME BİLGİSİ, TEMSİLCİLİKLERİMİZ, BİLGİ GÜVENLİĞİ POLİTİKASI, KVKK AYDINLATMA METNİ, TÖDEB HAKEM HEYETİ, ŞİRKET BİLGİLERİ, BİLGİ TOPLUMU HİZMETLERİ, vb.)

### 6.2 "İçerik + SSS" şablonu (sanal-pos, fiziki-pos, linkle-tahsilat)
Sıra (sanal-pos örneği):
1. **İki sütun tanıtım:** sol `col-lg-6` h2 "Online Ödeme Almanın En Kolay Yolu: Moka United Sanal POS" + paragraf; sağ `col-lg-5` görsel.
2. **3'lü bilgi kutusu satırı:** `transfer-boxes-item` x3 (`col-lg-4`, `background:#f8f8f8; border-radius:16px; padding:40px; height:100%`), her biri üstte görsel + h5 başlık + paragraf: "Sanal POS Nedir?", "Sanal POS Nasıl Alınır?", "Moka United Sanal POS Nedir?" (fiziki-pos: Nedir/Avantajları/Kimler Kullanabilir; linkle-tahsilat: Nedir/Moka United Linkle Tahsilat Nedir/Avantajları).
3. **Avantajlar:** sol metin + `ul` madde listesi (özel bullet ikonu), sağ görsel. (Maddeler: tek entegrasyon-çoklu banka, yüksek onay oranı, raporlama paneli, hızlı kurulum, güvenli altyapı, ölçeklenebilirlik.)
4. **"... ile Neler Yapabilirsiniz?"** tam genişlik metin + madde listesi (taksit, dövizli ödeme, 3D/Non-3D, banka kampanya entegrasyonları, kart saklama/tekrarlı ödeme).
5. **"Kimler Kullanabilir?"** metin + liste (e-ticaret, mobil uygulama, dijital platform, pazaryeri, abonelik/B2C) + görsel.
6. **SSS accordion** ("Sanal POS Hakkında Sıkça Sorulan Sorular", ~10 soru; güvenlik, komisyon, taksit, başvuru süresi, yurtdışı ödeme, kart şemaları, 3D Secure vb.) + `DAHA FAZLA GÖSTER`.

### 6.3 "Ürün detay" şablonu (kart-cozumleri, cuzdan-cozumleri, para-transferi, akilli-kasa, kiosk)
- Body'de tema sınıfı → sayfanın tamamı renkli zemin alır (bkz. 2.1 body renkleri) ve `product-detail` sınıfı.
- En üstte **Ribbon hero görseli** (`/medium/Ribbon/Image/...`) + dekoratif `band-5.png` renkli bant deseni (mobilde `band-5-sm.png`).
- Ardından değişken sayıda içerik bloğu: iki sütunlu görsel+metin bölümleri, `transfer-boxes-item` grid'leri, renkli `bg-colorful-*` şerit bölümleri.
- **ORTAK KALIP (2. tur tespiti):** Her ürün detay sayfasında sayfa içinde **inline talep formu** var (Ad, E-Posta, Telefon, Şirket [+bazılarında Konu], Aydınlatma Metni onayı, GÖNDER; başarı mesajı "MESAJINIZ BAŞARIYLA GÖNDERİLMİŞTİR" + 48 saat içinde dönüş notu). Klonda bu form hiçbir ürün sayfasında yok.
- Sayfa temaları ve öne çıkan bölümleri:
  - **kart-cozumleri** (`blue` → zemin #4daac6): "KART ÇÖZÜMLERİMİZLE FİNANSAL ÖZGÜRLÜĞÜN ANAHTARI CEBİNİZDE!" ribbon. **~10 bölüm (2. tur, sırayla):** 1) "KENDİ KART EKOSİSTEMİNİZİ YARATIN" (inline form), 2) "YALNIZCA BİRKAÇ GÜNDE MASTERCARD, VISA YA DA TROY KART PROGRAMI", 3) "SİZİN MARKANIZ, BİZİM ALTYAPIMIZ", 4) "MARKANIZA ÖZEL ÇÖZÜMLER" (dinamik harcama kontrolleri, MCC kategorileri, limitler, API entegrasyonları), 5) "GÜVENLİ İŞLEMLERLE KAFANIZ RAHAT ETSİN" (7/24 AI fraud izleme), 6) "SADAKAT PROGRAMLARI İLE KART İŞİNİZİ BÜYÜTÜN" (cashback), 7) "AÇIK API'LER İLE KART PROGRAMINIZI KURUN VE TEST EDİN" (developer portal), 8) "ŞEHİR KARTLARI: AYNI ŞEHRE AİT İNSANLAR", 9) "AKILLI ŞEHİR KARTLARI İLE SOSYAL FAYDA YARATIN" (belediye kartları: ulaşım, vergi, sosyal destek), 10) "BAĞIŞIN DEĞİŞİMİN GÜCÜNE İNANIYORUZ". ~16 görsel; SSS YOK.
  - **cuzdan-cozumleri** (`green-medium orange` → #00ab92): "YENİ NESİL İLETİŞİMİN ANAHTARI: DİJİTAL CÜZDAN" ribbon. Bölümler (2. tur): "PİŞMAN OLMAK YA DA CÜZDAN SAHİBİ OLMAK" (bireysel/ticari cüzdan, transfer, ön ödemeli kart; kredi/yatırım/sigorta, BNPL, cashback), "OTOMATİK OLARAK YÜKLENEN SÜPER GÜÇLER" (kutular: e-para lisansı, güçlü API'ler, ön ödemeli kart programı, teknik+yasal destek, proje rehberliği), **4 soruluk SSS** (6493 sayılı Kanun/TCMB/MASAK; faydalar; API kişiselleştirme; sandbox+developer portal), inline form: "FİNTEK DÜNYASINA İLK ADIMINIZI DİJİTAL CÜZDAN İLE ATIN!".
  - **para-transferi** (`yellow-soft purple`): "DÜNYANIN HER YERİNE IŞIK HIZINDA PARA TRANSFERİ" ribbon + açılış sorusu "Zamanınız çok kısıtlı ve dünya çok mu büyük?". Bölümler (2. tur): "BİZ İNSANLARI BİRLEŞTİRMEK VE DÜNYAYI BİR CEP TELEFONUNA SIĞDIRMAK İÇİN BURADAYIZ", avantaj kutuları (**%99,9 uptime, <3 dk işlem**, 7/24 takip, uyum/verimlilik), "ULUSLARARASI PARA TRANSFERİ" — Yurt Dışından/Türkiye'den ikilisi (iş ortakları: **Wise, TransferGO**), "TİCARİ İŞLETMELER İÇİN" (**190 ülke, 40+ para birimi** API), "Kendi Fintek Markanızı Hayata Geçirin!", ek hizmetler: **sanal hesap (TL)** ve **nöbetçi transfer** (mesai dışı), "Uyum ve Güvenlik" (TCMB/MASAK), form "TÜRKİYE'Yİ PARA TRANSFERİ AĞINIZA EKLEYİN" + **13 soruluk SSS** (lisans, kapsam, entegrasyon süresi, ülke/limitler, döviz, yasaklı sektörler: bahis/kumar/kripto).
  - **akilli-kasa** (`yellow` → #ffff9c): "NAKİT YÖNETİMİ ARTIK ÇOK DAHA KOLAY!" ribbon (depolama, toplama, dağıtım, izleme, sigorta). Bölümler (2. tur): tanışma bölümü (anında doğrulama/geçerlilik teyidi), verimlilik faydaları (sayım zamanından tasarruf, hızlı fon erişimi, sigorta kapsamı), operasyonel kolaylıklar (otomatik boşaltma izleme, banka masrafı yok, hafta sonu/tatil erişimi, taşıma sigortası), **inline form "AKILLI KASA İLE TANIŞMA ZAMANI" (2 konumda)** + SSS (kasa dolunca ne olur; banka masrafı; kayıp/çalıntı sorumluluğu).
  - **kiosk** (`green-dark blue` → #064a45, koyu): "SELF-SERVİS KİOSK DENEYİMİ İLE MÜŞTERİLERİNİZİ TANIŞTIRIN" ribbon. Bölümler (2. tur): inline form (dijitalleşme), "FARK YARATIN" (kaliteli malzeme/işçilik, dayanıklılık, özelleştirilebilir yazılım+donanım, kolay bakım, boyut/renk seçenekleri), "DÖNÜŞÜMÜ BAŞLATIN" (müşteri deneyimi, verimlilik, rekabet avantajı); sektör kutuları: TURİZM (otel check-in/out), HAVAALANI (lounge girişi, bagaj paketleme), PERAKENDE, FATURA SERVİSLERİ (akaryakıt, elektrik dağıtım), SAĞLIK (hızlı kayıt).

---

## 7. DİĞER SAYFALAR

### 7.1 İletişim (/tr/iletisim)
- H1 (ortalı): "SİZE NASIL YARDIMCI OLABİLİRİZ?"
- **Sol `col-lg-6`:** `.contact-box.active` — **siyah zeminli** form kutusu (`border-radius:16px; padding:50px 70px; height:580px`):
  - h3 "İLETİŞİM FORMUMUZU DOLDURUN"
  - `form#contact_form.ajax-form`: Ad + Soyad (yan yana, yalnız harf), Telefon (intl-tel-input, yalnız rakam) + E-Posta (yan yana), Mesajınız (textarea), KVKK onay checkbox'ı ("Kişisel verilerimin 'Aydınlatma Metninde' belirtilen amaçlarla işleneceğini okudum, anladım." — Aydınlatma Metni PDF linki), sağda `GÖNDER` (button-primary).
  - Başarı durumu: "MESAJINIZ BAŞARIYLA GÖNDERİLMİŞTİR." + 48 saat içinde dönüş notu; hata durumu: "FORMA GERİ DÖN" butonu.
  - (Mobilde aynı form accordion içinde ikinci kopya olarak var.)
- **Sağ `col-lg-6`:** iki `.contact-box` (beyaz, `border:1px solid #e2e2e2`):
  - "MÜŞTERİ HİZMETLERİ / BİZİ ARAYIN" + `ARA` butonu (tel link)
  - "WHATSAPP / WHATSAPP'TAN KONUŞALIM MI?" + `İLETİŞİME GEÇ` butonu
- Altta: h2 "**MOKA** ..." başlıklı ofisler bölümü — `.tab.tab-contact` şehir sekmeleri (footer'daki ofis adresleriyle aynı veri; harita/adres kartları).

### 7.2 Hikayemiz (/tr/hakkimizda/hikayemiz)
Body `product-detail`. Sıra:
1. H1 "HİKAYEMİZ" (gradyan) + h2 "FİNANSAL **ÇÖZÜM ANAHTARINIZ**" + davet cümlesi.
2. **Siyah şerit** (`bg-colorful-black dark blue`, tam genişlik): ortalı beyaz metin — müşteri zamanının değeri + "ZAMANDA ÖNE GEÇMENİZİ SAĞLAYAN / FİNANSAL ÇÖZÜM ANAHTARINIZ" başlıkları.
3. "ZAMAN İÇİNDE MOKA UNITED" — **iki ayrı kronoloji** (2. tur doğrulaması):
   - *United Payment hattı:* 2010 kuruluş; 2015 e-para lisansı; **2017 Wise ortaklığı, globalleşme başlangıcı**; 2019 Finberg yatırımı; 2021 **Remitly, TransferGo, PaySend, Azimo** ortaklıkları + OYAK Portföy yatırımı.
   - *Moka hattı:* 2014 kuruluş — Visa/MC/Amex/Troy onaylı ödeme kuruluşu; 2021 İş Bankası'nın satın alması; 2025 birleşme → **Moka United**.
4. Siyah şerit içinde büyük görsel.
5. Vurgu başlığı: "BU GÜÇLÜ BİRLEŞMEYLE **TÜRKİYE'NİN EN DEĞERLİ FİNTEK ŞİRKETİ** OLMA YOLCUĞUMUZ BURADA BAŞLIYOR."
6. `landing.special` kart-grid: "FİNANSAL **ÇÖZÜMLERİNİZ İÇİN** [HANGİ ANAHTARI İSTERSİNİZ?]" başlığıyla 5 ürün kartı (beyaz kartlar, mavi başlık).
7. Soru-cevap görselli bölümler: "NASIL BİR [DESTEK...]", "SİZİ NEREDE **HAYAL EDİYORUZ?**", "NASIL BİR **EKİBİMİZ VAR?**" (metin+görsel dönüşümlü, masaüstü/mobil için ayrı sıralı kopyalar).
8. **"NEREDEYİZ?"** — 6 ülke ofis haritası/görseli (Türkiye, Almanya, Azerbaycan, Özbekistan, Gürcistan, Birleşik Krallık). *(klonda YOK)*
9. **"BİZİ NE MOTİVE EDİYOR?"** — misyon metni (herkesin eşit rekabet ettiği finansal dünya). *(klonda YOK)*
10. **"SAYILARLA MOKA UNITED"** — ana sayfadaki sayaç bloğunun aynısı (6 ülke / 120M+ işlem / 250+ çalışan / 10 milyar USD). *(klonda YOK)*
11. Kapanış vurgusu: "Finansal teknolojilerin tek bir anahtara ihtiyacı var: Moka United". *(klonda YOK)*

### 7.3 Kurumsal Yönetim (/tr/hakkimizda/kurumsal-yonetim)
- H1 "KURUMSAL YÖNETİM"; yönetici kartları grid'i. Her kart: fotoğraf (`card-img`) + h3 isim + sağ ok ikonu (`arrow-right.png`) → tıklayınca **biyografi modal/expand** açılır (eğitim, kariyer geçmişi, mevcut görev).
- **Tam kadro — 19 kişi, unvanlarıyla (2. tur doğrulaması):**
  - *Yönetim Kurulu (9):* Necdet Akyel (Başkan), Yalçın Sezen (Başkan Vekili), Murat Özgen, Erhan Yeşilkaya, Sezgin Lüle, Hasan Cahit Çınar, Oğulcan Toper, Halim Memiş, İlker Sözdinler (Üyeler)
  - *Genel Müdür Yardımcıları (6):* Aslı Odabaşı (Strateji ve Büyüme), Başak Yüzbaşıoğlu (Bilgi Teknolojileri), Erender Çekim (Ürün ve İş Geliştirme), Mustafa Ömer Okay (Kamu İlişkileri), Şafak Ergönül (Operasyon ve Fraud), Erkut Gazioğulları (Finans)
  - *Direktörler (4):* Aziz Erdem (İç Denetim), Selma Sever (Kıdemli Risk Yönetimi), Bahar Örücü Atay (Kıdemli Pazarlama), Başak Sakarya Gül (İnsan Kaynakları)

### 7.4 Kariyer (/tr/hakkimizda/kariyer)
- H1 "MOKA UNITED'TA KARİYER"; "NEDEN [MOKA UNITED?]" başlıklı tanıtım bölümü + görseller; kültür anlatımı (200+ kişilik ekip, esnek çalışma modelleri, açık iletişim ve güvene dayalı kültür).
- **Açık Pozisyonlar bölümü:** LinkedIn ve Kariyer.net'e dış linkler ("Açık Pozisyonları Görmek İçin Tıklayın").
- **Başvuru formu (2. tur tespiti — klonda YOK):** Departman select'i (13 seçenek: Bilgi Teknolojileri, Hukuk, İç Kontrol & Uyum, İnsan Kaynakları, Mali ve İdari İşler, Operasyon & Fraud, Pazarlama İletişimi, Risk Yönetimi, Satış, Staj, Strateji ve Büyüme, Ürün, Genel Başvuru) + ad/soyad/iletişim alanları + **CV dosya yükleme** (PNG/JPG/PDF, max 10MB) + KVKK onayları + GÖNDER.

### 7.5 İştirakler (/tr/hakkimizda/istirakler)
- H1 "İŞTİRAKLER"; dört marka bölümü — her biri h2 başlık + açıklama + logo/görsel çifti (dönüşümlü sol/sağ yerleşim). **Detaylı içerik (2. tur doğrulaması):**
  - **RUUT** (2022, Londra; yasal ad: Is United Payment Systems Limited): İngiltere'deki KOBİ'lere ödeme kabul, ticari hesap/kart ve para transferini tek platformda sunar. İletişim: info@ruutapp.com
  - **Turan** (2022; Moka United hissesi %68 — 2025'te alındı): Türk Devletlerinde yaşayan kullanıcılar için finans uygulaması; 8 dil (TR, AZ Türkçesi, Özbekçe, Türkmence, Rusça, Gürcüce, Moğolca, EN); uluslararası para transferi.
  - **Up Enerji** (2021; hisse %75): Akaryakıt, EV şarj ve mobilite hizmetlerini dijital ekosistemde birleştiren enerji fintek'i.
  - **SmartUp** (SmartUp Teknoloji Araştırma ve Geliştirme A.Ş.): Kiosk sistemleri, akıllı kargo dolapları, RVM cihazları, EV şarj donanımı; mekanik tasarım + elektronik + gömülü sistem geliştirme.

---

## 8. ANİMASYON VE ETKİLEŞİM DAVRANIŞLARI

1. **ScrollSmoother:** tüm sayfa yumuşak kaydırma; `data-speed`/`data-lag` öznitelikleri kullanılıyor (paralaks katmanları).
2. **Sayfa yükleme:** `#overlay.overlay > .loader` — içerik hazır olunca kaybolur.
3. **Gradyan H1 animasyonu:** `anime` keyframe, 10s sonsuz, background-position kayması.
4. **Buton hover:** `:before/:after` katmanları soldan sağa dolarak renk değişimi (0.4-0.5s ease).
5. **Mega menü:** hover'da fade/slide açılış; öğelerde hover'da zemin rengi geçişi.
6. **Referans slider'ları:** 3 sıra Swiper, otomatik sürekli akış (marquee, `transition:all linear .125s`), sıralar zıt yönlü akabilir.
7. **Sayaçlar (nineth-section):** scroll'a girince 0'dan hedefe sayma animasyonu.
8. **Accordion:** başlık tıklamada `active` sınıfı, ok ikonu 180° döner (0.5s), gövde slide toggle. "DAHA FAZLA GÖSTER" gizli maddeleri açar.
9. **grow-bg blokları (fifth-section):** scroll ile büyüyen bar animasyonu (GSAP).
10. **two.js / matter.js:** ana sayfada dekoratif partikül/fizik animasyonları (hero ve renkli bölümlerde).
11. **Çerez bandı:** cookieconsent — alt köşe kart, "Çerez ayarlarını yapılandır" butonu, kabul/red butonları eşit genişlik, dil URL'den algılanır.
12. **Form:** AJAX post, inline başarı/hata durum panelleri; input validasyonları (only-letter, only-number sınıfları).
13. **instant.page:** hover'da link prefetch.

---

## 9. RESPONSIVE KURALLAR (ÖZET)

- `lg` (992px) altında: hamburger menü + tam ekran overlay menü; header butonları menü içine taşınır; mega menüler accordion benzeri dikey listeye dönüşür.
- Hero ve iki sütunlu bölümler alt alta (`col-12`), görsel metnin altına/üstüne geçer (bazı bölümlerde masaüstü/mobil için ayrı DOM kopyaları `d-none d-lg-inline-block` / `d-lg-none` ile).
- `transfer-boxes` 3'lü satırlar mobilde tek sütun; kart-grid 1 sütun.
- Sayaç kutuları mobilde 2 sütun küçük padding (`padding:70px 1vw`).
- Footer menü sütunları mobilde 2'li grid; ofis sekmeleri accordion olur; sağ altta sabit WhatsApp butonu yalnız mobilde.
- Tipografi tamamen `clamp()` ile akışkan — ayrı mobil font tanımı az.

---

## 10. KLON İÇİN DOSYA/VARLIK NOTLARI

- **Logolar:** `mokaunited-logo.svg` (koyu metinli) ve `mokaunited-logo-light.svg`. Bayraklar: `/_assets/images/header/flags/{en-US,tr-TR,az-AZ,ka-GE,uz-UZ,ru-RU}.svg`.
- **İkonlar:** `icon-global.svg`, `icon-exchange.svg`, `icon-people.svg`, `icon-money-send.svg`, footer sosyal SVG'leri, `arrow-right.png`, `bullet-blue.svg`, `band-5.png`/`band-5-sm.png`.
- **İçerik görselleri:** hepsi `/medium/...` GUID URL'leri — klonda `assets/images/` altına placeholder/indirilmiş kopya konulmalı.
- **Harici linkler:** basvuru.mokaunited.com (başvuru), pos.mokaunited.com (panel), WhatsApp `+908502522222`, sosyal medya hesapları (linkedin/instagram/x/youtube/snapchat/tiktok @mokaunited).
- **SEO:** her sayfada canonical, hreflang seti (tr/en/az/ka + x-default), OG etiketleri; title kalıbı `"{Sayfa} | Moka United"`, ana sayfa `"Moka United | Fintek Ödeme Hizmetleri"`; description fintek ödeme hizmetleri odaklı.
- **Önerilen klon yapısı:** saf HTML/CSS/JS (framework'süz) veya Next.js; ortak header/footer partial; `style.css` içinde bölüm 2'deki token'lar CSS değişkeni olarak tanımlanmalı.

---

## 11. UYGULAMA SIRASI ÖNERİSİ (1. tur — TAMAMLANDI)

> İlk tur tamamlandı: token'lar, header/footer, tüm sayfa iskeletleri kuruldu. Güncel görev listesi için **Bölüm 12**'ye geç.

1. ✅ Design token'ları + Poppins + buton/başlık bileşenleri (Bölüm 2).
2. ✅ Header (mega menü + mobil menü) ve Footer (#tenth CTA + footer) — `assets/js/components.js` ile tüm sayfalara enjekte.
3. ✅ Ana sayfa bölümleri (Bölüm 5) — akıllı kasa/kiosk blokları hariç.
4. ✅ Landing kart-grid şablonu → hakkimizda/urunler/pos-cozumleri/yasal.
5. ✅ İçerik+SSS şablonu → 3 POS alt sayfası (kısaltılmış içerikle).
6. ✅ Ürün detay sayfaları (tema zeminli) — içerik derinliği eksik.
7. ✅ İletişim, Hikayemiz, Kurumsal Yönetim, Kariyer, İştirakler (basitleştirilmiş).
8. ⚠️ Animasyonlar: reveal/sayaç/marquee/accordion var; smooth scroll, çerez bandı, arama overlay YOK.
9. ⚠️ Responsive temel düzeyde var, doğrulanmadı.

---

## 12. MEVCUT DURUM ANALİZİ VE YAPILACAKLAR (2. tur — ✅ TAMAMLANDI)

> Karşılaştırma tarihi: 2026-07-11. Klasör: `~/Downloads/Moko_United`. Klon, canlı sitenin tüm TR sayfalarıyla tek tek karşılaştırıldı.
> **3. TUR NOTU:** Bu bölümdeki 12.4 iş sırasının 7 maddesinin tamamı uygulandı ve canlı önizlemede doğrulandı
> (ürün sayfaları çok bölümlü + inline form, ana sayfa 13 SSS + akıllı kasa/kiosk blokları + doğru CTA,
> hikayemiz çift timeline, kurumsal yönetim 19 kişi + bio modal, kariyer formu, iştirak detayları,
> emoji→SVG ikonlar, favicon, 6 dil, arama overlay'i, Snapchat, footer ülke accordion'ları, çerez bandı,
> POS "Neler Yapabilirsiniz?" bölümleri, iletişim ofis kartları). Bu bölüm tarihsel referanstır;
> kalan işler için **Bölüm 13**'e geç.

### 12.1 Mimari — mevcut kurulum (değiştirme, üzerine inşa et)
- Saf HTML/CSS/JS. Sayfalar `build_pages.py` ile üretiliyor (index.html hariç). **Sayfa içeriği değişikliklerini `build_pages.py` içinde yap ve script'i çalıştır** (`python3 build_pages.py`); HTML dosyalarını elle düzenleme (index.html hariç).
- Ortak header / pre-footer CTA / footer: `assets/js/components.js` DOM'a enjekte ediyor (`#header-mount`, `#cta-mount`, `#footer-mount`, `data-active`).
- Etkileşimler: `assets/js/main.js` (loader, mobil menü, accordion+DAHA FAZLA GÖSTER, IntersectionObserver reveal, sayaç, marquee, iletişim formu, 4 adımlı başvuru sihirbazı).
- Stil: `assets/css/style.css` (~700 satır, token'lar Bölüm 2 ile uyumlu).
- Klona özgü ekstra sayfalar (orijinalde harici subdomain): `basvuru.html` (4 adımlı sihirbaz), `panel-giris.html` (demo login). **Bunlar bilinçli iyileştirme — korunacak.**
- İçerik politikası: metinler parafraze (telif nedeniyle birebir kopya değil) — bu kabul edilmiş bir karar, korunacak.

### 12.2 Sayfa karşılaştırma tablosu (klon vs canlı)

| Sayfa | Durum | Ana eksikler |
|---|---|---|
| index.html | 🟡 %75 | Akıllı kasa + kiosk tanıtım blokları (5.4b) yok; SSS 8/13 soru; CTA metni yanlış; referans/partner logoları metin |
| hakkimizda.html | 🟢 %95 | — |
| urunler.html | 🟢 %95 | — |
| pos-cozumleri.html | 🟢 %95 | — |
| sanal-pos.html | 🟡 %70 | "Neler Yapabilirsiniz?" bölümü (6.2 #4) yok; SSS 7/~10; info kutularında görsel yerine emoji |
| fiziki-pos.html | 🟡 %70 | SSS 4/~10; aynı emoji sorunu |
| linkle-tahsilat.html | 🟡 %70 | SSS 4/~10; aynı emoji sorunu |
| kart-cozumleri.html | 🔴 %30 | Orijinalde ~10 bölüm var, klonda 3 kısa split; inline form, şehir kartları, API, sadakat, güvenlik bölümleri yok (bkz. 6.3) |
| cuzdan-cozumleri.html | 🔴 %35 | "Süper güçler" kutu grid'i, 4 soruluk SSS, inline form yok (bkz. 6.3) |
| para-transferi.html | 🟡 %45 | Avantaj kutuları (%99,9/<3dk), Wise-TransferGO, 190 ülke/40+ kur, sanal hesap/nöbetçi transfer, form yok; SSS 4/13 (bkz. 6.3) |
| akilli-kasa.html | 🟡 %45 | Verimlilik/operasyonel kolaylık bölümleri, inline form (2 konum) yok (bkz. 6.3) |
| kiosk.html | 🟡 %55 | "FARK YARATIN"/"DÖNÜŞÜMÜ BAŞLATIN" bölümleri, inline form yok; sektör kutuları ✓ |
| hikayemiz.html | 🟡 %40 | Tek timeline var, orijinalde iki hat + 2017 Wise/2021 Remitly-TransferGo-PaySend-Azimo detayları; "NASIL BİR DESTEK/NEREDE HAYAL/EKİBİMİZ" soru-cevap bölümleri, NEREDEYİZ haritası, motivasyon, sayaç bloğu yok (bkz. 7.2) |
| kurumsal-yonetim.html | 🟡 %50 | 15/19 isim (Aziz Erdem, Selma Sever, Bahar Örücü Atay, Başak Sakarya Gül eksik); unvan/grup başlıkları yok; tıklayınca biyografi modal'ı yok (bkz. 7.3) |
| kariyer.html | 🔴 %30 | Açık pozisyon linkleri (LinkedIn/Kariyer.net) ve 13 departmanlı başvuru formu (CV upload) yok (bkz. 7.4) |
| istirakler.html | 🟡 %50 | Tek cümlelik açıklamalar; kuruluş yılı/hisse/dil/yasal ad detayları eklenmeli (bkz. 7.5) |
| iletisim.html | 🟡 %70 | Sayfa içi ofis sekmeleri bölümü (şehirler + YOL TARİFİ AL) yok — yalnız footer'da var; intl-tel-input yok |
| Yasal 6 sayfa | 🟢 %85 | Yeterli (örnek içerik bilinçli); yasal-belgeler grid'i 16/20 kart |
| basvuru / panel-giris | 🟢 | Klona özgü, tamam |

### 12.3 Ortak/altyapı eksikleri (tüm site)

**A. Görsel varlıklar (en görünür eksik)**
1. Emoji ikonlar SVG ile değiştirilecek: sayaç kutuları (🌍🔁👥💸 → icon-global/exchange/people/money-send tarzı çizgi SVG), arama 🔍, info-box ✳️, accordion oku ⌄, ok →, sihirbaz ✓.
2. Referans marquee'leri düz metin — her marka için beyaz hap kutuda **logo benzeri SVG/wordmark** üretilmeli (orijinal: 120px yükseklik, radius 188px).
3. Footer partner "logoları" metin span — TCMB/BKM/TÖDEB/PCI/Visa/MC/Troy/MASAK için basit SVG wordmark'lar.
4. Ürün/içerik görselleri tek tip `placeholder.svg` — sayfa temasına uyumlu, çeşitlendirilmiş illüstratif SVG'ler (kart mockup, cüzdan ekranı, transfer haritası, kasa, kiosk cihazı) üretilmeli.
5. Ürün detay sayfalarında **ribbon hero görseli + band-5 renkli bant deseni** karşılığı yok — CSS gradyan bantla temsil edilebilir.
6. Favicon + manifest yok.

**B. Header/Footer**
7. Dil dropdown'unda O'ZBEK ve РУССКИЙ eksik (4/6); bayraklar düz renk kutu — küçük SVG bayrak üretilebilir.
8. Arama: orijinaldeki **tam ekran overlay + input** (`placeholder="Ne Aramıştınız?"`) yerine `prompt()` alert kullanılıyor — overlay yapılacak (sonuç sayfası şart değil, istemci tarafı basit sayfa-adı eşleşmesi yeterli).
9. Pre-footer CTA metni: klonda "TEK ÇATI, TEK ENTEGRASYON" — orijinali **"TANIŞALIM MI?"** (gri) + "BİZ MOKA UNITED" (beyaz). Düzeltilecek.
10. CTA sosyal ikonlarında **Snapchat eksik** (orijinal: LinkedIn, Instagram, X, YouTube, Snapchat, TikTok).
11. Footer'da yalnız TR ofisleri var; orijinaldeki **ülke accordion'ları** (Türkiye/Birleşik Krallık/Azerbaycan/Almanya/Gürcistan — adresler Bölüm 4.2'de) eklenecek; TR içinde mevcut şehir sekmeleri korunacak.
12. Footer sub-menu'de "Bilgi Toplumu Hizmetleri" ✓ ama footer-logos dış linkleri yok (opsiyonel).

**C. Davranış/animasyon**
13. Çerez bandı (cookieconsent benzeri) hiç yok — alt köşe kart, "Kabul Et / Reddet / Çerez ayarları", localStorage ile hatırlama.
14. Yumuşak kaydırma: GSAP ScrollSmoother muadili yok — `scroll-behavior:smooth` var, yeterli sayılabilir; istenirse hafif paralaks (`data-speed` benzeri, rAF ile) eklenebilir. **Düşük öncelik.**
15. grow-bg barları statik — scroll'a bağlı "büyüyen bar" animasyonu (IntersectionObserver + CSS transition ile GSAP'sız yapılabilir).
16. Buton hover'ları düz renk geçişi — orijinaldeki `:before/:after` soldan dolan katman animasyonu CSS'e eklenebilir. **Düşük öncelik.**
17. two.js/matter.js/lottie dekoratif animasyonlar — **kapsam dışı bırakıldı, gerekmiyor.**

**D. SEO/meta**
18. Canonical, OG etiketleri, hreflang yok — `build_pages.py` shell'ine eklenebilir. **Düşük öncelik (yerel klon).**

### 12.4 Önerilen iş sırası (öncelikli → düşük)

1. **Ürün detay sayfalarını derinleştir** (en büyük fark): kart-cozumleri (~10 bölüm), cuzdan-cozumleri, para-transferi, akilli-kasa, kiosk — Bölüm 6.3'teki güncel yapıya göre `build_pages.py`'de. Ortak **inline talep formu** bileşeni yaz (mevcut `.contact-form` stilinden türet) ve 5 ürün sayfasına yerleştir.
2. **Ana sayfa tamamla:** akıllı kasa + kiosk split blokları (5.4b), SSS'yi 13 soruya çıkar (soru listesi Bölüm 5.7), CTA metnini "TANIŞALIM MI?" yap.
3. **Hakkımızda alt sayfalarını derinleştir:** hikayemiz (çift timeline + 4 yeni bölüm), kurumsal-yonetim (19 kişi + unvan grupları + biyografi modal), kariyer (pozisyon linkleri + departmanlı form + CV upload alanı [demo]), istirakler (detaylı metinler) — Bölüm 7'deki güncel verilerle.
4. **Görsel varlık turu:** emoji → SVG ikon seti, referans/partner wordmark'ları, temaya uygun ürün illüstrasyonları, favicon.
5. **Header/footer düzeltmeleri:** 6 dil, arama overlay'i, Snapchat ikonu, footer ülke accordion'ları.
6. **Çerez bandı** + POS sayfalarında "Neler Yapabilirsiniz?" bölümleri + SSS soru sayılarını artır.
7. **Cila:** grow-bar animasyonu, buton dolma hover'ı, iletişim sayfasına ofis sekmeleri, responsive doğrulama (375px / 768px / 1280px).

### 12.5 Kabul kriterleri (3. turda doğrulanan durum)
- [x] 5 ürün sayfasının her birinde ≥5 içerik bölümü + inline form var. *(kart: 9 bölüm; tarayıcıda doğrulandı)*
- [x] Ana sayfada 9 bölüm (hero, grow, kart&cüzdan, transfer, akıllı kasa, kiosk, referans, sayılar, SSS) + 13 soruluk SSS + doğru CTA metni ("TANIŞALIM MI? / BİZ MOKA UNITED").
- [ ] Hiçbir sayfada emoji ikon kalmadı. → **BİR KALINTI VAR:** header arama butonu hâlâ 🔍 emojisi (`components.js:59`) — bkz. 13.2/1.
- [x] Kurumsal yönetimde 19 kart, 3 grup başlığı, tıklayınca biyografi modal'ı açılıyor. *(Aziz Erdem modalı test edildi)*
- [x] Kariyerde 13 departmanlı, CV yüklemeli (10MB kontrollü) başvuru formu çalışıyor.
- [x] Çerez bandı ilk ziyarette çıkıyor, tercih localStorage'da hatırlanıyor.
- [x] Header'da 6 dil, tam ekran arama overlay'i (istemci tarafı sayfa araması, ESC/overlay-tık kapatma); CTA'da 6 sosyal ikon (Snapchat dahil).
- [x] `python3 build_pages.py` hatasız çalışıyor; 24 sayfa üretiliyor. Konsol hatası yok.

---

## 13. 3. TUR DURUM ANALİZİ VE KALAN İŞLER (Opus görev listesi)

> Karşılaştırma tarihi: 2026-07-11 (3. tur). Klon içerik/yapı olarak canlı siteyle büyük ölçüde eşleşti;
> kalan farklar ağırlıkla **görsel varlık kalitesi** ve **küçük kalıntılar**. İçerik değişiklikleri yine
> `build_pages.py` üzerinden yapılıp `python3 build_pages.py` ile üretilmeli (index.html elle).

### 13.1 Güncel sayfa durumu (klon vs canlı)

| Sayfa | Durum | Kalan fark |
|---|---|---|
| index.html | 🟢 ~%95 | Referans marquee logoları düz metin (SVG wordmark yok) |
| Ürün detay ×5 | 🟢 ~%85-90 | Görsel çeşitliliği düşük: `placeholder.svg` tekrar ediyor; orijinaldeki ribbon hero fotoğrafı yerine ürün SVG'si |
| POS ×3 | 🟢 ~%85-90 | sanal-pos SSS 10 ✓; fiziki-pos 7, linkle-tahsilat 6 soru (orijinal ~10) |
| hikayemiz | 🟢 ~%90 | Siyah şerit içindeki büyük görsel bloğu (spec 7.2 madde 4) yok |
| kurumsal-yonetim | 🟢 ~%95 | Fotoğraf yerine baş-harf avatar (bilinçli; istenirse stilize portre SVG üretilebilir) |
| kariyer / istirakler | 🟢 ~%90-95 | — |
| iletisim | 🟢 ~%90 | intl-tel-input muadili ülke kodu seçici yok (basit only-number input) |
| yasal-belgeler | 🟡 ~%80 | 20 belge kartının tamamı `javascript:;` ölü link — mevcut sayfalar bile bağlanmamış |
| basvuru / panel-giris | 🟢 | Klona özgü, tamam ("Şifremi unuttum" `javascript:;` — demo, bilinçli) |

### 13.2 Kalan işler (öncelik sırasıyla)

**A. Kalıntı temizliği (küçük, hızlı)**
1. **Header arama butonu 🔍 emojisi** → SVG büyüteç ikonu (`assets/js/components.js` satır ~59, `#searchToggle`). Sitedeki SON emoji ikon.
2. **Mobilde aramaya erişim yok:** `searchToggle` `desktop-only`; orijinaldeki gibi mobil menünün en üstüne "Ne aramıştınız?" arama tetikleyicisi ekle (`.mobile-menu` içine, `searchOverlay`'i açan link).
3. **İletişim formundaki "Aydınlatma Metni" linki `javascript:;`** → `kvkk-aydinlatma-metni.html` (build_pages.py `contact_form` bloğu; inline formlarda zaten doğru).
4. **Yasal belgeler kartlarını bağla:** sayfası olan 3 kart gerçek linke (`KVKK Aydınlatma Metni → kvkk-aydinlatma-metni.html`, `Bilgi Toplumu Hizmetleri → bilgi-toplumu-hizmetleri.html`, `Şirket Bilgileri → bilgi-toplumu-hizmetleri.html`); kalan 17 kart için tek jenerik `legal_page` şablonundan kısa örnek sayfalar üret veya kart tıklandığında "örnek belge" modalı göster (hangisi kolaysa).

**B. Görsel varlık kalitesi (en görünür kalan fark)**
5. **Referans marquee logo wordmark'ları:** 17 marka (Samsung, Decathlon, Sahibinden, Enerjisa, Yemeksepeti, BTA, Mars, ABB, Hektaş, Poca, Tatilbudur, UP Enerji, DOA, TBBB, Turan, Vavacars, Yandex) için basit tipografik SVG wordmark üret (her biri kendine özgü font-weight/renk tonuyla `<text>` SVG'si yeterli); `ref-item` içine `<img>` olarak koy.
6. **Footer partner logoları:** TCMB, BKM, TÖDEB, PCI DSS, Visa, Mastercard, Troy, MASAK için aynı yaklaşımla mini SVG wordmark (Visa/MC/Troy için renkli basit şekil + yazı).
7. **Ürün sayfası illüstrasyon çeşitliliği:** `placeholder.svg` tek tip; sayfa temalarına uygun 4-5 varyant üret (ör. `illus-security.svg` kalkan/kilit, `illus-api.svg` kod blokları, `illus-city.svg` şehir silueti+kart, `illus-team.svg` insanlar, `illus-growth.svg` grafik) ve `build_pages.py`'deki `split(...)/feature_split(...)` çağrılarına konuya uygun `img=` parametresi geçir.
8. (Opsiyonel) Yönetim kartlarına stilize vektör portre placeholder'ı (tek `avatar.svg`, hue-rotate ile çeşitlendirme) — baş harf avatarlar da kabul edilebilir.

**C. Animasyon/etkileşim cilası**
9. **grow-bg büyüme animasyonu:** `.grow-bg .block` barları statik; IntersectionObserver ile görünüme girince `height` transition'lı büyüme (CSS `.grow-section.in .b1{height:40%}` kalıbı, JS'de mevcut `reveal` gözlemcisine benzer).
10. **Çerez bandına "Çerez Ayarları" üçüncü aksiyonu:** tıklanınca zorunlu/analitik/pazarlama üç toggle'lı mini panel; tercihi `mu-cookie-consent`'e JSON yaz (orijinal cookieconsent kalıbı).
11. fiziki-pos ve linkle-tahsilat SSS'lerini ~10 soruya tamamla (komisyon, entegrasyon, iade, mutabakat, yurt dışı kart kabulü gibi konularla).

**D. Düşük öncelik (istenirse)**
12. SEO meta: `build_pages.py` shell'ine `canonical` + OG etiketleri (`og:title/description/type`) — tek satırlık ekleme; index.html'e elle.
13. İletişim/başvuru telefon alanına basit ülke kodu seçici (select + input; intl-tel-input muadili).
14. Hikayemiz siyah şeridine büyük görsel bloğu; tablet (768px) responsive geçişi gözle doğrula.
15. `index.html`'i de build script kapsamına alma (tek kaynak) — mimari tercih, zorunlu değil.

### 13.3 Kabul kriterleri (4. tur — ✅ TAMAMLANDI ve tarayıcıda doğrulandı)
- [x] Sitede hiçbir emoji ikon yok (🔍 → SVG büyüteç); mobil menüden arama açılıyor (menü kapanıp overlay geliyor).
- [x] Referans marquee'lerinde 17 marka + footer'da 8 partner SVG wordmark/logo (Visa/Mastercard/Troy şekilli).
- [x] Ürün sayfalarında ≥4 farklı illüstrasyon (kart: 6 farklı görsel — security/api/city/growth + prod-kart + placeholder).
- [x] Yasal belgeler: 6 kart gerçek sayfaya linkli, 14 kart "örnek belge" modalı açıyor, 0 ölü link.
- [x] grow-bg barları scroll'da büyüyor (`.grow-section.in`); çerez bandında 3 toggle'lı ayarlar paneli JSON tercih kaydediyor.
- [x] fiziki-pos ve linkle-tahsilat SSS 10'ar soru.
- [x] `python3 build_pages.py` hatasız (24 sayfa); konsol hatası yok; 375/768/1280px'te yatay taşma/bozulma yok.

**Bilinçli ertelenenler (13.2/D — "istenirse"):** #13 telefon ülke kodu seçici (intl-tel-input muadili) ve #15 (index.html'i build kapsamına alma) yapılmadı; görsel sadakati etkilemiyor, risk/karmaşıklık getiriyor. #12 SEO (OG etiketleri) ve #14 (hikayemiz görsel bloğu) uygulandı.

> **DURUM: 4. tur sonrası klon, canlı siteyle içerik/yapı/görsel olarak yüksek düzeyde eşleşiyor. Bilinen görsel eksik kalmadı.**
