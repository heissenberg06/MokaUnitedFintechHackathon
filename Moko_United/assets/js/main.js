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
  initFileInputs();
});
