/* ==========================================================================
   入口：把各模块按依赖顺序接起来
     data.js      → 数据
     starfield.js → 背景（自执行）
     modal.js     → 弹层
     render.js    → 卡片与长廊
     effects.js   → 交互与动画
   ========================================================================== */
(function () {
  'use strict';

  const AMP = window.AMP;
  if (!AMP) return;

  try {
    if (AMP.modal) AMP.modal.init();
    if (AMP.render) AMP.render();
    if (AMP.effects) AMP.effects.init();
  } catch (err) {
    console.error('[Amphoreus] 初始化失败：', err);
    const grid = document.getElementById('heirGrid');
    if (grid) {
      grid.innerHTML =
        '<p style="color:#e6c88f;letter-spacing:.1em">' +
        '数据加载失败，请通过本地服务器打开（python -m http.server），或查看控制台报错。' +
        '</p>';
    }
  }
})();
