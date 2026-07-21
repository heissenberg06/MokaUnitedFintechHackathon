(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var el = function (t, cls, html) {
    var e = document.createElement(t);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  };

  var STATUS_BADGE = {
    'yeni': 'n4b-badge-info', 'siniflandirildi': 'n4b-badge-info',
    'atandi': 'n4b-badge-neutral', 'islemde': 'n4b-badge-info',
    'beklemede': 'n4b-badge-risk', 'cozuldu': 'n4b-badge-ok',
    'kapandi': 'n4b-badge-neutral', 'yeniden-acildi': 'n4b-badge-breach',
  };
  var PRIORITY_BADGE = {
    'dusuk': 'n4b-badge-neutral', 'orta': 'n4b-badge-info',
    'yuksek': 'n4b-badge-risk', 'kritik': 'n4b-badge-breach',
  };
  var SLA_BADGE = { 'ok': 'n4b-badge-ok', 'risk': 'n4b-badge-risk', 'breach': 'n4b-badge-breach' };
  var SENTIMENT_BADGE = { 'ofkeli': 'n4b-badge-breach', 'olumsuz': 'n4b-badge-risk', 'notr': 'n4b-badge-neutral', 'olumlu': 'n4b-badge-ok' };
  var SRC_LABEL = { ai: 'Yapay Zeka', 'self-service': 'Self-Servis', email: 'E-posta', chat: 'Canlı Destek', whatsapp: 'WhatsApp' };
  var MAIN_FLOW = ['yeni', 'siniflandirildi', 'atandi', 'islemde', 'cozuldu', 'kapandi'];

  function badge(cls, text) { return '<span class="n4b-badge ' + cls + '">' + text + '</span>'; }
  function fmtDateTime(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    return d.toLocaleDateString('tr-TR') + ' ' + d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  }

  var id = new URLSearchParams(window.location.search).get('id');
  var meta = null;

  function stepperHtml(status) {
    var idx = MAIN_FLOW.indexOf(status);
    var offBranch = idx === -1; // beklemede / yeniden-acildi
    var labels = { yeni: 'Yeni', siniflandirildi: 'Sınıflandırıldı', atandi: 'Atandı', islemde: 'İşlemde', cozuldu: 'Çözüldü', kapandi: 'Kapandı' };
    var html = '<div class="n4b-stepper">';
    MAIN_FLOW.forEach(function (s, i) {
      var cls = i < idx || (offBranch && i <= 3) ? 'done' : (i === idx ? 'current' : '');
      html += '<div class="n4b-step ' + cls + '"><span class="n4b-step-dot">' + (cls === 'done' ? '✓' : (i + 1)) + '</span><span class="n4b-step-lbl">' + labels[s] + '</span></div>';
      if (i < MAIN_FLOW.length - 1) html += '<div class="n4b-step-line"></div>';
    });
    html += '</div>';
    if (offBranch) {
      html = '<div style="margin-bottom:10px;">' + badge(STATUS_BADGE[status], meta.status_label[status]) + ' <span style="font-size:12px;color:var(--n4b-slate-500);">— ana akıştan ayrı bir durumda</span></div>' + html;
    }
    return html;
  }

  function render(t) {
    var c = el('div');

    var head = el('div', 'n4b-detail-head');
    head.innerHTML =
      '<div style="display:flex;gap:14px;align-items:flex-start;">' +
      '<span class="n4b-avatar n4b-avatar-lg" title="' + t.requester_name + '">' + t.requester_initials + '</span>' +
      '<div><h1>#' + t.id + ' — ' + t.title + '</h1>' +
      '<div class="n4b-detail-meta">' +
      '<span>' + t.category + '</span>' +
      (t.merchant ? '<span class="sep">·</span><span>' + t.merchant + '</span>' : '') +
      '<span class="sep">·</span><span>' + SRC_LABEL[t.source] + '</span>' +
      '<span class="sep">·</span><span>' + t.requester_name + '</span>' +
      '<span class="sep">·</span><span>' + fmtDateTime(t.createdAt) + '</span>' +
      '</div></div></div>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap;">' + badge(PRIORITY_BADGE[t.priority], t.priority_label) +
      badge(SLA_BADGE[t.sla_state], t.sla_remaining) +
      badge(SENTIMENT_BADGE[t.sentiment] || 'n4b-badge-neutral', (meta.sentiment_label && meta.sentiment_label[t.sentiment]) || t.sentiment) + '</div>';
    c.appendChild(head);

    var stepperWrap = el('div');
    stepperWrap.innerHTML = stepperHtml(t.status);
    c.appendChild(stepperWrap);

    var grid = el('div', 'n4b-detail-grid');

    // --- sol: gövde + zaman çizelgesi ---
    var left = el('div');
    var bodyCard = el('div', 'n4b-panel');
    bodyCard.innerHTML = '<div class="n4b-panel-h"><h3>Talep Açıklaması</h3></div><div class="n4b-body-text">' + t.body + '</div>';
    left.appendChild(bodyCard);

    var tlCard = el('div', 'n4b-panel');
    tlCard.style.marginTop = '20px';
    var tlList = el('ul', 'n4b-timeline');
    (t.timeline || []).slice().reverse().forEach(function (e) {
      var li = el('li', 'n4b-tl-item');
      li.innerHTML = '<div class="n4b-tl-actor">' + e.actor + '</div><div class="n4b-tl-note">' + e.note + '</div><div class="n4b-tl-at">' + fmtDateTime(e.at) + '</div>';
      tlList.appendChild(li);
    });
    tlCard.innerHTML = '<div class="n4b-panel-h"><h3>Zaman Çizelgesi</h3></div>';
    tlCard.appendChild(tlList);
    var noteForm = el('form', 'n4b-note-form');
    noteForm.innerHTML = '<input type="text" id="noteInput" placeholder="Not ekle..." maxlength="500"><button type="submit">Ekle</button>';
    tlCard.appendChild(noteForm);
    left.appendChild(tlCard);
    grid.appendChild(left);

    // --- sağ: yönetim paneli ---
    var right = el('div', 'n4b-panel');
    var slaCls = t.sla_state;
    right.innerHTML =
      '<div class="n4b-side-block"><div class="n4b-side-lbl">SLA</div><div class="n4b-sla-box ' + slaCls + '"><div class="n4b-sla-val">' + t.sla_remaining + '</div>' +
      '<div style="font-size:11px;color:var(--n4b-slate-600);margin-top:2px;">Son tarih: ' + fmtDateTime(t.sla_due_at) + '</div></div></div>' +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Durum</div><select id="selStatus"></select></div>' +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Öncelik</div><select id="selPriority"></select></div>' +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Atanan Ekip</div><select id="selTeam"></select></div>' +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Atanan Kişi</div><input type="text" id="inpAssignee" maxlength="60" placeholder="İsim girin (opsiyonel)" value="' + (t.assignee_user || '') + '"></div>' +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Görevler</div><div id="taskList"></div></div>' +
      (t.approvals && t.approvals.length ? '<div class="n4b-side-block"><div class="n4b-side-lbl">Onaylar</div><div id="approvalList"></div></div>' : '') +
      '<div class="n4b-side-block"><div class="n4b-side-lbl">Ekler</div><div id="attachList"></div>' +
      '<form id="attachForm" style="display:flex;gap:6px;margin-top:8px;">' +
      '<input type="text" id="attachInput" placeholder="Dosya/doküman adı..." maxlength="80" style="flex:1;">' +
      '<button type="submit" style="font-size:12px;font-weight:600;padding:8px 12px;border-radius:8px;background:var(--n4b-cyan);color:#fff;">Ekle</button>' +
      '</form></div>';
    grid.appendChild(right);

    c.appendChild(grid);

    var wrap = $('#ticketDetail');
    wrap.innerHTML = '';
    wrap.appendChild(c);

    // selects doldur
    var selStatus = $('#selStatus'), selPriority = $('#selPriority'), selTeam = $('#selTeam');
    var allowedNext = (meta.allowed_transitions && meta.allowed_transitions[t.status]) || [];
    selStatus.appendChild(new Option(meta.status_label[t.status], t.status, true, true));
    allowedNext.forEach(function (s) { selStatus.appendChild(new Option(meta.status_label[s], s)); });
    meta.priorities.forEach(function (p) { selPriority.appendChild(new Option(meta.priority_label[p], p, false, p === t.priority)); });
    meta.teams.forEach(function (tm) { selTeam.appendChild(new Option(tm, tm, false, tm === t.assignee_team)); });

    selStatus.addEventListener('change', function () { patch({ status: selStatus.value }); });
    selPriority.addEventListener('change', function () { patch({ priority: selPriority.value }); });
    selTeam.addEventListener('change', function () { patch({ assignee_team: selTeam.value }); });

    var inpAssignee = $('#inpAssignee');
    inpAssignee.addEventListener('change', function () { patch({ assignee_user: inpAssignee.value }); });

    var taskList = $('#taskList');
    (t.tasks || []).forEach(function (task, idx) {
      var row = el('label', 'n4b-task-item' + (task.done ? ' done' : ''));
      row.innerHTML = '<input type="checkbox" ' + (task.done ? 'checked' : '') + '><span>' + task.title + '</span>';
      row.querySelector('input').addEventListener('change', function (e) {
        fetch('/api/tickets/' + id + '/tasks/' + idx, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ done: e.target.checked }),
        }).then(function (r) { return r.json(); }).then(function (d) { render(d); });
      });
      taskList.appendChild(row);
    });

    if (t.approvals && t.approvals.length) {
      var apList = $('#approvalList');
      t.approvals.forEach(function (a, aIdx) {
        var row = el('div', 'n4b-approval-item');
        var cls = a.state === 'onaylandi' ? 'n4b-badge-ok' : (a.state === 'reddedildi' ? 'n4b-badge-breach' : 'n4b-badge-risk');
        var lbl = a.state === 'onaylandi' ? 'Onaylandı' : (a.state === 'reddedildi' ? 'Reddedildi' : 'Bekliyor');
        var actions = a.state === 'bekliyor'
          ? '<button type="button" class="n4b-approve-btn">Onayla</button><button type="button" class="n4b-reject-btn">Reddet</button>'
          : '';
        row.innerHTML = '<span>' + a.role + '</span><span class="n4b-approval-actions">' + badge(cls, lbl) + actions + '</span>';
        apList.appendChild(row);
        if (a.state === 'bekliyor') {
          row.querySelector('.n4b-approve-btn').addEventListener('click', function () { patchApproval(aIdx, 'onaylandi'); });
          row.querySelector('.n4b-reject-btn').addEventListener('click', function () { patchApproval(aIdx, 'reddedildi'); });
        }
      });
    }

    var attachList = $('#attachList');
    if (t.attachments && t.attachments.length) {
      t.attachments.forEach(function (a) {
        var row = el('div', 'n4b-task-item');
        row.innerHTML = '<span>📎 ' + a.name + '</span>';
        attachList.appendChild(row);
      });
    } else {
      attachList.innerHTML = '<div style="font-size:12px;color:var(--n4b-slate-500);">Henüz ek yok.</div>';
    }
    $('#attachForm').addEventListener('submit', function (e) {
      e.preventDefault();
      var input = $('#attachInput');
      var val = input.value.trim();
      if (val.length < 2) return;
      fetch('/api/tickets/' + id + '/attachments', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: val }),
      }).then(function (r) { return r.json(); }).then(function (d) { render(d); });
    });

    $('#noteInput').closest('form').addEventListener('submit', function (e) {
      e.preventDefault();
      var input = $('#noteInput');
      var val = input.value.trim();
      if (val.length < 3) return;
      fetch('/api/tickets/' + id + '/notes', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ note: val }),
      }).then(function (r) { return r.json(); }).then(function (d) { render(d); });
    });
  }

  function patch(payload) {
    fetch('/api/tickets/' + id, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) {
          alert(res.d.error || 'Güncelleme başarısız oldu.');
          load();
          return;
        }
        render(res.d);
      });
  }

  function patchApproval(idx, state) {
    fetch('/api/tickets/' + id + '/approvals/' + idx, {
      method: 'PATCH', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: state }),
    }).then(function (r) { return r.json(); }).then(function (d) { render(d); });
  }

  function load() {
    if (!id) {
      $('#ticketDetail').innerHTML = '<div class="n4b-empty">Talep kimliği belirtilmedi.</div>';
      return;
    }
    Promise.all([
      fetch('/api/meta').then(function (r) { return r.json(); }),
      fetch('/api/tickets/' + id).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); }),
    ]).then(function (res) {
      meta = res[0];
      if (!res[1].ok) {
        $('#ticketDetail').innerHTML = '<div class="n4b-empty">Talep bulunamadı (#' + id + ').</div>';
        return;
      }
      render(res[1].d);
    }).catch(function (e) {
      $('#ticketDetail').innerHTML = '<div class="n4b-empty">Veri alınamadı: ' + e.message + '</div>';
    });
  }

  load();
})();
