// Ortak uygulama kabuğu (üst bar + sol nav) — her sayfada tekrar kullanılır.
(function () {
  var ICONS = {
    search: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.6"/><path d="M11 11L14.5 14.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    bell: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1.5c-2 0-3.2 1.5-3.2 3.6v2c0 .7-.3 1.4-.8 1.9L3 10h10l-1-1c-.5-.5-.8-1.2-.8-1.9v-2C11.2 3 10 1.5 8 1.5z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M6.3 12.5a1.7 1.7 0 003.4 0" stroke="currentColor" stroke-width="1.3"/></svg>',
    help: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6.2" stroke="currentColor" stroke-width="1.3"/><path d="M6.2 6.3c.2-1 1-1.6 1.9-1.6 1.1 0 1.9.7 1.9 1.7 0 .9-.5 1.3-1.2 1.8-.5.4-.7.7-.7 1.3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><circle cx="8" cy="11.6" r=".7" fill="currentColor"/></svg>',
    board: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="2.5" width="13" height="11" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M6 2.5v11M10.5 2.5v11" stroke="currentColor" stroke-width="1.3"/></svg>',
    list: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
    dashboard: '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1.5" y="1.5" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="8.5" y="1.5" width="6" height="9" rx="1" stroke="currentColor" stroke-width="1.3"/><rect x="1.5" y="9.5" width="6" height="5" rx="1" stroke="currentColor" stroke-width="1.3"/></svg>',
    chevronLeft: '<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    burger: '<svg width="18" height="18" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
  };

  var NAV_ITEMS = [
    { key: 'board', href: 'board.html', label: 'Pano', icon: ICONS.board },
    { key: 'list', href: 'list.html', label: 'Liste', icon: ICONS.list },
    { key: 'dashboard', href: 'dashboard.html', label: 'Kontrol Paneli', icon: ICONS.dashboard },
  ];

  function initialsAvatarColor(str) {
    var colors = ['#357DE8', '#22A06B', '#AF59E1', '#E06C00', '#2898BD', '#CD519D', '#6A9A23', '#B38600'];
    var h = 0;
    for (var i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
    return colors[h % colors.length];
  }
  window.MokaAvatarColor = initialsAvatarColor;

  function render(active) {
    var topbar = document.getElementById('jTopbar');
    var sidebar = document.getElementById('jSidebar');
    var main = document.getElementById('jMain');
    if (!topbar || !sidebar) return;

    topbar.className = 'j-topbar';
    topbar.innerHTML =
      '<button class="j-topbar-iconbtn" id="jBurgerBtn" style="display:none;">' + ICONS.burger + '</button>' +
      '<a href="board.html" class="j-topbar-logo"><span class="j-logo-mark">M</span>moka akış</a>' +
      '<div class="j-topbar-search"><span style="display:flex;color:#fff;">' + ICONS.search + '</span>' +
      '<input type="text" id="jSearchInput" placeholder="Talep ara... (MOKA-1, özet)"></div>' +
      '<div class="j-topbar-spacer"></div>' +
      '<div class="j-topbar-right">' +
      '<button class="j-btn j-btn-primary j-btn-sm" id="jCreateBtn">+ Oluştur</button>' +
      '<button class="j-topbar-iconbtn" title="Bildirimler">' + ICONS.bell + '</button>' +
      '<button class="j-topbar-iconbtn" title="Yardım">' + ICONS.help + '</button>' +
      '<span class="j-avatar j-avatar-md" style="background:' + initialsAvatarColor('Yönetici') + ';" title="Yönetici">YÖ</span>' +
      '</div>';

    sidebar.className = 'j-sidebar';
    sidebar.id = 'jSidebar';
    var itemsHtml = NAV_ITEMS.map(function (it) {
      return '<a href="' + it.href + '" class="j-sidebar-item' + (it.key === active ? ' j-active' : '') + '">' +
        it.icon + '<span class="j-sidebar-label">' + it.label + '</span></a>';
    }).join('');
    sidebar.innerHTML =
      '<div class="j-sidebar-title">Müşteri Talepleri &middot; MOKA</div>' +
      itemsHtml +
      '<button class="j-sidebar-collapse-btn" id="jCollapseBtn">' + ICONS.chevronLeft + '</button>';

    // Daraltma (desktop)
    var collapsed = localStorage.getItem('jSidebarCollapsed') === '1';
    function applyCollapsed() {
      sidebar.classList.toggle('j-collapsed', collapsed);
      if (main) main.classList.toggle('j-sidebar-collapsed', collapsed);
    }
    applyCollapsed();
    document.getElementById('jCollapseBtn').addEventListener('click', function () {
      collapsed = !collapsed;
      localStorage.setItem('jSidebarCollapsed', collapsed ? '1' : '0');
      applyCollapsed();
    });

    // Mobil: burger toggle
    var burgerBtn = document.getElementById('jBurgerBtn');
    function checkMobile() {
      var isMobile = window.innerWidth <= 900;
      burgerBtn.style.display = isMobile ? 'flex' : 'none';
    }
    checkMobile();
    window.addEventListener('resize', checkMobile);
    burgerBtn.addEventListener('click', function () {
      sidebar.classList.toggle('j-mobile-open');
    });
    document.addEventListener('click', function (e) {
      if (window.innerWidth > 900) return;
      if (sidebar.classList.contains('j-mobile-open') && !sidebar.contains(e.target) && e.target !== burgerBtn && !burgerBtn.contains(e.target)) {
        sidebar.classList.remove('j-mobile-open');
      }
    });

    // Arama: Enter -> liste sayfasına filtre ile git
    document.getElementById('jSearchInput').addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && e.target.value.trim()) {
        window.location.href = 'list.html?q=' + encodeURIComponent(e.target.value.trim());
      }
    });

    // Oluştur -> create-modal.js dinler
    document.getElementById('jCreateBtn').addEventListener('click', function () {
      document.dispatchEvent(new CustomEvent('j:open-create'));
    });
  }

  window.MokaShell = { init: render };
})();
