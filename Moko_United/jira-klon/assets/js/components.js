// Ortak render yardımcıları — lozenge, issue-type ikonu, priority ikonu, avatar.
// list.js / board.js / issue.js / dashboard.js tarafından paylaşılır.
(function () {
  function esc(s) {
    var d = document.createElement('div');
    d.textContent = s == null ? '' : String(s);
    return d.innerHTML;
  }

  var TYPE_ICON_SVG = {
    bug: '<svg viewBox="0 0 12 12" fill="none"><circle cx="6" cy="7" r="3.4" stroke="white" stroke-width="1.1"/><path d="M6 3.6V2M3.6 4.4L2.4 3.2M8.4 4.4l1.2-1.2" stroke="white" stroke-width="1.1" stroke-linecap="round"/></svg>',
    task: '<svg viewBox="0 0 12 12" fill="none"><path d="M2.5 6.2l2 2 5-5" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    story: '<svg viewBox="0 0 12 12" fill="none"><path d="M3 2h6v8l-3-2-3 2V2z" fill="white"/></svg>',
    epic: '<svg viewBox="0 0 12 12" fill="none"><path d="M6.5 1.5L3 6.5h2.3L4.5 10.5 9 5h-2.3l0.8-3.5z" fill="white"/></svg>',
    subtask: '<svg viewBox="0 0 12 12" fill="none"><path d="M3 2v4.5a1.5 1.5 0 001.5 1.5H8M8 8L6 6M8 8l-2 2" stroke="white" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  var PRIORITY_ICON_SVG = {
    kritik: '<svg viewBox="0 0 16 16" fill="none"><path d="M4 9l4-4 4 4M4 13l4-4 4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    yuksek: '<svg viewBox="0 0 16 16" fill="none"><path d="M4 10l4-4 4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    orta: '<svg viewBox="0 0 16 16" fill="none"><path d="M3.5 6.5h9M3.5 9.5h9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    dusuk: '<svg viewBox="0 0 16 16" fill="none"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  };

  function typeIcon(issuetype) {
    var svg = TYPE_ICON_SVG[issuetype] || TYPE_ICON_SVG.task;
    return '<span class="j-type-icon j-type-' + issuetype + '" title="' + issuetype + '">' + svg + '</span>';
  }

  function priorityIcon(priority, label) {
    var svg = PRIORITY_ICON_SVG[priority] || PRIORITY_ICON_SVG.orta;
    return '<span class="j-priority-icon j-priority-' + priority + '" title="' + esc(label || priority) + '">' + svg + '</span>';
  }

  function lozenge(category, label) {
    return '<span class="j-lozenge j-lozenge-' + category + '">' + esc(label) + '</span>';
  }

  function avatar(initials, name, size, unassigned) {
    size = size || 'md';
    if (unassigned) {
      return '<span class="j-avatar j-avatar-' + size + ' j-avatar-unassigned" title="Atanmamış">?</span>';
    }
    var color = window.MokaAvatarColor ? window.MokaAvatarColor(name || initials || '?') : '#357DE8';
    return '<span class="j-avatar j-avatar-' + size + '" style="background:' + color + ';" title="' + esc(name || '') + '">' + esc(initials || '?') + '</span>';
  }

  function tag(text) {
    return '<span class="j-tag">' + esc(text) + '</span>';
  }

  function fmtDateTime(iso) {
    if (!iso) return '—';
    try {
      var d = new Date(iso);
      return d.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short' }) + ' ' +
        d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
    } catch (e) { return iso; }
  }

  function toast(message, isError) {
    var stack = document.querySelector('.j-toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'j-toast-stack';
      document.body.appendChild(stack);
    }
    var el = document.createElement('div');
    el.className = 'j-toast' + (isError ? ' j-toast-danger' : '');
    el.textContent = message;
    stack.appendChild(el);
    requestAnimationFrame(function () { el.classList.add('j-toast-in'); });
    setTimeout(function () {
      el.classList.remove('j-toast-in');
      setTimeout(function () { el.remove(); }, 200);
    }, 1800);
  }

  window.MokaUI = { esc: esc, typeIcon: typeIcon, priorityIcon: priorityIcon, lozenge: lozenge, avatar: avatar, tag: tag, fmtDateTime: fmtDateTime, toast: toast };
})();
