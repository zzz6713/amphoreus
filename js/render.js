/* ==========================================================================
   渲染层：黄金裔卡片 + 光锥长廊
   对外：AMP.render()
   ========================================================================== */
(function (AMP) {
  'use strict';

  const CONE_DIR = 'assets/lightcones/';   // 光锥立绘（长廊 + 弹层）
  const HEIR_DIR = 'assets/heirs/';        // 角色海报（卡片）

  const IMG_FALLBACK = 'is-missing';

  function bindImageFallback(img) {
    img.addEventListener('error', () => img.classList.add(IMG_FALLBACK), { once: true });
  }

  function heirCard(h) {
    const card = document.createElement('article');
    card.className = 'heir-card reveal';
    card.style.setProperty('--hue', h.hue);
    card.innerHTML =
      '<button class="heir-click" type="button" aria-label="查看' + h.name + '的详情">' +
        '<div class="cone">' +
          '<div class="cone-fallback"><span>∞</span><em>光锥</em></div>' +
          '<img src="' + HEIR_DIR + h.id + '.webp" alt="' + h.name + '的角色海报" loading="lazy" />' +
          '<div class="cone-shine"></div>' +
          '<span class="numeral">' + h.numeral + '</span>' +
        '</div>' +
        '<div class="heir-info">' +
          '<h3>' + h.name + '</h3>' +
          '<p class="en">' + h.en + '</p>' +
          '<p class="title">' + h.title + '</p>' +
          '<span class="flame">' + h.flame + '</span>' +
        '</div>' +
      '</button>';
    bindImageFallback(card.querySelector('img'));
    card.addEventListener('click', () => AMP.modal.open(h));
    return card;
  }

  function railItem(h) {
    const item = document.createElement('div');
    item.className = 'rail-item reveal';
    item.style.setProperty('--hue', h.hue);
    item.innerHTML =
      '<div class="rail-frame">' +
        '<div class="cone-fallback"><span>∞</span><em>光锥</em></div>' +
        '<img src="' + CONE_DIR + h.id + '.webp" alt="' + h.name + '的光锥「' + h.cone + '」" loading="lazy" />' +
      '</div>' +
      '<p class="rail-name">' + h.cone + '</p>' +
      '<p class="rail-owner">' + h.name + '</p>';
    bindImageFallback(item.querySelector('img'));
    item.addEventListener('click', () => AMP.modal.open(h));
    return item;
  }

  function render() {
    const data = window.AMPHOREUS;
    const grid = document.getElementById('heirGrid');
    const rail = document.getElementById('coneRail');
    if (!data || !grid || !rail) return;

    const fragGrid = document.createDocumentFragment();
    const fragRail = document.createDocumentFragment();

    data.heirs.forEach((h) => {
      fragGrid.appendChild(heirCard(h));
      fragRail.appendChild(railItem(h));
    });

    grid.appendChild(fragGrid);
    rail.appendChild(fragRail);
  }

  AMP.render = render;
})(window.AMP = window.AMP || {});
