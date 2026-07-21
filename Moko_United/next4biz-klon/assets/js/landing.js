(function () {
  'use strict';
  var COOKIE_KEY = 'n4bCookieAccepted';

  var banner = document.getElementById('cookieBanner');
  if (banner) {
    if (localStorage.getItem(COOKIE_KEY) === '1') {
      banner.style.display = 'none';
    }
    var accept = document.getElementById('cookieAccept');
    var settings = document.getElementById('cookieSettings');
    if (accept) accept.addEventListener('click', function () {
      localStorage.setItem(COOKIE_KEY, '1');
      banner.style.display = 'none';
    });
    if (settings) settings.addEventListener('click', function () {
      localStorage.setItem(COOKIE_KEY, '1');
      banner.style.display = 'none';
    });
  }

  var burger = document.getElementById('burgerBtn');
  var nav = document.querySelector('.n4b-nav');
  if (burger && nav) {
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
