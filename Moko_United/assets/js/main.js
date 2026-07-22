/* ============================================================
   Etkileşimler: loader, mobil menü, accordion, sayaç,
   reveal, ofis sekmeleri, form, referans marquee klonu, arama
   ============================================================ */

// Loader kapat
window.addEventListener('load', () => {
  const l = document.getElementById('loader');
  if (l) setTimeout(() => l.classList.add('hidden'), 300);
});

function initInteractions() {
  // --- Mobil menü ---
  const burger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (burger && mobileMenu) {
    burger.addEventListener('click', () => {
      burger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });
    mobileMenu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      burger.classList.remove('active');
      mobileMenu.classList.remove('active');
      document.body.style.overflow = '';
    }));
  }

  // --- Arama overlay ---
  initSearch();

  // --- Çerez bandı ---
  initCookieBanner();

  // --- Biyografi modalı (kurumsal yönetim) ---
  initBioModal();

  // --- Yasal belge modalı ---
  initDocModal();

  // --- Ofis sekmeleri (footer) ---
  document.querySelectorAll('.office-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const key = tab.dataset.office;
      document.querySelectorAll('.office-tab').forEach(t => t.classList.toggle('active', t === tab));
      document.querySelectorAll('.office-pane').forEach(p => p.classList.toggle('active', p.dataset.office === key));
    });
  });
}

// --- Arama overlay: istemci tarafı sayfa araması ---
const SEARCH_INDEX = [
  { t: 'Ana Sayfa', u: 'index.html', k: 'anasayfa home moka united' },
  { t: 'Hakkımızda', u: 'hakkimizda.html', k: 'hakkimizda kurumsal' },
  { t: 'Hikayemiz', u: 'hikayemiz.html', k: 'hikaye tarihce zaman cizelgesi' },
  { t: 'Kurumsal Yönetim', u: 'kurumsal-yonetim.html', k: 'yonetim kadro yonetim kurulu' },
  { t: "Moka United'ta Kariyer", u: 'kariyer.html', k: 'kariyer is ilani basvuru pozisyon' },
  { t: 'İştirakler', u: 'istirakler.html', k: 'istirak ruut turan up enerji smartup' },
  { t: 'Ürünler', u: 'urunler.html', k: 'urun cozum' },
  { t: 'Kart Çözümleri', u: 'kart-cozumleri.html', k: 'kart fiziksel sehir karti odeme karti' },
  { t: 'Cüzdan Çözümleri', u: 'cuzdan-cozumleri.html', k: 'cuzdan dijital e-para wallet' },
  { t: 'Para Transferi', u: 'para-transferi.html', k: 'para transfer havale eft uluslararasi' },
  { t: 'Akıllı Kasa', u: 'akilli-kasa.html', k: 'akilli kasa nakit' },
  { t: 'Kiosk', u: 'kiosk.html', k: 'kiosk self servis' },
  { t: 'POS Çözümleri', u: 'pos-cozumleri.html', k: 'pos odeme' },
  { t: 'Sanal POS', u: 'sanal-pos.html', k: 'sanal pos online odeme e-ticaret' },
  { t: 'Fiziki POS', u: 'fiziki-pos.html', k: 'fiziki pos cihaz magaza' },
  { t: 'Linkle Tahsilat', u: 'linkle-tahsilat.html', k: 'link tahsilat odeme linki' },
  { t: 'İletişim', u: 'iletisim.html', k: 'iletisim adres telefon ofis' },
  { t: 'Hemen Başvurun', u: 'basvuru.html', k: 'basvuru pos basvuru' },
  { t: 'Panel Girişi', u: 'panel-giris.html', k: 'panel giris login' },
];
function trLower(s) { return s.replace(/İ/g, 'i').replace(/I/g, 'i').replace(/Ş/g, 's').replace(/Ç/g, 'c').replace(/Ğ/g, 'g').replace(/Ü/g, 'u').replace(/Ö/g, 'o').toLowerCase(); }
function initSearch() {
  const toggle = document.getElementById('searchToggle');
  const overlay = document.getElementById('searchOverlay');
  const input = document.getElementById('searchInput');
  const results = document.getElementById('searchResults');
  const closeBtn = document.getElementById('searchClose');
  const form = document.getElementById('searchForm');
  if (!toggle || !overlay) return;
  const open = () => { overlay.classList.add('active'); document.body.style.overflow = 'hidden'; setTimeout(() => input.focus(), 250); render(''); };
  const close = () => { overlay.classList.remove('active'); document.body.style.overflow = ''; input.value = ''; };
  function render(q) {
    const nq = trLower(q.trim());
    const list = !nq ? SEARCH_INDEX : SEARCH_INDEX.filter(i => trLower(i.t).includes(nq) || i.k.includes(nq));
    results.innerHTML = list.length
      ? list.map(i => `<a href="${i.u}">${i.t}</a>`).join('')
      : '<span class="no-result">Sonuç bulunamadı.</span>';
  }
  toggle.addEventListener('click', open);
  const mobileToggle = document.getElementById('mobileSearchToggle');
  if (mobileToggle) mobileToggle.addEventListener('click', () => {
    const mm = document.getElementById('mobileMenu');
    const burger = document.getElementById('hamburger');
    if (mm) mm.classList.remove('active');
    if (burger) burger.classList.remove('active');
    open();
  });
  if (closeBtn) closeBtn.addEventListener('click', close);
  if (input) input.addEventListener('input', () => render(input.value));
  if (form) form.addEventListener('submit', (e) => { e.preventDefault(); const first = results.querySelector('a'); if (first) window.location.href = first.getAttribute('href'); });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && overlay.classList.contains('active')) close(); });
}

// --- Çerez bandı (Kabul / Reddet / Ayarlar) ---
function initCookieBanner() {
  const banner = document.getElementById('cookieBanner');
  if (!banner) return;
  if (localStorage.getItem('mu-cookie-consent')) return;
  const settings = banner.querySelector('#cookieSettings');
  const analytics = banner.querySelector('[name="analytics"]');
  const marketing = banner.querySelector('[name="marketing"]');
  setTimeout(() => banner.classList.add('show'), 800);
  const save = (prefs) => {
    localStorage.setItem('mu-cookie-consent', JSON.stringify({ necessary: true, ...prefs, ts: Date.now() }));
    banner.classList.remove('show');
  };
  banner.querySelector('.cookie-config').addEventListener('click', () => {
    const open = settings.hasAttribute('hidden');
    if (open) { settings.removeAttribute('hidden'); banner.classList.add('expanded'); }
    else { settings.setAttribute('hidden', ''); banner.classList.remove('expanded'); }
  });
  banner.querySelector('.cookie-accept').addEventListener('click', () => {
    // Ayarlar paneli açıksa kullanıcı tercihini, değilse tümünü kabul et
    if (!settings.hasAttribute('hidden')) save({ analytics: analytics.checked, marketing: marketing.checked });
    else save({ analytics: true, marketing: true });
  });
  banner.querySelector('.cookie-reject').addEventListener('click', () => save({ analytics: false, marketing: false }));
}

// --- Biyografi modalı (kurumsal yönetim kartları) ---
function initBioModal() {
  const modal = document.getElementById('bioModal');
  if (!modal) return;
  const nameEl = document.getElementById('bioName');
  const titleEl = document.getElementById('bioTitle');
  const textEl = document.getElementById('bioText');
  const avatarEl = document.getElementById('bioAvatar');
  const close = () => { modal.classList.remove('active'); document.body.style.overflow = ''; };
  document.querySelectorAll('.team-card').forEach(card => {
    card.addEventListener('click', () => {
      nameEl.textContent = card.dataset.name;
      titleEl.textContent = card.dataset.title;
      textEl.textContent = card.dataset.bio;
      avatarEl.textContent = card.querySelector('.avatar')?.textContent || '';
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });
  modal.querySelector('.bio-close').addEventListener('click', close);
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.classList.contains('active')) close(); });
}

// --- Yasal belge modalı (örnek belge) ---
function initDocModal() {
  const modal = document.getElementById('docModal');
  if (!modal) return;
  const titleEl = document.getElementById('docTitle');
  const close = () => { modal.classList.remove('active'); document.body.style.overflow = ''; };
  document.querySelectorAll('.doc-card[data-doc]').forEach(card => {
    card.addEventListener('click', () => {
      titleEl.textContent = card.dataset.doc;
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });
  modal.querySelector('.bio-close').addEventListener('click', close);
  modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && modal.classList.contains('active')) close(); });
}

// --- Accordion (delege) ---
document.addEventListener('click', (e) => {
  const header = e.target.closest('.accordion-header');
  if (header) {
    const item = header.closest('.accordion-item');
    item.classList.toggle('active');
  }
  const showMore = e.target.closest('.show-more');
  if (showMore) {
    const scope = showMore.closest('.faq, .accordion-wrap') || document;
    scope.querySelectorAll('.accordion-item.hidden-item').forEach(i => i.classList.remove('hidden-item'));
    showMore.closest('.show-more-wrap').style.display = 'none';
  }
});

// --- Reveal on scroll ---
function initReveal() {
  const els = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
    });
  }, { threshold: 0.12 });
  els.forEach(el => io.observe(el));
}

// --- Sayaç animasyonu ---
function initCounters() {
  const nums = document.querySelectorAll('.number[data-target]');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target;
      const target = parseFloat(el.dataset.target);
      const suffix = el.dataset.suffix || '';
      const dur = 1600; const start = performance.now();
      function step(now) {
        const p = Math.min((now - start) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = target % 1 === 0 ? Math.round(target * eased) : (target * eased).toFixed(0);
        el.textContent = val + suffix;
        if (p < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      io.unobserve(el);
    });
  }, { threshold: 0.5 });
  nums.forEach(n => io.observe(n));
}

// --- Referans marquee: içeriği ikiye katla (kesintisiz döngü) ---
function initMarquee() {
  document.querySelectorAll('.marquee-track').forEach(track => {
    track.innerHTML += track.innerHTML;
  });
}

// --- İletişim formu (demo, backend yok) ---
function initContactForm() {
  document.querySelectorAll('.contact-form').forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      form.classList.add('sent');
    });
    // Sadece harf / sadece rakam kısıtı
    form.querySelectorAll('.only-letter').forEach(i =>
      i.addEventListener('input', () => i.value = i.value.replace(/[^A-Za-zğüşıöçĞÜŞİÖÇ\s]/g, '')));
    form.querySelectorAll('.only-number').forEach(i =>
      i.addEventListener('input', () => i.value = i.value.replace(/[^0-9+\s()]/g, '')));
  });
}

// --- Çok adımlı başvuru sihirbazı ---
function initApplyWizard() {
  const wizard = document.getElementById('applyWizard');
  const form = document.getElementById('applyForm');
  if (!wizard || !form) return;
  const steps = [...form.querySelectorAll('.form-step')];
  const progress = [...wizard.querySelectorAll('.wp-step')];
  let current = 0;

  const SUMMARY = [
    ['İşletme Türü', 'BizType'], ['İşletme / Unvan', 'Company'], ['Sektör', 'Sector'],
    ['Vergi / TC No', 'TaxNo'], ['Tahmini Aylık Ciro', 'Turnover'],
    ['Yetkili', ['FirstName', 'LastName']], ['Telefon', 'Phone'], ['E-Posta', 'Email'],
    ['Şehir', ['City', 'District']]
  ];

  function show(i) {
    steps.forEach((s, idx) => s.classList.toggle('active', idx === i));
    progress.forEach((p, idx) => {
      p.classList.toggle('active', idx === i);
      p.classList.toggle('done', idx < i);
    });
    current = i;
    wizard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function validateStep(i) {
    const fields = steps[i].querySelectorAll('input, select, textarea');
    for (const f of fields) {
      if (f.type === 'radio') {
        const group = steps[i].querySelectorAll(`[name="${f.name}"]`);
        if (f.required && ![...group].some(r => r.checked)) { f.reportValidity(); return false; }
      } else if (!f.checkValidity()) { f.reportValidity(); return false; }
    }
    // 3. adımda en az bir ürün seçili olmalı
    if (steps[i].dataset.step === '3') {
      const anyProduct = steps[i].querySelectorAll('[name="Product"]:checked').length > 0;
      if (!anyProduct) { alert('Lütfen en az bir çözüm seçin.'); return false; }
    }
    return true;
  }

  function fieldVal(key) {
    if (Array.isArray(key)) return key.map(fieldVal).filter(Boolean).join(' ');
    const el = form.elements[key];
    if (!el) return '';
    if (el.length && el[0] && el[0].type === 'radio') {
      const c = [...el].find(r => r.checked); return c ? c.value : '';
    }
    return el.value || '';
  }

  function buildSummary() {
    const box = document.getElementById('applySummary');
    let rows = SUMMARY.map(([label, key]) => {
      const v = fieldVal(key);
      return v ? `<div class="summary-row"><span class="sr-label">${label}</span><span class="sr-val">${v}</span></div>` : '';
    }).join('');
    const products = [...form.querySelectorAll('[name="Product"]:checked')].map(p => p.value).join(', ');
    if (products) rows += `<div class="summary-row"><span class="sr-label">Seçilen Çözümler</span><span class="sr-val">${products}</span></div>`;
    box.innerHTML = rows;
  }

  wizard.querySelectorAll('.wz-next').forEach(btn => btn.addEventListener('click', () => {
    if (!validateStep(current)) return;
    if (current + 1 === steps.length - 1) buildSummary();
    show(current + 1);
  }));
  wizard.querySelectorAll('.wz-prev').forEach(btn => btn.addEventListener('click', () => show(current - 1)));

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!validateStep(current)) return;
    wizard.classList.add('completed');
    document.getElementById('applySuccess').classList.add('show');
    window.scrollTo({ top: wizard.offsetTop - 80, behavior: 'smooth' });
  });

  // harf/rakam kısıtları
  form.querySelectorAll('.only-letter').forEach(i =>
    i.addEventListener('input', () => i.value = i.value.replace(/[^A-Za-zğüşıöçĞÜŞİÖÇ\s]/g, '')));
  form.querySelectorAll('.only-number').forEach(i =>
    i.addEventListener('input', () => i.value = i.value.replace(/[^0-9+\s()]/g, '')));
}

document.addEventListener('components:ready', () => {
  initInteractions();
});

// --- İtiraz / İşlem Sorgulama sihirbazı ---
// İşlem eşleştirme (mock veri) client'ta kalır; rate-limit, itiraz oluşturma (dosya yükleme dahil)
// ve durum sorgulama gerçek backend'e (itiraz_server.py, IP bazlı brute-force koruması) bağlıdır.
// Prod'da nginx aynı origin üzerinden /api/itiraz/'ı proxy'lediği için varsayılan boş (relative) bırakılır.
// Yerelde ayrı port üzerinden test etmek gerekirse: window.MOKA_ITIRAZ_API_URL = 'http://localhost:8757'
const ITIRAZ_API = window.MOKA_ITIRAZ_API_URL || '';

// ---- İtiraz: paylaşılan takip + kalıcılık yardımcıları (hem oluşturma hem durum sorgu sayfası kullanır) ----
// Not: tam itiraz kaydı artık backend'de saklanır; localStorage yalnızca "bu cihazda görüntülenen
// işlem numaraları" kısayol listesi için kullanılır (durum sorgulama sayfasında hızlı erişim).
function mokaRememberCaseId(id) {
  try {
    const ids = JSON.parse(localStorage.getItem('moka-dispute-ids') || '[]');
    const next = [id, ...ids.filter(x => x !== id)].slice(0, 8);
    localStorage.setItem('moka-dispute-ids', JSON.stringify(next));
  } catch (e) { /* yut */ }
}
function mokaRecentCaseIds() {
  try { return JSON.parse(localStorage.getItem('moka-dispute-ids') || '[]'); } catch (e) { return []; }
}

const MOKA_TRACK_STAGES = [
  { t: 'Talep Alındı', d: 'İtiraz talebiniz sisteme kaydedildi.' },
  { t: 'İnceleniyor', d: 'Uzman ekibimiz işlemi ve belgeleri değerlendiriyor.' },
  { t: 'Bankaya / İşyerine İletildi', d: 'Talebiniz ilgili taraflara resmî olarak iletildi.' },
  { t: 'Sonuçlandırıldı', d: 'Süreç tamamlandı; sonuç tarafınıza bildirildi.' },
];
function mokaRenderTracker(el, stage) {
  if (!el) return;
  el.innerHTML = MOKA_TRACK_STAGES.map((s, i) => {
    const n = i + 1;
    const cls = n < stage ? 'done' : (n === stage ? 'active' : '');
    return `<div class="track-step ${cls}"><span class="track-dot">${n < stage ? '✓' : n}</span>` +
      `<span class="track-info"><strong>${s.t}</strong><span>${s.d}</span></span></div>`;
  }).join('');
}
function mokaDisputeSummary(r) {
  return `
    <div class="summary-row"><span class="sr-label">İtiraz Sebebi</span><span class="sr-val">${r.reason}</span></div>
    <div class="summary-row"><span class="sr-label">İşlem Tipi</span><span class="sr-val">${r.txnType}</span></div>
    <div class="summary-row"><span class="sr-label">İşlem</span><span class="sr-val">${r.merchant} — ${formatTL(r.amount)}</span></div>
    <div class="summary-row"><span class="sr-label">İşlem Referansı</span><span class="sr-val">${r.ref}</span></div>
    <div class="summary-row"><span class="sr-label">Cep Telefonu</span><span class="sr-val">${r.phone}</span></div>
    ${r.email ? `<div class="summary-row"><span class="sr-label">E-Posta</span><span class="sr-val">${r.email}</span></div>` : ''}
    <div class="summary-row"><span class="sr-label">Oluşturulma</span><span class="sr-val">${formatTRDate(r.createdAt)}</span></div>
    <div class="summary-row"><span class="sr-label">Tahmini Sonuçlanma</span><span class="sr-val">7–14 iş günü</span></div>`;
}
async function mokaFetchStatus(caseId) {
  const r = await fetch(ITIRAZ_API + '/api/itiraz/status/' + encodeURIComponent(caseId), { cache: 'no-store' });
  if (!r.ok) return null;
  return r.json();
}
async function mokaAdvanceStage(caseId) {
  // Demo amaçlı: gerçek bankacılık entegrasyonu değildir, yalnızca takip ekranı deneyimi içindir.
  const r = await fetch(ITIRAZ_API + '/api/itiraz/' + encodeURIComponent(caseId) + '/advance', { method: 'POST' });
  if (!r.ok) return null;
  return r.json();
}

function initDisputeWizard() {
  const wizard = document.getElementById('disputeWizard');
  if (!wizard) return;

  // Giriş seçimi: "Yeni İtiraz Oluştur" tıklanınca wizard'ı göster
  const entry = document.getElementById('disputeEntry');
  const entryNew = document.getElementById('entryNew');
  if (entryNew) entryNew.addEventListener('click', () => {
    if (entry) entry.hidden = true;
    wizard.hidden = false;
    wizard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // Mock işlem kayıtları tek kaynaktan gelir: assets/data/dispute-txns.js (window.MOKA_DISPUTE_TXNS)
  const TXNS = window.MOKA_DISPUTE_TXNS || [];
  const STEP_BY_SCREEN = { query: 1, notfound: 1, locked: 1, disclosure: 2, remembered: 2, request: 3, otp: 3, 'already-open': 3, 'request-done': 4 };

  const screens = [...wizard.querySelectorAll('.dispute-screen')];
  const progress = [...wizard.querySelectorAll('.wp-step')];
  const queryForm = document.getElementById('disputeQueryForm');
  const queryAttempts = document.getElementById('queryAttempts');
  const lockedMsgEl = document.querySelector('[data-screen="locked"] .step-sub');
  const lockedDefaultMsg = lockedMsgEl ? lockedMsgEl.textContent : '';

  // Hızlı test butonları (jüri değerlendirmesi için) — formu örnek verilerle doldurur
  wizard.querySelectorAll('.qf-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      wizard.querySelectorAll('.qf-chip').forEach(c => c.classList.remove('qf-active'));
      chip.classList.add('qf-active');
      queryForm.TxnKurum.value = chip.dataset.kurum;
      queryForm.TxnCuzdanId.value = chip.dataset.cuzdan;
      queryForm.TxnAmount.value = chip.dataset.amount;
      queryForm.TxnDate.value = chip.dataset.date;
      queryForm.TxnPhone.value = chip.dataset.phone;
      // E-posta kasıtlı olarak doldurulmuyor — jüri kendi gerçek adresini yazmalı (bilgilendirme maili gerçekten gönderilir).
    });
  });

  let currentTxn = null;
  let currentPhone = '';
  let currentEmail = '';
  let pendingOtpCode = '';

  function showScreen(name) {
    screens.forEach(s => s.classList.toggle('active', s.dataset.screen === name));
    const stepIdx = STEP_BY_SCREEN[name] || 1;
    progress.forEach(p => {
      const n = +p.dataset.step;
      p.classList.toggle('active', n === stepIdx);
      p.classList.toggle('done', n < stepIdx);
    });
    wizard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function findTxn(kurum, cuzdanId, amount, dateStr) {
    const target = new Date(dateStr);
    const kurumNorm = trLower(kurum);
    return TXNS.find(t => {
      // Kurum: kullanıcının bildiği kısayol ad (ör. "Beymen"), tam işyeri kaydının
      // (ör. "Beymen – Akasya AVM") içinde geçmesi yeterli — TR-duyarlı, büyük/küçük harf yok sayılır.
      if (!trLower(t.merchant).includes(kurumNorm) || t.cuzdanId !== cuzdanId) return false;
      const monthly = Math.round((t.amount / t.installment) * 100) / 100;
      const amtMatch = Math.abs(t.amount - amount) < 0.01 || Math.abs(monthly - amount) < 0.01;
      if (!amtMatch) return false;
      const diffDays = Math.abs((new Date(t.date) - target) / 86400000);
      return diffDays <= 1;
    });
  }

  function attemptsLeftMsg(el, remaining) {
    el.hidden = false;
    el.classList.toggle('danger', remaining <= 1);
    el.textContent = `Kalan deneme hakkınız: ${remaining}`;
  }

  function showLocked(message) {
    if (lockedMsgEl) lockedMsgEl.textContent = message || lockedDefaultMsg;
    showScreen('locked');
  }

  // IP bazlı brute-force koruması: her sorgu denemesinden önce backend'e danışılır.
  // Sunucuya erişilemezse (backend kapalı/ağ hatası) fail-open: demo akışı bloklanmaz.
  async function checkRateLimit() {
    try {
      const r = await fetch(ITIRAZ_API + '/api/itiraz/attempt', { method: 'POST' });
      const d = await r.json().catch(() => ({}));
      if (r.status === 429) return { allowed: false, message: d.message };
      return { allowed: true, remaining: typeof d.remaining === 'number' ? d.remaining : null };
    } catch (e) {
      return { allowed: true, remaining: null };
    }
  }

  queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const submitBtn = queryForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    const gate = await checkRateLimit();
    submitBtn.disabled = false;
    if (!gate.allowed) { showLocked(gate.message); return; }
    if (gate.remaining != null) attemptsLeftMsg(queryAttempts, gate.remaining);

    const kurum = queryForm.TxnKurum.value.trim();
    const cuzdanId = queryForm.TxnCuzdanId.value.trim();
    const amount = parseFloat(queryForm.TxnAmount.value);
    const date = queryForm.TxnDate.value;
    if (!kurum || !cuzdanId || !amount || !date) { queryForm.reportValidity(); return; }
    if (!queryForm.TxnPhone.checkValidity()) { queryForm.reportValidity(); return; }
    if (!queryForm.TxnEmail.checkValidity()) { queryForm.reportValidity(); return; }

    const match = findTxn(kurum, cuzdanId, amount, date);
    if (!match) {
      showScreen('notfound');
      return;
    }
    currentTxn = match;
    currentPhone = queryForm.TxnPhone.value.trim();
    currentEmail = queryForm.TxnEmail.value.trim();
    const card = document.getElementById('disclosureCard');
    card.innerHTML = `
      <div class="dc-logo">${currentTxn.merchant.charAt(0)}</div>
      <div class="dc-body">
        <strong>${currentTxn.merchant}</strong>
        <span>${currentTxn.district} · ${currentTxn.category}</span>
        <div class="dc-amount">${formatTL(currentTxn.amount)} — ${formatTRDate(currentTxn.date)}</div>
      </div>`;
    showScreen('disclosure');
  });

  document.getElementById('disputeRetry').addEventListener('click', () => showScreen('query'));

  document.getElementById('btnRecall').addEventListener('click', () => {
    currentTxn = null;
    showScreen('remembered');
  });

  // ---- "HÂLÂ TANIMIYORUM" → resmi itiraz talebi oluşturma akışı ----
  let currentCaseId = null;

  const reqForm = document.getElementById('disputeRequestForm');
  const txnTypeSel = document.getElementById('disputeTxnType');
  const txnWrap = document.getElementById('disputeTxnWrap');
  const txnListEl = document.getElementById('disputeTxnList');

  // İtiraz edilebilecek işlem havuzu: aynı işyerinden diğer işlemler
  function disputePool() {
    let pool = TXNS.filter(t => t.merchant === currentTxn.merchant);
    if (pool.length < 3) pool = [currentTxn, ...TXNS.filter(t => t.ref !== currentTxn.ref).slice(0, 7)];
    const seen = new Set(); const out = [];
    [currentTxn, ...pool].forEach(t => { if (!seen.has(t.ref)) { seen.add(t.ref); out.push(t); } });
    return out;
  }
  function filterByType(pool, type) {
    if (type === 'ekstre') return pool.filter(t => t.settled);          // ekstreye yansımış
    if (type === 'acik-provizyon') return pool.filter(t => !t.settled); // bekleyen provizyon
    return pool;                                                        // dönem içi = tümü
  }
  function renderTxnList(type) {
    const list = filterByType(disputePool(), type);
    if (!list.length) { txnListEl.innerHTML = '<p class="txn-empty">Bu tipte itiraz edilebilecek işlem bulunamadı.</p>'; return; }
    const curInList = list.some(x => x.ref === currentTxn.ref);
    txnListEl.innerHTML = list.map((t, i) => {
      const checked = curInList ? (t.ref === currentTxn.ref ? 'checked' : '') : (i === 0 ? 'checked' : '');
      const badge = t.settled ? '<span class="txn-badge settled">Ekstrede</span>' : '<span class="txn-badge pending">Bekliyor</span>';
      return `<label class="txn-choice">
        <input type="radio" name="DisputeTxn" value="${t.ref}" ${checked} required>
        <span class="txn-logo">${t.merchant.charAt(0)}</span>
        <span class="txn-main"><span class="txn-merch">${t.merchant}</span><span class="txn-meta">${formatTRDate(t.date)} · ${t.category}</span></span>
        <span class="txn-right"><span class="txn-amt">${formatTL(t.amount)}</span>${badge}</span>
      </label>`;
    }).join('');
  }

  // ---- Destekleyici belge (dosya) yönetimi ----
  const fileInput = document.getElementById('disputeFileInput');
  const filePickBtn = document.getElementById('disputeFilePick');
  const fileListEl = document.getElementById('disputeFileList');
  const fileErrorEl = document.getElementById('disputeFileError');
  const MAX_FILES = 5, MAX_FILE_SIZE = 5 * 1024 * 1024, MAX_TOTAL_SIZE = 15 * 1024 * 1024;
  const ALLOWED_EXT = ['.pdf', '.jpg', '.jpeg', '.png', '.heic'];
  let selectedFiles = [];

  function fmtSize(b) { return b < 1024 * 1024 ? Math.round(b / 1024) + ' KB' : (b / (1024 * 1024)).toFixed(1) + ' MB'; }
  function resetFiles() { selectedFiles = []; if (fileInput) fileInput.value = ''; if (fileErrorEl) fileErrorEl.textContent = ''; renderFileList(); }
  function renderFileList() {
    if (!fileListEl) return;
    fileListEl.innerHTML = selectedFiles.map((f, i) => `
      <li class="file-chip"><span class="fc-ic">📄</span>
        <span class="fc-name">${f.name}</span><span class="fc-size">${fmtSize(f.size)}</span>
        <button type="button" class="fc-remove" data-i="${i}" aria-label="Kaldır">✕</button>
      </li>`).join('');
  }
  if (filePickBtn && fileInput) filePickBtn.addEventListener('click', () => fileInput.click());
  if (fileInput) fileInput.addEventListener('change', () => {
    fileErrorEl.textContent = '';
    for (const f of fileInput.files) {
      const ext = '.' + f.name.split('.').pop().toLowerCase();
      if (!ALLOWED_EXT.includes(ext)) { fileErrorEl.textContent = `'${f.name}': yalnızca PDF, JPG, PNG, HEIC kabul edilir.`; continue; }
      if (f.size > MAX_FILE_SIZE) { fileErrorEl.textContent = `'${f.name}' 5MB sınırını aşıyor.`; continue; }
      if (selectedFiles.length >= MAX_FILES) { fileErrorEl.textContent = `En fazla ${MAX_FILES} dosya yükleyebilirsiniz.`; break; }
      const total = selectedFiles.reduce((s, x) => s + x.size, 0) + f.size;
      if (total > MAX_TOTAL_SIZE) { fileErrorEl.textContent = 'Toplam dosya boyutu 15MB sınırını aşıyor.'; continue; }
      if (selectedFiles.some(x => x.name === f.name && x.size === f.size)) continue;
      selectedFiles.push(f);
    }
    fileInput.value = '';
    renderFileList();
  });
  if (fileListEl) fileListEl.addEventListener('click', (e) => {
    const b = e.target.closest('.fc-remove'); if (!b) return;
    selectedFiles.splice(+b.dataset.i, 1);
    renderFileList();
  });

  document.getElementById('btnNotRecall').addEventListener('click', () => {
    reqForm.reset();
    txnWrap.hidden = true; txnListEl.innerHTML = '';
    document.getElementById('disputeReqError').textContent = '';
    resetFiles();
    showScreen('request');
  });
  document.getElementById('disputeReqBack').addEventListener('click', () => showScreen('disclosure'));

  txnTypeSel.addEventListener('change', () => {
    if (txnTypeSel.value) { renderTxnList(txnTypeSel.value); txnWrap.hidden = false; }
    else { txnWrap.hidden = true; txnListEl.innerHTML = ''; }
  });

  // Talep formu geçerliyse doğrudan oluşturmaz — önce (demo) telefon/OTP doğrulamasına gönderir.
  reqForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const err = document.getElementById('disputeReqError');
    err.textContent = '';
    if (!reqForm.Reason.value) { err.textContent = 'Lütfen itiraz sebebini seçin.'; return; }
    if (!txnTypeSel.value) { err.textContent = 'Lütfen işlem tipini seçin.'; return; }
    const selTxn = reqForm.querySelector('input[name="DisputeTxn"]:checked');
    if (!selTxn) { err.textContent = 'Lütfen itiraz edilecek işlemi seçin.'; return; }
    if (reqForm.Note.value.trim().length < 15) { err.textContent = 'Açıklama en az 15 karakter olmalıdır.'; reqForm.Note.focus(); return; }

    pendingOtpCode = String(Math.floor(100000 + Math.random() * 900000));
    const maskedPhone = currentPhone.length >= 8
      ? currentPhone.slice(0, 4) + ' *** ** ' + currentPhone.slice(-2)
      : currentPhone;
    document.getElementById('otpPhoneDisplay').textContent = maskedPhone;
    document.getElementById('otpInput').value = '';
    document.getElementById('otpError').textContent = '';
    showScreen('otp');
  });

  document.getElementById('otpBack').addEventListener('click', () => showScreen('request'));

  document.getElementById('otpPasteBtn').addEventListener('click', () => {
    document.getElementById('otpInput').value = pendingOtpCode;
  });

  document.getElementById('otpVerify').addEventListener('click', async () => {
    const otpErr = document.getElementById('otpError');
    const entered = document.getElementById('otpInput').value.trim();
    if (entered !== pendingOtpCode) {
      otpErr.textContent = 'Kod hatalı. Lütfen tekrar deneyin.';
      return;
    }
    otpErr.textContent = '';
    await submitDisputeRequest();
  });

  async function submitDisputeRequest() {
    const err = document.getElementById('disputeReqError');
    const selTxn = reqForm.querySelector('input[name="DisputeTxn"]:checked');
    const txn = (selTxn && TXNS.find(t => t.ref === selTxn.value)) || currentTxn;
    const fd = new FormData();
    fd.append('Reason', reqForm.Reason.value);
    fd.append('TxnType', txnTypeSel.options[txnTypeSel.selectedIndex].text);
    fd.append('Ref', txn.ref);
    fd.append('Merchant', txn.merchant);
    fd.append('Amount', String(txn.amount));
    fd.append('Note', reqForm.Note.value.trim());
    fd.append('Phone', currentPhone);
    fd.append('Email', currentEmail);
    selectedFiles.forEach(f => fd.append('Evidence', f, f.name));

    const verifyBtn = document.getElementById('otpVerify');
    verifyBtn.disabled = true;
    let res, rec;
    try {
      res = await fetch(ITIRAZ_API + '/api/itiraz/create', { method: 'POST', body: fd });
      rec = await res.json();
    } catch (ex) {
      verifyBtn.disabled = false;
      document.getElementById('otpError').textContent = 'Sunucuya bağlanılamadı. İtiraz API çalışıyor mu? (itiraz_server.py)';
      return;
    }
    verifyBtn.disabled = false;

    if (res.status === 409 && rec.error === 'already_open') {
      currentCaseId = rec.caseId;
      mokaRememberCaseId(rec.caseId);
      document.getElementById('alreadyOpenMsg').textContent = rec.message;
      document.getElementById('alreadyOpenCaseId').textContent = rec.caseId;
      document.getElementById('alreadyOpenGo').href = 'itiraz-durum.html?case=' + encodeURIComponent(rec.caseId);
      showScreen('already-open');
      setTimeout(() => { window.location.href = 'itiraz-durum.html?case=' + encodeURIComponent(rec.caseId); }, 3500);
      return;
    }
    if (res.status === 429) {
      err.textContent = rec.message || 'Çok fazla talep oluşturuldu. Lütfen daha sonra tekrar deneyin.';
      showScreen('request');
      return;
    }
    if (!res.ok) {
      err.textContent = rec.error || 'İtiraz oluşturulamadı. Bilgilerinizi kontrol edip tekrar deneyin.';
      showScreen('request');
      return;
    }

    currentCaseId = rec.caseId;
    mokaRememberCaseId(rec.caseId);
    document.getElementById('disputeCaseId').textContent = rec.caseId;
    mokaRenderTracker(document.getElementById('disputeTracker'), rec.stage);
    document.getElementById('disputeReqSummary').innerHTML = mokaDisputeSummary(rec);
    showScreen('request-done');
  }

  document.getElementById('disputeTrackRefresh').addEventListener('click', async () => {
    if (!currentCaseId) return;
    const rec = await mokaAdvanceStage(currentCaseId);
    if (rec) mokaRenderTracker(document.getElementById('disputeTracker'), rec.stage);
  });
  document.getElementById('disputeCaseCopy').addEventListener('click', () => {
    const b = document.getElementById('disputeCaseCopy');
    navigator.clipboard && navigator.clipboard.writeText(document.getElementById('disputeCaseId').textContent);
    const old = b.textContent; b.textContent = 'Kopyalandı ✓';
    setTimeout(() => b.textContent = old, 1500);
  });

  // yalnızca rakam
  wizard.querySelectorAll('.only-number').forEach(i =>
    i.addEventListener('input', () => i.value = i.value.replace(/[^0-9]/g, '')));
}

// ---- İtiraz Durumu Sorgula sayfası (itiraz-durum.html) ----
function initDisputeStatus() {
  const page = document.getElementById('disputeStatusPage');
  if (!page) return;
  const form = document.getElementById('statusQueryForm');
  const input = document.getElementById('statusCaseInput');
  const resultWrap = document.getElementById('statusResult');
  const notFound = document.getElementById('statusNotFound');
  const recentWrap = document.getElementById('statusRecent');
  let activeId = null;

  function renderRecent() {
    const ids = mokaRecentCaseIds();
    if (!ids.length) { recentWrap.innerHTML = ''; return; }
    recentWrap.innerHTML = '<span class="sr-hint">Bu cihazda son sorguladıklarınız:</span>' +
      ids.slice(0, 5).map(id => `<button type="button" class="recent-chip" data-id="${id}">${id}</button>`).join('');
  }

  async function lookup(raw) {
    const id = (raw || '').trim().toUpperCase();
    if (!id) return;
    const rec = await mokaFetchStatus(id);
    if (!rec) { resultWrap.hidden = true; notFound.hidden = false; return; }
    notFound.hidden = true;
    activeId = rec.caseId;
    mokaRememberCaseId(rec.caseId);
    renderRecent();
    document.getElementById('statusCaseId').textContent = rec.caseId;
    mokaRenderTracker(document.getElementById('statusTracker'), rec.stage);
    document.getElementById('statusSummary').innerHTML = mokaDisputeSummary(rec);
    resultWrap.hidden = false;
    resultWrap.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  form.addEventListener('submit', (e) => { e.preventDefault(); lookup(input.value); });
  recentWrap.addEventListener('click', (e) => {
    const b = e.target.closest('[data-id]'); if (!b) return;
    input.value = b.dataset.id; lookup(b.dataset.id);
  });
  const refresh = document.getElementById('statusRefresh');
  if (refresh) refresh.addEventListener('click', async () => {
    if (!activeId) return;
    const rec = await mokaAdvanceStage(activeId);
    if (rec) mokaRenderTracker(document.getElementById('statusTracker'), rec.stage);
  });

  const qp = new URLSearchParams(location.search).get('case');
  if (qp) { input.value = qp; lookup(qp); }
  renderRecent();
}

function formatTL(n) {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 2 }).format(n);
}
function formatTRDate(iso) {
  return new Date(iso).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
}
// --- Dosya yükleme alanı: seçilen dosya adını göster ---
function initFileInputs() {
  document.querySelectorAll('.file-drop input[type="file"]').forEach(inp => {
    const label = inp.closest('.file-drop').querySelector('.file-drop-text');
    const def = label.textContent;
    inp.addEventListener('change', () => {
      if (inp.files.length) {
        const f = inp.files[0];
        if (f.size > 10 * 1024 * 1024) { alert('Dosya boyutu en fazla 10MB olmalıdır.'); inp.value = ''; label.textContent = def; return; }
        label.textContent = f.name;
        inp.closest('.file-drop').classList.add('has-file');
      } else { label.textContent = def; inp.closest('.file-drop').classList.remove('has-file'); }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  initCounters();
  initMarquee();
  initContactForm();
  initApplyWizard();
  initDisputeWizard();
  initDisputeStatus();
  initFileInputs();
});
