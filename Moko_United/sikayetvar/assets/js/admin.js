/* Moka Müşteri Zeka Paneli — /api/admin/insights verisini çizer.
   Bağımlılık yok; grafikler saf SVG/DOM. */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const el = (t, cls, html) => { const e = document.createElement(t); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; };
  const pct = (n) => (n > 0 ? '+' : '') + n + '%';
  const num = (n) => (n == null ? '—' : n.toLocaleString('tr-TR'));

  const URG_COLOR = (u) => u >= 8 ? 'var(--sv-red)' : u >= 6 ? 'var(--sv-orange)' : u >= 4 ? '#c9a227' : 'var(--sv-secondary)';

  async function load() {
    let data;
    try {
      const r = await fetch('/api/admin/insights', { cache: 'no-store' });
      if (!r.ok) throw new Error('HTTP ' + r.status);
      data = await r.json();
    } catch (e) {
      $('#dash').innerHTML = '<div class="err">İçgörü verisi alınamadı: ' + e.message +
        '<br><small>Sunucunun (python3 sikayetvar/server.py) çalıştığından emin olun.</small></div>';
      return;
    }
    render(data);
  }

  function render(d) {
    const dash = $('#dash');
    dash.innerHTML = '';
    dash.appendChild(kpiRow(d.kpis));
    dash.appendChild(aiCard(d.ai_summary, d.generated_at));
    dash.appendChild(twoCol(emergingCard(d.emerging), timeseriesCard(d.timeseries)));
    dash.appendChild(criticalCard(d.critical_issues));
    dash.appendChild(twoCol(categoriesCard(d.categories), segmentsCard(d.segments)));
    dash.appendChild(twoCol(sentimentCard(d.sentiment), benchmarkCard(d.benchmark)));
    if (d.clusters && d.clusters.length) dash.appendChild(clustersCard(d.clusters));
    dash.appendChild(recCard(d.recommendations));
  }

  function card(title, sub) {
    const c = el('section', 'card');
    if (title) {
      const h = el('div', 'card-h');
      h.appendChild(el('h3', null, title));
      if (sub) h.appendChild(el('span', 'card-sub', sub));
      c.appendChild(h);
    }
    return c;
  }
  function twoCol(a, b) { const w = el('div', 'grid-2'); w.append(a, b); return w; }

  /* ---- KPI ---- */
  function kpiRow(k) {
    const wrap = el('div', 'kpi-row');
    const trust = k.trust_score ?? 0;
    const items = [
      ['Toplam Şikayet', num(k.total), 'toplam'],
      ['Çözüm Oranı', '%' + (k.resolution_rate ?? 0), (k.solved ?? 0) + ' çözüldü · ' + (k.pending ?? 0) + ' bekliyor'],
      ['Ort. Yanıt Süresi', (k.avg_response_hours ?? '—') + ' sa', 'markanın ilk yanıtı'],
      ['Toplam Destek', num(k.total_supports), num(k.total_views) + ' görüntülenme'],
    ];
    // güven puanı halkası
    const ring = el('div', 'kpi kpi-ring');
    const deg = Math.round((trust / 100) * 360);
    const col = trust >= 70 ? 'var(--sv-secondary)' : trust >= 45 ? 'var(--sv-orange)' : 'var(--sv-red)';
    ring.innerHTML =
      '<div class="ring" style="background:conic-gradient(' + col + ' ' + deg + 'deg,#e8e8ef 0)">' +
      '<div class="ring-in"><strong>' + trust + '</strong><small>/100</small></div></div>' +
      '<div class="kpi-lbl">Güven Puanı</div>';
    wrap.appendChild(ring);
    items.forEach(([lbl, val, sub]) => {
      const c = el('div', 'kpi');
      c.innerHTML = '<div class="kpi-val">' + val + '</div><div class="kpi-lbl">' + lbl +
        '</div><div class="kpi-sub">' + sub + '</div>';
      wrap.appendChild(c);
    });
    return wrap;
  }

  /* ---- AI özet ---- */
  function aiCard(ai, at) {
    const c = card();
    c.classList.add('ai-card');
    const src = ai && ai.source;
    const badge = src && src.indexOf('qwen') === 0
      ? '<span class="ai-badge ok">🧠 Yerel model: ' + src + '</span>'
      : src === 'error'
        ? '<span class="ai-badge warn">⚠ LLM hatası — kural-tabanlı özet</span>'
        : '<span class="ai-badge">📊 Kural-tabanlı özet</span>';
    const pend = ai && ai.pending
      ? '<span class="ai-pending">Yerel model özeti arka planda hazırlanıyor…</span>' : '';
    c.innerHTML =
      '<div class="card-h"><h3>Yönetici Özeti</h3>' + badge + '</div>' +
      '<p class="ai-text">' + (ai ? ai.text : '—') + '</p>' + pend +
      '<div class="ai-foot">Üretim: ' + (at || '—') + '</div>';
    return c;
  }

  /* ---- Yükselen konular ---- */
  function emergingCard(items) {
    const c = card('Yükselen Konular', 'son 7 gün / önceki 7 gün');
    if (!items || !items.length) { c.appendChild(el('p', 'muted', 'Belirgin trend yok.')); return c; }
    const list = el('div', 'emg-list');
    items.forEach(e => {
      const up = e.pct >= 0;
      const row = el('div', 'emg');
      row.innerHTML = '<span class="emg-name">' + e.name + '</span>' +
        '<span class="emg-nums">' + e.prev + ' → ' + e.last + '</span>' +
        '<span class="emg-pct ' + (up ? 'up' : 'down') + '">' + (up ? '▲' : '▼') + ' ' + pct(e.pct) + '</span>';
      list.appendChild(row);
    });
    c.appendChild(list);
    return c;
  }

  /* ---- Zaman serisi (4 hafta) ---- */
  function timeseriesCard(ts) {
    const c = card('Şikayet Hacmi', 'haftalık, son 4 hafta');
    if (!ts || !ts.length) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    const max = Math.max(1, ...ts.map(b => b.count));
    const W = 280, H = 120, n = ts.length, bw = W / n * 0.55, gap = W / n;
    let bars = '', labels = '';
    ts.forEach((b, i) => {
      const h = Math.round(b.count / max * (H - 24));
      const x = i * gap + (gap - bw) / 2, y = H - h - 18;
      bars += '<rect x="' + x + '" y="' + y + '" width="' + bw + '" height="' + h +
        '" rx="4" fill="var(--sv-primary)"></rect>' +
        '<text x="' + (x + bw / 2) + '" y="' + (y - 4) + '" text-anchor="middle" class="bl">' + b.count + '</text>';
      labels += '<text x="' + (x + bw / 2) + '" y="' + (H - 4) + '" text-anchor="middle" class="ax">H' + (i + 1) + '</text>';
    });
    c.appendChild(el('div', 'chart', '<svg viewBox="0 0 ' + W + ' ' + H + '" class="svg-chart">' + bars + labels + '</svg>'));
    return c;
  }

  /* ---- Kritik sorunlar ---- */
  function criticalCard(items) {
    const c = card('Kritik Sorunlar', 'adet × ortalama aciliyet puanına göre');
    if (!items || !items.length) { c.appendChild(el('p', 'muted', 'Kayıt yok.')); return c; }
    items.slice(0, 5).forEach((it, i) => {
      const box = el('div', 'crit');
      const trendTxt = it.trend_pct ? ' · trend ' + pct(it.trend_pct) : '';
      const samples = (it.samples || []).map(s => '<li>' + s + '</li>').join('');
      box.innerHTML =
        '<div class="crit-top">' +
        '<span class="crit-rank">#' + (i + 1) + '</span>' +
        '<span class="crit-name">' + it.issue + '</span>' +
        '<span class="crit-badge" style="background:' + URG_COLOR(it.urgency) + '">Aciliyet ' + it.urgency + '/10</span>' +
        '</div>' +
        '<div class="crit-meta">' + it.count + ' şikayet · ' + it.pending + ' bekliyor' + trendTxt + '</div>' +
        '<div class="urg-bar"><span style="width:' + (it.urgency * 10) + '%;background:' + URG_COLOR(it.urgency) + '"></span></div>' +
        '<ul class="crit-samples">' + samples + '</ul>' +
        '<div class="crit-action"><strong>Öneri:</strong> ' + it.action + '</div>';
      c.appendChild(box);
    });
    return c;
  }

  /* ---- Kategori dağılımı ---- */
  function categoriesCard(cats) {
    const c = card('Kategori Dağılımı', 'AI ile otomatik sınıflandırma');
    if (!cats || !cats.length) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    const max = Math.max(...cats.map(x => x.count));
    cats.slice(0, 8).forEach(cat => {
      const row = el('div', 'barrow');
      row.innerHTML =
        '<span class="bar-lbl" title="' + cat.name + '">' + cat.name + '</span>' +
        '<span class="bar-track"><span class="bar-fill" style="width:' + (cat.count / max * 100) + '%"></span></span>' +
        '<span class="bar-val">' + cat.count + '</span>';
      c.appendChild(row);
    });
    return c;
  }

  /* ---- Segmentler ---- */
  function segmentsCard(segs) {
    const c = card('Müşteri Segmentleri', 'metin ipuçlarından çıkarım');
    if (!segs || !segs.length) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    segs.forEach(s => {
      const row = el('div', 'seg');
      row.innerHTML = '<div class="seg-top"><span class="seg-name">' + s.name +
        '</span><span class="seg-share">%' + s.share + '</span></div>' +
        '<div class="seg-sub">' + s.count + ' şikayet · en sık: ' + s.top_issue + '</div>' +
        '<div class="bar-track"><span class="bar-fill alt" style="width:' + s.share + '%"></span></div>';
      c.appendChild(row);
    });
    return c;
  }

  /* ---- Duygu ---- */
  function sentimentCard(items) {
    const c = card('Duygu Dağılımı', 'sözlük tabanlı');
    if (!items || !items.length) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    const total = items.reduce((a, b) => a + b.count, 0) || 1;
    const COL = { 'Öfkeli': 'var(--sv-red)', 'Olumsuz': 'var(--sv-orange)', 'Nötr': '#9aa0b0', 'Olumlu': 'var(--sv-secondary)' };
    const seg = items.map(i => '<span style="width:' + (i.count / total * 100) + '%;background:' + (COL[i.name] || '#ccc') + '" title="' + i.name + ': ' + i.count + '"></span>').join('');
    const legend = items.map(i => '<span class="lg"><i style="background:' + (COL[i.name] || '#ccc') + '"></i>' + i.name + ' (' + i.count + ')</span>').join('');
    c.appendChild(el('div', 'stack', seg));
    c.appendChild(el('div', 'legend', legend));
    return c;
  }

  /* ---- Benchmark ---- */
  function benchmarkCard(bm) {
    const c = card('Kıyaslama', 'çözüm oranı — temsilî rakip değerleri');
    if (!bm || bm.moka == null) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    const rows = [['Moka United', bm.moka, true]];
    Object.entries(bm.peers || {}).forEach(([k, v]) => rows.push([k, v, false]));
    const max = Math.max(...rows.map(r => r[1]));
    rows.forEach(([name, val, self]) => {
      const row = el('div', 'barrow');
      row.innerHTML = '<span class="bar-lbl">' + name + '</span>' +
        '<span class="bar-track"><span class="bar-fill' + (self ? '' : ' peer') + '" style="width:' + (val / max * 100) + '%"></span></span>' +
        '<span class="bar-val">%' + val + '</span>';
      c.appendChild(row);
    });
    return c;
  }

  /* ---- Kümeler ---- */
  function clustersCard(cl) {
    const c = card('Tekrar Eden Sorunlar', 'metin benzerliğiyle kümeleme (TF-IDF)');
    cl.forEach(k => {
      const box = el('div', 'clus');
      box.innerHTML = '<div class="clus-h"><span class="clus-badge">' + k.size + ' benzer</span> ' +
        '<span class="clus-cat">' + k.category + '</span></div>' +
        '<ul>' + k.titles.map(t => '<li>' + t + '</li>').join('') + '</ul>';
      c.appendChild(box);
    });
    return c;
  }

  /* ---- Öneriler ---- */
  function recCard(recs) {
    const c = card('Aksiyon Önerileri', 'en kritik 5 başlık');
    if (!recs || !recs.length) { c.appendChild(el('p', 'muted', 'Öneri yok.')); return c; }
    const ol = el('ol', 'rec-list');
    recs.forEach(r => ol.appendChild(el('li', null, '<strong>' + r.category + ':</strong> ' + r.text)));
    c.appendChild(ol);
    return c;
  }

  load();
  // AI özeti arka planda hazırlanırken paneli sessizce tazele (en fazla ~2 dk)
  let tries = 0;
  const poll = setInterval(async () => {
    tries++;
    try {
      const r = await fetch('/api/admin/insights', { cache: 'no-store' });
      const d = await r.json();
      render(d);
      if (!d.ai_summary || !d.ai_summary.pending) { if (tries > 1) clearInterval(poll); }
    } catch (e) { /* yut */ }
    if (tries >= 8) clearInterval(poll);
  }, 15000);
})();
