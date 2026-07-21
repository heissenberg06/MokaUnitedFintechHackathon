# next4biz "İş Süreçleri Yönetimi (BPM)" Klon Analizi ve Uygulama Planı

> Bu doküman **yalnızca analiz ve uygulama planıdır.** Kod bu dosyada yazılmaz; kodlama Sonnet ile yapılacaktır. Fable tarafından, `https://www.next4biz.com/tr/is-surecleri-yonetimi` (BPM) ve `.../musteri-hizmetleri-yonetimi` (CSM/ticket) sayfaları canlı olarak (tarayıcı + hesaplanmış CSS + içerik) incelenerek hazırlanmıştır.
> İnceleme tarihi: 2026-07-20.

---

## 0. Amaç ve Bağlam

Kendi yapay zeka hattımız (sikayetvar admin analiz motoru) müşteri şikayet/verisini işledikten sonra, sonuçları bir **ticket (talep) yönetim ekranına** düşürecek. Bu ekranın görsel dili ve iç yapı kurgusu next4biz'in BPM/CSM ürününden birebir klonlanacak. **Şu an AI ↔ ticket bağlantısı (entegrasyon) yapılmayacak** — önce arayüz ve veri yapısı ayağa kalkacak, entegrasyon sonraki faz.

İki katman klonlanıyor:
1. **Pazarlama/landing yüzü** — BPM tanıtım sayfasının bölüm bölüm tasarımı (renk, tipografi, kart düzeni).
2. **Uygulama yüzü** — ticket/talep yönetiminin veri modeli, yaşam döngüsü, SLA, atama, liste/detay kurgusu (bizim panelimizin asıl kalbi).

---

## 1. Marka & Tasarım Sistemi (birebir tokenlar)

Aşağıdaki değerler siteden **hesaplanmış (computed) CSS** ile birebir çekildi. Sonnet bunları doğrudan Tailwind config / CSS değişkeni olarak kullanmalı.

### 1.1 Renk paleti

| Rol | HEX | RGB | Kullanım |
|-----|-----|-----|----------|
| **Ana marka (camgöbeği)** | `#00A0C7` | rgb(0,160,199) | Birincil vurgu, "Demo Planla", ikon rengi, başlık altı çizgi |
| Marka varyant | `#00A6CE` | rgb(0,166,206) | İkincil buton metni, ince vurgular |
| **Turuncu CTA (koyu)** | `#ED561A` | rgb(237,86,26) | "Toplantı Planla" nav butonu |
| Turuncu CTA (açık) | `#F58220` | rgb(245,130,32) | "Yerimi Ayırt", "ANLADIM" (cookie) |
| **Teal (ikincil pill)** | `#2C9F95` | rgb(44,159,149) | "Müşteri Yorumları" nav butonu |
| Metin – koyu (slate-900) | `#0F172A` | rgb(15,23,42) | Gövde metni, H2 başlıklar |
| Başlık grisi | `#525454` | rgb(82,84,84) | H1/H3 başlık metni |
| Slate-700 | `#334155` | rgb(51,65,85) | Alt başlık/paragraf |
| Slate-600 | `#475569` | rgb(71,85,105) | İkincil metin |
| Slate-500 | `#64748B` | rgb(100,116,139) | Yardımcı/soluk metin |
| Beyaz | `#FFFFFF` | — | Sayfa & kart zemini |

**Tint (şeffaf) tonlar — birebir:**
- İkon kutusu zemini: `rgba(0,160,199,0.10)`
- Çok açık vurgu zemini: `rgba(0,160,199,0.05)`
- Kart kenarlığı: `rgba(146,148,151,0.20)`
- Turuncu tint: `rgba(245,130,32,0.10)`

> Not: Marka mavisi H1'de metnin **altına çizgi (underline aksanı)** olarak da kullanılıyor (hero'daki "Süreç Tasarım ve İşletim Sistemi" altındaki camgöbeği çizgiler).

### 1.2 Tipografi

- **Ana font:** `Poppins` (fallback: `Inter, system-ui, -apple-system, "Segoe UI", Roboto, ... , Arial, sans-serif`). Fontlar `fonts.css` üzerinden yerel servis ediliyor.
- **Ölçek (computed):**

| Öğe | Boyut | Ağırlık | Satır Y. | Renk |
|-----|-------|---------|----------|------|
| H1 (hero) | 60px | 700 | 60px | `#525454` |
| H2 (bölüm başlığı) | 36px | 700 | — | `#0F172A` |
| H3 (AI alt bölüm) | 30px | 700 | — | `#525454` |
| H3 (kart başlığı, geniş) | 24px | 700 | — | `#525454` |
| H3 (özellik başlığı) | 18–20px | 700 | — | `#525454` |
| H3 (footer sütun) | ~26px | 700 | — | `#525454` |
| Gövde | 16px (≈18px hero alt) | 400 | 1.6–1.7 | `#0F172A`/slate |

- Sadece **2 ağırlık** ana kullanımda: 400 (gövde), 700 (başlık). Butonlarda 500/600/700 karışık.

### 1.3 Bileşen tokenları (computed)

**Kart (feature card):**
- `border-radius: 24px`
- `border: 1px solid rgba(146,148,151,0.20)`
- `box-shadow: none` (gölge yok — düz/flat)
- `padding: 24px`
- `background: #FFFFFF`
- tipik genişlik ~365px (3'lü grid)

**İkon kutusu:**
- `48px × 48px`, `border-radius: 12px`
- `background: rgba(0,160,199,0.10)`
- içinde camgöbeği (stroke) ikon (katman, şimşek vb. — outline ikonlar)

**Butonlar (birebir):**

| Buton | Zemin | Metin | Radius | Padding | Font |
|-------|-------|-------|--------|---------|------|
| Demo Planla (birincil) | `#00A0C7` | beyaz | 8px | 16px 32px | 16px / 600 |
| Toplantı Planla (nav) | `#ED561A` | beyaz | 16px | 10px 20px | 14px / 500 |
| Müşteri Yorumları (nav) | `#2C9F95` | beyaz | 16px | 10px 20px | 14px / 500 |
| İkincil (outline) | beyaz | `#00A6CE` | 10px | 14px 24px | 15px / 600 |
| Yerimi Ayırt | `#F58220` | beyaz | 12px | 13px 26px | 16px / 700 |
| ANLADIM (cookie) | `#F58220` | beyaz | 6px | 8px 24px | 12px / 600 |

**Genel:** Flat tasarım (gölge yok), yuvarlatılmış köşeler (8–24px), bol beyaz alan, Tailwind utility tabanlı. Zemin daima beyaz/açık; koyu bölüm yok.

---

## 2. Landing Sayfası Yapısı (BPM) — bölüm bölüm

Yukarıdan aşağı akış (klonlanacak sıralama). Başlıklar sitedeki birebir Türkçe metinlerdir; **paragraf içerikleri kendi özgün metnimizle yeniden yazılmalı** (marka metnini birebir kopyalama).

1. **Header / Navigasyon** (sticky, beyaz, alt ince kenarlık)
   - Sol: `next4biz` logo (ortadaki "X" renkli/degrade harf).
   - Orta menü: `Lowcode · Prototip · Hepsi Bir Arada · Yapay Zeka · Entegrasyon`
   - Sağ: `Müşteri Yorumları` (teal pill) + `Toplantı Planla` (turuncu pill).
   - Mobilde hamburger (☰) menüye çöküyor.

2. **Hero** — sol metin / sağ görsel
   - H1: "Next4biz BPM: Süreç Tasarım ve İşletim Sistemi" (60px, altında camgöbeği underline aksanları).
   - Alt metin (18px): süreç tasarla → prototip → yayınla → ölç → geliştir.
   - CTA: "Demo Planla" (camgöbeği).
   - Sağda: laptop mockup + ürün ekran görüntüsü (form tasarımcısı / "NEW DATA FIELD" paneli). Bizde temsilî bir panel görseli konur.

3. **"Sadece Bir İş Akışı Aracı Değil"** (H2 36px)
   - Üstte açıklama paragrafı, altında **4 özellik kartı** (ikon kutusu + H3 18–20px + kısa açıklama):
     `Modellemenin ötesinde · Uçtan uca dijitalleştirme · Daha az IT bağımlılığı · Sürdürülebilir iyileştirme`

4. **"Low-Code Tasarım"** (H2)
   - 2 geniş alt blok (H3 24px):
     `İş Akışları, Formlar, Veri Yapıları ve Arayüzler` / `İş Kuralları, SLA'lar ve Otomasyon`
   - Görsel + madde listesi düzeni (metin bir yanda, ürün görseli diğer yanda — alternan).

5. **"Prototipleme: İş ve Teknoloji Arasındaki Boşluğu Kapatın"** (H2)
   - 4 özellik (H3 18px): `Görsel Geri Bildirim · Otomasyona Dönüşür · Riski Azaltır · Ortak Dil`
   - Yanında BPM prototip diyagramı (SVG).

6. **"Tek Bir Platformda Tasarımlayın, Test Edin ve Yayınlayın"** (H2)
   - 3 özellik: `Güncelleyin ve İyileştirin · Yayınlamadan Önce Test Edin · Kolayca Devreye Alım`

7. **"Ölçün, Analiz Edin ve Sürekli İyileştirin"** (H2)
   - `Raporlar ve Kontrol Panelleri` (H3 24px) — sürükle-bırak rapor, KPI, rol bazlı panolar, BI export.

8. **"AI Destekli Süreç Zekası"** (H2) — "Yakında" rozetli
   - `Anomaly.net ile Gelişmiş Analitik` (H3 30px) — grafik sinir ağları, transformer vb.
   - `Doğal Dilden BPMN'ye: Text2BPM` (H3 30px) — doğal dil → BPMN 2.0. Yanında animasyon (GIF).
   - > Bu bölüm bizde "yol haritası/yakında" olarak konur; bizim AI motorumuzla (şikayet analizi) burada ilişkilendirilebilir.

9. **"Erişimi Kontrol Edin, Paydaşları Sürece Dahil Edin"** (H2)
   - `Roller, Yetkiler ve Atama Kuralları` (H3 24px) / `Saha Operasyonları için Mobil BPM` (H3 24px).

10. **"BPM'inizi Genişletin ve Entegre Edin"** (H2)
    - `Akıllı Kodlama Katmanı` / `Kurumsal Sistemlerle Entegrasyonlar`.

11. **"Deneyim ve Yeniden Kullanılabilir Bileşenlerden Yararlanın"** (H2)
    - 6 özellik: `Kanıtlanmış Metodoloji · Yeniden Kullanılabilir Bileşenler · Özelleştirilmiş Şablonlar · Dışa Aktar ve Yeniden Kullan · Deneyimli Ekipler · Kendi Yapı Taşlarınızı Yeniden Kullanın`.

12. **Footer** — 3 sütun (`Keşfedin · Yapay Zeka · Sorularınız Var Mı?`, H3 ~26px) + yasal satır:
    `Gizlilik Politikası · KVKK Aydınlatma Metni · Kullanım Koşulları · Çerez Politikası · İçerik Bildirimi · Kalite Politikası` + dil seçici `EN | TR` + telif satırı.

13. **Cookie banner** (alt sabit şerit): açıklama + `AYARLAR` (outline) + `ANLADIM` (turuncu). Bizim sikayetvar KVKK deseniyle uyumlu.

---

## 3. Ticket / Talep Yönetim Yapısı (uygulama çekirdeği)

next4biz CSM tarafında ticket ("talep"/"bildirim") kurgusu şu bileşenlerden oluşuyor. Bu bizim panelimizin **asıl veri modeli** olacak.

### 3.1 Ticket yaşam döngüsü (state machine)
Gözlemlenen akış: **Giriş → Kategorize → Atama/Kuyruk → İşlem (görevler/onaylar) → SLA takibi → Çözüm → Kapanış** (+ denetim izi/audit trail).

Önerilen durumlar (bizim panel için):
- `yeni` (AI veya kullanıcı girişi)
- `siniflandirildi` (kategori atandı)
- `atandi` (ekip/kişi)
- `islemde`
- `beklemede` (müşteri/3. taraf bekliyor)
- `cozuldu`
- `kapandi`
- `yeniden-acildi`

### 3.2 Ticket veri modeli (önerilen alanlar)
Bizim sikayetvar veri modeliyle hizalı, next4biz alan mantığıyla genişletilmiş:

```
Ticket {
  id                : string/int
  createdAt         : ISO datetime
  source            : "ai" | "self-service" | "email" | "chat" | "whatsapp"   // omnichannel
  title             : string
  body              : string
  category          : string        // AI kategori tahmini (bizim analysis.py çıktısı)
  priority          : "dusuk"|"orta"|"yuksek"|"kritik"   // aciliyet skorundan türetilir
  status            : (yukarıdaki state)
  assignee_team     : string        // bizim TEAM_ROUTING eşlemesi (Güvenlik/Finans/Ürün...)
  assignee_user     : string|null
  sla_due_at        : ISO datetime  // adım başına + toplam
  sla_state         : "ok"|"risk"|"breach"
  sentiment         : "ofkeli"|"olumsuz"|"notr"|"olumlu"  // duygu analizi
  merchant          : string|null   // işyeri (fraud/risk bağlamı)
  tasks[]           : { title, done:bool, dueAt }         // görev/checklist
  approvals[]       : { role, state:"bekliyor|onaylandi|reddedildi" }
  timeline[]        : { at, actor, type, note }           // omnichannel birleşik zaman çizelgesi
  attachments[]     : { name, url }
  audit[]           : { at, actor, action }               // denetim izi
}
```

> **AI köprüsü (sonraki faz):** `source:"ai"` olan ticket'lar bizim `analysis.py` çıktısından beslenecek — `category`, `priority`, `assignee_team`, `sentiment`, `merchant` alanları doğrudan mevcut motorun ürettiği değerlerden gelir. Şu an bağlanmayacak; alanlar boş/manuel doldurulabilir bırakılır.

### 3.3 Uygulama ekranları (klonlanacak)
next4biz'de detaylı ekran görüntüsü public değildi; standart CSM/BPM konvansiyonuna göre kurgu:

1. **Ticket listesi** — kolonlar: ID, Başlık, Kategori, Öncelik (renk rozet), Durum (rozet), Atanan ekip, SLA (kalan süre / risk rengi), Oluşturma. Üstte filtre çubuğu (durum, kategori, ekip, SLA riski, kaynak), arama, sayfalama.
2. **Ticket detay** — sol: başlık/gövde + birleşik zaman çizelgesi (timeline); sağ panel: durum değiştir, atama, öncelik, SLA sayacı, etiketler, görev/checklist, onaylar. Üstte durum akış göstergesi (stepper).
3. **Kontrol paneli (dashboard)** — aşama/sahiplik/birikim/SLA riski anlık göstergeler (bizim admin.html kartlarıyla aynı dili konuşur: KPI + SVG grafikler).
4. **İş akışı/SLA görünümü** — adım başına zamanlayıcı, uyarı, hiyerarşik yükseltme (escalation).

### 3.4 SLA mantığı
- **Adım başına** ve **toplam akış** için ayrı sayaçlar.
- Eşik aşımında otomatik yükseltme (escalation) + tam bağlam.
- Panelde `ok/risk/breach` renk kodu (yeşil/amber/kırmızı) — bizim mevcut `URG_COLOR` paletine map edilebilir.

---

## 4. Bileşen Kütüphanesi (klon için atomlar)

| Bileşen | Spesifikasyon |
|---------|---------------|
| Nav pill (birincil) | turuncu `#ED561A`, radius 16px, 10px 20px, 14px/500, beyaz metin |
| Nav pill (ikincil) | teal `#2C9F95`, aynı ölçü |
| Buton (birincil) | camgöbeği `#00A0C7`, radius 8px, 16px 32px, 16px/600 |
| Buton (outline) | beyaz zemin, `#00A6CE` metin+kenar, radius 10px |
| Feature card | radius 24px, 1px `rgba(146,148,151,.2)` kenar, 24px padding, gölgesiz |
| Icon box | 48px, radius 12px, `rgba(0,160,199,.1)` zemin, outline ikon |
| Section başlık | H2 36px/700 `#0F172A`, ortalı veya sola dayalı |
| Rozet (durum/öncelik) | pill, kategori/SLA rengine göre tint zemin + koyu metin |
| Cookie banner | alt sabit şerit, AYARLAR (outline) + ANLADIM (turuncu) |

İkonlar outline stil (next4biz tarzı: katman, şimşek, kalkan, grafik). Bizde Tabler/Lucide outline veya inline SVG ile karşılanabilir.

---

## 5. Teknik Yaklaşım ve Dosya Yapısı (öneri)

Mevcut `sikayetvar` mimarisiyle **tutarlı** gitmek en verimlisi (stdlib Python server + statik HTML/CSS/JS, bağımlılıksız). Önerilen iskelet:

```
next4biz-klon/
├── ANALIZ.md                (bu dosya)
├── index.html               (BPM landing klonu — Bölüm 2)
├── tickets.html             (ticket listesi — Bölüm 3.3/1)
├── ticket.html              (ticket detay — Bölüm 3.3/2)
├── dashboard.html           (kontrol paneli — Bölüm 3.3/3)
├── assets/
│   ├── css/n4b.css          (tasarım tokenları — Bölüm 1)
│   ├── js/landing.js
│   ├── js/tickets.js        (liste/filtre/sayfalama)
│   └── js/ticket-detail.js  (durum/atama/SLA/timeline)
├── server.py                (stdlib HTTP + /api/tickets CRUD, sikayetvar deseniyle)
└── data/tickets.json        (seed + kalıcı depolama, atomik yazma + kilit)
```

- **CSS değişkenleri** olarak Bölüm 1 tokenları `:root`'a taşınır.
- Server, sikayetvar'daki `clean()` (XSS), isim maskeleme, `threading.Lock`, `os.replace` atomik yazma desenlerini tekrar kullanır.
- `/api/tickets` (GET liste+filtre, GET detay, POST oluştur, PATCH durum/atama) — **AI POST'u için `source:"ai"` alanı hazır bırakılır ama şimdilik bağlanmaz.**

---

## 6. Fazlı Uygulama Planı (Sonnet için)

**Faz 1 — Tasarım sistemi + landing**
1. `n4b.css`: Bölüm 1'deki tüm renk/tipografi/bileşen tokenlarını CSS değişkeni + utility sınıfı olarak kur.
2. `index.html`: Bölüm 2'deki 13 bölümü sırayla, kendi özgün Türkçe metinlerimizle klonla (başlık hiyerarşisi ve kart düzeni birebir).
3. Header (sticky + mobil hamburger), footer, cookie banner.

**Faz 2 — Ticket veri katmanı**
4. `server.py` + `data/tickets.json`: Bölüm 3.2 veri modeli, seed veri (10–20 örnek ticket), `/api/tickets` uçları.
5. Durum makinesi (Bölüm 3.1) ve SLA hesap mantığı (Bölüm 3.4).

**Faz 3 — Ticket ekranları**
6. `tickets.html` + `tickets.js`: liste, filtre, arama, sayfalama, durum/SLA rozetleri.
7. `ticket.html` + `ticket-detail.js`: detay, timeline, durum/atama değiştir, görev/onay, SLA sayacı.
8. `dashboard.html`: KPI + SVG grafikler (mevcut admin.html dilini yeniden kullan).

**Faz 4 — (sonraki) AI entegrasyonu**
9. `analysis.py` çıktısını `source:"ai"` ticket'a map eden köprü. **Bu fazda başlanmayacak** (kullanıcı talebi).

---

## 7. Klonlarken Dikkat (uyum/etik)

- **Marka metni birebir kopyalanmaz:** başlık *yapıları* ve tasarım tokenları klonlanır; paragraf/pazarlama metinleri özgün yazılır. `next4biz` logosu/markası kullanılmaz — kendi ürün adımız konur (sikayetvar/Moka ekosistemiyle uyumlu).
- **KVKK deseni** mevcut sikayetvar'daki gibi korunur (isim maskeleme, XSS temizleme, çerez onayı).
- Demo/eğitim amaçlı olduğu footer'da belirtilir.

---

## 8. Hızlı Referans — Tasarım Tokenları (kopyala-kullan)

```css
:root{
  --n4b-cyan:#00A0C7; --n4b-cyan-2:#00A6CE;
  --n4b-orange:#ED561A; --n4b-orange-2:#F58220;
  --n4b-teal:#2C9F95;
  --n4b-ink:#0F172A; --n4b-head:#525454;
  --n4b-slate-700:#334155; --n4b-slate-600:#475569; --n4b-slate-500:#64748B;
  --n4b-cyan-10:rgba(0,160,199,.10); --n4b-cyan-05:rgba(0,160,199,.05);
  --n4b-card-border:rgba(146,148,151,.20);
  --n4b-radius-card:24px; --n4b-radius-btn:8px; --n4b-radius-pill:16px;
  --n4b-font:"Poppins","Inter",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
}
```

| H1 | H2 | H3 | Gövde |
|----|----|----|-------|
| 60/700 `#525454` | 36/700 `#0F172A` | 18–30/700 `#525454` | 16/400 `#0F172A` |
