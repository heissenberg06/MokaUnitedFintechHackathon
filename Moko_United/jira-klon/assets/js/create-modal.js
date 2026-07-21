// Global "Oluştur" modalı — shell.js'in yaydığı 'j:open-create' olayını dinler.
// AI köprüsü bağlı değildir; bu yalnızca manuel/talep oluşturma formudur (bkz. JIRA_KLON_ANALIZ.md §4.5/§5).
(function () {
  var META = null;
  var overlay = null;

  function fetchMeta() {
    if (META) return Promise.resolve(META);
    return fetch('/api/meta').then(function (r) { return r.json(); }).then(function (m) { META = m; return m; });
  }

  function optionsHtml(pairs, selected) {
    return pairs.map(function (p) {
      return '<option value="' + p[0] + '"' + (p[0] === selected ? ' selected' : '') + '>' + p[1] + '</option>';
    }).join('');
  }

  function open() {
    fetchMeta().then(render);
  }

  function close() {
    if (overlay) { overlay.remove(); overlay = null; }
  }

  function render(m) {
    close();
    overlay = document.createElement('div');
    overlay.className = 'j-modal-overlay';
    overlay.innerHTML =
      '<div class="j-modal">' +
        '<div class="j-modal-head">' +
          '<h2 class="j-heading-m">Talep Oluştur</h2>' +
          '<button class="j-modal-close" id="cmClose">&times;</button>' +
        '</div>' +
        '<div id="cmError"></div>' +
        '<form id="cmForm">' +
          '<div class="j-form-group"><label class="j-form-label">Proje</label>' +
            '<input class="j-input" value="Müşteri Talepleri — ' + m.project_key + '" disabled></div>' +
          '<div style="display:flex;gap:12px;">' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">Talep Türü</label>' +
              '<select class="j-select" id="cmIssuetype">' + optionsHtml(m.issue_types.map(function (t) { return [t, m.issuetype_label[t]]; })) + '</select></div>' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">Kategori</label>' +
              '<select class="j-select" id="cmCategory">' + optionsHtml(m.categories.map(function (c) { return [c, c]; })) + '</select></div>' +
          '</div>' +
          '<div class="j-form-group"><label class="j-form-label">Yönlendirilecek Ekip (otomatik)</label>' +
            '<input class="j-input" id="cmTeamPreview" disabled></div>' +
          '<div class="j-form-group"><label class="j-form-label">Özet</label>' +
            '<input class="j-input" id="cmSummary" maxlength="120" placeholder="Talebi kısaca özetleyin (en az 10 karakter)"></div>' +
          '<div class="j-form-group"><label class="j-form-label">Açıklama</label>' +
            '<textarea class="j-textarea" id="cmDescription" maxlength="2000" placeholder="Talebin detayı (en az 20 karakter)"></textarea></div>' +
          '<div style="display:flex;gap:12px;">' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">Öncelik</label>' +
              '<select class="j-select" id="cmPriority">' + optionsHtml(m.priorities.map(function (p) { return [p, m.priority_label[p]]; }), 'orta') + '</select></div>' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">Kaynak</label>' +
              '<select class="j-select" id="cmSource">' + optionsHtml(m.sources.map(function (s) { return [s, m.source_label[s] || s]; }), 'self-service') + '</select></div>' +
          '</div>' +
          '<div class="j-form-group"><label class="j-form-label">Bildiren (Ad Soyad)</label>' +
            '<input class="j-input" id="cmReporter" maxlength="40" placeholder="Ör. Ayşe Yılmaz"></div>' +
          '<div style="display:flex;gap:12px;">' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">İşyeri (opsiyonel)</label>' +
              '<input class="j-input" id="cmMerchant" maxlength="80" placeholder="İlgiliyse işyeri/marka adı"></div>' +
            '<div class="j-form-group" style="flex:1;"><label class="j-form-label">Etiketler (opsiyonel, virgülle ayır)</label>' +
              '<input class="j-input" id="cmLabels" placeholder="ör. fraud-ring, oncelikli"></div>' +
          '</div>' +
        '</form>' +
        '<div class="j-modal-footer">' +
          '<button class="j-btn j-btn-subtle" id="cmCancel">İptal</button>' +
          '<button class="j-btn j-btn-primary" id="cmSubmit">Oluştur</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);

    var categoryIssuetype = m.category_issuetype;
    var categoryTeam = m.category_team;
    var catSelect = document.getElementById('cmCategory');
    var typeSelect = document.getElementById('cmIssuetype');
    var teamPreview = document.getElementById('cmTeamPreview');
    function syncCategory() {
      var suggested = categoryIssuetype[catSelect.value];
      if (suggested) typeSelect.value = suggested;
      teamPreview.value = categoryTeam[catSelect.value] || '';
    }
    catSelect.addEventListener('change', syncCategory);
    syncCategory();

    document.getElementById('cmClose').addEventListener('click', close);
    document.getElementById('cmCancel').addEventListener('click', close);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });

    document.getElementById('cmSubmit').addEventListener('click', function (e) {
      e.preventDefault();
      submit();
    });
  }

  function submit() {
    var errBox = document.getElementById('cmError');
    errBox.innerHTML = '';
    var labelsRaw = document.getElementById('cmLabels').value.trim();
    var labels = labelsRaw ? labelsRaw.split(',').map(function (s) {
      return s.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
    }).filter(Boolean) : [];
    var payload = {
      issuetype: document.getElementById('cmIssuetype').value,
      category: document.getElementById('cmCategory').value,
      summary: document.getElementById('cmSummary').value.trim(),
      description: document.getElementById('cmDescription').value.trim(),
      priority: document.getElementById('cmPriority').value,
      source: document.getElementById('cmSource').value,
      reporter: document.getElementById('cmReporter').value.trim(),
      merchant: document.getElementById('cmMerchant').value.trim(),
      labels: labels,
    };
    fetch('/api/issues', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) {
          errBox.innerHTML = '<div class="j-banner j-banner-danger">' + (res.d.error || 'Bir hata oluştu.') + '</div>';
          return;
        }
        close();
        window.MokaUI.toast(res.d.key + ' oluşturuldu');
        document.dispatchEvent(new CustomEvent('j:issue-created', { detail: res.d }));
        if (window.location.pathname.endsWith('list.html') || window.location.pathname.endsWith('board.html')) {
          // sayfa kendi listener'ında yeniden yükler
        } else {
          window.location.href = 'issue.html?id=' + res.d.id;
        }
      });
  }

  document.addEventListener('j:open-create', open);
})();
