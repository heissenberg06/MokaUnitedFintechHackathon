(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var el = function (t, cls, html) {
    var e = document.createElement(t);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  };
  var num = function (n) { return n == null ? '—' : n.toLocaleString('tr-TR'); };

  function card(title, sub) {
    var c = el('div', 'n4b-panel');
    if (title) {
      var h = el('div', 'n4b-panel-h');
      h.innerHTML = '<h3>' + title + '</h3>' + (sub ? '<span class="n4b-panel-sub">' + sub + '</span>' : '');
      c.appendChild(h);
    }
    return c;
  }

  function kpiRow(k) {
    var wrap = el('div', 'n4b-kpi-row');
    wrap.style.marginBottom = '20px';
    var items = [
      ['Toplam Talep', num(k.total), 'tüm zamanlar'],
      ['Açık Talep', num(k.open), num(k.closed) + ' kapalı'],
      ['SLA Aşan', num(k.sla_breach), 'acil müdahale gerekli'],
      ['SLA Riskli', num(k.sla_risk), 'yakında aşılabilir'],
      ['Ort. Yaş', (k.avg_age_hours != null ? k.avg_age_hours : '—') + ' sa.', 'talep açık kalma süresi'],
    ];
    items.forEach(function (it) {
      var c = el('div', 'n4b-kpi');
      c.innerHTML = '<div class="n4b-kpi-val">' + it[1] + '</div><div class="n4b-kpi-lbl">' + it[0] + '</div><div class="n4b-kpi-sub">' + it[2] + '</div>';
      wrap.appendChild(c);
    });
    return wrap;
  }

  function barChart(rows, labelKey, countKey, dangerFn) {
    var wrap = el('div');
    var max = Math.max(1, Math.max.apply(null, rows.map(function (r) { return r[countKey]; })));
    rows.forEach(function (r) {
      var row = el('div', 'n4b-barrow');
      var cls = dangerFn && dangerFn(r) === 'danger' ? 'danger' : (dangerFn && dangerFn(r) === 'warn' ? 'warn' : '');
      row.innerHTML =
        '<span class="n4b-bar-lbl" title="' + r[labelKey] + '">' + r[labelKey] + '</span>' +
        '<span class="n4b-bar-track"><span class="n4b-bar-fill ' + cls + '" style="width:' + (r[countKey] / max * 100) + '%"></span></span>' +
        '<span class="n4b-bar-val">' + r[countKey] + '</span>';
      wrap.appendChild(row);
    });
    return wrap;
  }

  function teamLoadCard(rows) {
    var c = card('Ekip Yükü', 'SLA riski yüksek ekipler üstte');
    if (!rows.length) { c.appendChild(el('p', null, 'Veri yok.')); return c; }
    rows.forEach(function (r) {
      var row = el('div', 'n4b-team-row');
      var badges = '';
      if (r.breach) badges += '<span class="n4b-badge n4b-badge-breach">' + r.breach + ' aşan</span>';
      if (r.risk) badges += '<span class="n4b-badge n4b-badge-risk">' + r.risk + ' riskli</span>';
      row.innerHTML =
        '<div class="n4b-team-top"><span class="n4b-team-name">' + r.team + '</span><div class="n4b-team-badges">' + badges + '</div></div>' +
        '<div class="n4b-bar-track" style="margin-bottom:6px;"><span class="n4b-bar-fill' + (r.breach ? ' danger' : (r.risk ? ' warn' : '')) + '" style="width:' + (r.open / Math.max(1, r.count) * 100) + '%"></span></div>' +
        '<div class="n4b-team-meta">' + r.count + ' toplam · ' + r.open + ' açık</div>';
      c.appendChild(row);
    });
    return c;
  }

  function render(d) {
    var dash = $('#dash');
    dash.innerHTML = '';
    dash.appendChild(kpiRow(d.kpis));

    var row1 = el('div', 'n4b-grid-dash');
    row1.appendChild(teamLoadCard(d.team_load));
    var statusCard = card('Durum Dağılımı', 'talep sayısına göre');
    statusCard.appendChild(barChart(d.status_dist, 'label', 'count'));
    row1.appendChild(statusCard);
    dash.appendChild(row1);

    var row2 = el('div', 'n4b-grid-dash');
    row2.style.marginTop = '20px';
    var prCard = card('Öncelik Dağılımı');
    prCard.appendChild(barChart(d.priority_dist, 'label', 'count', function (r) {
      return r.priority === 'kritik' ? 'danger' : (r.priority === 'yuksek' ? 'warn' : '');
    }));
    row2.appendChild(prCard);
    var catCard = card('Kategori Dağılımı', 'en çok talep gelen ilk 8');
    catCard.appendChild(barChart(d.category_dist.slice(0, 8), 'category', 'count'));
    row2.appendChild(catCard);
    dash.appendChild(row2);

    var foot = el('p', null, 'Üretim: ' + d.generated_at);
    foot.style.cssText = 'font-size:11px;color:var(--n4b-slate-500);margin-top:20px;';
    dash.appendChild(foot);
  }

  function load() {
    fetch('/api/dashboard').then(function (r) { return r.json(); }).then(render).catch(function (e) {
      $('#dash').innerHTML = '<div class="n4b-empty">Veri alınamadı: ' + e.message + '</div>';
    });
  }
  load();
})();
