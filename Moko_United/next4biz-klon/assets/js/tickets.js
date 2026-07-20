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

  var state = { page: 1, meta: null };

  function fmtDate(iso) {
    if (!iso) return '—';
    var d = new Date(iso);
    return d.toLocaleDateString('tr-TR') + ' ' + d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  }

  function badge(cls, text) {
    return '<span class="n4b-badge ' + cls + '">' + text + '</span>';
  }

  function buildQuery() {
    var p = new URLSearchParams();
    p.set('page', state.page);
    var q = $('#fSearch').value.trim();
    if (q) p.set('q', q);
    ['fStatus', 'fCategory', 'fTeam', 'fSla', 'fSource'].forEach(function (id) {
      var el = document.getElementById(id);
      var key = { fStatus: 'status', fCategory: 'category', fTeam: 'team', fSla: 'sla', fSource: 'source' }[id];
      if (el.value) p.set(key, el.value);
    });
    return p.toString();
  }

  function loadMeta() {
    return fetch('/api/meta').then(function (r) { return r.json(); }).then(function (m) {
      state.meta = m;
      var fStatus = $('#fStatus'), fCategory = $('#fCategory'), fTeam = $('#fTeam');
      m.statuses.forEach(function (s) {
        fStatus.appendChild(new Option(m.status_label[s], s));
      });
      m.categories.forEach(function (c) {
        fCategory.appendChild(new Option(c, c));
      });
      m.teams.forEach(function (t) {
        fTeam.appendChild(new Option(t, t));
      });
      var ntCategory = $('#ntCategory'), ntPriority = $('#ntPriority'), ntSource = $('#ntSource');
      m.categories.forEach(function (c) { ntCategory.appendChild(new Option(c, c)); });
      m.priorities.forEach(function (p) { ntPriority.appendChild(new Option(m.priority_label[p], p)); });
      var srcLabel = { ai: 'Yapay Zeka', 'self-service': 'Self-Servis', email: 'E-posta', chat: 'Canlı Destek', whatsapp: 'WhatsApp' };
      m.sources.forEach(function (s) { ntSource.appendChild(new Option(srcLabel[s] || s, s)); });
    });
  }

  function renderRows(items) {
    var tbody = $('#ticketRows');
    tbody.innerHTML = '';
    if (!items.length) {
      tbody.appendChild(el('tr', null, '<td colspan="7" class="n4b-empty">Filtreyle eşleşen talep bulunamadı.</td>'));
      return;
    }
    items.forEach(function (t) {
      var tr = el('tr', 'n4b-row-link');
      tr.innerHTML =
        '<td class="n4b-tid">#' + t.id + '</td>' +
        '<td><div class="n4b-ttitle">' + t.title + '</div>' +
        '<div class="n4b-tmeta">' + t.category + (t.merchant ? ' · ' + t.merchant : '') + '</div></td>' +
        '<td>' + badge(PRIORITY_BADGE[t.priority] || '', t.priority_label) + '</td>' +
        '<td>' + badge(STATUS_BADGE[t.status] || '', t.status_label) + '</td>' +
        '<td style="font-size:12.5px;">' + t.assignee_team + '</td>' +
        '<td>' + badge(SLA_BADGE[t.sla_state] || '', t.sla_remaining) + '</td>' +
        '<td style="font-size:12px;color:var(--n4b-slate-500);">' + fmtDate(t.createdAt) + '</td>';
      tr.addEventListener('click', function () {
        window.location.href = 'ticket.html?id=' + t.id;
      });
      tbody.appendChild(tr);
    });
  }

  function renderPagination(data) {
    var wrap = $('#pagination');
    wrap.innerHTML = '';
    if (data.totalPages <= 1) return;
    var prev = el('button', null, '‹ Önceki');
    prev.disabled = data.page <= 1;
    prev.addEventListener('click', function () { state.page--; load(); });
    wrap.appendChild(prev);
    wrap.appendChild(el('span', null, 'Sayfa ' + data.page + ' / ' + data.totalPages + ' · ' + data.total + ' talep'));
    var next = el('button', null, 'Sonraki ›');
    next.disabled = data.page >= data.totalPages;
    next.addEventListener('click', function () { state.page++; load(); });
    wrap.appendChild(next);
  }

  function load() {
    fetch('/api/tickets?' + buildQuery()).then(function (r) { return r.json(); }).then(function (data) {
      renderRows(data.items);
      renderPagination(data);
    }).catch(function (e) {
      $('#ticketRows').innerHTML = '<tr><td colspan="7" class="n4b-empty">Veri alınamadı: ' + e.message + '</td></tr>';
    });
  }

  var searchTimer = null;
  function onFilterChange() { state.page = 1; load(); }
  ['fStatus', 'fCategory', 'fTeam', 'fSla', 'fSource'].forEach(function (id) {
    document.getElementById(id).addEventListener('change', onFilterChange);
  });
  $('#fSearch').addEventListener('input', function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(onFilterChange, 300);
  });
  $('#fClear').addEventListener('click', function () {
    $('#fSearch').value = '';
    ['fStatus', 'fCategory', 'fTeam', 'fSla', 'fSource'].forEach(function (id) { document.getElementById(id).value = ''; });
    onFilterChange();
  });

  var toggle = $('#newTicketToggle'), form = $('#newTicketForm'), chevron = $('#newTicketChevron');
  toggle.addEventListener('click', function () {
    var open = form.style.display !== 'none';
    form.style.display = open ? 'none' : 'block';
    chevron.textContent = open ? '▾' : '▴';
  });

  $('#newTicketForm').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('#ntMsg');
    msg.innerHTML = '';
    var payload = {
      requester_name: $('#ntName').value,
      title: $('#ntTitle').value,
      body: $('#ntBody').value,
      category: $('#ntCategory').value,
      priority: $('#ntPriority').value,
      source: $('#ntSource').value,
      merchant: $('#ntMerchant').value,
    };
    fetch('/api/tickets', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    }).then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (res) {
        if (!res.ok) {
          msg.innerHTML = '<div class="n4b-form-err">' + (res.d.error || 'Talep oluşturulamadı.') + '</div>';
          return;
        }
        msg.innerHTML = '<div class="n4b-form-ok">Talep #' + res.d.id + ' oluşturuldu ve ' + res.d.assignee_team + ' ekibine yönlendirildi.</div>';
        $('#newTicketForm').reset();
        state.page = 1;
        load();
      }).catch(function (e) {
        msg.innerHTML = '<div class="n4b-form-err">Bağlantı hatası: ' + e.message + '</div>';
      });
  });

  loadMeta().then(load);
})();
