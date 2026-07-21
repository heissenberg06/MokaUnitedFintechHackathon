(function () {
  var API = '';
  var META = null;
  var page = 1;
  var qs = new URLSearchParams(window.location.search);

  function api(path) { return API + path; }

  function loadMeta() {
    return fetch(api('/api/meta')).then(function (r) { return r.json(); }).then(function (m) {
      META = m;
      fillSelect('fStatus', m.statuses.map(function (s) { return [s, m.status_label[s]]; }));
      fillSelect('fIssuetype', m.issue_types.map(function (t) { return [t, m.issuetype_label[t]]; }));
      fillSelect('fPriority', m.priorities.map(function (p) { return [p, m.priority_label[p]]; }));
      fillSelect('fCategory', m.categories.map(function (c) { return [c, c]; }));
      fillSelect('fTeam', m.teams.map(function (t) { return [t, t]; }));
    });
  }

  function fillSelect(id, pairs) {
    var el = document.getElementById(id);
    pairs.forEach(function (p) {
      var o = document.createElement('option');
      o.value = p[0]; o.textContent = p[1];
      el.appendChild(o);
    });
  }

  function currentFilters() {
    return {
      q: document.getElementById('fSearch').value.trim(),
      status: document.getElementById('fStatus').value,
      issuetype: document.getElementById('fIssuetype').value,
      priority: document.getElementById('fPriority').value,
      category: document.getElementById('fCategory').value,
      team: document.getElementById('fTeam').value,
      sla: document.getElementById('fSla').value,
    };
  }

  function buildQuery(filters) {
    var p = new URLSearchParams();
    Object.keys(filters).forEach(function (k) { if (filters[k]) p.set(k, filters[k]); });
    p.set('page', page);
    return p.toString();
  }

  function sla_dot(state) {
    var color = state === 'breach' ? 'var(--j-icon-red)' : state === 'risk' ? 'var(--j-icon-orange)' : 'var(--j-icon-green)';
    return '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + color + ';margin-right:6px;"></span>';
  }

  function renderRows(items) {
    var tbody = document.getElementById('issueRows');
    if (!items.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="j-empty">Sonuç bulunamadı.</td></tr>';
      return;
    }
    var ui = window.MokaUI;
    tbody.innerHTML = items.map(function (t) {
      var assignee = t.assignee_user
        ? ui.avatar(t.assignee_user.slice(0, 1).toUpperCase(), t.assignee_user, 'sm')
        : ui.avatar(null, null, 'sm', true);
      return '<tr class="j-list-row" data-id="' + t.id + '" style="border-bottom:1px solid var(--j-border);cursor:pointer;">' +
        '<td style="padding:8px 12px;">' + ui.typeIcon(t.issuetype) + '</td>' +
        '<td style="padding:8px 12px;">' +
          '<div style="font-family:var(--j-font-mono);font-size:12px;color:var(--j-text-subtlest);">' + t.key + '</div>' +
          '<div>' + ui.esc(t.summary) + '</div>' +
          (t.labels && t.labels.length ? '<div style="margin-top:4px;">' + t.labels.map(ui.tag).join(' ') + '</div>' : '') +
        '</td>' +
        '<td style="padding:8px 12px;">' + ui.priorityIcon(t.priority, t.priority_label) + '</td>' +
        '<td style="padding:8px 12px;">' + ui.lozenge(t.status_category, t.status_label) + '</td>' +
        '<td style="padding:8px 12px;">' + assignee + '</td>' +
        '<td style="padding:8px 12px;font-size:12px;">' + sla_dot(t.sla_state) + t.sla_remaining + '</td>' +
        '<td style="padding:8px 12px;font-size:12px;color:var(--j-text-subtlest);">' + ui.fmtDateTime(t.createdAt) + '</td>' +
        '</tr>';
    }).join('');
    Array.prototype.forEach.call(tbody.querySelectorAll('.j-list-row'), function (row) {
      row.addEventListener('click', function () {
        window.location.href = 'issue.html?id=' + row.dataset.id;
      });
    });
  }

  function renderPagination(total, totalPages) {
    var el = document.getElementById('pagination');
    if (totalPages <= 1) { el.innerHTML = ''; return; }
    var html = '';
    for (var i = 1; i <= totalPages; i++) {
      html += '<button class="j-btn j-btn-sm ' + (i === page ? 'j-btn-primary' : 'j-btn-default') + '" data-page="' + i + '">' + i + '</button>';
    }
    el.innerHTML = html;
    Array.prototype.forEach.call(el.querySelectorAll('button'), function (b) {
      b.addEventListener('click', function () { page = parseInt(b.dataset.page, 10); load(); });
    });
  }

  function load() {
    var filters = currentFilters();
    fetch(api('/api/issues?' + buildQuery(filters)))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        renderRows(d.items);
        renderPagination(d.total, d.totalPages);
      });
  }

  function wireFilters() {
    ['fStatus', 'fIssuetype', 'fPriority', 'fCategory', 'fTeam', 'fSla'].forEach(function (id) {
      document.getElementById(id).addEventListener('change', function () { page = 1; load(); });
    });
    var searchTimer;
    document.getElementById('fSearch').addEventListener('input', function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(function () { page = 1; load(); }, 250);
    });
    document.getElementById('fClear').addEventListener('click', function () {
      ['fStatus', 'fIssuetype', 'fPriority', 'fCategory', 'fTeam', 'fSla'].forEach(function (id) { document.getElementById(id).value = ''; });
      document.getElementById('fSearch').value = '';
      page = 1; load();
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    window.MokaShell.init('list');
    var initialQ = qs.get('q');
    loadMeta().then(function () {
      if (initialQ) document.getElementById('fSearch').value = initialQ;
      wireFilters();
      load();
    });
    document.addEventListener('j:issue-created', load);
  });
})();
