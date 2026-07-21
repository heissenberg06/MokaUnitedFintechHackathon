#!/usr/bin/env python3
"""Moka Müşteri Zeka Motoru — şikayet verisinden yönetici içgörüsü üretir.

İki katman:
  1) Deterministik çekirdek (yalnız stdlib): kategorize, aciliyet, duygu, trend,
     segment, kümeleme, benchmark, öneri. HER ZAMAN çalışır, ağ/gerektirmez.
  2) Opsiyonel yerel LLM (Ollama / qwen2.5): yönetici özeti anlatısı üretir.
     Ollama kapalıysa şablon özete düşer (graceful fallback).

Tüm veri KURGUDUR; benchmark rakip değerleri temsilîdir.
"""
import html
import json
import math
import re
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta

# ----------------------------------------------------------------------------
# TR metin yardımcıları
# ----------------------------------------------------------------------------
def tr_lower(s):
    return (s.replace('İ', 'i').replace('I', 'ı').replace('Ş', 'ş').replace('Ç', 'ç')
             .replace('Ğ', 'ğ').replace('Ü', 'ü').replace('Ö', 'ö').lower())

_WORD_RE = re.compile(r"[0-9a-zçğıöşü]+")
# Türkçe durak kelimeler (kümeleme/benzerlikte gürültüyü azaltır)
STOP = set("""ve veya ama fakat ile bir bu şu o da de ki mi mu için gibi çok daha en
ben sen biz siz onlar bana sana ona hiç her ise ya ne nasıl neden çünkü ancak
olarak oldu olan olması var yok değil beni seni bizi sizi""".split())

def norm(s):
    return html.unescape(str(s or ""))

def tokens(s):
    return [w for w in _WORD_RE.findall(tr_lower(norm(s))) if len(w) > 2 and w not in STOP]

# ----------------------------------------------------------------------------
# Kategori taksonomisi (anahtar kelime -> kategori)
# ----------------------------------------------------------------------------
CATEGORIES = {
    "Yetkisiz İşlem": ["yetkisiz", "onayım olmadan", "onayim olmadan", "tanımadığım",
                        "tanimadigim", "bilgim dışında", "bilgim disinda", "izinsiz",
                        "başlatmadığım", "baslatmadigim"],
    "Para İadesi": ["iade", "geri ödeme", "geri odeme", "yansımadı", "yansimadi",
                    "iade edilmedi", "para iadem", "geri almak"],
    "Komisyon & Ücret": ["komisyon", "ücret", "ucret", "kesinti", "kesildi", "hizmet bedeli",
                          "tahsilat", "üyelik ücreti", "uyelik ucreti", "fiyat"],
    "POS & Teslimat": ["pos cihaz", "cihaz", "teslim", "kargo", "fiziki pos"],
    "Sanal POS & Başvuru": ["sanal pos", "başvuru", "basvuru", "onaylan", "sonuçlanmadı",
                            "sonuclanmadi"],
    "Müşteri Hizmetleri": ["müşteri hizmet", "musteri hizmet", "çağrı merkez", "cagri merkez",
                           "ulaşamıyorum", "ulasamiyorum", "canlı destek", "canli destek",
                           "destek", "hat düş", "geri dönüş yok"],
    "Uygulama & Teknik": ["uygulama", "giriş yapamıyorum", "giris yapamiyorum", "hata veriyor",
                          "kapanıyor", "kapaniyor", "güncelleme", "guncelleme", "çöküyor",
                          "cokuyor", "sistem"],
    "Ödeme Linki": ["link", "ödeme sayfası", "odeme sayfasi", "ödeme linki", "odeme linki"],
    "Dijital Cüzdan": ["cüzdan", "cuzdan", "bakiye", "aktarılmadı", "aktarilmadi", "askıda"],
    "Hesap & Doğrulama": ["hesap doğrulama", "hesap dogrulama", "evrak", "belge", "inceleniyor",
                          "onaylanmadı", "onaylanmadi", "aktifleş"],
    "Mutabakat & Rapor": ["mutabakat", "gün sonu", "gun sonu", "rapor", "eksik işlem",
                          "tutmuyor"],
    "Sözleşme & İptal": ["sözleşme", "sozlesme", "iptal", "fesih", "feshet"],
}

# Aciliyet sinyalleri (kelime -> ağırlık)
URGENCY_SIGNALS = {
    "acil": 3, "yetkisiz": 3, "onayım olmadan": 3, "onayim olmadan": 3,
    "tanımadığım": 3, "tanimadigim": 3, "bilgim dışında": 3, "izinsiz": 3,
    "dolandır": 3, "dolandir": 3, "askıda": 2, "askida": 2,
    "günlerdir": 2, "gunlerdir": 2, "haftalardır": 2, "haftalardir": 2,
    "gündür": 2, "gundur": 2, "iade": 2, "para": 1, "kesinti": 2, "kesildi": 2,
    "ulaşamıyorum": 2, "ulasamiyorum": 2, "satışlarımı": 2, "satislarimi": 2,
    "çöküyor": 1, "hata": 1, "gecikme": 1, "mağdur": 2, "magdur": 2,
}

# Duygu sözlüğü
NEG_WORDS = ["mağdur", "magdur", "rezalet", "kötü", "kotu", "berbat", "yetersiz",
             "çözülmüyor", "cozulmuyor", "bıktım", "biktim", "hata", "sorun", "şikayet",
             "gecikme", "ulaşamıyorum", "ulasamiyorum", "dolandır", "dolandir", "kayıp",
             "yansımadı", "yansimadi", "askıda", "tutmuyor", "yüksek", "yuksek"]
POS_WORDS = ["teşekkür", "tesekkur", "çözüldü", "cozuldu", "memnun", "hızlı", "hizli",
             "yardımcı", "yardimci", "ilgili", "harika"]

# Müşteri segmenti ipuçları
SEGMENTS = {
    "Esnaf / İşletme": ["pos", "işyeri", "isyeri", "iş yeri", "komisyon", "satış", "satis",
                        "müşterilerime", "musterilerime", "tahsilat", "link", "gün sonu",
                        "mutabakat", "sanal pos"],
    "Bireysel Kullanıcı": ["kart", "uygulama", "cüzdan", "cuzdan", "bakiye", "üyelik",
                           "uyelik", "hesabımdan", "hesabimdan"],
    "İş Ortağı / Kurumsal": ["sözleşme", "sozlesme", "entegrasyon", "api", "fesih",
                             "kurumsal", "mutabakat"],
}

# Kategoriye özel yönetici önerileri
RECOMMENDATIONS = {
    "Yetkisiz İşlem": "Yetkisiz işlem itirazları için 24 saat içinde geçici iade + otomatik "
                      "fraud incelemesi akışı kurulmalı; bu şikayet tipi güven puanını en çok düşürüyor.",
    "Para İadesi": "İade sürecine görünür durum takibi (SLA sayacı) eklenmeli; müşteriye "
                   "banka yansıma süresi proaktif bildirilerek 'bilgi alamıyorum' şikayetleri kesilmeli.",
    "Komisyon & Ücret": "Kesinti kalemleri panelde şeffaf dökümle gösterilmeli; sözleşme dışı "
                        "algılanan ücretler için tek tık itiraz butonu eklenmeli.",
    "POS & Teslimat": "POS teslim sürecine kargo takip entegrasyonu + gerçekçi teslim tarihi "
                     "taahhüdü eklenmeli; gecikmede otomatik bilgilendirme gitmeli.",
    "Sanal POS & Başvuru": "Başvuru durumu için self-servis takip ekranı ve gün bazlı SLA "
                          "uyarısı kurulmalı; 3 iş günü taahhüdü sistemsel olarak izlenmeli.",
    "Müşteri Hizmetleri": "Çağrı merkezi bekleme süresi ve hat düşme oranı ölçülüp SLA'ya "
                         "bağlanmalı; canlı destekte geri arama (callback) opsiyonu açılmalı.",
    "Uygulama & Teknik": "Son sürüm çökme/giriş hatası için acil hotfix ve sürüm sağlığı "
                        "izleme (crash rate) paneli devreye alınmalı.",
    "Ödeme Linki": "Ödeme sayfasının cihaz/tarayıcı uyumluluğu test matrisi genişletilmeli; "
                  "link hatası doğrudan satış kaybı yarattığı için P1 önceliklendirilmeli.",
    "Dijital Cüzdan": "Cüzdan→banka aktarımında 'askıda kalan' işlemler için otomatik "
                     "mutabakat ve iade job'u kurulmalı.",
    "Hesap & Doğrulama": "Evrak onay süreci için tahmini süre göstergesi ve eksik belge "
                        "otomatik bildirimi eklenerek 'günlerce inceleniyor' durumu bitirilmeli.",
    "Mutabakat & Rapor": "Gün sonu mutabakat farkları için otomatik uzlaştırma raporu ve "
                        "eksik işlem alarmı geliştirilmeli.",
    "Sözleşme & İptal": "Panelde self-servis sözleşme iptali akışı açılmalı; iptal "
                       "sürtünmesi elde tutma yerine güven kaybına yol açıyor.",
    "Diğer": "Bu başlıktaki şikayetler manuel gözden geçirilmeli; belirgin bir kök neden "
             "kümesi tespit edilmedi.",
}

# Kategori -> sorumlu iç ekip (otomatik yönlendirme/triage için)
TEAM_ROUTING = {
    "Yetkisiz İşlem": "Güvenlik & Fraud Ekibi",
    "Para İadesi": "Finans & Ödemeler Ekibi",
    "Komisyon & Ücret": "Finans & Ödemeler Ekibi",
    "POS & Teslimat": "Operasyon & Lojistik Ekibi",
    "Sanal POS & Başvuru": "Satış & Onboarding Ekibi",
    "Müşteri Hizmetleri": "Müşteri Deneyimi Ekibi",
    "Uygulama & Teknik": "Ürün & Mühendislik Ekibi",
    "Ödeme Linki": "Ürün & Mühendislik Ekibi",
    "Dijital Cüzdan": "Finans & Ödemeler Ekibi",
    "Hesap & Doğrulama": "Uyum & Doğrulama (KYC) Ekibi",
    "Mutabakat & Rapor": "Finans & Ödemeler Ekibi",
    "Sözleşme & İptal": "Hukuk & Sözleşme Ekibi",
    "Diğer": "Müşteri Deneyimi Ekibi",
}

# Benchmark — temsilî rakip değerleri (KURGU)
BENCHMARK_PEERS = {"Sektör Ort.": 71, "Rakip A": 85, "Rakip B": 72}

# Sahtekarlık ağı tespiti: aynı işyerinde, kısa bir zaman penceresinde,
# farklı kullanıcılardan gelen "Yetkisiz İşlem" şikayetleri organize bir
# saldırı/güvenlik açığı sinyali olabilir.
FRAUD_RING_CATEGORY = "Yetkisiz İşlem"
FRAUD_RING_WINDOW_HOURS = 48
FRAUD_RING_MIN_COUNT = 3

# ----------------------------------------------------------------------------
# Çekirdek analiz
# ----------------------------------------------------------------------------
def _parse_dt(s):
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def categorize(text):
    low = tr_lower(norm(text))
    best, hits = "Diğer", 0
    for cat, kws in CATEGORIES.items():
        c = sum(1 for kw in kws if kw in low)
        if c > hits:
            best, hits = cat, c
    return best

def urgency_score(title, body, status):
    low = tr_lower(norm(title + " " + body))
    score = 3.0
    for sig, w in URGENCY_SIGNALS.items():
        if sig in low:
            score += w
    # sayı + "gün/gündür" birleşimi (ör. "10 gündür") ekstra ağırlık
    if re.search(r"\d+\s*g[üu]n", low):
        score += 2
    if status == "cozuldu":
        score -= 2  # çözülmüşse aciliyet düşer
    return max(1, min(10, round(score)))

def sentiment(text):
    low = tr_lower(norm(text))
    neg = sum(1 for w in NEG_WORDS if w in low)
    pos = sum(1 for w in POS_WORDS if w in low)
    net = pos - neg
    if net <= -2:
        return "Öfkeli", net
    if net < 0:
        return "Olumsuz", net
    if net == 0:
        return "Nötr", net
    return "Olumlu", net

def segment_of(text):
    low = tr_lower(norm(text))
    best, hits = "Bireysel Kullanıcı", 0
    for seg, kws in SEGMENTS.items():
        c = sum(1 for kw in kws if kw in low)
        if c > hits:
            best, hits = seg, c
    return best

def _tfidf_vectors(docs):
    """Basit TF-IDF (stdlib). docs: token listeleri. -> vektör (dict) listesi + idf."""
    N = len(docs)
    df = defaultdict(int)
    for d in docs:
        for t in set(d):
            df[t] += 1
    idf = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    vecs = []
    for d in docs:
        tf = defaultdict(int)
        for t in d:
            tf[t] += 1
        v = {t: (tf[t] / len(d)) * idf[t] for t in tf} if d else {}
        vecs.append(v)
    return vecs

def _cosine(a, b):
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(x * x for x in a.values()))
    nb = math.sqrt(sum(x * x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0

def find_clusters(complaints, threshold=0.15):
    """Benzer şikayetleri kümele (yakın-kopya / tekrar eden sorun tespiti)."""
    docs = [tokens(c.get('title', '') + " " + c.get('body', '')) for c in complaints]
    vecs = _tfidf_vectors(docs)
    n = len(complaints)
    seen = [False] * n
    clusters = []
    for i in range(n):
        if seen[i]:
            continue
        members = [i]
        seen[i] = True
        for j in range(i + 1, n):
            if not seen[j] and _cosine(vecs[i], vecs[j]) >= threshold:
                members.append(j)
                seen[j] = True
        if len(members) >= 2:
            clusters.append([complaints[k] for k in members])
    clusters.sort(key=len, reverse=True)
    return clusters

def detect_fraud_rings(enriched, window_hours=FRAUD_RING_WINDOW_HOURS,
                        min_count=FRAUD_RING_MIN_COUNT):
    """Aynı (normalize edilmiş) işyeri adı altında `window_hours` içinde en az
    `min_count` farklı 'Yetkisiz İşlem' şikayeti varsa, olası bir sahtekarlık
    ağı/saldırısı olarak raporla. Tek bir müşterinin tekrarlı şikayeti değil,
    FARKLI şikayetlerin aynı işyerinde kümelenmesi aranır."""
    by_merchant = defaultdict(list)
    for e in enriched:
        merchant = norm(e.get('merchant') or '').strip()
        if not merchant or e['_cat'] != FRAUD_RING_CATEGORY or e['_dt'] is None:
            continue
        by_merchant[tr_lower(merchant)].append(e)

    rings = []
    for items in by_merchant.values():
        items.sort(key=lambda x: x['_dt'])
        n = len(items)
        for i in range(n):
            window_end = items[i]['_dt'] + timedelta(hours=window_hours)
            group = [x for x in items[i:] if x['_dt'] <= window_end]
            if len(group) >= min_count:
                display_name = group[0].get('merchant') or '—'
                rings.append({
                    "merchant": display_name,
                    "count": len(group),
                    "first_at": group[0]['_dt'].replace(microsecond=0).isoformat(),
                    "last_at": group[-1]['_dt'].replace(microsecond=0).isoformat(),
                    "window_hours": window_hours,
                    "sample_titles": [g.get('title', '') for g in group[:4]],
                    "complaint_ids": [g.get('id') for g in group],
                })
                break  # bu işyeri için ilk (en erken) tetiklenen pencereyi raporla
    rings.sort(key=lambda r: r['count'], reverse=True)
    return rings

def hourly_distribution(enriched):
    """24 saatlik şikayet yoğunluğu — hangi saatlerde daha çok şikayet/işlem geliyor
    (grafikte kırmızıyla vurgulanan en yoğun saat + mesai içi/dışı oranı)."""
    buckets = [0] * 24
    for e in enriched:
        if e['_dt'] is not None:
            buckets[e['_dt'].hour] += 1
    total = sum(buckets)
    peak_hour = max(range(24), key=lambda h: buckets[h]) if total else 0
    business = sum(buckets[9:18])  # 09:00-17:59 mesai saatleri
    return {
        "buckets": buckets,
        "peak_hour": peak_hour,
        "peak_count": buckets[peak_hour] if total else 0,
        "business_hours_pct": round(business / total * 100) if total else 0,
        "off_hours_pct": round((total - business) / total * 100) if total else 0,
    }

def merchant_risk_ranking(enriched, ring_keys=None):
    """`merchant` alanı dolu olan tüm şikayetleri işyeri bazında toplayıp
    risk puanına (adet × ortalama aciliyet) göre sıralar; sahtekarlık ağı
    eşiğini geçen işyerleri `is_ring` ile işaretler."""
    ring_keys = ring_keys or set()
    by_merchant = defaultdict(list)
    for e in enriched:
        m = norm(e.get('merchant') or '').strip()
        if m:
            by_merchant[m].append(e)
    rows = []
    for name, items in by_merchant.items():
        avg_urg = round(sum(i['_urg'] for i in items) / len(items), 1)
        rows.append({
            "merchant": name,
            "count": len(items),
            "avg_urgency": avg_urg,
            "pending": sum(1 for i in items if i.get('status') != 'cozuldu'),
            "risk_score": round(len(items) * avg_urg, 1),
            "is_ring": tr_lower(name) in ring_keys,
        })
    rows.sort(key=lambda r: r['risk_score'], reverse=True)
    return rows

def route_to_teams(enriched):
    """Her şikayeti kategorisine göre sorumlu iç ekibe (Güvenlik, Finans, Ürün...)
    yönlendirir; ekip bazında yük (adet, bekleyen, ortalama aciliyet) çıkarır.
    Yükü en ağır ekip (bekleyen × aciliyet) en üstte listelenir."""
    by_team = defaultdict(list)
    for e in enriched:
        team = TEAM_ROUTING.get(e['_cat'], TEAM_ROUTING["Diğer"])
        by_team[team].append(e)
    rows = []
    for team, items in by_team.items():
        cat_counts = defaultdict(int)
        for i in items:
            cat_counts[i['_cat']] += 1
        top_category = max(cat_counts.items(), key=lambda x: x[1])[0]
        pending = sum(1 for i in items if i.get('status') != 'cozuldu')
        avg_urg = round(sum(i['_urg'] for i in items) / len(items), 1)
        samples = sorted(items, key=lambda x: x['_urg'], reverse=True)
        rows.append({
            "team": team,
            "count": len(items),
            "pending": pending,
            "avg_urgency": avg_urg,
            "top_category": top_category,
            "samples": [s.get('title', '') for s in samples[:3]],
        })
    rows.sort(key=lambda r: r['pending'] * r['avg_urgency'], reverse=True)
    return rows

def analyze(data, now=None):
    """Ana giriş: complaints listesi -> tam içgörü sözlüğü."""
    complaints = data.get('complaints', []) if isinstance(data, dict) else data
    now = now or datetime.now()
    total = len(complaints)
    if total == 0:
        return {"kpis": {}, "categories": [], "critical_issues": [], "trend": {},
                "segments": [], "benchmark": {}, "recommendations": [], "clusters": [],
                "fraud_rings": [], "merchant_risk": [], "team_routing": [],
                "hourly": {"buckets": [0] * 24, "peak_hour": 0, "peak_count": 0,
                           "business_hours_pct": 0, "off_hours_pct": 0}}

    solved = sum(1 for c in complaints if c.get('status') == 'cozuldu')
    pending = total - solved
    resolution_rate = round(solved / total * 100)

    # yanıt süresi (çözülmüş + marka yorumu olanlarda)
    resp_hours = []
    for c in complaints:
        cdt = _parse_dt(c.get('createdAt', ''))
        brand = next((cm for cm in c.get('comments', []) if cm.get('isBrand')), None)
        if cdt and brand:
            bdt = _parse_dt(brand.get('createdAt', ''))
            if bdt and bdt >= cdt:
                resp_hours.append((bdt - cdt).total_seconds() / 3600)
    avg_resp = round(sum(resp_hours) / len(resp_hours), 1) if resp_hours else None

    # her şikayete türetilmiş alanlar
    enriched = []
    for c in complaints:
        cat = categorize(c.get('title', '') + " " + c.get('body', ''))
        urg = urgency_score(c.get('title', ''), c.get('body', ''), c.get('status', ''))
        sent, snet = sentiment(c.get('title', '') + " " + c.get('body', ''))
        seg = segment_of(c.get('title', '') + " " + c.get('body', ''))
        enriched.append({**c, "_cat": cat, "_urg": urg, "_sent": sent, "_seg": seg,
                         "_dt": _parse_dt(c.get('createdAt', ''))})

    # kategori dağılımı
    cat_map = defaultdict(list)
    for e in enriched:
        cat_map[e['_cat']].append(e)
    categories = []
    for cat, items in cat_map.items():
        categories.append({
            "name": cat, "count": len(items),
            "share": round(len(items) / total * 100),
            "avg_urgency": round(sum(i['_urg'] for i in items) / len(items), 1),
            "pending": sum(1 for i in items if i.get('status') != 'cozuldu'),
            "solved": sum(1 for i in items if i.get('status') == 'cozuldu'),
        })
    categories.sort(key=lambda x: (x['count'], x['avg_urgency']), reverse=True)

    # trend: son 7 gün vs önceki 7 gün (kategori bazında % değişim)
    def in_window(dt, lo, hi):
        return dt is not None and lo <= dt < hi
    w_now = now
    w1_lo, w1_hi = w_now - timedelta(days=7), w_now + timedelta(seconds=1)
    w0_lo, w0_hi = w_now - timedelta(days=14), w_now - timedelta(days=7)
    trend_cats = []
    for cat, items in cat_map.items():
        last = sum(1 for i in items if in_window(i['_dt'], w1_lo, w1_hi))
        prev = sum(1 for i in items if in_window(i['_dt'], w0_lo, w0_hi))
        if last == 0 and prev == 0:
            continue
        if prev == 0:
            pct = 100 * last  # sıfırdan artış
        else:
            pct = round((last - prev) / prev * 100)
        trend_cats.append({"name": cat, "last": last, "prev": prev, "pct": pct})
    trend_cats.sort(key=lambda x: x['pct'], reverse=True)

    # zaman serisi (haftalık kova, son 4 hafta) — grafik için
    buckets = []
    for wk in range(3, -1, -1):
        lo = w_now - timedelta(days=7 * (wk + 1))
        hi = w_now - timedelta(days=7 * wk)
        cnt = sum(1 for e in enriched if in_window(e['_dt'], lo, hi))
        buckets.append({"label": f"{wk*7 or 0}-{(wk+1)*7} gün", "count": cnt})
    buckets.reverse()  # eskiden yeniye

    # kritik sorunlar: (adet * ort. aciliyet) puanına göre
    trend_by_cat = {t['name']: t for t in trend_cats}
    critical = []
    for c in categories:
        score = c['count'] * c['avg_urgency']
        tr = trend_by_cat.get(c['name'])
        samples = [tr_ for tr_ in cat_map[c['name']]]
        samples.sort(key=lambda x: x['_urg'], reverse=True)
        critical.append({
            "issue": c['name'],
            "count": c['count'],
            "urgency": c['avg_urgency'],
            "pending": c['pending'],
            "score": round(score, 1),
            "trend_pct": tr['pct'] if tr else 0,
            "samples": [s.get('title', '') for s in samples[:3]],
            "action": RECOMMENDATIONS.get(c['name'], RECOMMENDATIONS["Diğer"]),
        })
    critical.sort(key=lambda x: x['score'], reverse=True)

    # segmentler
    seg_map = defaultdict(list)
    for e in enriched:
        seg_map[e['_seg']].append(e)
    segments = []
    for seg, items in seg_map.items():
        top_cat = defaultdict(int)
        for i in items:
            top_cat[i['_cat']] += 1
        tc = max(top_cat.items(), key=lambda x: x[1])[0] if top_cat else "-"
        segments.append({
            "name": seg, "count": len(items),
            "share": round(len(items) / total * 100),
            "top_issue": tc,
        })
    segments.sort(key=lambda x: x['count'], reverse=True)

    # duygu dağılımı
    sent_map = defaultdict(int)
    for e in enriched:
        sent_map[e['_sent']] += 1

    # sahtekarlık ağı: aynı işyerinde, kısa sürede biriken farklı şikayetler
    fraud_rings = detect_fraud_rings(enriched)
    ring_keys = {tr_lower(r['merchant']) for r in fraud_rings}

    # işyeri risk sıralaması + saatlik yoğunluk
    merchant_risk = merchant_risk_ranking(enriched, ring_keys)
    hourly = hourly_distribution(enriched)

    # şikayetlerin ilgili iç ekiplere otomatik yönlendirilmesi
    team_routing = route_to_teams(enriched)

    # kümeler (tekrar eden sorunlar)
    clusters_raw = find_clusters(enriched)
    clusters = [{
        "size": len(cl),
        "category": cl[0]['_cat'],
        "titles": [m.get('title', '') for m in cl[:4]],
    } for cl in clusters_raw[:5]]

    # güven puanı: çözüm oranı + düşük aciliyet karışımı (0-100)
    avg_urg_all = sum(e['_urg'] for e in enriched) / total
    trust = round(resolution_rate * 0.6 + (10 - avg_urg_all) * 10 * 0.4)
    trust = max(0, min(100, trust))

    # öneriler (en kritik ilk 5)
    recommendations = [{"category": c['issue'], "text": c['action']} for c in critical[:5]]

    return {
        "generated_at": now.replace(microsecond=0).isoformat(),
        "kpis": {
            "total": total, "solved": solved, "pending": pending,
            "resolution_rate": resolution_rate,
            "avg_response_hours": avg_resp,
            "trust_score": trust,
            "total_supports": sum(int(c.get('supports', 0)) for c in complaints),
            "total_views": sum(int(c.get('views', 0)) for c in complaints),
        },
        "categories": categories,
        "critical_issues": critical,
        "emerging": trend_cats[:5],
        "timeseries": buckets,
        "segments": segments,
        "sentiment": [{"name": k, "count": v} for k, v in
                      sorted(sent_map.items(), key=lambda x: -x[1])],
        "benchmark": {"moka": resolution_rate, "peers": BENCHMARK_PEERS},
        "recommendations": recommendations,
        "clusters": clusters,
        "fraud_rings": fraud_rings,
        "merchant_risk": merchant_risk,
        "hourly": hourly,
        "team_routing": team_routing,
    }

# ----------------------------------------------------------------------------
# LLM katmanı (Ollama / yerel) — opsiyonel, fallback'li
# ----------------------------------------------------------------------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

def _template_summary(ins):
    k = ins.get('kpis', {})
    crit = ins.get('critical_issues', [])
    top = crit[0]['issue'] if crit else "-"
    emg = ins.get('emerging', [])
    rising = ", ".join(f"{e['name']} (%{e['pct']:+d})" for e in emg[:2]) if emg else "belirgin trend yok"
    return (
        f"Bu dönem toplam {k.get('total', 0)} şikayet alındı; çözüm oranı %{k.get('resolution_rate', 0)}, "
        f"güven puanı {k.get('trust_score', 0)}/100. En kritik başlık '{top}'. "
        f"Yükselen konular: {rising}. Ortalama yanıt süresi "
        f"{k.get('avg_response_hours', '—')} saat. Öncelik: en yüksek aciliyet puanlı "
        f"başlıkların SLA'ya bağlanması."
    )

def llm_summary(ins, timeout=90):
    """Ollama ile Türkçe yönetici özeti üret. Başarısızsa şablon özete düş."""
    facts = {
        "toplam": ins['kpis'].get('total'),
        "cozum_orani": ins['kpis'].get('resolution_rate'),
        "guven_puani": ins['kpis'].get('trust_score'),
        "ort_yanit_saat": ins['kpis'].get('avg_response_hours'),
        "kritik_basliklar": [c['issue'] for c in ins.get('critical_issues', [])[:3]],
        "yukselen": [f"{e['name']} %{e['pct']:+d}" for e in ins.get('emerging', [])[:3]],
        "segmentler": [f"{s['name']} %{s['share']}" for s in ins.get('segments', [])],
    }
    prompt = (
        "Sen bir fintech şirketinin müşteri deneyimi analistisin. Aşağıdaki JSON verilere "
        "dayanarak yöneticiye 3-4 cümlelik, net ve profesyonel bir Türkçe durum özeti yaz. "
        "Sadece verilenlere dayan, uydurma sayı ekleme. Madde işareti kullanma, düz paragraf yaz.\n\n"
        f"VERİ:\n{json.dumps(facts, ensure_ascii=False)}\n\nÖZET:"
    )
    payload = json.dumps({
        "model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.3, "num_predict": 220},
    }).encode('utf-8')
    try:
        req = urllib.request.Request(OLLAMA_URL, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.loads(r.read().decode('utf-8'))
        text = (out.get('response') or '').strip()
        if len(text) < 40:
            return {"text": _template_summary(ins), "source": "template"}
        return {"text": text, "source": OLLAMA_MODEL}
    except Exception as e:
        return {"text": _template_summary(ins), "source": "template", "error": str(e)[:120]}


if __name__ == '__main__':
    # hızlı elle test
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'data', 'complaints.json'), encoding='utf-8') as f:
        d = json.load(f)
    ins = analyze(d)
    print(json.dumps(ins, ensure_ascii=False, indent=2)[:2000])
    print("\n--- LLM özet ---")
    print(llm_summary(ins))
