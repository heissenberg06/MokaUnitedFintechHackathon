(function () {
  'use strict';
  var COOKIE_KEY = 'n4bCookieAccepted';

  var banner = document.getElementById('cookieBanner');
  if (banner) {
    if (localStorage.getItem(COOKIE_KEY)) {
      banner.style.display = 'none';
    }
    var accept = document.getElementById('cookieAccept');
    var settings = document.getElementById('cookieSettings');
    // D7: "Ayarlar" artık "Anladım" ile aynı şeyi yapmıyor — yalnızca zorunlu
    // çerezleri kabul eder, opsiyonel/analitik çerezleri reddeder.
    if (accept) accept.addEventListener('click', function () {
      localStorage.setItem(COOKIE_KEY, 'accepted');
      banner.style.display = 'none';
    });
    if (settings) settings.addEventListener('click', function () {
      localStorage.setItem(COOKIE_KEY, 'essential-only');
      banner.style.display = 'none';
    });
  }

  // event delegation: klonlanan (mobil menüdeki) .n4b-inert linkler için de çalışır
  document.addEventListener('click', function (e) {
    var target = e.target.closest && e.target.closest('.n4b-inert');
    if (target) e.preventDefault();
  });

  var burger = document.getElementById('burgerBtn');
  var nav = document.querySelector('.n4b-nav');
  var ctas = document.querySelector('.n4b-header-ctas');
  if (burger && nav) {
    // D3: mobilde header CTA'ları (Toplantı Planla / Müşteri Yorumları) erişilemez
    // kalmasın diye mobil menüye bir kez klonlanır.
    if (ctas) {
      ctas.querySelectorAll('a').forEach(function (a) {
        var clone = a.cloneNode(true);
        clone.classList.add('n4b-mobile-cta-clone');
        clone.style.textAlign = 'center';
        clone.style.marginTop = '4px';
        nav.appendChild(clone);
      });
    }
    burger.addEventListener('click', function () {
      var open = nav.style.display === 'flex';
      nav.style.display = open ? 'none' : 'flex';
      nav.style.flexDirection = 'column';
      nav.style.position = 'absolute';
      nav.style.top = '76px';
      nav.style.left = '0';
      nav.style.right = '0';
      nav.style.background = '#fff';
      nav.style.padding = '16px 24px';
      nav.style.borderBottom = '1px solid var(--n4b-card-border)';
      nav.style.gap = '14px';
    });
  }
})();
