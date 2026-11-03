/* ==========================================================================
   交互效果：导航 / 进度条 / 回到顶部 / 章节高亮 / 入场动画 / 翻转卡
   对外：AMP.effects.init() / AMP.effects.observeNew(nodes)
   ========================================================================== */
(function (AMP) {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  let revealObserver = null;

  /* ---------- 滚动状态：导航实底 + 进度条 + 回到顶部 ---------- */

  function initScrollState() {
    const nav = $('#nav');
    const bar = $('#progressBar');
    const toTop = $('#toTop');

    function onScroll() {
      const y = window.scrollY || document.documentElement.scrollTop;
      const max = document.documentElement.scrollHeight - window.innerHeight;

      nav.classList.toggle('is-solid', y > 40);
      if (bar) bar.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + '%';
      if (toTop) toTop.classList.toggle('is-show', y > 620);
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();

    if (toTop) {
      toTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  /* ---------- 章节高亮：滚动到哪个版块，导航就点亮哪一项 ---------- */

  function initScrollSpy() {
    const links = new Map();
    $$('.nav-links a[href^="#"]').forEach((a) => {
      links.set(a.getAttribute('href').slice(1), a);
    });
    if (!links.size) return;

    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((a) => a.classList.remove('is-active'));
        const active = links.get(entry.target.id);
        if (active) active.classList.add('is-active');
      });
    }, { rootMargin: '-42% 0px -52% 0px' });

    $$('main section[id]').forEach((section) => spy.observe(section));
  }

  /* ---------- 入场动画 ---------- */

  function initReveal() {
    revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -8% 0px' });

    $$('.reveal').forEach((node, i) => {
      node.style.transitionDelay = Math.min(i % 6, 5) * 60 + 'ms';
      revealObserver.observe(node);
    });
  }

  function observeNew(nodes) {
    if (!revealObserver) return;
    Array.from(nodes).forEach((node) => revealObserver.observe(node));
  }

  /* ---------- 第十三位：翻转卡 ---------- */

  function initFlip() {
    const card = $('#flipCard');
    if (!card) return;

    const data = window.AMPHOREUS && window.AMPHOREUS.thirteenth;
    if (data) {
      const meta = $('.flip-meta', card);
      if (meta) {
        meta.querySelector('em').textContent = data.name + ' · ' + data.en;
        meta.querySelector('b').textContent = '「' + data.title + '」';
        meta.querySelector('i').textContent = data.prophecy;
      }
    }

    card.addEventListener('click', () => {
      const flipped = card.classList.toggle('is-flipped');
      card.setAttribute('aria-label', flipped ? '合上第十三位' : '翻开第十三位');
    });
  }

  /* ---------- 初始化 ---------- */

  function init() {
    initScrollState();
    initScrollSpy();
    initFlip();
    initReveal();
  }

  AMP.effects = { init, observeNew };
})(window.AMP = window.AMP || {});
