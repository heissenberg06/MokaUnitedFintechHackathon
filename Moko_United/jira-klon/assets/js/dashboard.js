(function () {
  var CAT_COLOR = {
    new: 'var(--j-discovery-bg-bold)', default: 'var(--j-icon-subtle)', inprogress: 'var(--j-info-bg-bold)',
    moved: 'var(--j-warning-bg-bold)', success: 'var(--j-success-bg-bold)', removed: 'var(--j-danger-bg-bold)',
  };
  var PRIORITY_COLOR = { kritik: 'var(--j-icon-red)', yuksek: 'var(--j-icon-red)', orta: 'var(--j-icon-orange)', dusuk: 'var(--j-icon-blue)' };
  var SENTIMENT_COLOR = { ofkeli: 'var(--j-icon-red)', olumsuz: 'var(--j-icon-orange)', notr: 'var(--j-icon-subtle)', olumlu: 'var(--j-icon-green)' };
  var TYPE_COLOR = { bug: 'var(--j-icon-red)', task: 'var(--j-icon-blue)', story: 'var(--j-icon-green)', epic: 'var(--j-icon-purple)', subtask: 'var(--j-icon-blue)' };

  function barChart(title, items, keyField, colorMap) {
    var max = Math.max.apply(null, items.map(function (i) { return i.count; }).concat([1]));
    var rows = items.map(function (i) {
      var color = colorMap[i[keyField]] || 'var(--j-icon-subtle)';
      var pct = Math.round((i.count / max) * 100);
      return '<div class="j-bar-row"><span class="j-bar-label">' + i.label + '</span>' +
        '<span class="j-bar-track"><span class="j-bar-fill" style="width:' + pct + '%;background:' + color + ';"></span></span>' +
        '<span class="j-bar-count">' + i.count + '</span></div>';
    }).join('');
    return '<div class="j-panel"><div class="j-heading-xs" style="margin-bottom:12px;">' + title + '</div>' + (rows || '<div class="j-text-subtlest" style="font-size:13px;">Veri yok.</div>') + '</div>';
  }

  function render(d) {
    var ui = window.MokaUI;
    var k = d.kpis;
    var kpis = [
      { label: 'Toplam Talep', value: k.total },
      { label: 'Açık', value: k.open },
      { label: 'Kapanan', value: k.closed },
      { label: 'SLA Aşımı', value: k.sla_breach },
      { label: 'SLA Riski', value: k.sla_risk },
      { label: 'Ort. Açık Yaş (sa)', value: k.avg_open_age_hours != null ? k.avg_open_age_hours : '—' },
      { label: 'Ort. Çözüm Süresi (sa)', value: k.avg_resolution_hours != null ? k.avg_resolution_hours : '—' },
    ];
    var kpiHtml = '<div class="j-kpi-grid">' + kpis.map(function (kk) {
      return '<div class="j-kpi-card"><div class="j-kpi-value">' + kk.value + '</div><div class="j-kpi-label">' + kk.label + '</div></div>';
    }).join('') + '</div>';

    var statusItems = d.status_dist.map(function (s) { return { label: s.label, count: s.count, category: s.category }; });
    var priorityItems = d.priority_dist.map(function (p) { return { label: p.label, count: p.count, priority: p.priority }; });
    var sentimentItems = d.sentiment_dist.map(function (s) { return { label: s.label, count: s.count, sentiment: s.sentiment }; });
    var typeItems = d.issuetype_dist.map(function (t) { return { label: t.label, count: t.count, issuetype: t.issuetype }; });
    var categoryItems = d.category_dist.slice(0, 8).map(function (c) { return { label: c.category, count: c.count, cat: 'x' }; });

    var teamRows = d.team_load.map(function (t) {
      return '<tr style="border-bottom:1px solid var(--j-border);">' +
        '<td style="padding:8px 12px;">' + ui.esc(t.team) + '</td>' +
        '<td style="padding:8px 12px;text-align:center;">' + t.count + '</td>' +
        '<td style="padding:8px 12px;text-align:center;">' + t.open + '</td>' +
        '<td style="padding:8px 12px;text-align:center;">' + (t.breach ? ui.lozenge('removed', t.breach + ' aşım') : '—') + '</td>' +
        '<td style="padding:8px 12px;text-align:center;">' + (t.risk ? ui.lozenge('moved', t.risk + ' risk') : '—') + '</td>' +
        '</tr>';
    }).join('');
    var teamTable = '<div class="j-panel"><div class="j-heading-xs" style="margin-bottom:12px;">Ekip Yükü</div>' +
      '<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="border-bottom:1px solid var(--j-border);color:var(--j-text-subtlest);font-size:12px;text-transform:uppercase;">' +
      '<th style="text-align:left;padding:8px 12px;">Ekip</th><th style="padding:8px 12px;">Toplam</th><th style="padding:8px 12px;">Açık</th><th style="padding:8px 12px;">SLA Aşımı</th><th style="padding:8px 12px;">SLA Riski</th></tr></thead>' +
      '<tbody>' + teamRows + '</tbody></table></div>';

    var body = document.getElementById('dashBody');
    body.innerHTML = kpiHtml +
      '<div class="j-dash-grid">' +
        barChart('Durum Dağılımı', statusItems, 'category', CAT_COLOR) +
        barChart('Öncelik Dağılımı', priorityItems, 'priority', PRIORITY_COLOR) +
        barChart('Talep Türü Dağılımı', typeItems, 'issuetype', TYPE_COLOR) +
        barChart('Müşteri Duygu Durumu', sentimentItems, 'sentiment', SENTIMENT_COLOR) +
      '</div>' +
      '<div style="margin-top:16px;">' + barChart('Kategori Dağılımı (ilk 8)', categoryItems, 'cat', {}) + '</div>' +
      '<div style="margin-top:16px;">' + teamTable + '</div>';
  }

  function load() {
    fetch('/api/dashboard').then(function (r) { return r.json(); }).then(render);
  }

  document.addEventListener('DOMContentLoaded', function () {
    window.MokaShell.init('dashboard');
    load();
    document.addEventListener('j:issue-created', load);
  });
})();
