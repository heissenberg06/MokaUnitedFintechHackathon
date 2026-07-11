/* ============================================================
   Ortak bileşenler: Header, Pre-footer CTA, Footer
   Tüm sayfalara enjekte edilir. Aktif menü linki data-active ile.
   ============================================================ */

const LOGO_SVG = `<svg viewBox="0 0 200 40" xmlns="http://www.w3.org/2000/svg" aria-label="Moka United">
  <text x="0" y="30" font-family="Poppins, sans-serif" font-weight="800" font-size="30" fill="#0d3c94">moka</text>
  <text x="82" y="30" font-family="Poppins, sans-serif" font-weight="300" font-size="30" fill="#0d3c94">united</text>
  <circle cx="192" cy="12" r="6" fill="#2bfb97"/>
</svg>`;

const ICONS = {
  linkedin: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05C20.4 8.65 22 11 22 14.5V21h-4v-5.7c0-1.36-.02-3.1-1.9-3.1s-2.2 1.48-2.2 3v5.8H9z"/></svg>',
  instagram: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 2H22l-7 8 8.2 12h-6.4l-5-7.3L5.6 22H2.5l7.5-8.6L2 2h6.6l4.6 6.7zM17.8 20h1.7L8.3 4H6.5z"/></svg>',
  youtube: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23 12s0-3.2-.4-4.7a2.5 2.5 0 0 0-1.8-1.8C19.3 5 12 5 12 5s-7.3 0-8.8.5A2.5 2.5 0 0 0 1.4 7.3C1 8.8 1 12 1 12s0 3.2.4 4.7a2.5 2.5 0 0 0 1.8 1.8C4.7 19 12 19 12 19s7.3 0 8.8-.5a2.5 2.5 0 0 0 1.8-1.8C23 15.2 23 12 23 12zM9.8 15.2V8.8l6 3.2z"/></svg>',
  tiktok: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16 3c.3 2.2 1.6 3.7 3.7 3.9v2.5c-1.3.1-2.5-.3-3.7-1v6.2c0 3.7-2.6 5.9-5.6 5.9-2.8 0-5.1-2-5.1-4.9 0-3.1 2.6-5.2 6-4.6v2.7c-.4-.1-.9-.2-1.3-.2-1.3 0-2.2.9-2.2 2.1 0 1.3 1 2.1 2.2 2.1 1.4 0 2.4-1 2.4-2.9V3z"/></svg>',
  snapchat: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c2.6 0 4.3 2 4.4 4.5.1.9 0 1.8.1 2.3.1.3.5.4.9.3.3-.1.5-.2.8-.2.5 0 .9.3.9.8 0 .6-.7.9-1.3 1.1-.4.2-.9.3-.9.7 0 .2.1.4.3.7.6 1.1 1.6 2 2.8 2.4.4.1.6.3.6.6 0 .6-1.1.9-1.8 1-.2 0-.3.2-.4.5-.1.3-.2.7-.6.7-.5 0-.9-.3-1.7-.3-1.1 0-1.5.9-3.4.9s-2.3-.9-3.4-.9c-.8 0-1.2.3-1.7.3-.4 0-.5-.4-.6-.7-.1-.3-.2-.5-.4-.5-.7-.1-1.8-.4-1.8-1 0-.3.2-.5.6-.6 1.2-.4 2.2-1.3 2.8-2.4.2-.3.3-.5.3-.7 0-.4-.5-.5-.9-.7-.6-.2-1.3-.5-1.3-1.1 0-.5.4-.8.9-.8.3 0 .5.1.8.2.4.1.8 0 .9-.3.1-.5 0-1.4.1-2.3C7.7 4 9.4 2 12 2z"/></svg>',
  whatsapp: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15L2 22l5.1-1.3A10 10 0 1 0 12 2zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .2-3.3-.7-2.8-1.1-4.5-4-4.7-4.2-.1-.2-1-1.4-1-2.6s.6-1.8.9-2.1c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.4.5c-.2.2-.3.3-.1.6.2.3.9 1.4 1.9 2.3 1.3 1.1 2.3 1.5 2.6 1.6.3.1.5.1.6-.1l.7-.9c.2-.2.4-.2.6-.1l1.9.9c.2.1.4.2.5.3.1.2.1.7-.1 1.3z"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>'
};

function buildHeader(active = '') {
  const isA = (k) => active === k ? 'style="background:var(--box-gray-2)"' : '';
  return `
  <header class="site-header">
    <a class="logo" href="index.html" aria-label="Moka United ana sayfa">${LOGO_SVG}</a>
    <nav class="main-menu">
      <div class="menu-item">
        <a href="hakkimizda.html" ${isA('hakkimizda')}>HAKKIMIZDA <em class="menu-caret">⌄</em></a>
        <div class="mega-menu items-4">
          <a class="mega-menu-item" href="hikayemiz.html"><span>HİKAYEMİZ</span></a>
          <a class="mega-menu-item" href="kurumsal-yonetim.html"><span>KURUMSAL YÖNETİM</span></a>
          <a class="mega-menu-item" href="kariyer.html"><span>MOKA UNITED'TA KARİYER</span></a>
          <a class="mega-menu-item" href="istirakler.html"><span>İŞTİRAKLER</span></a>
        </div>
      </div>
      <div class="menu-item">
        <a href="urunler.html" ${isA('urunler')}>ÜRÜNLER <em class="menu-caret">⌄</em></a>
        <div class="mega-menu items-5">
          <a class="mega-menu-item has-img" href="kart-cozumleri.html"><span>KART ÇÖZÜMLERİ</span><img src="assets/images/prod-kart.svg" alt="Kart Çözümleri" width="200" height="200" loading="lazy"></a>
          <a class="mega-menu-item has-img" href="cuzdan-cozumleri.html"><span>CÜZDAN ÇÖZÜMLERİ</span><img src="assets/images/prod-cuzdan.svg" alt="Cüzdan Çözümleri" width="200" height="200" loading="lazy"></a>
          <a class="mega-menu-item has-img" href="para-transferi.html"><span>PARA TRANSFERİ</span><img src="assets/images/prod-transfer.svg" alt="Para Transferi" width="200" height="200" loading="lazy"></a>
          <a class="mega-menu-item has-img" href="akilli-kasa.html"><span>AKILLI KASA</span><img src="assets/images/prod-kasa.svg" alt="Akıllı Kasa" width="200" height="200" loading="lazy"></a>
          <a class="mega-menu-item has-img" href="kiosk.html"><span>KİOSK</span><img src="assets/images/prod-kiosk.svg" alt="Kiosk" width="200" height="200" loading="lazy"></a>
        </div>
      </div>
      <div class="menu-item">
        <a href="pos-cozumleri.html" ${isA('pos')}>POS ÇÖZÜMLERİ <em class="menu-caret">⌄</em></a>
        <div class="mega-menu items-3">
          <a class="mega-menu-item" href="sanal-pos.html"><span>SANAL POS</span></a>
          <a class="mega-menu-item" href="fiziki-pos.html"><span>FİZİKİ POS</span></a>
          <a class="mega-menu-item" href="linkle-tahsilat.html"><span>LİNKLE TAHSİLAT</span></a>
        </div>
      </div>
    </nav>
    <div class="header-buttons">
      <a class="button button-secondary desktop-only" href="basvuru.html"><span>HEMEN BAŞVURUN</span></a>
      <a class="button button-primary desktop-only" href="panel-giris.html"><span>PANEL GİRİŞİ</span></a>
      <button class="button-third desktop-only" id="searchToggle" aria-label="Ara">${ICONS.search}</button>
      <div class="lang-wrapper desktop-only">
        <a class="lang-button" href="javascript:;">TR ▾</a>
        <div class="lang-dropdown">
          <a href="https://www.mokaunited.com" target="_blank" rel="noopener"><span class="flag flag-gb"></span> ENGLISH</a>
          <a href="index.html"><span class="flag flag-tr"></span> TÜRKÇE</a>
          <a href="https://www.unitedpayment.az" target="_blank" rel="noopener"><span class="flag flag-az"></span> AZƏRBAYCAN</a>
          <a href="https://www.unitedpayment.ge" target="_blank" rel="noopener"><span class="flag flag-ge"></span> ქართული</a>
          <a href="https://www.unitedpayment.uz" target="_blank" rel="noopener"><span class="flag flag-uz"></span> O‘ZBEK</a>
          <a href="javascript:;"><span class="flag flag-ru"></span> РУССКИЙ</a>
        </div>
      </div>
      <button class="hamburger" id="hamburger" aria-label="Menü"><span></span><span></span><span></span></button>
    </div>
  </header>

  <div class="mobile-menu" id="mobileMenu">
    <button class="mobile-search-toggle" id="mobileSearchToggle">${ICONS.search}<span>Ne aramıştınız?</span></button>
    <a href="hakkimizda.html">HAKKIMIZDA</a>
    <div class="sub">
      <a href="hikayemiz.html">Hikayemiz</a>
      <a href="kurumsal-yonetim.html">Kurumsal Yönetim</a>
      <a href="kariyer.html">Moka United'ta Kariyer</a>
      <a href="istirakler.html">İştirakler</a>
    </div>
    <a href="urunler.html">ÜRÜNLER</a>
    <div class="sub">
      <a href="kart-cozumleri.html">Kart Çözümleri</a>
      <a href="cuzdan-cozumleri.html">Cüzdan Çözümleri</a>
      <a href="para-transferi.html">Para Transferi</a>
      <a href="akilli-kasa.html">Akıllı Kasa</a>
      <a href="kiosk.html">Kiosk</a>
    </div>
    <a href="pos-cozumleri.html">POS ÇÖZÜMLERİ</a>
    <div class="sub">
      <a href="sanal-pos.html">Sanal POS</a>
      <a href="fiziki-pos.html">Fiziki POS</a>
      <a href="linkle-tahsilat.html">Linkle Tahsilat</a>
    </div>
    <a href="iletisim.html">İLETİŞİM</a>
    <div class="m-buttons">
      <a class="button button-secondary" href="basvuru.html"><span>HEMEN BAŞVURUN</span></a>
      <a class="button button-primary" href="panel-giris.html"><span>PANEL GİRİŞİ</span></a>
    </div>
  </div>

  <div class="search-overlay" id="searchOverlay">
    <button class="search-close" id="searchClose" aria-label="Kapat">×</button>
    <form class="search-wrapper" id="searchForm">
      <label class="search-label">Ne Aramıştınız?</label>
      <input type="search" name="q" id="searchInput" placeholder="Sayfa ara: sanal pos, kart, iletişim..." autocomplete="off">
      <div class="search-results" id="searchResults"></div>
    </form>
  </div>`;
}

function buildFooterCTA() {
  return `
  <section class="cta-tenth reveal">
    <h2><span class="muted">TANIŞALIM MI?</span><br>BİZ MOKA UNITED</h2>
    <div class="links-wrapper">
      <div class="whatsapp-box">
        <span class="wa-icon" style="color:#25d366">${ICONS.whatsapp}</span>
        <div class="wa-text">
          <small>Whatsapp Numarası</small>
          <a class="num" href="https://api.whatsapp.com/send?phone=908502522222" target="_blank" rel="noopener">0850 252 22 22</a>
        </div>
        <a class="button button-primary" href="https://api.whatsapp.com/send?phone=908502522222" target="_blank" rel="noopener"><span>İLETİŞİME GEÇ</span></a>
      </div>
      <div class="social-links">
        <a href="https://www.linkedin.com/company/mokaunited" target="_blank" rel="noopener" aria-label="LinkedIn">${ICONS.linkedin}</a>
        <a href="https://instagram.com/mokaunited" target="_blank" rel="noopener" aria-label="Instagram">${ICONS.instagram}</a>
        <a href="https://x.com/mokaunited" target="_blank" rel="noopener" aria-label="X">${ICONS.x}</a>
        <a href="https://www.youtube.com/@mokaunited" target="_blank" rel="noopener" aria-label="YouTube">${ICONS.youtube}</a>
        <a href="https://www.snapchat.com/add/mokaunited" target="_blank" rel="noopener" aria-label="Snapchat">${ICONS.snapchat}</a>
        <a href="https://www.tiktok.com/@mokaunited" target="_blank" rel="noopener" aria-label="TikTok">${ICONS.tiktok}</a>
      </div>
    </div>
  </section>`;
}

const OFFICES = {
  merkez: { name: 'İstanbul Merkez', addr: 'Levent Mah. Meltem Sk. İş Bankası Kuleleri No: 10 Kule: 2 PK. 34330 Beşiktaş/İstanbul', tel: '+90 850 252 22 22', faks: '0 (212) 241 59 59', mail: 'info@mokaunited.com', mersis: '0178071182100017' },
  ankara: { name: 'Ankara', addr: 'Macun Mah. 187 Cad. No: 54/89 Yenimahalle/Ankara', tel: '+90 850 252 22 22', mail: 'info@mokaunited.com' },
  teknopark: { name: 'İstanbul Teknopark', addr: 'Kazlıçeşme Mah. 245. Sk. No: 5 Zeytinburnu/İstanbul', tel: '+90 850 252 22 22', mail: 'info@mokaunited.com' },
  gayrettepe: { name: 'İstanbul Gayrettepe', addr: 'Esentepe Mah. Büyükdere Cad. No:102/14 Maya Akar Center, Şişli/İstanbul', tel: '+90 850 252 22 22', faks: '0 (212) 241 54 59', mail: 'info@mokaunited.com', mersis: '0178071182100017' }
};

// Footer partner/regülasyon logoları (basit SVG wordmark'lar)
const wm = (label, w, fill, weight = 800, extra = '') =>
  `<svg class="partner-logo" viewBox="0 0 ${w} 32" role="img" aria-label="${label}">${extra}<text x="${w / 2}" y="22" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="${weight}" font-size="18" fill="${fill}">${label}</text></svg>`;
const PARTNER_LOGOS = {
  tcmb: wm('TCMB', 70, '#6b7280'),
  bkm: wm('BKM', 62, '#6b7280'),
  todeb: wm('TÖDEB', 78, '#6b7280'),
  pci: wm('PCI DSS', 90, '#6b7280'),
  visa: `<svg class="partner-logo" viewBox="0 0 70 32" role="img" aria-label="Visa"><text x="35" y="23" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="900" font-style="italic" font-size="22" fill="#1a1f71">VISA</text></svg>`,
  mastercard: `<svg class="partner-logo" viewBox="0 0 118 32" role="img" aria-label="Mastercard"><circle cx="16" cy="16" r="11" fill="#EB001B"/><circle cx="28" cy="16" r="11" fill="#F79E1B" fill-opacity=".9"/><text x="76" y="21" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="700" font-size="14" fill="#6b7280">mastercard</text></svg>`,
  troy: `<svg class="partner-logo" viewBox="0 0 64 32" role="img" aria-label="Troy"><circle cx="12" cy="16" r="6" fill="#00a4a6"/><text x="40" y="22" text-anchor="middle" font-family="Poppins,sans-serif" font-weight="800" font-size="18" fill="#e30613">troy</text></svg>`,
  masak: wm('MASAK', 82, '#6b7280'),
};

// Uluslararası ofisler (ülke accordion'ları)
const INTL_OFFICES = [
  { name: 'Birleşik Krallık', addr: '1 King William St, London EC4N 7AF', mail: 'info@ruutapp.com' },
  { name: 'Azerbaycan', addr: 'Alaaddin Guliyev 1131, Babek Plaza A Block, Bakü', mail: 'info@mokaunited.com' },
  { name: 'Almanya', addr: 'Maxi Digital GmbH, Taunustor 1, Frankfurt am Main', mail: 'info@ruutapp.com' },
  { name: 'Gürcistan', addr: 'United Payment Georgia LTD, D. Arakishvili St., Tiflis', mail: 'info@unitedpayment.ge' },
];

function buildFooter() {
  const paneRow = (label, val) => val ? `<div class="office-info"><span>${label}</span><span>${val}</span></div>` : '';
  const tabs = Object.entries(OFFICES).map(([k, o], i) =>
    `<button class="office-tab ${i === 0 ? 'active' : ''}" data-office="${k}">${o.name}</button>`).join('');
  const panes = Object.entries(OFFICES).map(([k, o], i) =>
    `<div class="office-pane ${i === 0 ? 'active' : ''}" data-office="${k}">
       <p class="addr">${o.addr}</p>
       ${paneRow('Telefon', o.tel)}${paneRow('Faks', o.faks)}${paneRow('E-Posta', o.mail)}${paneRow('Mersis No', o.mersis)}
     </div>`).join('');
  const intlAccordions = INTL_OFFICES.map(o =>
    `<div class="accordion-item country-item">
       <button class="accordion-header">${o.name}<span class="chev">⌄</span></button>
       <div class="accordion-body"><div class="accordion-body-inner">
         <p class="addr">${o.addr}</p>${paneRow('E-Posta', o.mail)}
       </div></div>
     </div>`).join('');
  const partners = Object.values(PARTNER_LOGOS).map(svg => `<span class="partner">${svg}</span>`).join('');

  return `
  <footer class="site-footer">
    <div class="footer-top">
      <nav class="footer-menu">
        <div class="footer-col">
          <h5><a href="hakkimizda.html">Hakkımızda</a></h5>
          <a href="hikayemiz.html">Hikayemiz</a>
          <a href="kurumsal-yonetim.html">Kurumsal Yönetim</a>
          <a href="kariyer.html">Moka United'ta Kariyer</a>
          <a href="istirakler.html">İştirakler</a>
        </div>
        <div class="footer-col">
          <h5><a href="urunler.html">Ürünler</a></h5>
          <a href="kart-cozumleri.html">Kart Çözümleri</a>
          <a href="cuzdan-cozumleri.html">Cüzdan Çözümleri</a>
          <a href="para-transferi.html">Para Transferi</a>
          <a href="akilli-kasa.html">Akıllı Kasa</a>
          <a href="kiosk.html">Kiosk</a>
        </div>
        <div class="footer-col">
          <h5><a href="pos-cozumleri.html">POS Çözümleri</a></h5>
          <a href="sanal-pos.html">Sanal POS</a>
          <a href="fiziki-pos.html">Fiziki POS</a>
          <a href="linkle-tahsilat.html">Linkle Tahsilat</a>
        </div>
        <div class="footer-col">
          <h5><a href="iletisim.html">İletişim</a></h5>
          <a href="iletisim.html">Bize Ulaşın</a>
          <a href="cerez-politikasi.html">Çerez Politikası</a>
        </div>
      </nav>
      <div class="footer-contact">
        <h5>İLETİŞİM</h5>
        <div class="accordion country-accordion">
          <div class="accordion-item country-item active">
            <button class="accordion-header">Türkiye<span class="chev">⌄</span></button>
            <div class="accordion-body"><div class="accordion-body-inner">
              <div class="office-tabs">${tabs}</div>
              <div class="office-panes">${panes}</div>
            </div></div>
          </div>
          ${intlAccordions}
        </div>
        <div class="footer-partners">${partners}</div>
      </div>
    </div>
    <div class="footer-bottom">
      <div style="display:flex;justify-content:center">${LOGO_SVG}</div>
      <nav class="footer-sub-menu">
        <a href="yasal-belgeler-ve-temsilcilikler.html">Yasal Belgeler ve Temsilcilikler</a>
        <a href="gizlilik-politikasi.html">Gizlilik Politikası</a>
        <a href="kisisel-verilerin-korunmasi.html">Kişisel Verilerin Korunması</a>
        <a href="bilgi-toplumu-hizmetleri.html">Bilgi Toplumu Hizmetleri</a>
      </nav>
      <p style="text-align:center;color:#999;font-size:12px;margin-top:20px">© 2026 Moka United — Klon (eğitim amaçlı). Bu bir demo çalışmasıdır.</p>
    </div>
  </footer>
  <a class="mobile-wa" href="https://api.whatsapp.com/send?phone=908502522222" target="_blank" rel="noopener" aria-label="WhatsApp">${ICONS.whatsapp}</a>

  <div class="cookie-banner" id="cookieBanner">
    <div class="cookie-text">
      <strong>Çerez Kullanımı</strong>
      <p>Web sitemizde deneyiminizi iyileştirmek için çerezler kullanıyoruz. Detaylar için <a href="cerez-politikasi.html">Çerez Politikası</a>’nı inceleyebilirsiniz.</p>
    </div>
    <div class="cookie-actions">
      <button class="button button-secondary cookie-reject"><span>REDDET</span></button>
      <button class="button button-primary cookie-accept"><span>KABUL ET</span></button>
    </div>
  </div>`;
}

/* Enjeksiyon: sayfa data-active ile hangi menünün aktif olduğunu belirtir */
document.addEventListener('DOMContentLoaded', () => {
  const active = document.body.dataset.active || '';
  const headerMount = document.getElementById('header-mount');
  const ctaMount = document.getElementById('cta-mount');
  const footerMount = document.getElementById('footer-mount');
  if (headerMount) headerMount.innerHTML = buildHeader(active);
  if (ctaMount) ctaMount.innerHTML = buildFooterCTA();
  if (footerMount) footerMount.innerHTML = buildFooter();
  document.dispatchEvent(new Event('components:ready'));
});
