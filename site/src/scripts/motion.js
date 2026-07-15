import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const coarse = window.matchMedia('(pointer: coarse)').matches;

gsap.registerPlugin(ScrollTrigger);

/* ---------------- Lenis smooth scroll + ScrollTrigger sync ---------------- */
let lenis = null;
if (!reduce) {
  lenis = new Lenis({
    duration: 1.05,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
  });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
}

/* ---------------- Nav: scrolled state + mobile menu ---------------- */
const nav = document.querySelector('[data-nav]');
const setScrolled = () => {
  if (!nav) return;
  window.scrollY > 20 ? nav.setAttribute('data-scrolled', '') : nav.removeAttribute('data-scrolled');
};
setScrolled();
window.addEventListener('scroll', setScrolled, { passive: true });

const navToggle = document.querySelector('[data-nav-toggle]');
const mobileMenu = document.querySelector('[data-mobile-menu]');
function openMenu() {
  if (!mobileMenu) return;
  mobileMenu.setAttribute('data-open', '');
  nav.setAttribute('data-menu-open', '');
  navToggle.setAttribute('aria-expanded', 'true');
  navToggle.setAttribute('aria-label', 'Close menu');
}
function closeMenu() {
  if (!mobileMenu || navToggle?.getAttribute('aria-expanded') !== 'true') return;
  mobileMenu.removeAttribute('data-open');
  nav.removeAttribute('data-menu-open');
  navToggle.setAttribute('aria-expanded', 'false');
  navToggle.setAttribute('aria-label', 'Open menu');
}
navToggle?.addEventListener('click', () =>
  navToggle.getAttribute('aria-expanded') === 'true' ? closeMenu() : openMenu());
document.querySelectorAll('[data-mobile-link]').forEach((l) => l.addEventListener('click', closeMenu));
window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

/* Anchor links → smooth scroll with nav offset */
document.querySelectorAll('a[href^="#"]').forEach((a) => {
  a.addEventListener('click', (e) => {
    const id = a.getAttribute('href');
    if (!id || id === '#') return;
    const el = document.querySelector(id);
    if (!el) return;
    e.preventDefault();
    closeMenu();
    if (lenis) lenis.scrollTo(el, { offset: id === '#top' ? 0 : -64 });
    else el.scrollIntoView({ behavior: 'smooth' });
  });
});

/* ---------------- Reveal on scroll (staggered) ---------------- */
if (reduce) {
  document.querySelectorAll('[data-reveal]').forEach((el) => el.classList.add('is-in'));
} else {
  ScrollTrigger.batch('[data-reveal]', {
    start: 'top 90%',
    once: true,
    onEnter: (batch) => batch.forEach((el, i) => setTimeout(() => el.classList.add('is-in'), i * 90)),
  });
}

/* ---------------- Hero name — line rise-in on load ---------------- */
const heroName = document.querySelector('[data-hero-name]');
if (heroName && !reduce) {
  const spans = heroName.querySelectorAll('.line span');
  gsap.set(spans, { yPercent: 115 });
  gsap.to(spans, { yPercent: 0, duration: 1.05, ease: 'power4.out', stagger: 0.1, delay: 0.12 });
}

/* ---------------- Project card tilt (fine pointers only) ---------------- */
if (!coarse && !reduce) {
  document.querySelectorAll('[data-tilt]').forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const r = card.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      gsap.to(card, { rotateX: -py * 4, rotateY: px * 5, y: -6, duration: 0.4, ease: 'power2.out', transformPerspective: 900, transformOrigin: 'center' });
    });
    card.addEventListener('mouseleave', () => {
      gsap.to(card, { rotateX: 0, rotateY: 0, y: 0, duration: 0.55, ease: 'power3.out' });
    });
  });
}

/* ---------------- Cursor-reactive technical grid ---------------- */
(function grid() {
  const canvas = document.getElementById('grid-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.setAttribute('data-live', '');
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  const GAP = 54, RADIUS = 118, CORE = 44;
  let W, H, mx = -9999, my = -9999, cx = -9999, cy = -9999, hasMouse = false;

  function resize() {
    W = canvas.width = window.innerWidth * DPR;
    H = canvas.height = window.innerHeight * DPR;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
  }
  function baseGrid(alpha) {
    const g = GAP * DPR;
    ctx.lineWidth = DPR;
    ctx.strokeStyle = 'rgba(255,255,255,' + alpha + ')';
    ctx.beginPath();
    for (let x = 0; x <= W; x += g) { ctx.moveTo(x, 0); ctx.lineTo(x, H); }
    for (let y = 0; y <= H; y += g) { ctx.moveTo(0, y); ctx.lineTo(W, y); }
    ctx.stroke();
  }
  function drawStatic() { ctx.clearRect(0, 0, W, H); baseGrid(0.05); }

  resize();
  window.addEventListener('resize', () => { resize(); if (reduce || coarse) drawStatic(); });

  if (reduce || coarse) { drawStatic(); return; }

  window.addEventListener('mousemove', (e) => { mx = e.clientX * DPR; my = e.clientY * DPR; hasMouse = true; }, { passive: true });
  document.addEventListener('mouseleave', () => { hasMouse = false; });

  function frame() {
    cx += (mx - cx) * 0.18;
    cy += (my - cy) * 0.18;
    ctx.clearRect(0, 0, W, H);
    baseGrid(0.045);

    if (hasMouse) {
      const g = GAP * DPR, rad = RADIUS * DPR, core = CORE * DPR;
      ctx.save();
      ctx.beginPath(); ctx.arc(cx, cy, rad, 0, Math.PI * 2); ctx.clip();
      const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
      grd.addColorStop(0, 'rgba(240,178,74,0.55)');
      grd.addColorStop(core / rad, 'rgba(240,178,74,0.28)');
      grd.addColorStop(1, 'rgba(240,178,74,0)');
      ctx.lineWidth = DPR * 1.1;
      ctx.strokeStyle = grd;
      ctx.beginPath();
      const sx = Math.floor((cx - rad) / g) * g, sy = Math.floor((cy - rad) / g) * g;
      for (let x = sx; x <= cx + rad; x += g) { ctx.moveTo(x, cy - rad); ctx.lineTo(x, cy + rad); }
      for (let y = sy; y <= cy + rad; y += g) { ctx.moveTo(cx - rad, y); ctx.lineTo(cx + rad, y); }
      ctx.stroke();
      ctx.restore();

      const ix = Math.floor((cx - rad) / g) * g, iy = Math.floor((cy - rad) / g) * g;
      for (let x = ix; x <= cx + rad; x += g) {
        for (let y = iy; y <= cy + rad; y += g) {
          const d = Math.hypot(x - cx, y - cy);
          if (d < rad) {
            const a = 1 - d / rad;
            ctx.beginPath();
            ctx.arc(x, y, DPR * (0.8 + a * 1.8), 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(240,178,74,' + (a * a * 0.9) + ')';
            ctx.fill();
          }
        }
      }
      const amb = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
      amb.addColorStop(0, 'rgba(240,178,74,0.07)');
      amb.addColorStop(1, 'rgba(240,178,74,0)');
      ctx.fillStyle = amb;
      ctx.beginPath(); ctx.arc(cx, cy, rad, 0, Math.PI * 2); ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

/* ---------------- Contact form — validation + submit ---------------- */
(function contact() {
  const form = document.querySelector('[data-contact]');
  if (!form) return;
  const status = form.querySelector('[data-form-status]');
  const el = (n) => form.elements[n];
  const errBox = (n) => form.querySelector(`[data-err-for="${n}"]`);

  function setErr(n, msg) {
    const field = el(n).closest('.field');
    const box = errBox(n);
    if (msg) { field.setAttribute('data-invalid', ''); box.hidden = false; box.textContent = msg; }
    else { field.removeAttribute('data-invalid'); box.hidden = true; box.textContent = ''; }
  }
  function validate() {
    let ok = true;
    const name = el('name').value.trim();
    const email = el('email').value.trim();
    const message = el('message').value.trim();
    if (!name) { setErr('name', 'Please enter your name.'); ok = false; } else setErr('name');
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { setErr('email', 'Enter a valid email address.'); ok = false; } else setErr('email');
    if (!message) { setErr('message', 'Add a short message.'); ok = false; } else setErr('message');
    return ok;
  }
  ['name', 'email', 'message'].forEach((n) => el(n).addEventListener('input', () => setErr(n)));

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    status.removeAttribute('data-ok'); status.removeAttribute('data-bad'); status.textContent = '';
    if (!validate()) {
      status.setAttribute('data-bad', '');
      status.textContent = 'Please fix the highlighted fields.';
      form.querySelector('[data-invalid] input, [data-invalid] textarea')?.focus();
      return;
    }
    const data = { name: el('name').value.trim(), email: el('email').value.trim(), message: el('message').value.trim() };
    const endpoint = form.getAttribute('data-endpoint');

    if (endpoint && endpoint !== 'mailto') {
      const btn = form.querySelector('.contact-submit');
      btn.disabled = true; status.textContent = 'Sending…';
      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(data),
        });
        if (!res.ok) throw new Error('bad');
        form.reset();
        status.setAttribute('data-ok', '');
        status.textContent = 'Thanks — your message is on its way. I’ll be in touch soon.';
      } catch {
        status.setAttribute('data-bad', '');
        status.textContent = 'Something went wrong — please email hello@jackmotzkin.com directly.';
      } finally { btn.disabled = false; }
    } else {
      const subject = encodeURIComponent(`Portfolio enquiry — ${data.name}`);
      const body = encodeURIComponent(`${data.message}\n\n— ${data.name}\n${data.email}`);
      window.location.href = `mailto:hello@jackmotzkin.com?subject=${subject}&body=${body}`;
      status.setAttribute('data-ok', '');
      status.textContent = 'Opening your email app… if nothing happens, email hello@jackmotzkin.com directly.';
    }
  });
})();

window.addEventListener('load', () => ScrollTrigger.refresh());
