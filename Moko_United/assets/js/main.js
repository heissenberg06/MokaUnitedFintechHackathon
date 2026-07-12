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

// --- İtiraz / İşlem Sorgulama sihirbazı (frontend mock — gerçek backend yok) ---
// ---- İtiraz: paylaşılan takip + kalıcılık yardımcıları (hem oluşturma hem durum sorgu sayfası kullanır) ----
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
function mokaLoadDisputes() { try { return JSON.parse(localStorage.getItem('moka-disputes') || '{}'); } catch (e) { return {}; } }
function mokaSaveDispute(r) { const all = mokaLoadDisputes(); all[r.caseId] = r; localStorage.setItem('moka-disputes', JSON.stringify(all)); }
function mokaSetStage(id, stage) { const all = mokaLoadDisputes(); if (all[id]) { all[id].stage = stage; localStorage.setItem('moka-disputes', JSON.stringify(all)); } }

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
  const MAX_ATTEMPTS = 3;
  const STEP_BY_SCREEN = { query: 1, notfound: 1, locked: 1, disclosure: 2, remembered: 2, request: 3, 'request-done': 4 };

  const screens = [...wizard.querySelectorAll('.dispute-screen')];
  const progress = [...wizard.querySelectorAll('.wp-step')];
  const queryForm = document.getElementById('disputeQueryForm');
  const queryAttempts = document.getElementById('queryAttempts');

  let attempts = 0;
  let currentTxn = null;

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

  function findTxn(bin, last4, amount, dateStr) {
    const target = new Date(dateStr);
    return TXNS.find(t => {
      if (t.bin !== bin || t.last4 !== last4) return false;
      const monthly = Math.round((t.amount / t.installment) * 100) / 100;
      const amtMatch = Math.abs(t.amount - amount) < 0.01 || Math.abs(monthly - amount) < 0.01;
      if (!amtMatch) return false;
      const diffDays = Math.abs((new Date(t.date) - target) / 86400000);
      return diffDays <= 1;
    });
  }

  function attemptsLeftMsg(el) {
    const left = MAX_ATTEMPTS - attempts;
    el.hidden = false;
    el.classList.toggle('danger', left <= 1);
    el.textContent = `Kalan deneme hakkınız: ${left}`;
  }

  queryForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (attempts >= MAX_ATTEMPTS) { showScreen('locked'); return; }
    const bin = queryForm.TxnBin.value.trim();
    const last4 = queryForm.TxnLast4.value.trim();
    const amount = parseFloat(queryForm.TxnAmount.value);
    const date = queryForm.TxnDate.value;
    if (bin.length !== 6 || last4.length !== 4 || !amount || !date) { queryForm.reportValidity(); return; }

    const match = findTxn(bin, last4, amount, date);
    if (!match) {
      attempts++;
      if (attempts >= MAX_ATTEMPTS) { showScreen('locked'); return; }
      attemptsLeftMsg(queryAttempts);
      showScreen('notfound');
      return;
    }
    currentTxn = match;
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
    attempts = 0; currentTxn = null;
    showScreen('remembered');
  });

  // ---- "HÂLÂ TANIMIYORUM" → resmi itiraz talebi oluşturma akışı ----
  let trackStage = 2;
  let currentCaseId = null;

  const reqForm = document.getElementById('disputeRequestForm');
  const txnTypeSel = document.getElementById('disputeTxnType');
  const txnWrap = document.getElementById('disputeTxnWrap');
  const txnListEl = document.getElementById('disputeTxnList');
  const wantMail = document.getElementById('disputeWantMail');
  const mailWrap = document.getElementById('disputeMailWrap');

  // İtiraz edilebilecek işlem havuzu: aynı kart ailesinden (BIN) işlemler
  function disputePool() {
    let pool = TXNS.filter(t => t.bin === currentTxn.bin);
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

  document.getElementById('btnNotRecall').addEventListener('click', () => {
    reqForm.reset();
    txnWrap.hidden = true; txnListEl.innerHTML = '';
    mailWrap.hidden = true; mailWrap.querySelector('input').required = false;
    document.getElementById('disputeReqError').textContent = '';
    showScreen('request');
  });
  document.getElementById('disputeReqBack').addEventListener('click', () => showScreen('disclosure'));

  txnTypeSel.addEventListener('change', () => {
    if (txnTypeSel.value) { renderTxnList(txnTypeSel.value); txnWrap.hidden = false; }
    else { txnWrap.hidden = true; txnListEl.innerHTML = ''; }
  });
  wantMail.addEventListener('change', () => {
    mailWrap.hidden = !wantMail.checked;
    mailWrap.querySelector('input').required = wantMail.checked;
  });

  reqForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const err = document.getElementById('disputeReqError');
    err.textContent = '';
    if (!reqForm.Reason.value) { err.textContent = 'Lütfen itiraz sebebini seçin.'; return; }
    if (!txnTypeSel.value) { err.textContent = 'Lütfen işlem tipini seçin.'; return; }
    const selTxn = reqForm.querySelector('input[name="DisputeTxn"]:checked');
    if (!selTxn) { err.textContent = 'Lütfen itiraz edilecek işlemi seçin.'; return; }
    if (reqForm.Note.value.trim().length < 15) { err.textContent = 'Açıklama en az 15 karakter olmalıdır.'; reqForm.Note.focus(); return; }
    if (reqForm.Phone.value.trim().length < 10) { err.textContent = 'Geçerli bir cep telefonu girin.'; reqForm.Phone.focus(); return; }
    let email = '';
    if (wantMail.checked) {
      email = reqForm.Email.value.trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = 'Geçerli bir e-posta girin.'; reqForm.Email.focus(); return; }
    }

    const txn = TXNS.find(t => t.ref === selTxn.value) || currentTxn;
    const caseId = 'MU-ITZ-' + new Date().getFullYear() + '-' + String(Math.floor(100000 + Math.random() * 900000));
    currentCaseId = caseId;
    trackStage = 2;

    const phone = reqForm.Phone.value.trim();
    const maskPhone = phone.length >= 8 ? phone.slice(0, 4) + ' *** ** ' + phone.slice(-2) : phone;
    const rec = {
      caseId, createdAt: new Date().toISOString(), stage: trackStage,
      reason: reqForm.Reason.value,
      txnType: txnTypeSel.options[txnTypeSel.selectedIndex].text,
      merchant: txn.merchant, amount: txn.amount, ref: txn.ref,
      phone: maskPhone, email,
    };
    mokaSaveDispute(rec);

    document.getElementById('disputeCaseId').textContent = caseId;
    mokaRenderTracker(document.getElementById('disputeTracker'), trackStage);
    document.getElementById('disputeReqSummary').innerHTML = mokaDisputeSummary(rec);
    showScreen('request-done');
  });

  document.getElementById('disputeTrackRefresh').addEventListener('click', () => {
    if (trackStage < MOKA_TRACK_STAGES.length) {
      trackStage++;
      mokaRenderTracker(document.getElementById('disputeTracker'), trackStage);
      if (currentCaseId) mokaSetStage(currentCaseId, trackStage);
    }
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
  let activeId = null, activeStage = 2;

  function renderRecent() {
    const all = mokaLoadDisputes();
    const ids = Object.keys(all).sort((a, b) => new Date(all[b].createdAt) - new Date(all[a].createdAt));
    if (!ids.length) { recentWrap.innerHTML = ''; return; }
    recentWrap.innerHTML = '<span class="sr-hint">Bu cihazdaki kayıtlarınız:</span>' +
      ids.slice(0, 5).map(id => `<button type="button" class="recent-chip" data-id="${id}">${id}</button>`).join('');
  }
  function lookup(raw) {
    const id = (raw || '').trim().toUpperCase();
    const rec = mokaLoadDisputes()[id];
    if (!rec) { resultWrap.hidden = true; notFound.hidden = false; return; }
    notFound.hidden = true;
    activeId = rec.caseId; activeStage = rec.stage || 2;
    document.getElementById('statusCaseId').textContent = rec.caseId;
    mokaRenderTracker(document.getElementById('statusTracker'), activeStage);
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
  if (refresh) refresh.addEventListener('click', () => {
    if (activeId && activeStage < MOKA_TRACK_STAGES.length) {
      activeStage++;
      mokaRenderTracker(document.getElementById('statusTracker'), activeStage);
      mokaSetStage(activeId, activeStage);
    }
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
