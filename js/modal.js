/* ==========================================================================
   详情弹层：打开 / 关闭 / 焦点管理
   对外：AMP.modal.open(heir) / AMP.modal.close() / AMP.modal.init()
   ========================================================================== */
(function (AMP) {
  'use strict';

  const HEIR_DIR = 'assets/heirs/';

  let modal, closeBtn;
  let lastFocus = null;
  let isOpen = false;

  const el = (id) => document.getElementById(id);

  function render(h) {
    // 同一张海报：一张虚化做背景，一张清晰做前景
    const src = HEIR_DIR + h.id + '.webp';
    const blur = el('modalBlur');
    const photo = el('modalPhoto');
    if (blur) blur.src = src;
    if (photo) {
      photo.src = src;
      photo.alt = h.name + ' 的角色海报';
    }
    el('modalIndex').textContent = 'NO. ' + h.numeral + '　·　黄金裔';
    el('modalName').textContent = h.name;
    el('modalEn').textContent = h.en;
    el('modalTitle').textContent = h.title + '　·　' + h.flame + '的火种　·　' + h.city;

    const tags = el('modalTags');
    tags.innerHTML = '';
    [h.flame + '·火种', h.city, '光锥：' + h.cone].forEach((txt) => {
      const s = document.createElement('span');
      s.textContent = txt;
      tags.appendChild(s);
    });

    const quote = el('modalQuote');
    quote.textContent = h.verse;
    quote.style.borderLeftColor = h.hue;

    el('modalDetail').textContent = h.detail || h.intro;
    el('modalProphecy').textContent = h.prophecy;
  }

  function open(h) {
    render(h);
    lastFocus = document.activeElement;
    isOpen = true;
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    closeBtn.focus({ preventScroll: true });
  }

  function close() {
    isOpen = false;
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }

  // 焦点锁在弹层内，Tab 不会跑到背后的页面
  function trapFocus(e) {
    if (e.key !== 'Tab' || !isOpen) return;
    const focusables = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function init() {
    modal = el('modal');
    if (!modal) return;
    closeBtn = modal.querySelector('.modal-close');

    modal.querySelectorAll('[data-close]').forEach((node) => {
      node.addEventListener('click', close);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && isOpen) close();
      trapFocus(e);
    });
  }

  AMP.modal = { open, close, init };
})(window.AMP = window.AMP || {});
