# Jira Klon — Analiz ve Uygulama Planı (Moka Akış)

> **Amaç:** Moka United'ın yapay zekâ katmanı (Şikayetvar paneli), müşteri şikayetini analiz ettikten
> sonra bunu bir **iş kaydı / talep (issue)** olarak bir **Jira benzeri iş yönetim sistemine** düşürecek.
> Bu doküman, Jira'nın issue (talep) yönetimi yüzeylerini — renk paleti, tipografi, boşluk sistemi,
> bileşenler ve ekran yapıları — **birebir** klonlamak için gereken her şeyi içerir.
>
> **Bu doküman yalnızca ANALİZ + UYGULAMA PLANIDIR. Kod yazılmamıştır.** Kodlamayı Sonnet yapacak.
>
> **Kaynak doğrulaması:** Renk / boşluk / radius / tipografi değerleri, Atlassian'ın canlı tasarım-token
> paketinden (`@atlaskit/tokens@16.1.0`, ham token dosyaları) çekilmiştir — tahmin değil, gerçek değerler.
>
> **Not (branding):** Ürün adımız **Moka Akış**. Atlassian'ın "Atlassian Sans" / "Charlie" markalı
> fontları ve "Jira" logosu/telifli metinleri BİREBİR kullanılmayacak; yapı ve görsel dil klonlanacak,
> font olarak metrik olarak en yakın açık kaynak olan **Inter** self-host edilecek (bkz. §2.2).

---

## 0. Yönetici Özeti

Jira'nın issue yönetimi 4 ana yüzeyden oluşur ve bizim için hepsi kritik:

1. **Global navigasyon** — üst bar (arama, Oluştur, bildirim, profil) + sol proje kenar çubuğu.
2. **Board (Kano/Kanban) görünümü** — sütunlar = durumlar; kartlar = talepler.
3. **Backlog / Liste görünümü** — gruplu, satır-içi düzenlenebilir talep listesi.
4. **Issue (Talep) detay görünümü** — Jira'nın kalbi: solda içerik (özet, açıklama, ekler, alt görevler,
   aktivite/yorumlar), sağda "Ayrıntılar" paneli (durum, atanan, öncelik, etiketler vb.).

Jira'yı **Jira yapan** görsel imza şunlardır ve klonda birebir olmalıdır:

- **Lozenge (durum rozeti):** Küçük, yuvarlak köşeli, BÜYÜK HARF, renk-kodlu durum etiketi. (#1 görsel işaret)
- **Issue type ikonları:** Story (yeşil), Task (mavi), Bug (kırmızı), Epic (mor), Alt görev.
- **Priority (öncelik) ikonları:** Highest/High kırmızı ↑, Medium turuncu =, Low/Lowest mavi ↓.
- **Renkli baş-harf avatarları.**
- **Issue key:** `MOKA-123` biçiminde proje-anahtarı + sayı.
- **Satır-içi düzenleme:** Alanların üzerine tıklayınca yerinde düzenlenmesi.

**Mevcut varlıklardan yeniden kullanım:** `next4biz-klon/server.py` içindeki talep veri modeli
(durum makinesi, kategori→ekip yönlendirme, SLA, sentiment, ekler, denetim günlüğü) **büyük ölçüde
yeniden kullanılabilir** — değişen şey **ön yüz (tasarım dili + terminoloji + ekran yapısı)** ve birkaç
alan eklemesi (issue type, priority ikonu, story points, epic/parent, sprint gibi Jira-özgü alanlar).
Yani bu bir "sıfırdan backend" değil, **backend'i koru + ön yüzü Jira'ya göre yeniden derle** işidir.

---

## 1. Kapsam — Neyi Klonluyoruz?

| Yüzey | Klonlanacak mı? | Öncelik | Notlar |
|---|---|---|---|
| Global üst bar + sol nav | ✅ Evet | Yüksek | Jira'nın 2024+ yeni navigasyonu |
| Board (Kanban) görünümü | ✅ Evet | Yüksek | Demo'nun görsel vurucu ekranı |
| Backlog / Liste görünümü | ✅ Evet | Orta | Talep akışının ana çalışma alanı |
| Issue (Talep) detay görünümü | ✅ Evet | **En yüksek** | Jira'nın kalbi; AI verisinin düştüğü yer |
| Create (Oluştur) modalı | ✅ Evet | Yüksek | AI'nın issue enjekte edeceği nokta |
| Dashboard / Reports | ⚠️ Sadeleştirilmiş | Orta | Mevcut dashboard'u Jira diline uydur |
| Timeline / Gantt | ❌ Hayır | — | Kapsam dışı (demo için gereksiz) |
| Sprint yönetimi (tam) | ⚠️ Görsel-only | Düşük | Sprint alanı gösterilir, tam agile akışı yok |

**AI entegrasyon noktası:** Create modalı / `POST /api/issues`. **Bu bağlantı ŞU AN YAPILMAYACAK**
(önceki talimat gereği); doküman yalnızca "AI verisi buraya şu şemayla düşecek" diye işaretler.

---

## 2. Tasarım Sistemi — Kesin Token'lar

> Bunlar Atlassian'ın canlı tasarım token paketinden alınan **gerçek** değerlerdir. Doğrudan CSS
> custom-property olarak kullanılabilir. `--j-` öneki "Jira/klon" içindir.

### 2.1 Renk Token'ları (Açık tema — güncel Atlassian paleti, 2026)

**Marka / birincil (mavi):**
```
--j-brand-bold            #1868DB   /* birincil buton, seçili, link, marka */
--j-brand-bold-hover      #1558BC
--j-brand-bold-pressed    #144794
--j-selected-bg           #E9F2FE   /* seçili satır/sekme arka planı (açık mavi) */
--j-selected-bg-hover     #CFE1FD
--j-link                  #1868DB
--j-link-pressed          #1558BC
--j-border-selected       #1868DB
--j-border-focused        #4688EC   /* focus ring */
```

**Metin:**
```
--j-text                  #292A2E   /* ana metin (neredeyse siyah, saf siyah DEĞİL) */
--j-text-subtle           #505258   /* ikincil metin, alan etiketleri */
--j-text-subtlest         #6B6E76   /* meta, zaman damgası, placeholder */
--j-text-inverse          #FFFFFF
--j-text-brand            #1868DB
--j-text-disabled         #080F214A  /* alpha */
```

**Yüzey / arka plan (elevation):**
```
--j-surface               #FFFFFF   /* ana yüzey (kart, panel, modal) */
--j-surface-hover         #F0F1F2
--j-surface-pressed       #DDDEE1
--j-surface-sunken        #F8F8F8   /* board arka planı, "gömük" alanlar */
--j-surface-raised        #FFFFFF   /* kartlar (gölge ile ayrılır) */
--j-neutral-subtle        #0515240F  /* alpha — hover dolgu, çip arka planı */
```

**Kenarlık:**
```
--j-border                #0B120E24  /* alpha — standart ince çizgi */
--j-border-input          #8C8F97    /* form input kenarı */
--j-border-bold           #7D818A
--j-border-disabled       #0515240F
```

**Durum renkleri (status/feedback) — lozenge ve mesajlar için:**
```
/* success / done (yeşil) */
--j-success-bg            #EFFFD6   --j-success-bg-bold  #5B7F24   --j-success-text  #4C6B1F
/* danger / bug / breach (kırmızı) */
--j-danger-bg             #FFECEB   --j-danger-bg-bold   #C9372C   --j-danger-text   #AE2E24
/* warning (turuncu/sarı) */
--j-warning-bg            #FFF5DB   --j-warning-bg-bold  #FBC828   --j-warning-text  #9E4C00
/* information / in-progress (mavi) */
--j-info-bg               #E9F2FE   --j-info-bg-bold     #1868DB   --j-info-text     #1558BC
/* discovery / new / epic (mor) */
--j-discovery-bg          #F8EEFE   --j-discovery-bg-bold #964AC0  --j-discovery-text #803FA5
```

**İkon aksan renkleri (issue type / priority ikonları için):**
```
--j-icon-green    #22A06B   /* Story */
--j-icon-blue     #357DE8   /* Task */
--j-icon-red      #C9372C   /* Bug, Highest/High priority */
--j-icon-purple   #AF59E1   /* Epic */
--j-icon-orange   #E06C00   /* Medium priority */
--j-icon-teal     #2898BD
--j-icon-yellow   #B38600
--j-icon-subtle   #505258   /* nötr ikonlar */
```

> **Dikkat:** Klasik Jira mavisi eskiden `#0052CC` idi; Atlassian 2023-2024'te paleti güncelledi ve
> yeni marka mavisi **#1868DB**. Klonu "güncel Jira" göstermek için yeni paleti kullan.

### 2.2 Tipografi

Atlassian artık **"Atlassian Sans"** (özel, telifli) kullanıyor. Biz bunu **shipleyemeyiz**; metrik
olarak en yakın açık kaynak **Inter**'i self-host edeceğiz (tıpkı next4biz-klonda Poppins'i self-host
ettiğimiz gibi). Kod (monospace) için **JetBrains Mono** veya sistem mono.

**Font ailesi (CSS):**
```css
--j-font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
--j-font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
```

**Ağırlıklar:** Atlassian gövde 400, orta 500, yarı-kalın 600, başlık "bold" = 653 (≈650).
→ Inter'de **400 / 500 / 600 / 700** yükle; başlıklarda **600** kullan (653'e en yakın pratik değer).

**Tip ölçeği (birebir Atlassian):**
| Rol | Boyut / satır-yük. | Ağırlık | Kullanım |
|---|---|---|---|
| Heading XXL | 32/36 | 600 | Sayfa başlığı (nadiren) |
| Heading XL | 28/32 | 600 | Büyük başlık |
| Heading L | 24/28 | 600 | Bölüm başlığı |
| Heading M | 20/24 | 600 | Issue özeti (detay sayfası başlığı) |
| Heading S | 16/20 | 600 | Alt başlık, panel başlığı |
| Heading XS | 14/20 | 600 | Küçük başlık |
| Heading XXS | 12/16 | 600 | ETİKET (genelde harf-aralığı + BÜYÜK HARF) |
| **Body (default)** | **14/20** | **400** | **Varsayılan gövde metni** |
| Body large | 16/24 | 400 | Rahat gövde |
| Body small | 12/16 | 400 | Meta, yardımcı metin |

> **Kritik:** Jira'nın varsayılan gövde metni **14px**'tir (16 değil). Bu, arayüzün "yoğun/profesyonel"
> hissini verir. Klonda 14px varsayılanı koru.

### 2.3 Boşluk Sistemi (8px grid)

Atlassian **8px temelli** boşluk ölçeği kullanır (yarım adımlar 4px):
```
--j-space-025  2px    --j-space-050  4px    --j-space-075  6px
--j-space-100  8px    --j-space-150  12px   --j-space-200  16px
--j-space-250  20px   --j-space-300  24px   --j-space-400  32px
--j-space-500  40px   --j-space-600  48px   --j-space-800  64px
```
> Tüm padding/margin/gap değerleri bu ölçekten seçilmeli. Örn. kart içi padding = 12px (space-150),
> panel padding = 16px (space-200), alanlar arası dikey boşluk = 8px (space-100).

### 2.4 Köşe Yarıçapı (radius)

```
--j-radius-xs     2px    /* lozenge, küçük çipler */
--j-radius-sm     4px    /* buton, input, kart */
--j-radius-md     6px    /* panel, modal */
--j-radius-lg     8px
--j-radius-xl     12px
--j-radius-full   9999px /* avatar, yuvarlak çipler */
```
> Jira görünümü **az yuvarlatılmış** (3-6px) köşelerle gelir; aşırı yuvarlatma "Jira değil" hissi verir.

### 2.5 Gölge / Elevation

```
--j-shadow-raised:  0 1px 1px #1E1F211f, 0 0 1px #1E1F2129;   /* kartlar */
--j-shadow-overlay: 0 4px 8px #1E1F211f, 0 0 1px #1E1F2129;   /* modal, dropdown, popover */
```
> Jira kartları neredeyse düz; ince, düşük-opaklık gölge ile yüzeyden ayrılır. Ağır gölge kullanma.

### 2.6 Layout Ölçüleri (Jira kabuğu)

```
Üst bar (global nav) yüksekliği     56px
Sol proje kenar çubuğu genişliği    ~240px (daraltılabilir → 20px ikon-only)
Issue detay ana kolon max-genişlik  ~680–740px
Issue detay sağ panel genişliği     ~360px
Board sütun genişliği               ~270px
İçerik yatay padding                24px–40px
```

---

## 3. Bileşen Envanteri (klonlanacak atomik parçalar)

Her biri tek bir CSS bileşeni olarak kurulmalı. Sonnet bunları `jira.css` içinde token'larla üretir.

### 3.1 Lozenge (Durum Rozeti) — **EN KRİTİK BİLEŞEN**
- Küçük etiket: `padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.5px; line-height: 16px;`
- İki stil: **subtle** (açık zemin + koyu metin) ve **bold** (dolu zemin + beyaz/koyu metin).
- Renk aileleri (durum kategorisine göre):
  | Kategori | subtle bg / text | Kullanım |
  |---|---|---|
  | Default (gri) | `#0515240F` / `#505258` | "Yapılacak / To Do" |
  | In-progress (mavi) | `#E9F2FE` / `#1558BC` | "Devam ediyor" |
  | Success (yeşil) | `#EFFFD6` / `#4C6B1F` | "Bitti / Çözüldü" |
  | Moved (sarı) | `#FFF5DB` / `#9E4C00` | "Beklemede" |
  | Removed (kırmızı) | `#FFECEB` / `#AE2E24` | "İptal / SLA aşımı" |
  | New (mor) | `#F8EEFE` / `#803FA5` | "Yeni / Triyaj" |

### 3.2 Issue Type İkonu (16×16 kare, yuvarlatılmış zemin + beyaz simge)
| Tür | Zemin rengi | Simge | Türkçe karşılık (Moka) |
|---|---|---|---|
| Story | `#22A06B` yeşil | yer imi | "Talep" (genel) |
| Task | `#357DE8` mavi | onay ✓ | "Görev" |
| Bug | `#C9372C` kırmızı | daire | "Arıza/Şikayet" |
| Epic | `#AF59E1` mor | şimşek | "Konu/Epik" |
| Sub-task | `#357DE8` mavi | alt-dal | "Alt görev" |

### 3.3 Priority (Öncelik) İkonu (renkli ok, zemin yok)
| Öncelik | Renk | Simge |
|---|---|---|
| Highest | `#C9372C` | çift ↑ |
| High | `#C9372C` | ↑ |
| Medium | `#E06C00` | = (yatay çift çizgi) |
| Low | `#357DE8` | ↓ |
| Lowest | `#357DE8` | çift ↓ |

### 3.4 Avatar
- Yuvarlak (`border-radius: 50%`), 24px (satır) / 32px (detay) / 20px (kompakt).
- Fotoğraf yoksa **renkli baş harf** — arka plan, isimden deterministik hash → paletten bir renk.
- Atanmamış: kesikli gri daire + kişi ikonu.

### 3.5 Buton
| Varyant | Zemin | Metin | Kullanım |
|---|---|---|---|
| Primary | `#1868DB` (hover `#1558BC`) | beyaz | "Oluştur", ana eylem |
| Default/Subtle | şeffaf → hover `#0515240F` | `#505258` | ikincil eylemler |
| Danger | `#C9372C` | beyaz | silme/reddetme |
- Ölçü: `padding: 6px 12px; border-radius: 3px; font-size: 14px; font-weight: 500; height: 32px.`

### 3.6 Tag / Label çipi
- `background: #0515240F; color: #292A2E; border-radius: 3px; padding: 2px 6px; font-size: 12px.`

### 3.7 Field (satır-içi düzenlenebilir alan) — Jira imza etkileşimi
- Görünüm modunda düz metin; hover'da hafif zemin (`#0515240F`) + kalem imleci.
- Tıklayınca input/textarea/select'e döner; ESC iptal, blur/Enter kaydet.
- Sağ paneldeki her alan bu desende (Durum, Atanan, Öncelik, Etiketler, ...).

### 3.8 Issue Card (board kartı)
- Beyaz yüzey, `--j-shadow-raised`, `border-radius: 3px`, padding 8–12px.
- İçerik dikey sıra: **özet metni** → alt satırda: issue-type ikonu + **KEY** + (etiket çipleri) +
  öncelik ikonu + (story points) + sağa yaslı **avatar**.

### 3.9 Diğer
- **Breadcrumb:** `Proje / Epik > KEY-123` (küçük, subtle metin, `/` ayraç).
- **Dropdown / Popover:** beyaz, `--j-shadow-overlay`, `radius 6px`.
- **Tab çubuğu:** alt-çizgi göstergeli (aktif sekme mavi alt-çizgi + koyu metin).
- **Section message / banner:** durum-renkli açık zemin + ikon (bilgi/uyarı/hata).

---

## 4. Ekran-Ekran Yapı Analizi

### 4.1 Global Navigasyon (her sayfada)
**Üst bar (56px):**
- Sol: (uygulama-switcher ▦ ikonu) + **Moka Akış** logosu.
- Orta: geniş **arama** kutusu ("Talep ara...").
- Sağ: **Oluştur** (mavi primary buton) · bildirim 🔔 · yardım ? · profil avatarı.

**Sol proje kenar çubuğu (~240px, daraltılabilir):**
- Proje başlığı + anahtar (örn. "Müşteri Talepleri — MOKA").
- Menü öğeleri (ikon + etiket): **Board** · **Backlog** · **Liste** · **Panolar/Reports** · **Talepler**.
- Aktif öğe: `#E9F2FE` zemin + mavi sol-şerit + koyu metin.

### 4.2 Board (Kanban) Görünümü
- Üstte: görünüm başlığı, arama, atanan-avatar filtreleri, "Group by" vs.
- Gövde: yatay **sütunlar** = durumlar (**Yapılacak · Devam Ediyor · İncelemede · Bitti**).
- Her sütun başlığında ad + kart sayısı (çip).
- Sütun içinde **Issue Card**'lar (§3.8) dikey dizili; sürükle-bırakla durum değişir (demo'da
  en azından tıkla→durum menüsü ile taşıma yeterli, gerçek DnD opsiyonel).
- Arka plan `--j-surface-sunken` (#F8F8F8), sütunlar hafif ayrık.

### 4.3 Backlog / Liste Görünümü
- Filtre çubuğu (arama, durum, atanan, öncelik, etiket).
- Kolonlu tablo/liste: **Tür ikonu · KEY · Özet · Öncelik · Durum(lozenge) · Atanan(avatar) ·
  SLA · Oluşturma**. Satıra tıkla → issue detay.
- Satır hover'da hafif zemin; seçili satır `#E9F2FE`.
- (Mevcut `tickets.html` bu görünümün temeli — Jira diline + lozenge/avatar/type-ikon ile yeniden derlenecek.)

### 4.4 Issue (Talep) Detay Görünümü — **Jira'nın kalbi**
**Üst şerit:** Breadcrumb (`MOKA / Epik adı > MOKA-123`) · sağda eylemler (Ekle, Uygula, ⋯, paylaş).

**Ana kolon (sol, ~700px):**
1. **Özet (summary)** — büyük başlık (Heading M, 20px), satır-içi düzenlenebilir.
2. Hızlı eylem butonları: **Ekle** (dosya/alt görev/link), (durum butonu bazı düzenlerde burada).
3. **Açıklama (description)** — zengin metin bloğu; satır-içi düzenlenebilir.
4. **Ekler (attachments)** — küçük önizleme kartları (mevcut minimal ek listesi buraya uyar).
5. **Alt görevler / Child issues** — mini liste (tür ikonu + KEY + özet + durum lozenge).
6. **Bağlı talepler (linked issues)** — "engelliyor / ilişkili" grupları (opsiyonel).
7. **Aktivite** — sekmeler: **Yorumlar · Geçmiş · Çalışma günlüğü**. Yorum kutusu + zaman-sıralı akış.
   (Mevcut `timeline`/audit verisi "Geçmiş" sekmesine birebir oturur.)

**Sağ panel — "Ayrıntılar" (~360px, açılır-kapanır):**
Her satır = etiket (subtle, 12px) + değer (satır-içi düzenlenebilir field, §3.7):
- **Durum** (lozenge + dropdown → izinli geçişler; mevcut `ALLOWED_TRANSITIONS` birebir kullanılır)
- **Atanan (Assignee)** (avatar + ad; mevcut `assignee_user`)
- **Bildiren (Reporter)** (müşteri; AI kaynaklı talepte müşteri adı)
- **Öncelik (Priority)** (öncelik ikonu + ad)
- **Etiketler (Labels)**
- **Ekip / Bileşen (Component)** (mevcut kategori→ekip yönlendirmesi)
- **Sprint** (opsiyonel, görsel)
- **Story point estimate** (opsiyonel, sayı)
- **Son tarih (Due date)** / **SLA** (mevcut SLA hesabı → burada "SLA riski" göstergesi)
- **Oluşturma / Güncelleme** zaman damgaları (subtlest metin, en altta)

### 4.5 Create (Oluştur) Modalı — **AI enjeksiyon noktası**
- Ortada modal (`--j-shadow-overlay`, radius 6px), başlık "Talep oluştur".
- Alanlar: **Proje** (sabit MOKA) · **Issue type** (Şikayet/Görev/Arıza...) · **Özet** · **Açıklama** ·
  **Öncelik** · **Atanan** · **Etiketler** · **Bileşen/Ekip**.
- Alt: "İptal" (subtle) + "Oluştur" (primary).
- **AI köprüsü (ŞİMDİ YAPILMAYACAK):** AI çıktısı bu modalın alanlarına ya da doğrudan
  `POST /api/issues`'a şu şemayla düşecek — bkz. §5. Şimdilik sadece boş/manuel modal kurulur.

### 4.6 Dashboard / Reports (sadeleştirilmiş)
- Mevcut dashboard'u Jira diline uyarla: durum dağılımı (kategori renkleriyle), öncelik dağılımı,
  ekip yükü, SLA riski, sentiment dağılımı. Kart düzeni + Jira token'ları.

---

## 5. Veri Modeli Eşlemesi (Jira issue ↔ mevcut ticket modeli)

Mevcut `server.py` talep şeması Jira'ya **%80 hazır**. Eşleme ve eklenecek alanlar:

| Jira alanı | Mevcut alan | Durum |
|---|---|---|
| `key` (MOKA-123) | `id` | ➕ Görsel biçim: `MOKA-{n}` üret |
| `issuetype` | (yok) | ➕ **Eklenecek** (story/task/bug/epic) |
| `summary` | `title` | ✅ Var |
| `description` | `body` | ✅ Var |
| `status` | `status` | ✅ Var (+ `ALLOWED_TRANSITIONS` zaten var) |
| `statusCategory` | (durumdan türet) | ➕ gri/mavi/yeşil eşlemesi ekle (lozenge rengi için) |
| `priority` | `priority` | ✅ Var (+ ikon eşlemesi ekle) |
| `assignee` | `assignee_user` | ✅ Var |
| `reporter` | müşteri adı/`requester` | ✅ Var |
| `labels` | (yok/etiket) | ➕ Eklenecek (dizi) |
| `components` | `team`/`category` | ✅ Var (ekip=bileşen) |
| `attachments` | `attachments` | ✅ Var (minimal liste) |
| `comments` | timeline/yorum | ⚠️ Yorum akışı ayrıştırılabilir |
| `history` | `audit`/`timeline` | ✅ Var → "Geçmiş" sekmesi |
| `created`/`updated` | var | ✅ Var |
| `resolutiondate` | `resolved_at` | ✅ Var |
| `duedate` / SLA | SLA hesabı | ✅ Var (Jira "SLA/Due" olarak göster) |
| `storyPoints` | (yok) | ➕ Opsiyonel, görsel |
| `sprint` | (yok) | ➕ Opsiyonel, görsel |
| `parent`/`epic` | (yok) | ➕ Opsiyonel (alt görev/epik ilişkisi) |

**AI'nın üreteceği issue şeması (köprü İLERİDE bağlanacak — şimdi değil):**
```jsonc
POST /api/issues
{
  "issuetype": "bug",            // AI: şikayet türü sınıflandırması
  "summary": "...",              // AI: kısa başlık
  "description": "...",          // AI: müşteri metni + özet
  "priority": "high",            // AI: aciliyet skorundan
  "labels": ["fraud-ring", "..."], // AI: tespit ettiği etiketler
  "component": "Güvenlik & Fraud", // AI: kategori→ekip yönlendirmesi
  "reporter": "Müşteri adı",
  "source": "ai",                // izlenebilirlik
  "ai_meta": { "sentiment": "...", "confidence": 0.0 }
}
```
> **Tekrar:** Bu köprü şimdi kurulmayacak. Sadece backend `POST /api/issues` bu şemayı kabul edecek
> şekilde tasarlanacak ki ileride AI tarafı bağlanınca hazır olsun.

---

## 6. Terminoloji Sözlüğü (Jira → Moka Akış / Türkçe)

Telifli birebir kopya yerine kendi dilimiz; ama Jira zihinsel modelini koru:

| Jira (EN) | Moka Akış (TR) |
|---|---|
| Issue / Work item | Talep |
| Issue key | Talep no (MOKA-123) |
| Board | Pano |
| Backlog | Birikim / Bekleyenler |
| Sprint | Dönem (opsiyonel) |
| Epic | Konu |
| Story | Talep |
| Task | Görev |
| Bug | Arıza / Şikayet |
| Sub-task | Alt görev |
| Assignee | Atanan |
| Reporter | Bildiren |
| Priority | Öncelik |
| Labels | Etiketler |
| Component | Ekip / Birim |
| Status | Durum |
| To Do / In Progress / Done | Yapılacak / Devam Ediyor / Bitti |
| Story points | Puan (opsiyonel) |
| Comments / Activity | Yorumlar / Aktivite |
| Create | Oluştur |

---

## 7. Uygulama Planı (Fazlı, dosya-dosya) — Sonnet için

> Klasör: yeni `jira-klon/` (mevcut `next4biz-klon/` yerine geçecek yeni ön yüz; backend mantığı
> oradan taşınıp Jira alanlarıyla genişletilecek). Zero-dependency stdlib server + statik HTML/CSS/JS,
> mevcut projeyle aynı mimari.

### Faz 0 — İskelet & Tasarım Token'ları
- `jira-klon/assets/css/tokens.css` — §2'deki tüm token'lar (`:root` custom properties).
- `jira-klon/assets/css/fonts.css` + `assets/fonts/` — **Inter** woff2 (400/500/600/700, latin+latin-ext)
  self-host (next4biz'deki Poppins yöntemiyle birebir).
- `jira-klon/assets/css/jira.css` — bileşenler (§3): lozenge, issue-type ikon, priority ikon, avatar,
  buton, tag, field, card, breadcrumb, dropdown, tab, banner.
- Favicon (Moka Akış mavi SVG).

### Faz 1 — Uygulama Kabuğu (global nav)
- Ortak header + sol nav parça(lar)ı (her sayfada). 56px üst bar + 240px sol nav + daraltma.
- `app.js` — nav aktiflik, arama kutusu iskeleti, Oluştur butonu → Create modalı açar.

### Faz 2 — Backend Genişletme (`server.py`)
- Mevcut modeli koru; **ekle:** `issuetype`, `labels`, `statusCategory` türetimi, `MOKA-{n}` key,
  (opsiyonel) `story_points`, `sprint`, `parent`.
- `POST /api/issues` — §5 şemasını kabul et (AI köprüsü İÇİN hazır, ama bağlama yok).
- `/api/meta` — issue type listesi, priority listesi + ikon eşlemesi, statusCategory eşlemesi döndür.
- Seed verisini Jira alanlarıyla zenginleştir (tür, etiket, key).

### Faz 3 — Liste / Backlog Görünümü
- `list.html` + `list.js` — filtre çubuğu + Jira satır düzeni (tür ikon · KEY · özet · öncelik ·
  durum lozenge · atanan · SLA · tarih). Mevcut `tickets.js` mantığı yeniden derlenir.

### Faz 4 — Board (Kanban) Görünümü
- `board.html` + `board.js` — durum sütunları + issue card render. En azından kart→durum menüsü ile
  taşıma; (opsiyonel) HTML5 drag-drop.

### Faz 5 — Issue Detay Görünümü (**en yüksek özen**)
- `issue.html` + `issue.js` — §4.4 tam düzen: ana kolon (özet/açıklama/ekler/alt görev/aktivite
  sekmeleri) + sağ "Ayrıntılar" paneli (satır-içi field'lar, durum dropdown = izinli geçişler,
  atanan, öncelik, etiketler, bileşen, SLA, zaman damgaları).
- Yorumlar + Geçmiş sekmeleri (mevcut timeline/audit).

### Faz 6 — Create Modalı
- Global "Oluştur" → modal (§4.5). Manuel oluşturma çalışır; `POST /api/issues`'a gider.
- **AI köprüsü bağlanmaz** — sadece şema hazır.

### Faz 7 — Dashboard/Reports (Jira dili)
- Mevcut dashboard'u Jira token'ları + terminolojisiyle yeniden derle.

### Faz 8 — Uçtan Uca Test & Sadakat Geçişi
- §8 kontrol listesi ile görsel sadakat + fonksiyon testi (curl + tarayıcı).

---

## 8. Klon Sadakati Kontrol Listesi

Görsel:
- [ ] Gövde metni 14px, ana metin `#292A2E` (saf siyah değil).
- [ ] Birincil mavi `#1868DB`; linkler ve seçili durum mavi.
- [ ] Lozenge'ler: 11px, BÜYÜK HARF, harf-aralıklı, doğru kategori renkleri.
- [ ] Issue-type ikonları doğru renk/simge; her satır ve kartta görünür.
- [ ] Priority ikonları doğru renk/yön.
- [ ] Avatarlar yuvarlak, renkli baş-harf fallback.
- [ ] KEY biçimi `MOKA-123`, monospace/subtle.
- [ ] Köşeler 3–6px (aşırı yuvarlatma yok), gölgeler ince.
- [ ] Board arka planı `#F8F8F8`, kartlar beyaz + ince gölge.
- [ ] Sağ "Ayrıntılar" paneli field düzeni Jira sırasında.
- [ ] Boşluklar 8px grid'e oturuyor.

Fonksiyon:
- [ ] Durum dropdown yalnız izinli geçişleri gösteriyor (mevcut `ALLOWED_TRANSITIONS`).
- [ ] Satır-içi field düzenleme (hover→tıkla→kaydet/ESC) çalışıyor.
- [ ] Create modalı `POST /api/issues` ile talep oluşturuyor.
- [ ] Board ↔ Liste ↔ Detay gezintisi tutarlı.
- [ ] SLA/Due göstergesi doğru; resolved_at damgası set/temizle.
- [ ] Geçmiş sekmesi audit/timeline'ı gösteriyor.

---

## 9. Yasal / Branding Notları

- **Font:** "Atlassian Sans"/"Charlie" **kullanılmayacak**; Inter self-host (metrik yakın, açık lisans).
- **Logo/marka:** "Jira" adı/logosu kullanılmayacak; ürün **Moka Akış**. Atlassian'ın telifli
  arayüz metinleri (yardım metinleri, slogan vb.) **birebir kopyalanmayacak** — kendi TR metinlerimiz.
- **Klonlanan:** yapı, düzen, etkileşim desenleri ve **kamuya açık tasarım token'ları** (renk/boşluk/
  radius/tip ölçeği = işlevsel/olgusal değerler). Bunlar bir yarışma demosu için görsel dil klonlamaktır.
- **Renk değerleri** Atlassian'ın açık `@atlaskit/tokens` paketinden alınmıştır (kamuya açık).

---

## 10. Mevcut next4biz-klon ile İlişki

- **Yeniden kullanılacak:** backend talep modeli, durum makinesi (`ALLOWED_TRANSITIONS`), SLA hesabı,
  kategori→ekip yönlendirme, sentiment, ekler, audit/timeline, denetim/rate-limit sertleştirmeleri.
- **Değişecek:** tüm ön yüz tasarım dili (next4biz cyan → Jira mavi/nötr paleti), terminoloji (§6),
  ekran yapıları (Jira board/backlog/issue-view), yeni alanlar (issuetype, labels, key, story points).
- **Karar:** `next4biz-klon`'u silme; `jira-klon`'u yeni ana ürün ön yüzü olarak kur. Backend kodunun
  büyük kısmı kopyalanıp Jira alanlarıyla genişletilir (sıfırdan değil).

---

## 11. Kod Sonrası Uygulama Denetimi (Opus, canlı test ile)

> Bu bölüm, Sonnet'in Faz 0-8'i kodlamasının **ardından** yapılan tarafsız denetimdir. Canlı sunucu
> (`http://127.0.0.1:8780`) tarayıcıda 1440px ve mobilde test edildi; API'ler curl + tarayıcı ile
> doğrulandı; kod dosyaları satır bazında incelendi. **Bu bölüm yalnızca bulgu listesidir — kod
> yazılmamıştır.** Düzeltmeler Sonnet tarafından yapılacak.

### 11.0 Genel Değerlendirme
Klon **plana büyük ölçüde uygun ve fonksiyonel**. 8 ekranın tamamı çalışıyor; durum makinesi, SLA,
satır-içi düzenleme, create modal, dashboard, mobil menü ve güvenlik sertleştirmeleri yerinde.
Aşağıda **1 kritik, 1 orta, birkaç düşük** öncelikli bulgu + tasarım-sadakat notları + plandan
bilinçli/opsiyonel eksikler listelenir.

### 11.1 Fonksiyon / Kod Bulguları

> **Durum (Sonnet, kod turu 2):** F1-F4 aşağıda düzeltildi ve canlı test edildi (bkz. §11.6).

**✅ DÜZELTİLDİ — F1 — Çift HTML-escape: özel karakterli metinler bozuk görünüyor (KRİTİK, görünür)**
- **Belirti:** Açıklama/özet/işyeri gibi alanlarda `'` `"` `&` `<` `>` içeren metinler entity olarak
  düz görünüyor. Örn. MOKA-1 açıklamasında *"Hızlı Ödeme Bayii**&#x27;**nde"* yazıyor (olması gereken:
  "Bayii'nde"). Canlı doğrulandı: API ham değer `...Bayii&#x27;nde`, ekranda da aynen.
- **Kök neden:** Sunucu `clean()` = `html.escape()` ile veriyi **saklarken** escape ediyor
  (`server.py:118`, kullanım `:293-294`, `:688-689`, `:873`), istemci ise render'da `MokaUI.esc()`
  ile (`components.js:4`, textContent→innerHTML) **ikinci kez** escape ediyor. `&#x27;` içindeki `&`
  tekrar `&amp;`'e dönüşüp entity düz metin oluyor.
- **Ek risk (birikme):** Bir alanı satır-içi düzenlerken input'a escaped değer (`&#x27;`) geliyor;
  değişmeden kaydedilse bile sunucu tekrar escape edip **üçlü+ birikme** yapıyor (`issue.js`
  openInlineText currentVal = ham-escaped değer).
- **Çözüm yönü (kod Sonnet'te):** Tek escape noktası seç. **Tercih:** sunucuyu "ham sakla" yap
  (`_create_issue`/seed/`_add_note`/`_add_attachment`'ta `clean()` yerine yalnız `.strip()` /
  uzunluk kontrolü; XSS savunması zaten istemci `MokaUI.esc()` ile sağlanıyor). Alternatif: sunucu
  escape'i korunur, istemci `esc()` yapmadan `innerHTML`e ham koyar (daha kırılgan; F1 tekrarını
  önlemek için tavsiye edilmez). **Not:** Mevcut veri dosyasında da escaped değerler var → düzeltme
  sonrası `data/issues.json` silinip seed yeniden üretilmeli.

**✅ DÜZELTİLDİ — F2 — Satır-içi alanlar klavyeyle açılmıyor (a11y)**
- **Belirti:** Ayrıntılar panelindeki düzenlenebilir alanlar `role="button" tabindex="0"` ile
  odaklanabiliyor ama **Enter/Space** ile açılmıyor; yalnız fare `click`'i çalışıyor. Canlı test:
  `fldPriority.focus()` + Enter → düzenleme açılmadı.
- **Kök neden:** `issue.js:240-283` alan açma dinleyicileri yalnız `'click'`. Klavye kullanıcısı
  odaklanabilir ama etkinleştiremez.
- **Çözüm yönü:** Her `fld*` için eş bir `keydown` (Enter/Space → aynı açma fonksiyonu) ekle veya
  ortak bir delegasyon yaz.

**✅ DÜZELTİLDİ — F3 — "Kaynak" ham kod olarak görünüyor**
- **Belirti:** Issue detayında **Kaynak: `ai`** (ham kod) yazıyor; Create modalı "Kaynak" dropdown'u
  da `ai`, `self-service`, `whatsapp` ham değerleri gösteriyor. (Timeline'da doğru: "Yapay Zeka".)
- **Kök neden:** `issue.js:76` `ui.esc(t.source)` ham; sunucuda `SOURCE_LABEL` sözlüğü yok
  (`server.py:92` yalnız `SOURCES`).
- **Çözüm yönü:** `SOURCE_LABEL = {ai:"Yapay Zeka", "self-service":"Self-Servis", email:"E-posta",
  chat:"Canlı Destek", whatsapp:"WhatsApp"}` ekle, `/api/meta`'da döndür, detay + modalda kullan.

**✅ DÜZELTİLDİ — F4 — Kayıt sonrası kullanıcı geri bildirimi yok (küçük UX)**
- SLA doğru yeniden hesaplanıyor ama önceden başarı göstergesi yoktu; hata durumunda blocking
  `alert()` kullanılıyordu. Artık paylaşılan bir toast bileşeni (`MokaUI.toast`, bkz. §11.6) her
  başarılı kayıtta "Kaydedildi", hatada ise engellemeyen kırmızı bir toast gösteriyor; board'da
  durum taşımasında ve create modalında da kullanılıyor.

### 11.2 Tasarım Sadakat Notları

**🟡 T1 — Üst navigasyon rengi.** Mevcut üst bar koyu lacivert (`--j-brand-boldest #1C2B42`). Güncel
Jira (2024+) **açık/beyaz** bir üst nav kullanıyor; koyu bar **klasik Jira** görünümüdür. Karar
gerektirir: "klasik Jira" olarak kalabilir (tutarlı ve şık) ya da en güncel görünüm için beyaz+alt
kenarlıklı üst bara çevrilebilir.

**✅ KISMEN UYGULANDI — T2 — Sağ "Ayrıntılar" paneli konteyneri.** Gerçek Jira'da sağ panel "Details"
başlıklı, kenarlıklı, katlanabilir bir kutudur. Panele **"AYRINTILAR" başlığı** eklendi (bkz. §11.6);
katlama (collapse) eklenmedi — düşük öncelik, istenirse ayrıca yapılabilir.

**🟡 T3 — Board başlığı minimal.** Gerçek Jira board üstünde arama, atanan-avatar filtreleri,
"Group by" ve swimlane bulunur. Mevcut board yalnız başlık + sütunlar. Demo için yeterli; istenirse
board üstüne hızlı filtre çubuğu eklenebilir.

**🟢 T4 — İyi olanlar.** Lozenge (11px, BÜYÜK HARF, doğru kategori renkleri), issue-type ikonları
(mavi görev / kırmızı arıza), priority ikonları, renkli baş-harf avatarları, `MOKA-{n}` mono key,
kart gölgeleri, 8px boşluk, Inter tipografisi ve marka mavisi `#1868DB` — Jira'ya sadık.

### 11.3 Plandan Bilinçli/Opsiyonel Eksikler (kapsam kararı)
Bunlar hata değil; §4/§7'de opsiyonel işaretlenmiş ya da kapsam dışı bırakılmış parçalar:
- **P1** Alt görevler statik checklist (§4.4-5'teki "child issues" = kendi KEY/durum/tür ile gerçek
  alt-talep değil). İstenirse gerçek alt-talep modeline yükseltilebilir.
- **P2** Bağlı talepler (linked issues, §4.4-6) — yok (opsiyoneldi).
- **P3** Epic/parent alanı + breadcrumb'da epik adı (§4.4) — yok; breadcrumb yalnız `MOKA / KEY`.
- **P4** Sprint alanı (§4.4, opsiyonel görsel) — yok.
- **P5** Gerçek sürükle-bırak board — yok; kart **⋯ → durum menüsü** ile taşıma var (plan DnD'yi
  opsiyonel demişti, izinli-geçiş doğrulaması bu menüde de uygulanıyor ✔).
- **P6** Topbar hızlı-arama dropdown'u yok; Enter ile Liste'ye `?q=` yönlendiriyor (kabul edilebilir).

### 11.4 Doğrulanan Güçlü Yönler (canlı test)
- Durum makinesi hem UI (yalnız izinli geçişler) hem API (geçersiz geçiş → 400) düzeyinde çalışıyor.
- `resolved_at` set/temizle: cozuldu/kapandi'da damga, geri açılınca temizleniyor (test edildi).
- Create modal uçtan uca talep oluşturuyor; kategoriye göre ekip + tür otomatik öneriliyor.
- Dashboard: 7 KPI + 5 dağılım grafiği + ekip yükü tablosu doğru; bar renkleri kategori-semantik.
- Mobil: burger menü + responsive board çalışıyor.
- Güvenlik: `127.0.0.1` bağlama, `X-Content-Type-Options`/`Referrer-Policy`, rate-limit korunmuş.

### 11.5 Önerilen Düzeltme Sırası (Sonnet için)
1. **F1** (kritik, görünür bozukluk) — escape stratejisini teke indir + `data/issues.json` yenile.
2. **F2** (a11y) — satır-içi alanlara klavye açma.
3. **F3** — `SOURCE_LABEL` ile kaynak etiketleri.
4. **T1/T2/T3** — kapsam/tasarım kararına göre (üst bar rengi, Details başlığı, board filtreleri).
5. **P1-P6** — yalnız kapsam genişletilmek istenirse.

### 11.6 Düzeltme Turu — Uygulanan Değişiklikler ve Doğrulama (Sonnet, kod turu 2)

**Yapılan değişiklikler:**
- **F1:** `server.py` — `clean()` artık yalnız `.strip()` yapıyor, `html.escape()` kaldırıldı (ve
  kullanılmayan `import html` silindi). Tek escape noktası artık istemci (`MokaUI.esc`, render
  anında). `data/issues.json` silinip seed temiz (escape'siz) veriyle yeniden üretildi.
- **F2:** `issue.js` — ortak `onActivate(el, handler)` yardımcısı eklendi; tüm `fld*` alanları hem
  `click` hem `keydown` (Enter/Space, `preventDefault` ile) ile açılıyor.
- **F3:** `server.py` — `SOURCE_LABEL` sözlüğü eklendi, `/api/meta` ve `_decorate()` (`source_label`
  alanı) üzerinden dışa veriliyor. `issue.js` Kaynak alanı ve `create-modal.js` Kaynak dropdown'u
  artık `source_label` kullanıyor (ham kod yerine "Yapay Zeka" vb.).
- **F4:** `jira.css`'e `.j-toast`/`.j-toast-stack` eklendi; `components.js`'e paylaşılan
  `MokaUI.toast(message, isError)` yardımcı fonksiyonu eklendi. `issue.js` `patch()` başarıda
  "Kaydedildi" toast'ı, hatada (eski blocking `alert()` yerine) kırmızı toast gösteriyor.
  `board.js` durum taşımasında da aynı mekanizma kullanılıyor. `create-modal.js` başarılı
  oluşturmada `"MOKA-N oluşturuldu"` toast'ı veriyor.
- **T2:** `issue.js` sağ panele **"AYRINTILAR"** başlığı eklendi (katlama hariç).

**Canlı doğrulama (tarayıcı + curl):**
- MOKA-1 açıklaması artık `Hızlı Ödeme Bayii'nde ...` (düz kesme işareti, entity yok) — hem API hem
  ekranda doğrulandı.
- `fldPriority.focus()` + `Enter` → satır-içi `<select>` açıldığı doğrulandı (klavye ile).
- Issue detayda **Kaynak: "Yapay Zeka"** (ham `ai` değil); create modal Kaynak dropdown'unda da
  okunur etiketler.
- `MokaUI.toast()` çağrıldığında elemanın DOM'a eklenip (`opacity:0` başlangıç), bir süre sonra
  DOM'dan kaldırıldığı doğrulandı (göster→sön→kaldır döngüsü tam çalışıyor).
- Ekip alanı satır-içi değiştirildi (Güvenlik & Fraud → Finans & Ödemeler), SLA yeniden hesaplandı.
- 4 sayfa da (board/list/issue/dashboard) 200 dönüyor, konsolda hata yok, sunucu `127.0.0.1:8780`'de
  temiz seed veriyle çalışıyor.

**Değiştirilmeyenler (bilinçli, kapsam dışı bırakıldı):** T1 (üst bar rengi — "klasik Jira" olarak
korundu), T3 (board üstü filtre/arama çubuğu), T2'nin katlama kısmı, P1-P6 (opsiyonel derinleştirmeler).

---

*Hazırlayan: Opus · §0-10 plan + §11 kod-sonrası denetim · Kodlama Sonnet tarafından yapılacak.*
