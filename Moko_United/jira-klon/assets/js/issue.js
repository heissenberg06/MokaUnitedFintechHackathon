(function () {
  var META = null;
  var ISSUE = null;
  var id = new URLSearchParams(window.location.search).get('id');
  var activeTab = 'comments';

  function api(path, opts) { return fetch(path, opts); }

  function patch(body) {
    return api('/api/issues/' + id, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    }).then(function (r) {
      return r.json().then(function (d) {
        if (!r.ok) { window.MokaUI.toast(d.error || 'Güncelleme başarısız.', true); return load(); }
        ISSUE = d; render();
        window.MokaUI.toast('Kaydedildi');
      });
    });
  }

  function load() {
    return api('/api/issues/' + id).then(function (r) {
      if (!r.ok) {
        document.getElementById('issueBody').innerHTML = '<div class="j-empty">Talep bulunamadı.</div>';
        throw new Error('not_found');
      }
      return r.json();
    }).then(function (d) { ISSUE = d; render(); });
  }

  function fieldRow(label, valueHtml) {
    return '<div class="j-field-row"><div class="j-field-label">' + label + '</div>' + valueHtml + '</div>';
  }

  function renderSide() {
    var ui = window.MokaUI;
    var t = ISSUE;
    var html = '<div class="j-panel">';
    html += '<div class="j-heading-xxs" style="margin-bottom:16px;">Ayrıntılar</div>';

    // Durum
    html += fieldRow('Durum',
      '<div class="j-field-value" id="fldStatus" role="button" tabindex="0" style="cursor:pointer;">' + ui.lozenge(t.status_category, t.status_label) + '</div>');

    // Öncelik
    html += fieldRow('Öncelik',
      '<div class="j-field-value" id="fldPriority" role="button" tabindex="0" style="cursor:pointer;gap:6px;">' + ui.priorityIcon(t.priority, t.priority_label) + ' ' + ui.esc(t.priority_label) + '</div>');

    // Atanan
    var assigneeDisplay = t.assignee_user
      ? ui.avatar(t.assignee_user.slice(0, 1).toUpperCase(), t.assignee_user, 'sm') + ' ' + ui.esc(t.assignee_user)
      : ui.avatar(null, null, 'sm', true) + ' <span class="j-text-subtlest">Atanmamış</span>';
    html += fieldRow('Atanan', '<div class="j-field-value" id="fldAssignee" role="button" tabindex="0" style="cursor:pointer;gap:6px;">' + assigneeDisplay + '</div>');

    // Bildiren (read-only)
    html += fieldRow('Bildiren',
      '<div class="j-field-value" style="gap:6px;">' + ui.avatar(t.reporter_initials, t.reporter_name, 'sm') + ' ' + ui.esc(t.reporter_name) + '</div>');

    // Ekip
    html += fieldRow('Ekip', '<div class="j-field-value" id="fldTeam" role="button" tabindex="0" style="cursor:pointer;">' + ui.esc(t.assignee_team) + '</div>');

    // Etiketler
    var labelsHtml = t.labels && t.labels.length ? t.labels.map(ui.tag).join(' ') : '<span class="j-text-subtlest">Etiket yok</span>';
    html += fieldRow('Etiketler', '<div class="j-field-value" id="fldLabels" role="button" tabindex="0" style="cursor:pointer;">' + labelsHtml + '</div>');

    // Puan
    html += fieldRow('Puan (Story Points)',
      '<div class="j-field-value" id="fldPoints" role="button" tabindex="0" style="cursor:pointer;">' + (t.story_points != null ? t.story_points : '<span class="j-text-subtlest">—</span>') + '</div>');

    // SLA
    var slaColor = t.sla_state === 'breach' ? 'var(--j-icon-red)' : t.sla_state === 'risk' ? 'var(--j-icon-orange)' : 'var(--j-icon-green)';
    html += fieldRow('SLA',
      '<div class="j-field-value" style="gap:6px;">' +
        '<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:' + slaColor + ';"></span>' +
        ui.esc(t.sla_remaining) + '</div>');

    // Kaynak
    html += fieldRow('Kaynak', '<div class="j-field-value">' + ui.esc(t.source_label || t.source) + '</div>');

    if (t.merchant) {
      html += fieldRow('İşyeri', '<div class="j-field-value">' + ui.esc(t.merchant) + '</div>');
    }

    html += '</div>';

    // Onaylar
    if (t.approvals && t.approvals.length) {
      html += '<div class="j-panel" style="margin-top:16px;"><div class="j-heading-xxs" style="margin-bottom:12px;">Onaylar</div>';
      t.approvals.forEach(function (a, idx) {
        var stateLabel = { onaylandi: 'Onaylandı', reddedildi: 'Reddedildi', bekliyor: 'Bekliyor' }[a.state];
        var cat = a.state === 'onaylandi' ? 'success' : a.state === 'reddedildi' ? 'removed' : 'default';
        html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;">' +
          '<span>' + ui.esc(a.role) + '</span>' + ui.lozenge(cat, stateLabel) + '</div>';
        if (a.state === 'bekliyor') {
          html += '<div style="display:flex;gap:8px;margin-top:4px;">' +
            '<button class="j-btn j-btn-sm" style="background:var(--j-success-bg-bold);color:#fff;" data-approve="' + idx + '">Onayla</button>' +
            '<button class="j-btn j-btn-sm j-btn-danger" data-reject="' + idx + '">Reddet</button></div>';
        }
      });
      html += '</div>';
    }

    // zaman damgaları
    html += '<div style="margin-top:16px;font-size:12px;color:var(--j-text-subtlest);">' +
      'Oluşturuldu: ' + ui.fmtDateTime(t.createdAt) + '<br>' +
      (t.resolved_at ? 'Çözüldü: ' + ui.fmtDateTime(t.resolved_at) : '') +
      '</div>';

    return html;
  }

  function renderMain() {
    var ui = window.MokaUI;
    var t = ISSUE;
    var html = '<div class="j-panel">';
    html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">' +
      ui.typeIcon(t.issuetype) + '<span class="j-text-subtlest" style="font-family:var(--j-font-mono);font-size:12px;">' + t.key + '</span></div>';
    html += '<div class="j-field-value j-heading-m" id="fldSummary" role="button" tabindex="0" style="cursor:pointer;padding:4px 8px;">' + ui.esc(t.summary) + '</div>';

    html += '<div class="j-heading-xxs" style="margin:20px 0 8px;">Açıklama</div>';
    html += '<div class="j-field-value j-desc-block" id="fldDescription" role="button" tabindex="0" style="cursor:pointer;min-height:60px;">' + ui.esc(t.description) + '</div>';

    // Ekler
    html += '<div class="j-heading-xxs" style="margin:20px 0 8px;">Ekler (' + (t.attachments ? t.attachments.length : 0) + ')</div>';
    html += '<div id="attachmentList">' + (t.attachments || []).map(function (a) {
      return '<div class="j-attachment-row">📎 ' + ui.esc(a.name) + '<span class="j-text-subtlest" style="font-size:12px;"> — ' + ui.fmtDateTime(a.addedAt) + '</span></div>';
    }).join('') + '</div>';
    html += '<div style="display:flex;gap:8px;margin-top:8px;">' +
      '<input type="text" class="j-input" id="attachmentName" placeholder="Ek adı (ör. dekont.pdf)" style="max-width:260px;">' +
      '<button class="j-btn j-btn-default j-btn-sm" id="attachmentAdd">Ekle</button></div>';

    // Alt görevler
    html += '<div class="j-heading-xxs" style="margin:20px 0 8px;">Alt Görevler</div>';
    html += '<div id="subtaskList">' + (t.tasks || []).map(function (task, idx) {
      return '<div class="j-subtask-row' + (task.done ? ' done' : '') + '">' +
        '<input type="checkbox" data-task-idx="' + idx + '"' + (task.done ? ' checked' : '') + '>' +
        '<span class="j-subtask-title">' + ui.esc(task.title) + '</span></div>';
    }).join('') + '</div>';

    html += '</div>'; // .j-panel

    // Aktivite
    html += '<div class="j-panel" style="margin-top:16px;">';
    html += '<div class="j-tabs">' +
      '<div class="j-tab' + (activeTab === 'comments' ? ' j-active' : '') + '" data-tab="comments">Yorumlar</div>' +
      '<div class="j-tab' + (activeTab === 'history' ? ' j-active' : '') + '" data-tab="history">Geçmiş</div>' +
      '</div>';
    html += '<div id="tabBody">' + renderTabBody() + '</div>';
    html += '</div>';

    return html;
  }

  function renderTabBody() {
    var ui = window.MokaUI;
    var t = ISSUE;
    if (activeTab === 'comments') {
      var notes = (t.timeline || []).filter(function (e) { return e.type === 'not'; });
      var html = '<div style="display:flex;gap:8px;margin-bottom:16px;">' +
        '<input type="text" class="j-input" id="noteInput" placeholder="Bir not ekleyin...">' +
        '<button class="j-btn j-btn-default j-btn-sm" id="noteAdd">Ekle</button></div>';
      if (!notes.length) {
        html += '<div class="j-text-subtlest" style="font-size:13px;">Henüz yorum yok.</div>';
      } else {
        html += notes.slice().reverse().map(function (n) {
          return '<div class="j-timeline-item"><div style="flex:1;"><b>' + ui.esc(n.actor) + '</b> — ' + ui.esc(n.note) +
            '<div class="j-text-subtlest" style="font-size:11px;">' + ui.fmtDateTime(n.at) + '</div></div></div>';
        }).join('');
      }
      return html;
    }
    // history
    var items = (t.timeline || []).slice().reverse();
    if (!items.length) return '<div class="j-text-subtlest" style="font-size:13px;">Geçmiş yok.</div>';
    return items.map(function (e) {
      return '<div class="j-timeline-item"><div style="flex:1;"><b>' + ui.esc(e.actor) + '</b> — ' + ui.esc(e.note) +
        '<div class="j-text-subtlest" style="font-size:11px;">' + ui.fmtDateTime(e.at) + '</div></div></div>';
    }).join('');
  }

  function render() {
    document.getElementById('crumbKey').textContent = ISSUE.key;
    document.title = ISSUE.key + ' · ' + ISSUE.summary + ' | Moka Akış';
    var banner = document.getElementById('issueBanner');
    banner.innerHTML = ISSUE.sla_state === 'breach'
      ? '<div class="j-banner j-banner-danger">Bu talep SLA süresini aştı. Öncelikli müdahale gerekiyor.</div>'
      : ISSUE.sla_state === 'risk'
      ? '<div class="j-banner j-banner-warning">SLA süresi dolmak üzere.</div>' : '';

    var body = document.getElementById('issueBody');
    body.innerHTML =
      '<div class="j-issue-main">' + renderMain() + '</div>' +
      '<div class="j-issue-side">' + renderSide() + '</div>';

    wireInteractions();
  }

  function openInlineSelect(fieldEl, options, currentVal, onPick) {
    var select = document.createElement('select');
    select.className = 'j-select';
    options.forEach(function (opt) {
      var o = document.createElement('option');
      o.value = opt[0]; o.textContent = opt[1];
      if (opt[0] === currentVal) o.selected = true;
      select.appendChild(o);
    });
    fieldEl.innerHTML = '';
    fieldEl.appendChild(select);
    fieldEl.classList.add('j-field-editing');
    select.focus();
    function commit() {
      var v = select.value;
      if (v !== currentVal) onPick(v); else render();
    }
    select.addEventListener('change', commit);
    select.addEventListener('blur', function () { setTimeout(function () { if (document.body.contains(select)) render(); }, 150); });
  }

  function openInlineText(fieldEl, currentVal, onSave, isTextarea) {
    var input = document.createElement(isTextarea ? 'textarea' : 'input');
    if (!isTextarea) input.type = 'text';
    input.className = isTextarea ? 'j-textarea' : 'j-input';
    input.value = currentVal || '';
    fieldEl.innerHTML = '';
    fieldEl.appendChild(input);
    fieldEl.classList.add('j-field-editing');
    input.focus();
    function commit() {
      var v = input.value.trim();
      if (v !== (currentVal || '')) onSave(v); else render();
    }
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !isTextarea) { e.preventDefault(); commit(); }
      if (e.key === 'Escape') render();
    });
    input.addEventListener('blur', commit);
  }

  // Fare click'i ve klavye (Enter/Space) etkinleştirmesini tek noktadan bağlar (a11y, bkz. §11.1 F2).
  function onActivate(el, handler) {
    el.addEventListener('click', handler);
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
        e.preventDefault();
        handler.call(el, e);
      }
    });
  }

  function wireInteractions() {
    var t = ISSUE;

    onActivate(document.getElementById('fldStatus'), function () {
      var allowed = META.allowed_transitions[t.status] || [];
      var options = [[t.status, t.status_label]].concat(allowed.map(function (s) { return [s, META.status_label[s]]; }));
      openInlineSelect(this, options, t.status, function (v) { patch({ status: v }); });
    });

    onActivate(document.getElementById('fldPriority'), function () {
      openInlineSelect(this, META.priorities.map(function (p) { return [p, META.priority_label[p]]; }), t.priority, function (v) { patch({ priority: v }); });
    });

    onActivate(document.getElementById('fldAssignee'), function () {
      openInlineText(this, t.assignee_user || '', function (v) { patch({ assignee_user: v }); });
    });

    onActivate(document.getElementById('fldTeam'), function () {
      openInlineSelect(this, META.teams.map(function (tm) { return [tm, tm]; }), t.assignee_team, function (v) { patch({ assignee_team: v }); });
    });

    onActivate(document.getElementById('fldLabels'), function () {
      openInlineText(this, (t.labels || []).join(', '), function (v) {
        var labels = v ? v.split(',').map(function (s) { return s.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, ''); }).filter(Boolean) : [];
        patch({ labels: labels });
      });
    });

    onActivate(document.getElementById('fldPoints'), function () {
      openInlineText(this, t.story_points != null ? String(t.story_points) : '', function (v) {
        patch({ story_points: v === '' ? null : v });
      });
    });

    onActivate(document.getElementById('fldSummary'), function () {
      openInlineText(this, t.summary, function (v) {
        if (v.length < 10) { alert('Özet en az 10 karakter olmalı.'); return render(); }
        patch({ summary: v });
      });
    });

    onActivate(document.getElementById('fldDescription'), function () {
      openInlineText(this, t.description, function (v) {
        if (v.length < 20) { alert('Açıklama en az 20 karakter olmalı.'); return render(); }
        patch({ description: v });
      }, true);
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-task-idx]'), function (cb) {
      cb.addEventListener('change', function () {
        var idx = parseInt(cb.dataset.taskIdx, 10);
        api('/api/issues/' + id + '/tasks/' + idx, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ done: cb.checked }),
        }).then(function (r) { return r.json(); }).then(function (d) { ISSUE = d; render(); });
      });
    });

    document.getElementById('attachmentAdd').addEventListener('click', function () {
      var input = document.getElementById('attachmentName');
      var name = input.value.trim();
      if (name.length < 2) { alert('Ek adı en az 2 karakter olmalı.'); return; }
      api('/api/issues/' + id + '/attachments', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name }),
      }).then(function (r) { return r.json(); }).then(function (d) { ISSUE = d; render(); });
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-approve]'), function (btn) {
      btn.addEventListener('click', function () {
        api('/api/issues/' + id + '/approvals/' + btn.dataset.approve, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ state: 'onaylandi' }),
        }).then(function (r) { return r.json(); }).then(function (d) { ISSUE = d; render(); });
      });
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-reject]'), function (btn) {
      btn.addEventListener('click', function () {
        api('/api/issues/' + id + '/approvals/' + btn.dataset.reject, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ state: 'reddedildi' }),
        }).then(function (r) { return r.json(); }).then(function (d) { ISSUE = d; render(); });
      });
    });

    Array.prototype.forEach.call(document.querySelectorAll('[data-tab]'), function (tab) {
      tab.addEventListener('click', function () { activeTab = tab.dataset.tab; render(); });
    });

    var noteAdd = document.getElementById('noteAdd');
    if (noteAdd) {
      noteAdd.addEventListener('click', function () {
        var input = document.getElementById('noteInput');
        var text = input.value.trim();
        if (text.length < 3) { alert('Not en az 3 karakter olmalı.'); return; }
        api('/api/issues/' + id + '/notes', {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ note: text }),
        }).then(function (r) { return r.json(); }).then(function (d) { ISSUE = d; render(); });
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    window.MokaShell.init('list');
    fetch('/api/meta').then(function (r) { return r.json(); }).then(function (m) {
      META = m;
      load();
    });
  });
})();
