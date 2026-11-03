/* ==========================================================================
   星海背景：canvas 粒子 + 视差 + 流星
   独立模块，不依赖其它脚本
   ========================================================================== */
(function () {
  'use strict';

  const canvas = document.getElementById('starfield');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let w = 0, h = 0, dpr = 1;
  let stars = [];
  let shooting = [];
  const pointer = { x: 0, y: 0, tx: 0, ty: 0 };

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = canvas.clientWidth;
    h = canvas.clientHeight;
    canvas.width = Math.floor(w * dpr);
    canvas.height = Math.floor(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
  }

  function build() {
    const count = Math.min(210, Math.round((w * h) / 9800));
    stars = new Array(count).fill(0).map(() => {
      const depth = Math.random();
      return {
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.3 + depth * 1.1,
        a: 0.1 + Math.random() * 0.55,
        depth,
        speed: 0.006 + depth * 0.03,
        phase: Math.random() * Math.PI * 2,
        tw: 0.25 + Math.random() * 1.1,
        hue: Math.random() > 0.86 ? '232,214,170'
          : Math.random() > 0.6 ? '196,186,232'
          : '236,238,255'
      };
    });
  }

  function spawnShooting() {
    if (reduce) return;
    const fromLeft = Math.random() > 0.5;
    shooting.push({
      x: fromLeft ? Math.random() * w * 0.4 : w * 0.6 + Math.random() * w * 0.4,
      y: Math.random() * h * 0.45,
      vx: (fromLeft ? 1 : -1) * (3.4 + Math.random() * 3),
      vy: 1.5 + Math.random() * 1.6,
      life: 1,
      len: 90 + Math.random() * 120
    });
  }

  let t = 0;
  function frame() {
    t += 0.016;
    pointer.x += (pointer.tx - pointer.x) * 0.05;
    pointer.y += (pointer.ty - pointer.y) * 0.05;

    ctx.clearRect(0, 0, w, h);

    for (const s of stars) {
      const dx = pointer.x * s.depth * 26;
      const dy = pointer.y * s.depth * 26;
      const twinkle = reduce ? 1 : 0.62 + 0.38 * Math.sin(t * s.tw + s.phase);

      ctx.beginPath();
      ctx.fillStyle = 'rgba(' + s.hue + ',' + (s.a * twinkle).toFixed(3) + ')';
      ctx.arc(s.x + dx, s.y + dy, s.r, 0, Math.PI * 2);
      ctx.fill();

      if (s.depth > 0.82 && s.r > 1.1) {
        ctx.beginPath();
        ctx.fillStyle = 'rgba(' + s.hue + ',' + (0.055 * twinkle).toFixed(3) + ')';
        ctx.arc(s.x + dx, s.y + dy, s.r * 5, 0, Math.PI * 2);
        ctx.fill();
      }

      if (!reduce) {
        s.y += s.speed;
        if (s.y > h + 2) { s.y = -2; s.x = Math.random() * w; }
      }
    }

    for (let i = shooting.length - 1; i >= 0; i--) {
      const m = shooting[i];
      m.x += m.vx;
      m.y += m.vy;
      m.life -= 0.012;
      if (m.life <= 0) { shooting.splice(i, 1); continue; }

      const gx = m.x - m.vx * (m.len / 6);
      const gy = m.y - m.vy * (m.len / 6);
      const grad = ctx.createLinearGradient(m.x, m.y, gx, gy);
      grad.addColorStop(0, 'rgba(246,230,194,' + (0.9 * m.life).toFixed(3) + ')');
      grad.addColorStop(1, 'rgba(246,230,194,0)');

      ctx.strokeStyle = grad;
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      ctx.moveTo(m.x, m.y);
      ctx.lineTo(gx, gy);
      ctx.stroke();
    }

    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', (e) => {
    pointer.tx = (e.clientX / window.innerWidth - 0.5) * 2;
    pointer.ty = (e.clientY / window.innerHeight - 0.5) * 2;
  }, { passive: true });

  resize();
  requestAnimationFrame(frame);
  if (!reduce) {
    setInterval(() => { if (shooting.length < 2) spawnShooting(); }, 7800);
  }
})();
