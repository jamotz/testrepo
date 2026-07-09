import gsap from "gsap";
import Lenis from "lenis";

const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const finePointer = window.matchMedia("(pointer: fine)").matches;

/* ---------------- Theme ---------------- */
const THEME_KEY = "motz-theme";
function applyTheme(t) {
  const root = document.documentElement;
  if (t === "light" || t === "dark") root.setAttribute("data-theme", t);
  else root.removeAttribute("data-theme");
}
function currentTheme() {
  const explicit = document.documentElement.getAttribute("data-theme");
  if (explicit) return explicit;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".theme-toggle");
  if (btn) {
    btn.addEventListener("click", () => {
      const next = currentTheme() === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
    });
  }
});

/* ---------------- Smooth scroll ---------------- */
if (!reduce) {
  const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
  function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
  requestAnimationFrame(raf);
  // anchor links -> lenis
  document.querySelectorAll('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (id.length > 1) {
        const el = document.querySelector(id);
        if (el) { e.preventDefault(); lenis.scrollTo(el, { offset: -80 }); }
      }
    });
  });
}

/* ---------------- Nav scrolled state ---------------- */
const nav = document.querySelector(".nav");
const onScroll = () => { if (nav) nav.classList.toggle("scrolled", window.scrollY > 12); };
onScroll();
window.addEventListener("scroll", onScroll, { passive: true });

/* ---------------- Scroll reveals ---------------- */
(() => {
  const els = document.querySelectorAll(".reveal");
  if (reduce) { els.forEach((el) => el.classList.add("in")); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((en) => {
      if (en.isIntersecting) {
        const el = en.target;
        const delay = parseInt(el.dataset.delay || "0", 10);
        el.style.transitionDelay = delay + "ms";
        el.classList.add("in");
        io.unobserve(el);
      }
    });
  }, { threshold: 0.14, rootMargin: "0px 0px -8% 0px" });
  els.forEach((el) => io.observe(el));
})();

/* ---------------- Hero intro ---------------- */
window.addEventListener("DOMContentLoaded", () => {
  if (reduce) return;
  const q = (s) => document.querySelector(s);
  const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
  if (q(".hero .kicker")) tl.from(".hero .kicker", { y: 18, opacity: 0, duration: 0.6 });
  if (q(".hero h1")) tl.from(".hero h1", { y: 28, opacity: 0, duration: 0.85 }, "-=0.3");
  if (q(".hero .lede")) tl.from(".hero .lede", { y: 22, opacity: 0, duration: 0.7 }, "-=0.5");
  if (q(".hero .cta-row")) tl.from(".hero .cta-row > *", { y: 16, opacity: 0, duration: 0.5, stagger: 0.1 }, "-=0.4");
  if (q(".hero .proof")) tl.from(".hero .proof .p", { y: 14, opacity: 0, duration: 0.5, stagger: 0.08 }, "-=0.3");
  const path = q(".hero h1 .accent path");
  if (path) {
    const len = path.getTotalLength();
    gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
    tl.to(path, { strokeDashoffset: 0, duration: 0.9, ease: "power2.inOut" }, "-=0.9");
  }
  const mark = q(".brand .mark");
  if (mark) tl.from(mark, { rotate: -30, scale: 0.6, opacity: 0, duration: 0.6, ease: "back.out(1.7)" }, 0);
});

/* ---------------- Card 3D tilt ---------------- */
if (finePointer && !reduce) {
  document.querySelectorAll(".proj").forEach((c) => {
    c.addEventListener("mousemove", (e) => {
      const r = c.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      c.style.transform = `perspective(900px) rotateX(${-py * 4}deg) rotateY(${px * 5}deg) translateY(-5px)`;
    });
    c.addEventListener("mouseleave", () => { c.style.transform = ""; });
  });
}

/* ---------------- Custom cursor ---------------- */
if (finePointer && !reduce) {
  document.body.classList.add("has-cursor");
  const dot = document.querySelector(".cursor");
  const ring = document.querySelector(".cursor-ring");
  if (dot && ring) {
    let mx = 0, my = 0, rx = 0, ry = 0;
    window.addEventListener("mousemove", (e) => {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = `translate(${mx}px,${my}px)`;
    });
    const loop = () => { rx += (mx - rx) * 0.18; ry += (my - ry) * 0.18;
      ring.style.transform = `translate(${rx}px,${ry}px)`; requestAnimationFrame(loop); };
    loop();
    document.querySelectorAll("a,button,.proj,.ecard").forEach((el) => {
      el.addEventListener("mouseenter", () => ring.classList.add("hot"));
      el.addEventListener("mouseleave", () => ring.classList.remove("hot"));
    });
  }
}

/* ---------------- Hero aura canvas ---------------- */
(() => {
  if (reduce) return;
  const cv = document.querySelector("canvas.aura");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  let W, H, dots;
  const palette = () => {
    const cs = getComputedStyle(document.documentElement);
    return [cs.getPropertyValue("--primary").trim() || "#7A55F0",
            cs.getPropertyValue("--gold-bright").trim() || "#C9962A"];
  };
  let colors = palette();
  function size() {
    const rect = cv.getBoundingClientRect();
    W = cv.width = rect.width * DPR; H = cv.height = rect.height * DPR;
    const n = Math.min(26, Math.floor(rect.width / 46));
    dots = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: (30 + Math.random() * 60) * DPR,
      vx: (Math.random() - 0.5) * 0.14 * DPR, vy: (Math.random() - 0.5) * 0.14 * DPR,
      c: Math.random() > 0.5 ? 0 : 1,
    }));
  }
  size();
  window.addEventListener("resize", () => { size(); colors = palette(); });
  document.querySelector(".theme-toggle")?.addEventListener("click",
    () => setTimeout(() => { colors = palette(); }, 60));
  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";
    for (const d of dots) {
      d.x += d.vx; d.y += d.vy;
      if (d.x < -d.r) d.x = W + d.r; if (d.x > W + d.r) d.x = -d.r;
      if (d.y < -d.r) d.y = H + d.r; if (d.y > H + d.r) d.y = -d.r;
      const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r);
      const col = colors[d.c];
      g.addColorStop(0, hexA(col, 0.10)); g.addColorStop(1, hexA(col, 0));
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalCompositeOperation = "source-over";
    requestAnimationFrame(draw);
  }
  function hexA(hex, a) {
    hex = hex.replace("#", "");
    if (hex.length === 3) hex = hex.split("").map((c) => c + c).join("");
    const n = parseInt(hex, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }
  draw();
})();
