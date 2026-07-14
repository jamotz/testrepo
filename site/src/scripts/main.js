import Lenis from "lenis";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const fine = window.matchMedia("(pointer: fine)").matches;
const css = (name, el = document.documentElement) =>
  getComputedStyle(el).getPropertyValue(name).trim();
function hexA(hex, a) {
  hex = (hex || "#7C5CFF").replace("#", "");
  if (hex.length === 3) hex = hex.split("").map((c) => c + c).join("");
  const n = parseInt(hex, 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}

/* ---------------- Theme ---------------- */
function currentTheme() {
  const ex = document.documentElement.getAttribute("data-theme");
  if (ex) return ex;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".theme-toggle");
  btn?.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    try { localStorage.setItem("motz-theme", next); } catch (e) {}
    window.dispatchEvent(new Event("themechange"));
  });
});

/* ---------------- Smooth scroll ---------------- */
if (!reduce) {
  const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
  const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) { e.preventDefault(); lenis.scrollTo(el, { offset: -76 }); }
      }
    });
  });
}

/* ---------------- Nav scrolled ---------------- */
const nav = document.querySelector(".nav");
const onScroll = () => nav && nav.classList.toggle("scrolled", window.scrollY > 12);
onScroll();
window.addEventListener("scroll", onScroll, { passive: true });

/* ---------------- Mobile menu ---------------- */
(() => {
  const toggle = document.querySelector(".nav-toggle");
  const menu = document.querySelector("#mobile-menu");
  if (!toggle || !menu || !nav) return;
  const open = () => {
    menu.classList.add("open");
    nav.setAttribute("data-menu", "");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close menu");
  };
  const close = () => {
    menu.classList.remove("open");
    nav.removeAttribute("data-menu");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
  };
  toggle.addEventListener("click", () =>
    toggle.getAttribute("aria-expanded") === "true" ? close() : open());
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
  window.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
})();

/* ---------------- Reveals ---------------- */
(() => {
  const els = document.querySelectorAll(".reveal");
  if (reduce) return els.forEach((el) => el.classList.add("in"));
  const io = new IntersectionObserver((ents) => {
    ents.forEach((en) => {
      if (en.isIntersecting) {
        en.target.style.transitionDelay = (parseInt(en.target.dataset.delay || "0", 10)) + "ms";
        en.target.classList.add("in");
        io.unobserve(en.target);
      }
    });
  }, { threshold: 0.14, rootMargin: "0px 0px -8% 0px" });
  els.forEach((el) => io.observe(el));
})();

/* ---------------- Magnetic buttons ---------------- */
if (fine && !reduce) {
  document.querySelectorAll(".btn-primary, .theme-toggle").forEach((b) => {
    b.addEventListener("mousemove", (e) => {
      const r = b.getBoundingClientRect();
      const x = e.clientX - r.left - r.width / 2;
      const y = e.clientY - r.top - r.height / 2;
      b.style.transform = `translate(${x * 0.25}px, ${y * 0.3}px)`;
    });
    b.addEventListener("mouseleave", () => { b.style.transform = ""; });
  });
}

/* ---------------- Custom cursor + coordinate readout ---------------- */
if (fine && !reduce) {
  document.body.classList.add("has-cursor");
  const dot = document.querySelector(".cursor");
  const ring = document.querySelector(".cursor-ring");
  const coords = document.querySelector(".coords");
  let mx = 0, my = 0, rx = 0, ry = 0;
  window.addEventListener("mousemove", (e) => {
    mx = e.clientX; my = e.clientY;
    if (dot) dot.style.transform = `translate(${mx}px,${my}px)`;
    if (coords) coords.textContent =
      `x:${String(mx).padStart(4, "0")}  y:${String(my).padStart(4, "0")}`;
  });
  const loop = () => {
    rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18;
    if (ring) ring.style.transform = `translate(${rx}px,${ry}px)`;
    requestAnimationFrame(loop);
  };
  loop();
  document.querySelectorAll("a,button,.proj,.ecard").forEach((el) => {
    el.addEventListener("mouseenter", () => ring?.classList.add("hot"));
    el.addEventListener("mouseleave", () => ring?.classList.remove("hot"));
  });
}

/* ---------------- Hero signal-map ---------------- */
(() => {
  if (reduce) return;
  const cv = document.querySelector("canvas.signal");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  let W, H, nodes, accent, signal, mouse = { x: -9999, y: -9999 };
  function readColors() {
    accent = css("--accent") || "#7C5CFF";
    signal = css("--signal") || accent;
  }
  function size() {
    const r = cv.getBoundingClientRect();
    W = cv.width = Math.max(1, r.width * DPR);
    H = cv.height = Math.max(1, r.height * DPR);
    cv.style.width = r.width + "px"; cv.style.height = r.height + "px";
    const n = Math.min(56, Math.floor(r.width / 26));
    nodes = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.22 * DPR, vy: (Math.random() - 0.5) * 0.22 * DPR,
    }));
  }
  readColors(); size();
  window.addEventListener("resize", () => { size(); readColors(); });
  window.addEventListener("themechange", () => setTimeout(readColors, 60));
  cv.parentElement.addEventListener("mousemove", (e) => {
    const r = cv.getBoundingClientRect();
    mouse.x = (e.clientX - r.left) * DPR; mouse.y = (e.clientY - r.top) * DPR;
  });
  cv.parentElement.addEventListener("mouseleave", () => { mouse.x = mouse.y = -9999; });
  const LINK = 132 * DPR, PULL = 150 * DPR;
  function frame() {
    ctx.clearRect(0, 0, W, H);
    for (const p of nodes) {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;
      const md = Math.hypot(p.x - mouse.x, p.y - mouse.y);
      const near = md < PULL;
      ctx.beginPath();
      ctx.arc(p.x, p.y, (near ? 2.6 : 1.6) * DPR, 0, 6.29);
      ctx.fillStyle = hexA(accent, near ? 0.95 : 0.55);
      ctx.fill();
    }
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < LINK) {
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = hexA(signal, (1 - d / LINK) * 0.26);
          ctx.lineWidth = DPR * 0.6; ctx.stroke();
        }
      }
      // link to cursor
      const a = nodes[i];
      const dm = Math.hypot(a.x - mouse.x, a.y - mouse.y);
      if (dm < PULL) {
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(mouse.x, mouse.y);
        ctx.strokeStyle = hexA(accent, (1 - dm / PULL) * 0.4);
        ctx.lineWidth = DPR * 0.7; ctx.stroke();
      }
    }
    requestAnimationFrame(frame);
  }
  frame();
})();

/* ---------------- Project mini node clusters ---------------- */
(() => {
  if (reduce) return;
  document.querySelectorAll(".proj .art canvas").forEach((cv) => {
    const proj = cv.closest(".proj");
    const ctx = cv.getContext("2d");
    const DPR = Math.min(window.devicePixelRatio || 1, 2);
    let W, H, pts;
    const color = () => css("--ac", proj) || css("--accent");
    function size() {
      const r = cv.getBoundingClientRect();
      W = cv.width = Math.max(1, r.width * DPR); H = cv.height = Math.max(1, r.height * DPR);
      pts = Array.from({ length: 9 }, () => ({
        x: Math.random() * W, y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.12 * DPR, vy: (Math.random() - 0.5) * 0.12 * DPR,
      }));
    }
    size(); window.addEventListener("resize", size);
    function frame() {
      const c = color();
      ctx.clearRect(0, 0, W, H);
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i]; p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1; if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.beginPath(); ctx.arc(p.x, p.y, 2 * DPR, 0, 6.29); ctx.fillStyle = hexA(c, 0.8); ctx.fill();
        for (let j = i + 1; j < pts.length; j++) {
          const q = pts[j], d = Math.hypot(p.x - q.x, p.y - q.y);
          if (d < 70 * DPR) {
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = hexA(c, (1 - d / (70 * DPR)) * 0.5); ctx.lineWidth = DPR * 0.5; ctx.stroke();
          }
        }
      }
      requestAnimationFrame(frame);
    }
    frame();
  });
})();
