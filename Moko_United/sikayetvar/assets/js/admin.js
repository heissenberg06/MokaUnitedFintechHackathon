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

  let lastData = null;

  function render(d) {
    lastData = d;
    const dash = $('#dash');
    dash.innerHTML = '';
    dash.appendChild(kpiRow(d.kpis));
    dash.appendChild(fraudRingCard(d.fraud_rings));
    dash.appendChild(aiCard(d.ai_summary, d.generated_at));
    dash.appendChild(twoCol(hourlyCard(d.hourly), merchantRiskCard(d.merchant_risk)));
    dash.appendChild(twoCol(emergingCard(d.emerging), timeseriesCard(d.timeseries)));
    dash.appendChild(criticalCard(d.critical_issues));
    dash.appendChild(teamRoutingCard(d.team_routing));
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

  /* ---- Sahtekarlık ağı ---- */
  function fraudRingCard(rings) {
    const c = card('Sahtekarlık Ağı Tespiti', 'aynı işyerinde, kısa sürede birikmiş farklı şikayetler');
    c.classList.add('ring-card');
    if (!rings || !rings.length) {
      c.appendChild(el('p', 'ring-clear-txt', '✓ Şu an aktif bir sahtekarlık ağı sinyali tespit edilmedi.'));
      return c;
    }
    rings.forEach(r => {
      const box = el('div', 'ring-alert');
      const titles = (r.sample_titles || []).map(t => '<li>' + t + '</li>').join('');
      box.innerHTML =
        '<div class="ring-top"><span class="ring-ic">⚠</span>' +
        '<span class="ring-merchant">' + r.merchant + '</span>' +
        '<span class="ring-badge">' + r.count + ' farklı şikayet</span></div>' +
        '<div class="ring-meta">Son ' + r.window_hours + ' saat içinde ' + r.count +
        ' farklı kullanıcıdan "Yetkisiz İşlem" şikayeti geldi — organize bir saldırı sinyali olabilir.</div>' +
        '<ul class="ring-samples">' + titles + '</ul>' +
        '<div class="ring-action"><strong>Önerilen aksiyon:</strong> Bu işyerine ait işlemleri geçici ' +
        'olarak inceleme kuyruğuna al; etkilenen kart ailelerini fraud izleme listesine ekle.</div>';
      c.appendChild(box);
    });
    return c;
  }

  /* ---- Saatlik yoğunluk ---- */
  function hourlyCard(h) {
    const c = card('Saatlik Yoğunluk', 'şikayetlerin/işlemlerin geldiği saat dağılımı (00-23)');
    if (!h || !h.buckets || !h.buckets.some(x => x > 0)) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    const max = Math.max(1, ...h.buckets);
    const W = 300, H = 130, n = 24, bw = W / n * 0.6, gap = W / n;
    let bars = '';
    h.buckets.forEach((v, i) => {
      const barH = Math.round(v / max * (H - 26));
      const x = i * gap + (gap - bw) / 2, y = H - barH - 18;
      const isPeak = i === h.peak_hour && v > 0;
      bars += '<rect x="' + x + '" y="' + y + '" width="' + bw + '" height="' + Math.max(barH, 1) +
        '" rx="2" fill="' + (isPeak ? 'var(--sv-red)' : 'var(--sv-primary)') + '"><title>' +
        String(i).padStart(2, '0') + ':00 — ' + v + ' şikayet</title></rect>';
      if (i % 3 === 0) {
        bars += '<text x="' + (x + bw / 2) + '" y="' + (H - 4) + '" text-anchor="middle" class="ax">' + i + '</text>';
      }
    });
    c.appendChild(el('div', 'chart', '<svg viewBox="0 0 ' + W + ' ' + H + '" class="svg-chart hourly-chart">' + bars + '</svg>'));
    if (h.peak_count > 0) {
      c.appendChild(el('p', 'hourly-foot',
        'En yoğun saat: <strong>' + String(h.peak_hour).padStart(2, '0') + ':00</strong> (' + h.peak_count + ' şikayet) · ' +
        'Mesai saatleri (09-18): <strong>%' + h.business_hours_pct + '</strong> · Mesai dışı: <strong>%' + h.off_hours_pct + '</strong>'));
    }
    return c;
  }

  /* ---- İşyeri risk sıralaması ---- */
  function merchantRiskCard(rows) {
    const c = card('İşyeri Risk Sıralaması', 'işyeri bazında şikayet yoğunluğu × aciliyet');
    if (!rows || !rows.length) { c.appendChild(el('p', 'muted', 'İşyeri bazlı şikayet kaydı yok.')); return c; }
    const max = Math.max(...rows.map(r => r.risk_score));
    rows.slice(0, 8).forEach(r => {
      const row = el('div', 'mrisk-row' + (r.is_ring ? ' mrisk-danger' : ''));
      row.innerHTML =
        '<div class="mrisk-top"><span class="mrisk-name">' + r.merchant +
        (r.is_ring ? ' <span class="mrisk-flag">⚠ Ağ</span>' : '') + '</span>' +
        '<span class="mrisk-score">Risk ' + r.risk_score + '</span></div>' +
        '<div class="bar-track"><span class="bar-fill' + (r.is_ring ? ' danger' : '') +
        '" style="width:' + (r.risk_score / max * 100) + '%"></span></div>' +
        '<div class="mrisk-meta">' + r.count + ' şikayet · ort. aciliyet ' + r.avg_urgency +
        '/10 · ' + r.pending + ' bekliyor</div>';
      c.appendChild(row);
    });
    return c;
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

  /* ---- Ekip yönlendirme ---- */
  function teamRoutingCard(rows) {
    const c = card('İlgili Ekibe Yönlendirme', 'kategoriye göre otomatik triage — hangi sorun hangi ekibe düşüyor');
    if (!rows || !rows.length) { c.appendChild(el('p', 'muted', 'Veri yok.')); return c; }
    rows.forEach(r => {
      const box = el('div', 'team-row' + (r.pending > 0 && r.avg_urgency >= 6 ? ' team-hot' : ''));
      const samples = (r.samples || []).map(s => '<li>' + s + '</li>').join('');
      box.innerHTML =
        '<div class="team-top"><span class="team-name">→ ' + r.team + '</span>' +
        '<span class="team-badge">' + r.pending + ' bekliyor / ' + r.count + ' toplam</span></div>' +
        '<div class="team-meta">En sık: ' + r.top_category + ' · ort. aciliyet ' + r.avg_urgency + '/10</div>' +
        '<ul class="team-samples">' + samples + '</ul>';
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

  /* ---- Rapor oluşturma ---- */
  function buildReportText(d) {
    const L = [];
    const line = (s) => L.push(s || '');
    const rule = () => line('-'.repeat(48));
    const now = new Date();
    line('MOKA MÜŞTERİ ZEKÂ PANELİ — YÖNETİCİ RAPORU');
    line('Oluşturulma: ' + now.toLocaleString('tr-TR'));
    line('Veri üretimi: ' + (d.generated_at || '—'));
    rule();

    const k = d.kpis || {};
    line('GENEL DURUM');
    line('  Toplam şikayet     : ' + num(k.total));
    line('  Çözüm oranı        : %' + (k.resolution_rate ?? 0) + '  (' + (k.solved ?? 0) + ' çözüldü, ' + (k.pending ?? 0) + ' bekliyor)');
    line('  Ort. yanıt süresi  : ' + (k.avg_response_hours ?? '—') + ' saat');
    line('  Güven puanı        : ' + (k.trust_score ?? '—') + '/100');
    line('  Toplam destek/gör. : ' + num(k.total_supports) + ' / ' + num(k.total_views));
    line('');

    line('SAHTEKARLIK AĞI TESPİTİ');
    if (d.fraud_rings && d.fraud_rings.length) {
      d.fraud_rings.forEach(r => {
        line('  ⚠ ' + r.merchant + ' — ' + r.count + ' farklı şikayet, son ' + r.window_hours + ' saat içinde');
      });
    } else {
      line('  Aktif bir sahtekarlık ağı sinyali tespit edilmedi.');
    }
    line('');

    if (d.hourly) {
      line('SAATLİK YOĞUNLUK');
      line('  En yoğun saat      : ' + String(d.hourly.peak_hour).padStart(2, '0') + ':00 (' + d.hourly.peak_count + ' şikayet)');
      line('  Mesai saatleri (09-18): %' + d.hourly.business_hours_pct + '   Mesai dışı: %' + d.hourly.off_hours_pct);
      line('');
    }

    if (d.merchant_risk && d.merchant_risk.length) {
      line('İŞYERİ RİSK SIRALAMASI (ilk 8)');
      d.merchant_risk.slice(0, 8).forEach((r, i) => {
        line('  ' + (i + 1) + '. ' + r.merchant + (r.is_ring ? ' [AĞ]' : '') +
          ' — risk ' + r.risk_score + ' (' + r.count + ' şikayet, ort. aciliyet ' + r.avg_urgency + '/10, ' + r.pending + ' bekliyor)');
      });
      line('');
    }

    line('KRİTİK SORUNLAR (ilk 5)');
    if (d.critical_issues && d.critical_issues.length) {
      d.critical_issues.slice(0, 5).forEach((it, i) => {
        line('  ' + (i + 1) + '. ' + it.issue + ' — aciliyet ' + it.urgency + '/10, ' + it.count + ' şikayet, ' + it.pending + ' bekliyor');
        line('     Öneri: ' + it.action);
      });
    } else { line('  Kayıt yok.'); }
    line('');

    if (d.team_routing && d.team_routing.length) {
      line('İLGİLİ EKİBE YÖNLENDİRME');
      d.team_routing.forEach(r => {
        line('  → ' + r.team + ' — ' + r.pending + ' bekliyor / ' + r.count + ' toplam (en sık: ' + r.top_category + ', ort. aciliyet ' + r.avg_urgency + '/10)');
      });
      line('');
    }

    if (d.categories && d.categories.length) {
      line('KATEGORİ DAĞILIMI');
      d.categories.slice(0, 8).forEach(c => line('  ' + c.name + ': ' + c.count));
      line('');
    }

    if (d.segments && d.segments.length) {
      line('MÜŞTERİ SEGMENTLERİ');
      d.segments.forEach(s => line('  ' + s.name + ': %' + s.share + ' (' + s.count + ' şikayet, en sık: ' + s.top_issue + ')'));
      line('');
    }

    if (d.sentiment && d.sentiment.length) {
      line('DUYGU DAĞILIMI');
      d.sentiment.forEach(s => line('  ' + s.name + ': ' + s.count));
      line('');
    }

    if (d.recommendations && d.recommendations.length) {
      line('AKSİYON ÖNERİLERİ');
      d.recommendations.forEach((r, i) => line('  ' + (i + 1) + '. [' + r.category + '] ' + r.text));
      line('');
    }

    if (d.ai_summary && d.ai_summary.text) {
      rule();
      line('YÖNETİCİ ÖZETİ (' + (d.ai_summary.source || 'kural-tabanlı') + ')');
      line(d.ai_summary.text);
    }
    rule();
    line('Bu rapor yalnızca eğitim/demo amaçlıdır; tüm veriler kurgudur.');
    return L.join('\n');
  }

  function downloadReport() {
    if (!lastData) return;
    const text = buildReportText(lastData);
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = el('a');
    const stamp = new Date().toISOString().slice(0, 16).replace(/[-:T]/g, '').replace(/(\d{8})(\d{4})/, '$1-$2');
    a.href = url;
    a.download = 'moka-yonetici-raporu-' + stamp + '.txt';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  const btnReport = $('#btnReport');
  if (btnReport) btnReport.addEventListener('click', downloadReport);

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
