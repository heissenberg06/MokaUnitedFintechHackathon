/* ============================================================
   Şikayetvar — Moka United klonu (frontend mantığı)
   Not: Kullanıcı içeriği sunucuda html.escape ile kaçırılır;
   burada escaped string'ler innerHTML ile basılır (XSS güvenli,
   çünkü < > & zaten &lt; &gt; &amp; olarak gelir → çalışmaz).
   ============================================================ */
(function () {
  'use strict';

  // Moka United logosu (ana klondan alınmış sade wordmark)
  const MOKA_LOGO = `<svg viewBox="0 0 200 44" xmlns="http://www.w3.org/2000/svg" aria-label="Moka United">
    <text x="0" y="30" font-family="Arial, sans-serif" font-weight="800" font-size="28" fill="#0d3c94">moka</text>
    <text x="78" y="30" font-family="Arial, sans-serif" font-weight="300" font-size="28" fill="#0d3c94">united</text>
    <circle cx="186" cy="13" r="6" fill="#2bfb97"/></svg>`;

  const ICON = {
    eye: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1.5 12S5 5 12 5s10.5 7 10.5 7-3.5 7-10.5 7S1.5 12 1.5 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    heart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.3-9.2-8.4C1.3 9 2.4 5.8 5.5 5c2-.5 3.7.6 4.5 2 .8-1.4 2.5-2.5 4.5-2 3.1.8 4.2 4 2.7 6.6C19 15.7 12 20 12 20z"/></svg>',
    chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 9.9 9.9 0 0 1-4-.8L3 21l1.9-4.9A8.4 8.4 0 1 1 21 11.5z"/></svg>',
    empty: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>',
  };

  const TAGS = ['para iadesi', 'pos başvurusu', 'komisyon oranı', 'müşteri hizmetleri',
                'hesap onayı', 'cihaz teslimatı', 'link ile ödeme', 'cüzdan bakiyesi'];

  const state = { page: 1, q: '', activeTag: null };
  const supported = JSON.parse(localStorage.getItem('sv-supported') || '[]');
  const viewed = new Set(JSON.parse(localStorage.getItem('sv-viewed') || '[]'));

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ---- tarih ----
  function relDate(iso) {
    const d = new Date(iso), now = new Date(), diff = (now - d) / 1000;
    if (diff < 60) return 'az önce';
    if (diff < 3600) return Math.floor(diff / 60) + ' dakika önce';
    if (diff < 86400) return Math.floor(diff / 3600) + ' saat önce';
    if (diff < 172800) return 'dün';
    const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'];
    return d.getDate() + ' ' + months[d.getMonth()] + ' ' + d.getFullYear();
  }

  // ---- API ----
  async function api(path, opts) {
    const res = await fetch(path, opts);
    let data = null;
    try { data = await res.json(); } catch (e) {}
    return { ok: res.ok, status: res.status, data };
  }
  const getList = (page, q) => api(`/api/complaints?page=${page}&q=${encodeURIComponent(q || '')}`);
  const getDetail = (id) => api(`/api/complaints/${id}`);
  const postJSON = (path, body) => api(path, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {}),
  });

  // ---- render: kart ----
  function statusBadge(status) {
    if (status === 'cozuldu') return `<span class="status-badge status-cozuldu">${ICON.check} Çözüldü</span>`;
    return `<span class="status-badge status-yanit-bekliyor">Yanıt bekliyor</span>`;
  }

  function cardHTML(c) {
    const isSupported = supported.includes(c.id);
    return `<div class="card collapsed" data-id="${c.id}">
      <div class="card-top">
        <div class="avatar">${c.initials || '?'}</div>
        <div class="card-user">
          <span class="u-name">${c.name}</span>
          <span class="u-date">${relDate(c.createdAt)}</span>
        </div>
        ${statusBadge(c.status)}
      </div>
      <h3 class="card-title" data-open="${c.id}">${c.title}</h3>
      <div class="card-body">${c.body}</div>
      <div class="card-stats">
        <span class="stat">${ICON.eye}<span data-views>${c.views}</span></span>
        <button class="stat support-btn ${isSupported ? 'supported' : ''}" data-support="${c.id}" ${isSupported ? 'disabled' : ''}>
          ${ICON.heart}<span data-supports>${c.supports}</span> ${isSupported ? 'Desteklendi' : 'Destekle'}
        </button>
        <button class="stat comment-btn" data-open="${c.id}">${ICON.chat}<span data-ccount>${c.comments ? c.comments.length : 0}</span> Yorum</button>
      </div>
      <div class="detail" data-detail="${c.id}"></div>
    </div>`;
  }

  function commentsHTML(c) {
    const list = (c.comments || []).map(cm => `
      <div class="comment ${cm.isBrand ? 'brand' : ''}">
        <div class="avatar ${cm.isBrand ? 'brand' : ''}">${cm.isBrand ? 'M' : (cm.initials || '?')}</div>
        <div class="c-main">
          <div class="c-head">
            <span class="c-name">${cm.name}</span>
            ${cm.isBrand ? '<span class="c-badge">Marka Yanıtı</span>' : ''}
            <span class="c-date">${relDate(cm.createdAt)}</span>
          </div>
          <div class="c-body">${cm.body}</div>
        </div>
      </div>`).join('');
    const empty = (c.comments && c.comments.length) ? '' : '<p class="comment-empty">Henüz yorum yok. İlk yorumu sen yaz.</p>';
    return `<div class="comments">
      <h4>Yorumlar (${c.comments ? c.comments.length : 0})</h4>
      ${empty}${list}
      <form class="comment-form" data-comment-form="${c.id}">
        <div class="cf-row">
          <input type="text" class="cf-name" name="name" placeholder="Ad Soyad" maxlength="40" required>
        </div>
        <textarea name="body" placeholder="Yorumunu yaz…" maxlength="500" required></textarea>
        <span class="field-error" data-cerror></span>
        <div class="cf-actions"><button type="submit" class="btn btn-primary">Yorum Yap</button></div>
      </form>
    </div>`;
  }

  // ---- liste render ----
  async function loadList(flashId) {
    const listEl = $('#complaintList');
    const r = await getList(state.page, state.q);
    if (!r.ok) { listEl.innerHTML = '<div class="empty-state">Bir hata oluştu.</div>'; return; }
    const { items, total, page, totalPages } = r.data;
    $('#complaintTotal').textContent = total;
    $('#listCount').textContent = total ? `(${total} sonuç)` : '';
    if (!items.length) {
      listEl.innerHTML = `<div class="empty-state">${ICON.empty}<p>${state.q ? 'Aramanla eşleşen şikayet bulunamadı.' : 'Henüz şikayet yok.'}</p></div>`;
      $('#pagination').innerHTML = '';
      return;
    }
    listEl.innerHTML = items.map(cardHTML).join('');
    renderPagination(page, totalPages);
    if (flashId) {
      const card = $(`.card[data-id="${flashId}"]`);
      if (card) { card.classList.add('flash'); card.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
    }
  }

  function renderPagination(page, totalPages) {
    const el = $('#pagination');
    if (totalPages <= 1) { el.innerHTML = ''; return; }
    let html = `<button ${page === 1 ? 'disabled' : ''} data-page="${page - 1}">‹</button>`;
    for (let i = 1; i <= totalPages; i++) {
      html += `<button class="${i === page ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    html += `<button ${page === totalPages ? 'disabled' : ''} data-page="${page + 1}">›</button>`;
    el.innerHTML = html;
  }

  // ---- detay aç/kapat ----
  async function toggleDetail(id) {
    const card = $(`.card[data-id="${id}"]`);
    if (!card) return;
    const detail = card.querySelector(`[data-detail="${id}"]`);
    if (card.classList.contains('open')) {
      card.classList.remove('open'); card.classList.add('collapsed');
      detail.innerHTML = '';
      return;
    }
    card.classList.remove('collapsed'); card.classList.add('open');
    detail.innerHTML = '<div class="loading" style="padding:16px"><div class="spinner"></div></div>';
    // görüntülenme (kişi başına 1 kez)
    if (!viewed.has(id)) {
      viewed.add(id);
      localStorage.setItem('sv-viewed', JSON.stringify([...viewed]));
      const vr = await postJSON(`/api/complaints/${id}/view`);
      if (vr.ok) { const vEl = card.querySelector('[data-views]'); if (vEl) vEl.textContent = vr.data.views; }
    }
    const r = await getDetail(id);
    if (!r.ok) { detail.innerHTML = '<p class="comment-empty">Detay yüklenemedi.</p>'; return; }
    detail.innerHTML = commentsHTML(r.data);
    // kart gövdesini tam metne çevir (zaten collapsed kaldırıldı)
  }

  // ---- yorum gönder ----
  async function submitComment(form) {
    const id = +form.dataset.commentForm;
    const name = form.name.value.trim();
    const body = form.body.value.trim();
    const errEl = form.querySelector('[data-cerror]');
    errEl.textContent = '';
    const r = await postJSON(`/api/complaints/${id}/comments`, { name, body });
    if (!r.ok) { errEl.textContent = (r.data && r.data.error) || 'Gönderilemedi.'; return; }
    // yorumu listeye ekle
    const card = $(`.card[data-id="${id}"]`);
    const detail = card.querySelector(`[data-detail="${id}"]`);
    // güncel detayı yeniden çek (sayaç + liste tutarlı olsun)
    const dr = await getDetail(id);
    detail.innerHTML = commentsHTML(dr.data);
    const cc = card.querySelector('[data-ccount]');
    if (cc) cc.textContent = dr.data.comments.length;
  }

  // ---- destekle ----
  async function support(id, btn) {
    if (supported.includes(id)) return;
    const r = await postJSON(`/api/complaints/${id}/support`);
    if (!r.ok) return;
    supported.push(id);
    localStorage.setItem('sv-supported', JSON.stringify(supported));
    const span = btn.querySelector('[data-supports]');
    span.textContent = r.data.supports;
    while (span.nextSibling) btn.removeChild(span.nextSibling);
    btn.appendChild(document.createTextNode(' Desteklendi'));
    btn.classList.add('supported'); btn.disabled = true;
  }

  // ---- şikayet yaz modalı ----
  function openModal() {
    $('#writeModal').classList.add('active');
    $('#writeFormWrap').style.display = '';
    $('#writeSuccess').style.display = 'none';
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    $('#writeModal').classList.remove('active');
    document.body.style.overflow = '';
    $('#complaintForm').reset();
    $$('.field-error').forEach(e => e.textContent = '');
  }

  async function submitComplaint(e) {
    e.preventDefault();
    const form = e.target;
    $$('[data-error]', form).forEach(el => el.textContent = '');
    if (!$('#cConsent').checked) return;
    const payload = { name: form.name.value.trim(), title: form.title.value.trim(), body: form.body.value.trim() };
    const r = await postJSON('/api/complaints', payload);
    if (!r.ok) {
      const field = r.data && r.data.field;
      const msg = (r.data && r.data.error) || 'Gönderilemedi.';
      const target = form.querySelector(`[data-error="${field}"]`) || form.querySelector('[data-error="body"]');
      if (target) target.textContent = msg;
      return;
    }
    // başarı
    $('#writeFormWrap').style.display = 'none';
    $('#writeSuccess').style.display = 'block';
    // arama/sayfa sıfırla ki yeni şikayet en üstte görünsün
    state.q = ''; state.page = 1; state.activeTag = null;
    $('#searchInput').value = '';
    $$('.chip').forEach(c => c.classList.remove('active'));
    setTimeout(() => { closeModal(); loadList(r.data.id); }, 1100);
  }

  // ---- arama (debounce) ----
  let searchTimer;
  function onSearch(val) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.q = val.trim(); state.page = 1; state.activeTag = null;
      $$('.chip').forEach(c => c.classList.remove('active'));
      loadList();
    }, 300);
  }

  // ---- etiketler ----
  function renderTags() {
    const el = $('#tagCloud');
    TAGS.forEach(t => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = t;
      chip.addEventListener('click', () => {
        const active = chip.classList.contains('active');
        $$('.chip').forEach(c => c.classList.remove('active'));
        if (active) { state.q = ''; $('#searchInput').value = ''; }
        else { chip.classList.add('active'); state.q = t; $('#searchInput').value = t; }
        state.page = 1;
        loadList();
      });
      el.appendChild(chip);
    });
  }

  // ---- skor rozeti rengi ----
  function paintScore() {
    const val = 56;
    const ring = $('#scoreRing');
    let color = '#dc3545';           // 0-40 kırmızı
    if (val >= 70) color = '#3ad08f'; // 70+ yeşil
    else if (val >= 40) color = '#ec8a27'; // 40-70 turuncu (yalnız skor halkası)
    ring.style.background = `conic-gradient(${color} ${val * 3.6}deg, #eceff1 0deg)`;
    ring.style.boxShadow = 'inset 0 0 0 8px #fff';
  }

  // ---- olay bağlama ----
  function bind() {
    $('#brandLogo').innerHTML = MOKA_LOGO;
    renderTags();
    paintScore();

    $('#writeBtnHeader').addEventListener('click', openModal);
    $('#writeBtnHero').addEventListener('click', openModal);
    $('#modalClose').addEventListener('click', closeModal);
    $('#writeModal').addEventListener('click', e => { if (e.target.id === 'writeModal') closeModal(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    $('#complaintForm').addEventListener('submit', submitComplaint);
    $('#searchInput').addEventListener('input', e => onSearch(e.target.value));

    // liste içi delege
    $('#complaintList').addEventListener('click', e => {
      const open = e.target.closest('[data-open]');
      if (open) { toggleDetail(+open.dataset.open); return; }
      const sup = e.target.closest('[data-support]');
      if (sup) { support(+sup.dataset.support, sup); return; }
    });
    $('#complaintList').addEventListener('submit', e => {
      const form = e.target.closest('[data-comment-form]');
      if (form) { e.preventDefault(); submitComment(form); }
    });

    // sayfalama delege
    $('#pagination').addEventListener('click', e => {
      const b = e.target.closest('[data-page]');
      if (!b || b.disabled) return;
      state.page = +b.dataset.page;
      loadList();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // demo linkler
    $$('[data-demo]').forEach(a => a.addEventListener('click', () => {
      alert('Bu bir demo/klon çalışmasıdır — bu bölüm aktif değildir.');
    }));

    loadList();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind);
  else bind();
})();
