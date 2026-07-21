# Moka Akış (next4biz klonu) — Tasarım & Kod Denetimi ve Düzenleme Planı

> Bu doküman **yalnızca analiz ve düzenleme planıdır** — burada kod yazılmaz.
> Kodlanmış mevcut durum (Sonnet çıktısı) satır satır incelendi; klonlama sırasında
> **eksik/yanlış kalan tasarımlar** ve **kodlama hataları** aşağıda önem sırasına göre
> listelendi. Her bulgunun altında hangi dosyada, ne yapılması gerektiği yazılıdır.
>
> Referans hedef: [ANALIZ.md](ANALIZ.md) (orijinal next4biz BPM/CSM tasarım analizi).
> İnceleme tarihi: 2026-07-20. İnceleme yöntemi: kaynak okuma + `http://localhost:8770`
> üzerinde canlı DOM/CSS ölçümü (font yükleme, responsive kırılım, hero aksanı doğrulandı).

---

## 0. Özet — Genel Durum

Klon **işlevsel olarak sağlam**: 4 sayfa (landing, liste, detay, dashboard) + sıfır
bağımlılık stdlib sunucu çalışıyor, TEAM_ROUTING sikayetvar ile birebir tutarlı, XSS
savunması (`clean()` / `html.escape`) ve isim maskeleme (KVKK) yerinde, masaüstü grid'ler
(`grid-4 → 4 sütun`) ve mobil kırılımlar (`≤900px → tek sütun + burger`) doğru çalışıyor,
hero underline aksanı görünür durumda. **Bozuk/çalışmayan bir şey yok.**

Ancak **klonlama sadakati** ve **veri modeli bütünlüğü** açısından açık kalan noktalar var.
En kritik ikisi:

1. **Poppins fontu hiç yüklenmiyor** (canlı ölçüm: `@font-face` sayısı = 0, font `<link>` yok)
   → next4biz'in bütün tipografik kimliği kaybolma riski; jüri/demo makinesinde sistem
   fontuna düşüyor.
2. **Durum makinesi zorlanmıyor** — talep herhangi bir durumdan herhangi bir duruma
   atlayabiliyor (ör. `yeni → kapandi`), ANALIZ §3.1'deki yaşam döngüsü kâğıtta kalıyor.

Önem sınıflandırması:

| Sınıf | Anlamı |
|-------|--------|
| 🔴 Yüksek | Klon sadakatini/veri bütünlüğünü doğrudan bozan, düzeltilmesi gereken |
| 🟠 Orta | Görünür eksik/tutarsızlık; demo kalitesini etkiler |
| 🟡 Düşük | Cilalama / sağlamlaştırma; opsiyonel |

---

## 1. TASARIM BULGULARI (klonlamada eksik/yanlış)

### 🔴 D1 — Poppins fontu bundle edilmemiş (sadakat kaybı)
- **Kanıt:** Canlı DOM ölçümünde `document.fonts.size === 0`, `link[href*="font"]` yok.
  `--n4b-font` değişkeni `"Poppins", "Inter", system-ui...` diyor ama hiçbir yerde
  `@font-face` veya font `<link>` tanımlı değil. ANALIZ §1.2 açıkça "Fontlar `fonts.css`
  üzerinden yerel servis ediliyor" diyor — bu `fonts.css` **hiç oluşturulmamış**.
- **Sonuç:** Poppins kurulu olmayan makinede site Inter'e, o da yoksa `system-ui`'ye
  düşüyor. next4biz'in en belirgin görsel imzası (Poppins'in yuvarlak, geniş karakteri)
  kayboluyor. Bizim makinede tesadüfen kurulu olması sorunu gizliyor.
- **Düzenleme planı:**
  - `assets/fonts/` altına Poppins `woff2` dosyaları (400, 500, 600, 700) yerel olarak konur
    (CDN **yok** — offline/CSP güvenli).
  - `assets/css/fonts.css` oluşturulup 4 ağırlık için `@font-face` (`font-display: swap`) tanımlanır.
  - 4 HTML dosyasının (`index/tickets/ticket/dashboard`) `<head>`'ine `n4b.css`'ten **önce**
    `<link rel="stylesheet" href="assets/css/fonts.css?v=1">` eklenir.
  - Alternatif (font dosyası eklenemezse): `--n4b-font`'u kasıtlı olarak sistem yığınına
    (`-apple-system, "Segoe UI", Roboto...`) sabitleyip ANALIZ §1.2 notu buna göre güncellenir
    — ama bu, klon sadakatinden ödün verir; tercih **self-host Poppins**.

### 🟠 D2 — Uygulama header'ında mobil davranış yok
- **Kanıt:** `.n4b-app-header` / `.n4b-app-nav` (tickets/ticket/dashboard) her zaman `flex`;
  burger yok, daralınca logo + 3 sekme (`Talepler · Kontrol Paneli · Tanıtım`) sıkışıyor.
  Marketing header'ında (`.n4b-header`) burger var, uygulama header'ında yok.
- **Düzenleme planı:** `n4b.css`'e `@media (max-width:640px)` altında `.n4b-app-nav` için
  yatay kaydırma (`overflow-x:auto; flex-wrap:nowrap`) veya kompakt ikon-sekme düzeni;
  gerekiyorsa app sayfalarına da küçük bir menü toggle. Tablo zaten `overflow-x:auto`.

### 🟠 D3 — Mobilde header CTA'ları tamamen kayboluyor
- **Kanıt:** `@media (max-width:900px){ .n4b-header-ctas{ display:none } }` ve `landing.js`
  burger yalnızca `.n4b-nav`'ı açıyor. Sonuç: mobilde "Toplantı Planla" ve "Müşteri Yorumları"
  hiçbir yerden erişilemiyor.
- **Düzenleme planı:** Burger açılınca açılan mobil menüye CTA butonlarını da dahil et
  (JS'te `.n4b-nav` yerine header alt açılır panelini doldur), veya CTA'ları mobilde
  `.n4b-nav` içine taşıyan bir düzen kur.

### 🟠 D4 — Bileşen stilleri `index.html` içinde inline `<style>` bloğunda
- **Kanıt:** `.n4b-hero`, `.n4b-cta-band`, `.n4b-alt-row`, `.n4b-feature-list`,
  `.n4b-diagram-box`, `.n4b-mock*` stilleri `index.html` `<head>`'inde inline; `n4b.css`'te
  yok. ANALIZ §5/§8 "tek kaynak tasarım tokenı" yaklaşımına aykırı ve bu bileşenler başka
  sayfalarda yeniden kullanılamıyor.
- **Düzenleme planı:** Bu blokları `n4b.css`'e taşı (token'larla). `index.html` inline
  `<style>`'ı boşalt. Görsel çıktı birebir korunmalı (sadece taşıma).

### 🟠 D5 — Talep sahibinin avatar/baş harf rozeti gösterilmiyor
- **Kanıt:** Sunucu her talebe `requester_initials` hesaplayıp saklıyor ama liste/detayda
  hiç kullanılmıyor. next4biz/CSM konvansiyonunda talep satırında ve detayda dairesel
  baş-harf avatarı olur.
- **Düzenleme planı:** `tickets.js` satır render'ına ve `ticket-detail.js` başlığına küçük
  dairesel avatar (camgöbeği-10 zemin, baş harfler) ekle; `n4b.css`'e `.n4b-avatar` sınıfı.

### 🟠 D6 — Duygu analizi (sentiment) hiçbir yerde görünmüyor
- **Kanıt:** `sentiment` alanı seed'de ve veri modelinde var (ANALIZ §3.2 çekirdek alan,
  sikayetvar paritesi) ama liste, detay ve dashboard'da **hiç render edilmiyor** → ölü veri.
- **Düzenleme planı:** Detay başlığına duygu rozeti (`öfkeli/olumsuz/nötr/olumlu` → renk
  eşlemi), dashboard'a "Duygu Dağılımı" bar kartı ekle (`compute_dashboard` zaten dağılım
  üretiyor; sentiment sayımı eklenir). Bkz. C10 (deterministik sentiment).

### 🟡 D7 — Çerez "AYARLAR" butonu her şeyi kabul ediyor
- **Kanıt:** `landing.js`'te `cookieSettings` ve `cookieAccept` **aynı** handler → ikisi de
  `localStorage='1'` yapıp kapatıyor. Gizlilik-öncelikli varsayılan, "Ayarlar"da isteğe
  bağlı çerezleri **reddedebilmeyi** gerektirir.
- **Düzenleme planı:** Ya küçük bir tercih mini-paneli (zorunlu/opsiyonel ayrımı) aç, ya da
  butonu "REDDET" olarak yeniden adlandırıp reddi kaydet. Demo kapsamında düşük öncelik.

### 🟡 D8 — Favicon yok
- **Kanıt:** `/favicon.ico` → 404; tarayıcı sekmesi boş. `_ctype` ico'yu destekliyor ama
  dosya yok.
- **Düzenleme planı:** 4 sayfaya inline SVG favicon (`data:` URI veya `assets/favicon.svg`)
  ekle — camgöbeği "akış" işareti.

### 🟡 D9 — Ölü bağlantılar (`href="#"`)
- **Kanıt:** "Müşteri Yorumları", "Toplantı Planla", footer "İletişim" ve yasal linkler hep
  `#`. Demo için kabul edilebilir ama tıklama hissi kırık.
- **Düzenleme planı:** Ya bir placeholder/`mailto:` hedefi ver, ya da bu butonları demo
  kapsamında pasif (cursor/`aria-disabled`) göster.

### 🟡 D10 — Hero underline aksanı `z-index:-1`'e bağımlı (kırılgan)
- **Kanıt:** `.n4b-accent-underline::after { z-index:-1; opacity:.55 }`. Şu an hero
  gradyanı üstünde **görünür** (canlı doğrulandı), ama zemin opak beyaz olsaydı aksan kaybolurdu.
- **Düzenleme planı (opsiyonel):** Negatif z-index yerine `background-image: linear-gradient`
  ile alt-çizgi (metnin arkasına değil, satır kutusunun altına) — daha dayanıklı. Düşük öncelik.

---

## 2. KODLAMA BULGULARI (hatalı/eksik mantık)

### 🔴 C1 — Durum makinesi geçişleri doğrulanmıyor
- **Kanıt:** `server.py::_update_ticket` gelen `status`'u yalnızca `STATUSES` üyeliğine göre
  kontrol ediyor; **geçiş kuralı yok**. `yeni → kapandi`, `kapandi → yeni`, `cozuldu → atandi`
  gibi mantıksız atlamalar serbest. ANALIZ §3.1 yaşam döngüsü tanımlı ama uygulanmıyor.
- **Düzenleme planı:**
  - `server.py`'de `ALLOWED_TRANSITIONS = { "yeni": {...}, "siniflandirildi": {...}, ... }`
    haritası tanımla (ör. `cozuldu → {kapandi, yeniden-acildi}`; `kapandi → {yeniden-acildi}`).
  - `_update_ticket` içinde yeni durum, mevcut durumun izinli komşusu değilse `400` döndür.
  - `ticket-detail.js`'te durum `<select>`'ini yalnızca izinli sonraki durumlarla doldur
    (meta'ya `allowed_transitions` ekleyip istemciye taşı). Stepper zaten ana akışı çiziyor.

### 🔴 C2 — `avg_age_hours` KPI'ı yanlış anlam / yanlış etiket
- **Kanıt:** `compute_dashboard`'da yaş, **tüm talepler** (kapananlar dahil) için
  `now - createdAt` ortalaması. `dashboard.js` etiketi: **"talep açık kalma süresi"**. Kapalı
  talepler bu değeri şişiriyor ve bu "açık kalma" değil, "oluşturmadan bu yana geçen" süre.
- **Düzenleme planı:** İki seçenek:
  1. Ortalamayı **yalnızca `OPEN_STATUSES`** talepler üzerinden hesapla (etiketle uyumlu), **veya**
  2. Etiketi "ortalama talep yaşı (tüm)" yap ve ayrıca **çözülenler için** "ortalama çözüm
     süresi" ekle (bkz. C3 `resolved_at`).
  - Önerilen: (1) açık talep yaşı + (2) çözüm süresi, iki ayrı KPI.

### 🟠 C3 — Çözüm/kapanış zaman damgası tutulmuyor
- **Kanıt:** Durum `cozuldu`/`kapandi`'ye geçince `resolved_at`/`closed_at` yazılmıyor;
  gerçek çözüm-süresi metriği imkânsız, `yeniden-acildi` geçmişi de damgasız.
- **Düzenleme planı:** `_update_ticket`'te `cozuldu`/`kapandi` geçişinde `resolved_at = now`
  yaz; `yeniden-acildi`'de temizle. Veri modeline `resolved_at` alanı ekle. C2 metriğini besler.

### 🟠 C4 — `load_data()` her istekte diskten okuyup parse ediyor
- **Kanıt:** Liste/detay/dashboard her çağrıda `tickets.json`'ı yeniden okuyup `json.load`
  ediyor; global `LOCK` ile tüm trafik disk I/O üzerinde seri hâle geliyor. Doğruluk hatası
  değil ama ölçeklenmez.
- **Düzenleme planı:** Bellek-içi cache (`_CACHE = None`), ilk yüklemede doldur, `_write`'ta
  hem diske hem cache'e yaz, okumalar cache'ten. `LOCK` korumasını koru. Atomik yazma
  (`os.replace`) aynı kalır.

### 🟠 C5 — Onaylar (approvals) yalnızca görüntüleniyor, aksiyon yok
- **Kanıt:** `ticket-detail.js` onay durumunu render ediyor ama onayla/reddet aksiyonu yok;
  `server.py`'de onay güncelleme ucu da yok. Model bir onay iş akışı ima ediyor (ANALIZ §3.2).
- **Düzenleme planı:** `PATCH /api/tickets/{id}/approvals/{idx}` ucu (state: onaylandi/reddedildi)
  + detayda "Onayla / Reddet" butonları. **Not:** geri alınması zor aksiyon → UI'da tek adım
  onay yeterli, ama audit'e yazılmalı; timeline'a olay düşülmeli.

### 🟠 C6 — `assignee_user` (kişi ataması) UI'dan erişilemiyor
- **Kanıt:** `_update_ticket` `assignee_user`'ı destekliyor ama detay sayfasında hiçbir
  kontrol yok; sadece ekip atanabiliyor.
- **Düzenleme planı:** Yan panele "Atanan Kişi" input/`select`'i ekle → mevcut PATCH ucunu
  kullan. (İstersen ekip başına örnek kullanıcı listesi meta'dan gelir.)

### 🟡 C7 — Sunucu `0.0.0.0`'a bağlanıyor (tüm arayüzler)
- **Kanıt:** `ThreadingHTTPServer(('0.0.0.0', PORT), ...)` → LAN'a açık. Yerel demo için
  `127.0.0.1` yeterli ve daha güvenli. (sikayetvar sunucusuyla tutarlılığı da kontrol et.)
- **Düzenleme planı:** Bind adresini `127.0.0.1` yap (veya bir env değişkeniyle seçilebilir kıl).

### 🟡 C8 — Yanıtlarda güvenlik başlığı yok
- **Kanıt:** Statik/JSON yanıtlarında `X-Content-Type-Options: nosniff`, `X-Frame-Options`
  yok. Yerel güvenilir ortam ama ucuz sertleştirme.
- **Düzenleme planı:** `_json` ve `_static`'a `X-Content-Type-Options: nosniff` (+ istenirse
  `Referrer-Policy: no-referrer`) ekle.

### 🟡 C9 — `attachments[]` model dışı: reklam var, uygulama yok
- **Kanıt:** ANALIZ §3.2 veri modelinde `attachments[]` var; landing "foto/doküman ekleyin"
  diyor; ama sunucu/UI'da ek dosya desteği **hiç yok**.
- **Düzenleme planı:** Kapsam kararı: ya minimal ek-listesi (yalnızca ad/etiket, gerçek yükleme
  yok — dosya yükleme bu fazda kapsam dışı) ekle, ya da landing'deki iddiayı "yol haritası"
  olarak işaretle. Karar demoya göre verilir.

### 🟡 C10 — Seed sentiment deterministik değil
- **Kanıt:** `build_seed`'de `random.choice(SENTIMENTS)` → her taze `data/` farklı değer;
  demolar/ekran görüntüleri tutarsız ve (D6 ile birlikte) ölü veri.
- **Düzenleme planı:** Her seed satırına sabit, anlamlı sentiment ata (ör. `Yetkisiz İşlem`/
  `kritik` → `ofkeli`; `cozuldu` → `notr/olumlu`). D6 görünürlüğüyle birlikte anlam kazanır.

### 🟡 C11 — Rate-limit sözlüğü (`_RATE`) IP başına büyüyor
- **Kanıt:** `_RATE` her farklı IP için bir giriş tutuyor; girişler zamanla budanıyor ama
  sözlük anahtarları birikiyor. Yerel demoda önemsiz, açık dağıtımda küçük bellek sızıntısı.
- **Düzenleme planı:** Periyodik/olay-tetikli prune (boş listeleri sil). Düşük öncelik.

---

## 3. DOĞRU ÇALIŞAN / DOKUNULMAYACAK KISIMLAR

Bu kısımlar sağlam; düzenlemede **korunmalı**:

- **TEAM_ROUTING** — sikayetvar ile birebir; kategori→ekip eşlemesi tutarlı.
- **XSS savunması** — `clean()`/`html.escape` yazımda uygulanıyor; istemci zaten
  escape'lenmiş veriyi `innerHTML`'e basıyor → çift güvenli. Yeni XSS açığı **yok**.
- **KVKK** — `mask_name` (baş harf + `**`) ve `initials` doğru; isimler asla açık saklanmıyor.
- **Atomik yazma + kilit** — `os.replace` + `threading.Lock` doğru; eşzamanlı yazımda güvenli.
- **Doğrulama** — `v_name/v_len/v_choice` uçlarda sağlam; sınır değerleri (10–120 başlık,
  20–2000 gövde) makul.
- **Responsive iskelet** — `grid-2/3/4 → tek sütun @900px`, tablo `overflow-x:auto`, hero
  tek sütun; masaüstünde 4 sütun doğrulandı.
- **SLA hesap mantığı** — `sla_state_of` (breach/risk/ok, %20 risk eşiği) ve öncelik→SLA
  penceresi (`kritik 4s … dusuk 120s`) tutarlı; öncelik değişince `sla_due_at` yeniden
  hesaplanıyor.
- **Path traversal koruması** — `_static`'te `full.startswith(ROOT + os.sep)` kontrolü var.

---

## 4. FAZLI DÜZENLEME PLANI (Sonnet için uygulama sırası)

Bağımlılık ve etki sırasına göre:

**Faz A — Klon sadakati (görsel, en yüksek etki)**
1. **D1** Poppins self-host + `fonts.css` + 4 HTML'e link. *(dosyalar: yeni `assets/fonts/`,
   yeni `assets/css/fonts.css`, `index/tickets/ticket/dashboard.html`)*
2. **D4** Inline stilleri `n4b.css`'e taşı. *(`index.html`, `n4b.css`)*
3. **D8** Favicon; **D9** ölü linkleri düzelt/pasifle. *(4 HTML)*

**Faz B — Veri modeli bütünlüğü (kod doğruluğu)**
4. **C1** Durum-makinesi geçiş doğrulaması (sunucu + meta + detay select). *(`server.py`,
   `ticket-detail.js`)*
5. **C3** `resolved_at` damgası → **C2** KPI'ları düzelt (açık-yaş + çözüm süresi).
   *(`server.py`, `dashboard.js`)*
6. **C10** Deterministik sentiment → **D6** sentiment'i detay + dashboard'da göster.
   *(`server.py`, `ticket-detail.js`, `dashboard.js`, `n4b.css`)*

**Faz C — Ekran tamamlığı**
7. **D5** Avatar/baş harf rozeti (liste + detay). *(`tickets.js`, `ticket-detail.js`, `n4b.css`)*
8. **C6** `assignee_user` UI kontrolü; **C5** onay aksiyonları + ucu. *(`ticket-detail.js`,
   `server.py`)*
9. **D2/D3** Uygulama header + mobil CTA davranışı. *(`n4b.css`, `landing.js`, app HTML'leri)*

**Faz D — Sertleştirme (opsiyonel/düşük öncelik)**
10. **C4** Bellek-içi cache; **C7** `127.0.0.1` bind; **C8** güvenlik başlıkları;
    **C11** rate-limit prune; **D7** çerez tercih paneli; **D10** underline sağlamlaştırma.
    *(çoğu `server.py`; D7/D10 `landing.js`/`n4b.css`)*

**Faz E — (kapsam kararı)**
11. **C9** `attachments[]`: minimal liste mi, yol haritası notu mu — demo kapsamına göre karar.

> **Sürüm/kaç-busting notu:** CSS/JS değiştikçe ilgili `?v=N`'i artır (şu an hepsi `?v=1`).
> Font eklenince `fonts.css?v=1` ilk kez gelecek; `n4b.css` değişirse `?v=2`.

**Kapsam dışı (kasıtlı, dokunma):** AI ↔ ticket köprüsü (ANALIZ §6 Faz 4). `source:"ai"`
alanı ve seed'deki AI kaynaklı talepler yerinde bırakılır ama `analysis.py` bağlanmaz.

---

## 5. Hızlı Kontrol Listesi (düzeltme bitince test)

- [ ] Poppins gerçekten yükleniyor mu? (`document.fonts.size > 0`, DevTools > Network > woff2 200)
- [ ] `yeni → kapandi` gibi geçiş 400 dönüyor mu? Detay select yalnızca izinli durumları mı gösteriyor?
- [ ] Dashboard "açık yaş" ve "çözüm süresi" ayrı ve doğru mu? (kapalılar açık-yaşı şişirmiyor)
- [ ] Sentiment rozeti detayda, dağılımı dashboard'da görünüyor mu? Seed sabit mi?
- [ ] Avatar baş harfleri liste + detayda çıkıyor mu?
- [ ] Mobilde (≤640px) app header ve CTA'lar erişilebilir mi?
- [ ] Onay onayla/reddet timeline + audit'e yazılıyor mu?
- [ ] XSS/KVKK regresyon yok mu? (başlığa `<script>` → escape'li metin; isim maskeli)
