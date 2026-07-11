# ŞİKAYETVAR — MOKA UNITED SAYFASI KLON SPESİFİKASYONU

> Kaynak: https://www.sikayetvar.com/moka-united
> Analiz tarihi: 2026-07-11 (Fable). Amaç: Bu dokümana bakarak sayfanın çalışan bir klonunu üretebilmek.
> **Kapsam:** Şikayetvar'ın TAMAMI değil; yalnızca Moka United marka şikayet sayfası + şikayet/yorum ekleme akışı.
> **Backend şartı:** Kullanıcı şikayet ve yorum ekleyebilmeli, eklenenler sayfada kalıcı görünmeli (küçük, yerel backend).
> Konum: `~/Downloads/Moko_United/sikayetvar/` (ana Moka United klonunun alt projesi; ana klondan bağımsız çalışır).
> **GÜNCELLEME (2026-07-11, 2. tur):** Klon işlevsel olarak tamam; ancak RENK PALETİ YANLIŞ çıktı
> (orijinal CSS indirilip doğrulandı: beyaz header + mor #695de9). Düzeltme listesi: **Bölüm 10** — kodlamaya oradan başla.
> Bölüm 3'teki renk tablosu gerçek değerlerle güncellendi.

---

## 1. AMAÇ VE KAPSAM KARARLARI

| Konu | Karar |
|---|---|
| Klonlanan | Tek sayfa: marka başlığı + şikayet listesi + şikayet detayı + yorumlar |
| Klonlanmayan | Şikayetvar ana sayfa, diğer markalar, üyelik/giriş, Trend 100, video oynatma, gerçek arama backend'i |
| Üyelik | YOK — şikayet/yorum formunda "Ad Soyad" alanı ile anonim gönderim (rumuz mantığı) |
| Sayfalama | Basitleştirilmiş: seed + kullanıcı şikayetleri tek listede, "Daha Fazla Göster" veya basit 1-2-3 sayfalama (sayfa başı 10 kart) |
| Şikayet detayı | Ayrı sayfa YERİNE aynı sayfada genişleyen kart **veya** `?id=` parametreli detay görünümü — yorumlar burada listelenir/eklenir |
| Video şikayetler | Statik dekoratif şerit (tıklanmaz) veya tamamen atlanabilir — düşük öncelik |
| İçerik politikası | **Gerçek şikayet metinleri ve gerçek kullanıcı adları KOPYALANMAZ** (telif + KVKK). Seed verisi tamamen kurgu; konu başlıkları sitedeki temalardan esinlenerek yeniden yazılır (ör. para iadesi, POS başvurusu, komisyon). |

---

## 2. KAYNAK SAYFA YAPISI (canlıdan çıkarılan)

### 2.1 Header (Şikayetvar genel header'ı)
```
header
├── Logo: "şikayetvar" (beyaz wordmark, turkuaz zemin üstünde)
├── Arama çubuğu: placeholder "Sonuçlarda ara..." (geniş, ortada)
├── Nav: Şikayetler | Trend 100 | Video
├── "Giriş Yap / Üye Ol" linki (klonda dekoratif, tıklanınca "demo" tooltip/uyarı)
└── "Şikayet Yaz" butonu (vurgulu CTA — headerda ve marka bloğunda tekrar eder)
```

### 2.2 Marka başlık bloğu (hero)
- Marka logosu (Moka United — ana klondaki `LOGO_SVG` yeniden kullanılabilir).
- Marka adı: **Moka United** (h1).
- **Puan göstergesi: "56/100"** + "(789 değerlendirme)" — dairesel/rozet stili skor.
- **Toplam şikayet sayısı: "4.535 şikayet"** (klonda: seed + kullanıcı eklemeleriyle dinamik sayı; başlangıç değeri seed sayısı olabilir, birebir 4.535 yazmak şart değil — "X şikayet" dinamik).
- Büyük **"Şikayet Yaz"** butonu → şikayet formu modalını açar.
- (Orijinalde marka profil sekmeleri olabilir: Şikayetler/Çözülenler — klonda tek liste + "Çözüldü" rozetli kartlar yeterli.)

### 2.3 Şikayet kartı (listenin ana bileşeni — sayfada ~15 adet)
Her kart:
```
.complaint-card
├── Üst satır: avatar (baş harfli daire) + kullanıcı adı (link görünümlü) + tarih/saat
├── Başlık (h2/h3, tıklanabilir → detay)
├── Özet metin (2-3 satır, ellipsis ile kısaltılmış)
├── Alt satır (istatistik şeridi):
│   ├── Görüntülenme sayısı (göz ikonu + sayı, örn. 185)
│   ├── Destek sayısı (destekle butonu + sayı)
│   ├── Yorum sayısı (balon ikonu + sayı)
│   └── Durum rozeti: "Çözüldü" (yeşil) — bazı kartlarda
└── (Opsiyonel) görsel küçük resmi — klonda atlanabilir
```
- Marka yanıtı: bazı şikayetlerin altında "Moka United yanıtladı" tarzı kurumsal yanıt bloğu görünür — klonda yorumlarda `isBrand:true` işaretli yorum olarak temsil edilir (farklı zemin + marka logosu).

### 2.4 Etiket bulutu (sol/üst bölge)
- Sık geçen konu etiketleri (hap şeklinde chip'ler). Klonda 6-8 kurgu etiket: "para iadesi", "pos başvurusu", "komisyon oranı", "müşteri hizmetleri", "hesap onayı", "cihaz teslimatı". Tıklanınca istemci tarafı filtre (başlık/metin içinde geçenler) — opsiyonel ama ucuz.

### 2.5 Video şikayetler şeridi
- "Video Şikayetler" başlığı + "Tümünü Gör" linki + küçük kart sırası. **Klonda düşük öncelik:** statik 2-3 kapak kartı (tıklanmaz) veya atla.

### 2.6 Footer
- Sütunlar: Hakkımızda / Markalar İçin / ACE Ödülleri; Kullanım Şartları / Çerez Politikası; Şikayetler / Markalar / Konular; sosyal ikonlar (X, YouTube, Facebook, LinkedIn).
- Klonda: tek satırlık sadeleştirilmiş footer + "Bu bir klon/demo çalışmasıdır" notu ZORUNLU.

### 2.7 Sayfalama
- Orijinal: `1 2 3 4 … 189` + ileri oku. Klonda: sayfa başı 10 kart, toplam sayfa dinamik; sade sayı düğmeleri.

---

## 3. TASARIM SİSTEMİ — GERÇEK PALET (2. turda orijinal CSS'ten doğrulandı)

> **ÖNEMLİ DÜZELTME (2. tur):** İlk turdaki turkuaz/turuncu palet YANLIŞTI (göz kararı tahmindi).
> Orijinal sitenin CSS değişkenleri indirilip doğrulandı (`files.sikayetvar.com/.../*.css` → `:root` bloğu).
> Şikayetvar'ın gerçek kimliği: **BEYAZ header + MOR birincil renk**. Aşağıdaki tablo artık kesin kaynaktır.

| Token (yeni ad) | GERÇEK değer (orijinal CSS'ten) | Kullanım |
|---|---|---|
| `--sv-primary` | **`#695de9`** (mor) | "Şikayet Yaz" butonları, linkler, aktif durumlar, focus ring — orijinalde `--primary` |
| `--sv-primary-dark` | `#5551ff` (canlı mor-mavi) | Hover/vurgu varyantı (orijinalde sık geçen ikinci ton) |
| `--sv-primary-light` | `#b2c1f6` (açık mor) | Chip zeminleri, hover zeminleri, highlight |
| `--sv-secondary` | **`#3ad08f`** (yeşil) | "Çözüldü" rozeti, başarı — orijinalde `--secondary` |
| `--sv-green-light` | `#b3f3d8` | Çözüldü rozet zemini |
| `--sv-dark` | **`#272635`** (koyu mürekkep) | Başlıklar, ana metin, footer zemini — orijinalde `--dark` |
| `--sv-light` | **`#f4f5f9`** (açık gri-mavi) | Sayfa zemini — orijinalde `--light` |
| `--sv-border` | `#dcdde1` (ikincil: `#e4e4e7`) | Kart/input çerçeveleri |
| `--sv-muted` | `#7c7b85` (açık: `#afb0b6`) | İkincil metin, ikonlar |
| `--sv-red` | `#dc3545` (koyu: `#c32c3a`; pembe varyant: `#ff4267`) | Hata mesajları, olumsuz durum |
| `--sv-orange` | `#ec8a27` | YALNIZCA orta-skor göstergesi/yıldız tonu (CTA DEĞİL!) |
| Header | **BEYAZ zemin** (`theme-color: #ffffff`), alt çizgi `--sv-border` | Logo koyu `#272635` + mor vurgu; nav linkleri koyu; arama kutusu `#f4f5f9` zeminli hap |
| Radius | kart 12px, buton 8px, chip 20px, avatar 50% | (değişmedi) |
| Font | Sistem sans (`-apple-system, 'Segoe UI', Roboto, sans-serif`) | (değişmedi; orijinal Tailwind tabanlı) |
| Skor rozeti | 56/100: halka `#ec8a27` (orta skor kuralı: 0-40 `--sv-red`, 40-70 `#ec8a27`, 70+ `--sv-secondary`) | (kural aynı, tonlar güncel) |

Layout: maksimum ~1080px orta sütun; tek sütun liste + üstte marka bloğu. Mobilde tek sütun. (değişmedi)

---

## 4. EKLEME AKIŞLARI (klonun kalbi)

### 4.1 Şikayet Yaz akışı
1. "Şikayet Yaz" butonu → modal açılır (ana klondaki `bio-modal` kalıbı yeniden kullanılabilir).
2. Alanlar: **Ad Soyad** (2-40 karakter, yalnız harf+boşluk), **Başlık** (10-100), **Şikayet Metni** (textarea, 30-2000), KVKK/demo onay checkbox'ı ("Bu bir demo sitedir, gerçek şikayet iletmez").
3. GÖNDER → `POST /api/complaints` → başarıda modal kapanır, yeni şikayet **listenin en üstünde** görünür (yeniden fetch veya optimistic ekleme), kart kısa süre vurgulanır (highlight animasyonu).
4. Hata durumunda alan altı kırmızı mesaj.

### 4.2 Yorum ekleme akışı
1. Kart başlığına/`Yorumlar (n)` linkine tıkla → detay görünümü açılır (kart genişler veya `?id=` görünümü).
2. Detayda: tam şikayet metni + yorum listesi (avatar+ad+tarih+metin; `isBrand:true` ise "Moka United" rozetli farklı zemin).
3. Alt kısımda yorum formu: **Ad Soyad** + **Yorum** (5-500) + GÖNDER → `POST /api/complaints/{id}/comments` → yorum anında listeye eklenir, karttaki yorum sayacı artar.

### 4.3 Destekle (opsiyonel, ucuz)
- Karttaki "Destekle" → `POST /api/complaints/{id}/support` → sayı +1; `localStorage`'a id yazılır, ikinci tıklamada buton pasif ("Desteklendi").

### 4.4 Görüntülenme
- Detay her açıldığında `views` +1 (`POST /api/complaints/{id}/view` veya detay GET'inin yan etkisi). Basitlik için POST tercih edilir (GET yan etkisiz kalsın).

---

## 5. BACKEND SPESİFİKASYONU (detaylı)

### 5.1 Teknoloji kararı
- **Python 3 stdlib** — `http.server.ThreadingHTTPServer` + özel `BaseHTTPRequestHandler`. **Sıfır bağımlılık** (pip yok, Flask yok) → projenin mevcut `python3` akışıyla ve `launch.json` düzeniyle bire bir uyumlu.
- Tek dosya: `sikayetvar/server.py`. Hem **statik dosyaları** (index.html, assets) hem **JSON API**'yi aynı porttan servis eder → CORS derdi yok.
- **Port: 8756** (ana klonun statik sunucusu 8755'te; çakışmasın).

### 5.2 API uç noktaları

| Metot | Yol | Gövde (JSON) | Yanıt | Açıklama |
|---|---|---|---|---|
| GET | `/api/complaints` | — | `{total, page, pageSize, items:[...]}` | Yeni→eski sıralı liste. Query: `?page=1&q=arama` (q: başlık+metin içinde, TR küçük harf duyarlı arama — ana klondaki `trLower` mantığı) |
| GET | `/api/complaints/{id}` | — | tek şikayet (yorumlar dahil) | 404: `{error:"not_found"}` |
| POST | `/api/complaints` | `{name, title, body}` | 201 + oluşturulan kayıt | Doğrulama başarısızsa 400 + `{error, field}` |
| POST | `/api/complaints/{id}/comments` | `{name, body}` | 201 + oluşturulan yorum | — |
| POST | `/api/complaints/{id}/support` | — | `{supports}` | Sayaç +1 |
| POST | `/api/complaints/{id}/view` | — | `{views}` | Sayaç +1 |
| GET | `/` ve diğer yollar | — | statik dosya | `index.html`, `assets/...`; bilinmeyen → 404 |

Ortak kurallar:
- İstek/yanıt `Content-Type: application/json; charset=utf-8`.
- Tüm string girdiler sunucuda **HTML-escape** edilir (`html.escape`) — XSS ana savunması sunucuda; istemci ayrıca `textContent` kullanır.
- Maks gövde boyutu ~16KB; aşarsa 413.
- Basit flood koruması (opsiyonel): IP başına dakikada 5 POST; aşarsa 429.

### 5.3 Veri modeli — `sikayetvar/data/complaints.json`
```json
{
  "seq": 12,
  "complaints": [
    {
      "id": 12,
      "name": "A** K**",
      "title": "POS cihazım hâlâ teslim edilmedi",
      "body": "…kurgu metin…",
      "createdAt": "2026-07-10T14:32:00",
      "views": 47,
      "supports": 3,
      "status": "yanit-bekliyor",
      "comments": [
        { "id": 1, "name": "Moka United", "isBrand": true,
          "body": "…kurgu marka yanıtı…", "createdAt": "2026-07-10T16:05:00" }
      ]
    }
  ]
}
```
Notlar:
- `status`: `"cozuldu" | "yanit-bekliyor"`. Kullanıcı eklemeleri her zaman `yanit-bekliyor` başlar.
- Kullanıcı adı gösterimi: Şikayetvar tarzı **maskeleme** — ad soyadın ilk harfleri + `**` (örn. "Ahmet Kaya" → "A** K**"). Maskeleme sunucuda yapılır, ham ad saklanmaz (KVKK-benzeri hijyen). Avatar baş harfleri maskelenmemiş ilk harflerden üretilir.
- `isBrand` yorumları yalnızca seed'de bulunur (kullanıcı marka adına yorum ekleyemez — form bunu sunmaz).

### 5.4 Kalıcılık ve eşzamanlılık
- Yazma stratejisi: bellekte dict + her mutasyonda diske yaz.
- **Atomic write:** önce `complaints.json.tmp`'ye yaz → `os.replace` ile taşı (yarım dosya riski yok).
- **`threading.Lock`** ile tüm okuma-değiştirme-yazma blokları korunur (ThreadingHTTPServer eşzamanlı istek alır).
- Dosya yoksa ilk açılışta **seed** ile oluşturulur (aşağıda).

### 5.5 Seed verisi
- 10-12 **tamamen kurgu** şikayet; konu dağılımı gerçekçi: para iadesi gecikmesi, sanal POS başvuru süreci, komisyon kesintisi itirazı, müşteri hizmetlerine ulaşamama, cihaz teslimatı, hesap doğrulama, link ile ödeme sorunu, cüzdan bakiye aktarımı.
- 3-4 tanesi `cozuldu` + `isBrand` marka yanıtı içerir; görüntülenme 20-400 arası rastgele; tarihler son 30 güne yayılır.
- **Kaynak sitedeki gerçek metin/rumuz kullanılmaz.**

### 5.6 Çalıştırma / launch entegrasyonu
- `python3 sikayetvar/server.py` → `http://localhost:8756`.
- `Moko_United/.claude/launch.json`'a ikinci konfigürasyon eklenir:
  `{"name":"sikayetvar","runtimeExecutable":"python3","runtimeArgs":["sikayetvar/server.py"],"port":8756}`
- Sunucu, statik kökü `sikayetvar/` klasörü olarak kullanır (path traversal koruması: `..` içeren yollar 403).

---

## 6. FRONTEND DAVRANIŞLARI

1. Yüklemede `GET /api/complaints?page=1` → kartlar render edilir; marka bloğundaki "X şikayet" sayısı `total`'dan gelir.
2. Render **tamamen JS ile** (`fetch` + DOM); şablon: `document.createElement`/template literal, kullanıcı verisi daima `textContent` ile basılır.
3. Şikayet formu submit → POST → 201 ise liste başına ekle + sayaç güncelle + highlight; modal kapat.
4. Detay aç/kapa: kart tıklanınca `GET /api/complaints/{id}` + `POST .../view`; yorum formu POST sonrası yorum listesine append.
5. Arama kutusu (header): 300ms debounce ile `GET /api/complaints?q=` → liste yenilenir (istemci tarafı da olabilir; API'de olması "gerçek backend" hissini güçlendirir, maliyeti düşük).
6. Etiket chip'i tıklama = arama kutusuna o etiketi yazıp aramayı tetikleme.
7. Boş durum: hiç sonuç yoksa "Aramanla eşleşen şikayet bulunamadı" kartı.
8. Tarih gösterimi: "az önce / X saat önce / 12 Temmuz" biçiminde göreli/kısa format (JS'te tek yardımcı fonksiyon).

---

## 7. DOSYA YAPISI

```
Moko_United/sikayetvar/
├── SIKAYETVAR_KLON_ANALIZ.md   (bu dosya)
├── index.html                   (tek sayfa; header + marka bloğu + liste + modallar + footer)
├── server.py                    (statik + JSON API, stdlib-only)
├── data/
│   └── complaints.json          (seed; server ilk açılışta yoksa üretir)
└── assets/
    ├── css/sv.css               (Şikayetvar temasi — ana klonun style.css'inden BAĞIMSIZ)
    └── js/sv.js                 (fetch/render/form/modal mantığı)
```
- Ana klonla paylaşım: yalnızca Moka United logosu (SVG inline kopyalanabilir). CSS/JS paylaşılmaz — iki site farklı marka.

---

## 8. İŞ SIRASI (Opus için)

1. `server.py`: statik servis + GET/POST complaints + comments + seed üretimi + atomic write + Lock (Bölüm 5).
2. `index.html` iskeleti + `sv.css` token'ları (Bölüm 3) — header, marka bloğu, kart, modal, footer.
3. `sv.js`: liste render + şikayet formu + detay/yorum akışı (Bölüm 4, 6).
4. Destekle + görüntülenme sayaçları + arama/etiket filtresi.
5. Sayfalama + boş durum + tarih formatı + highlight animasyonu.
6. `launch.json`'a `sikayetvar` konfigi; önizlemede uçtan uca test.

### Kabul kriterleri (✅ TAMAMLANDI — 2026-07-11, tarayıcı + curl ile doğrulandı)
- [x] `python3 sikayetvar/server.py` tek komutla çalışıyor; hiçbir pip paketi gerekmiyor (yalnız stdlib).
- [x] Sayfa açılınca 12 seed şikayet listeleniyor; marka bloğunda dinamik toplam sayı + 56/100 skor rozeti (conic-gradient turuncu halka) var.
- [x] "Şikayet Yaz" modalından gönderilen şikayet listenin başında flash animasyonuyla beliriyor ve **sunucu yeniden başlatılınca da duruyor** (JSON'a atomic write; restart sonrası doğrulandı).
- [x] Şikayet detayı açılıp yorum eklenebiliyor; yorum sayacı (1→2) ve liste anında güncelleniyor; yorum kalıcı.
- [x] Marka yanıtı (`isBrand`) yorumları "Marka Yanıtı" rozeti + farklı zeminle görünüyor.
- [x] XSS denemesi (`<script>alert(1)</script>`) sunucuda `html.escape` ile kaçırılıp zararsız düz metin olarak görünüyor (çalışmıyor).
- [x] Arama `q` TR-duyarlı çalışıyor (komisyon → 1 sonuç); destekle 2. kez tıklanamıyor (localStorage + disabled).
- [x] Footer'da "eğitim/demo klon" ibaresi var; hiçbir gerçek şikayet metni/rumuz kopyalanmadı (seed tamamen kurgu).
- [x] 375px ve 1100px+'ta yatay taşma/bozulma yok; konsol hatası yok. Path traversal (`/../`, `%2e%2e/`) → 403.

**Önizleme notu:** Önizleme harness'i `launch.json`'ı oturum kök dizininden (Teknofest) okuduğu için `sikayetvar` konfigini otomatik başlatmayabiliyor; sunucu doğrudan `python3 sikayetvar/server.py` (port 8756) ile çalıştırılır, tarayıcı `http://localhost:8756`'ya yönlendirilir. Konfig yine de `Moko_United/.claude/launch.json`'a eklendi.

---

## 9. ETİK / TELİF NOTU
- Şikayetvar'ın marka logosu birebir kopyalanmaz; "şikayetvar" benzeri sade tipografik wordmark yeterli (klon/eğitim amaçlı olduğu footer'da açıkça yazar).
- Gerçek kullanıcı içeriği ve kişisel veri taşınmaz; tüm şikayet/yorum metinleri kurgudur.
- Google vignette/reklam bileşenleri klonlanmaz.

---

## 10. 2. TUR ANALİZ — RENK DÜZELTMELERİ VE GELİŞTİRMELER (Opus görev listesi)

> Analiz tarihi: 2026-07-11 (2. tur, Fable). Klonun canlı hali incelendi ve orijinal sitenin
> **gerçek CSS dosyaları indirilip** renk değişkenleri doğrulandı. Sonuç: klonun işlevselliği tam
> (Bölüm 8 kabul kriterleri geçti) ancak **renk kimliği yanlış** — ilk turda göz kararı seçilen
> turkuaz/turuncu palet, orijinalin BEYAZ header + MOR (#695de9) kimliğiyle uyuşmuyor.
> Bölüm 3'teki tablo gerçek değerlerle güncellendi; bu bölüm uygulama listesidir.

### 10.1 Klonun mevcut durumu (tespit)

| Öğe | Klonda şu an | Orijinalde (doğrulanmış) |
|---|---|---|
| Header zemini | Turkuaz `#14b9c6`, beyaz metin | **BEYAZ**, koyu (#272635) metin, altta ince `#dcdde1` çizgi |
| "Şikayet Yaz" butonu | Turuncu `#ff7a00` | **MOR `#695de9`**, beyaz metin |
| Linkler/vurgu | Turkuaz | Mor `#695de9` |
| Sayfa zemini | `#f4f6f8` | `#f4f5f9` (çok yakın — küçük düzeltme) |
| "Çözüldü" rozeti | `#2ecc71` tonu | `#3ad08f` (zemin `#b3f3d8`) |
| Başlık/metin rengi | `#163b4d` (navy) | `#272635` (mürekkep) |
| Footer | Navy `#163b4d` | Koyu `#272635` |
| Avatar | Turkuaz | Mor tonları |
| Destekle (kalp) hover/aktif | Turuncu | Mor (birincil etkileşim rengi) |
| Skor halkası | Turuncu conic — kural doğru | Aynı kural; turuncu tonu `#ec8a27` olmalı |
| Favicon | Turkuaz balon | Mor'a çevrilmeli |
| Logo wordmark | beyaz "şikayet" + turuncu "var" (turkuaz zeminde) | Koyu `#272635` "şikayet" + mor `#695de9` "var" (beyaz zeminde) — klon-özgü sade wordmark korunur, renkleri değişir |

### 10.2 Uygulama listesi — renk geçişi (öncelik 1)

Tümü `assets/css/sv.css` içinde; HTML/JS değişikliği gerektirenler ayrıca işaretli:

1. `:root` bloğunu Bölüm 3'teki YENİ tabloyla değiştir: `--sv-teal*` ve `--sv-navy` değişkenlerini `--sv-primary`, `--sv-primary-dark`, `--sv-primary-light`, `--sv-dark` olarak yeniden adlandır ve tüm kullanımları güncelle (sed benzeri toplu değişim güvenli; değişken sayısı az).
2. **Header'ı beyaza çevir:** `.sv-header{background:#fff; color:var(--sv-dark); border-bottom:1px solid var(--sv-border)}`; nav linkleri koyu, hover mor; arama input'u `#f4f5f9` zeminli (şu an beyaz-üstü-beyaz kalacağı için zemin şart); logo renkleri `.sv-logo{color:var(--sv-dark)}`, `.dot{color:var(--sv-primary)}`.
3. `.btn-orange` sınıfını **`.btn-primary`** yap (index.html'deki 2 buton + sv.js'teki sınıf adı dahil — JS'te sınıf adı geçiyor mu kontrol et; geçmiyorsa yalnız HTML+CSS): zemin `--sv-primary`, hover `#574bd6` civarı koyu mor.
4. `.btn-teal` (yorum gönder) → `--sv-primary` ailesine geçir; tek buton ailesi yeterli.
5. Rozetler: `.status-cozuldu{background:#e7f9ef→#b3f3d8'e yakın açık ton; color:#1e9e57→#2aa871 civarı}`; `.status-yanit-bekliyor` turuncu tonu yerine nötr gri-mor (`#f0effc` zemin + `#695de9` metin) — orijinal kimliğe daha uygun.
6. Chip'ler: zemin `#f0effc` (açık mor), metin `--sv-primary`; aktif: mor zemin + beyaz.
7. `.support-btn:hover/.supported` turuncu → mor; `.card.flash` animasyon zemini `#fff7e8` → `#f0effc`.
8. Avatarlar: `--sv-primary`; marka avatarı `--sv-dark` kalabilir.
9. Footer: `--sv-navy` → `--sv-dark` (#272635).
10. Skor halkası JS'te (`paintScore`, sv.js): 40-70 aralığı rengi `#ff9f1a` → `#ec8a27`. **(JS değişikliği)**
11. Favicon (`assets/img/favicon.svg`): zemin `#695de9`'a çevrilir.
12. Modal focus/`input:focus` çerçeveleri turkuaz → mor.

### 10.3 Renk dışı geliştirmeler (öncelik 2 — detaylı incelemede görülen)

13. **Destekle etiketi:** karttaki kalp butonuna "Destekle" metni ekle (orijinalde "destek" ifadesi kullanılıyor; şu an yalnız ikon+sayı — sayı+"Destekle" olmalı). **(sv.js cardHTML)**
14. **Seed tema güncellemesi:** Orijinal sayfadaki güncel şikayetlerin baskın teması "bilgim dışında / yetkisiz işlem-çekim" türü bireysel mağduriyetler (tema düzeyinde gözlem; metin kopyalanmadı ve KOPYALANMAYACAK). Seed'e 2-3 adet TAMAMEN KURGU "yetkisiz işlem" temalı şikayet ekle/dönüştür (ör. kurgu: "Bilgim dışında üyelik ücreti yansıtılmış", "Kartımdan onayım olmadan tahsilat yapılmış" gibi kendi yazdığımız metinlerle) — sayfa gerçekçiliği artar. **(server.py SEED_COMPLAINTS)**
15. **Marka bloğuna yıldız satırı (opsiyonel):** "789 değerlendirme" yanına 5'li yıldız göstergesi (~2.8/5 dolu, `#ec8a27`); ucuz ve sayfayı orijinale yaklaştırır.
16. **Görüntülenme ikonu davranışı:** görüntülenme sayısı yalnız detay açılınca artıyor (doğru) ama seed `views` değerleri sabit; sorun değil — değişiklik gerekmez (not).
17. **"Yanıt bekliyor" rozet metni** orijinalde farklı olabilir; nötr kalması kabul (değişiklik gerekmez).

### 10.4 Kabul kriterleri (2. tur sonu)
- [ ] Header beyaz; logo koyu+mor; arama kutusu açık gri zeminli; hiçbir yerde turkuaz `#14b9c6` kalmadı (CSS'te grep ile doğrula).
- [ ] Tüm CTA/etkileşim vurguları `#695de9` ailesinde; turuncu yalnız skor halkasında (`#ec8a27`).
- [ ] "Çözüldü" `#3ad08f` ailesinde; sayfa zemini `#f4f5f9`; metin/footer `#272635`.
- [ ] Favicon mor; flash/chip/destekle mor ailede.
- [ ] Destekle butonunda "Destekle" etiketi var.
- [ ] Seed'de 2-3 kurgu "yetkisiz işlem" temalı şikayet var (`data/complaints.json` silinip yeniden üretilerek test edilir).
- [ ] Şikayet ekleme + yorum + kalıcılık akışları hâlâ çalışıyor (regresyon: Bölüm 8 kriterlerinden hızlı geçiş); konsol hatasız; 375px/1100px düzen sağlam.
