(function () {
  var META = null;

  function loadMeta() {
    return fetch('/api/meta').then(function (r) { return r.json(); }).then(function (m) { META = m; return m; });
  }

  function loadIssues() {
    // Board: tüm talepleri tek seferde çek (sayfalama yok, demo hacmi küçük).
    return fetch('/api/issues?page=1&pageSize=200').then(function (r) { return r.json(); });
  }

  function renderCard(t) {
    var ui = window.MokaUI;
    var assignee = t.assignee_user
      ? ui.avatar(t.assignee_user.slice(0, 1).toUpperCase(), t.assignee_user, 'sm')
      : ui.avatar(null, null, 'sm', true);
    return '<div class="j-card" data-id="' + t.id + '">' +
      '<div class="j-card-summary">' + ui.esc(t.summary) + '</div>' +
      (t.labels && t.labels.length ? '<div style="margin-bottom:8px;">' + t.labels.map(ui.tag).join(' ') + '</div>' : '') +
      '<div class="j-card-footer">' +
        ui.typeIcon(t.issuetype) +
        '<span class="j-card-key">' + t.key + '</span>' +
        '<span class="j-status-menu-anchor" data-status-anchor="' + t.id + '" style="margin-left:4px;">' +
          '<button class="j-btn j-btn-subtle j-btn-sm" style="height:22px;padding:0 6px;" data-status-btn="' + t.id + '">⋯</button>' +
        '</span>' +
        '<span class="j-card-spacer"></span>' +
        ui.priorityIcon(t.priority, t.priority_label) +
        assignee +
      '</div>' +
    '</div>';
  }

  function render(data) {
    var body = document.getElementById('boardBody');
    var byStatus = {};
    META.statuses.forEach(function (s) { byStatus[s] = []; });
    data.items.forEach(function (t) { (byStatus[t.status] || (byStatus[t.status] = [])).push(t); });

    var html = '<div class="j-board-wrap">';
    META.statuses.forEach(function (s) {
      var items = byStatus[s] || [];
      html += '<div class="j-board-col" data-col="' + s + '">' +
        '<div class="j-board-col-head"><span>' + META.status_label[s] + '</span><span class="j-board-col-count">' + items.length + '</span></div>' +
        '<div class="j-board-col-body">' +
          items.map(renderCard).join('') +
        '</div></div>';
    });
    html += '</div>';
    body.innerHTML = html;

    Array.prototype.forEach.call(body.querySelectorAll('.j-card'), function (card) {
      card.addEventListener('click', function (e) {
        if (e.target.closest('[data-status-btn]')) return;
        window.location.href = 'issue.html?id=' + card.dataset.id;
      });
    });
    Array.prototype.forEach.call(body.querySelectorAll('[data-status-btn]'), function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        openStatusMenu(btn, parseInt(btn.dataset.statusBtn, 10));
      });
    });
  }

  function closeMenus() {
    Array.prototype.forEach.call(document.querySelectorAll('.j-dropdown-panel'), function (m) { m.remove(); });
  }

  function openStatusMenu(btn, issueId) {
    closeMenus();
    var issue = window._boardData.items.find(function (t) { return t.id === issueId; });
    if (!issue) return;
    var allowed = META.allowed_transitions[issue.status] || [];
    var rect = btn.getBoundingClientRect();
    var menu = document.createElement('div');
    menu.className = 'j-dropdown-panel';
    menu.style.top = (rect.bottom + window.scrollY + 4) + 'px';
    menu.style.left = (rect.left + window.scrollX) + 'px';
    if (!allowed.length) {
      menu.innerHTML = '<div class="j-dropdown-item" style="color:var(--j-text-subtlest);">Geçiş yok</div>';
    } else {
      menu.innerHTML = allowed.map(function (s) {
        return '<div class="j-dropdown-item" data-target-status="' + s + '">' + META.status_label[s] + '</div>';
      }).join('');
    }
    document.body.appendChild(menu);
    Array.prototype.forEach.call(menu.querySelectorAll('[data-target-status]'), function (item) {
      item.addEventListener('click', function () {
        moveIssue(issueId, item.dataset.targetStatus);
        closeMenus();
      });
    });
    setTimeout(function () {
      document.addEventListener('click', closeMenus, { once: true });
    }, 0);
  }

  function moveIssue(id, status) {
    fetch('/api/issues/' + id, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: status }),
    }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) { window.MokaUI.toast(res.d.error || 'Durum güncellenemedi.', true); }
        else { window.MokaUI.toast('Durum güncellendi'); }
        refresh();
      });
  }

  function refresh() {
    loadIssues().then(function (data) {
      window._boardData = data;
      render(data);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    window.MokaShell.init('board');
    loadMeta().then(refresh);
    document.addEventListener('j:issue-created', refresh);
  });
})();
