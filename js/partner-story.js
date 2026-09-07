// ERA Partner Story: a lightweight reveal engine, deliberately independent of the public
// story's scroll-motor (index.html's <script data-dc-script>). That engine is a bespoke
// custom-element compiler tightly coupled to the homepage's own chapters; a partner story
// should not require touching it to ship a new partner, so this file is generic and reusable
// across /partner/<slug> pages instead. IntersectionObserver toggles `.in-view` on `.reveal`,
// `.reveal-stagger` and `.reveal-img` elements; partner.css defines the before/after state.
// `prefers-reduced-motion` is handled purely in CSS, so this script has nothing special to do
// for it — the class still gets added, it just triggers no visible transition.
(function () {
  if (!("IntersectionObserver" in window)) {
    document.querySelectorAll(".reveal, .reveal-stagger, .reveal-img, .p-transition").forEach(function (el) { el.classList.add("in-view"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in-view"); io.unobserve(e.target); }
    });
  }, { threshold: 0.35, rootMargin: "0px 0px -8% 0px" });
  document.querySelectorAll(".reveal, .reveal-stagger, .reveal-img, .p-transition").forEach(function (el) { io.observe(el); });
})();

// Minimal nav: highlight the in-view act in the dedicated partner pill (not the public nav).
(function () {
  var links = [].slice.call(document.querySelectorAll(".p-pill [data-act]"));
  var sections = links.map(function (a) { return document.getElementById(a.getAttribute("data-act")); }).filter(Boolean);
  if (!sections.length) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var link = links[sections.indexOf(e.target)];
      if (!link) return;
      if (e.isIntersecting) links.forEach(function (l) { l.removeAttribute("aria-current"); });
      if (e.isIntersecting) link.setAttribute("aria-current", "true");
    });
  }, { rootMargin: "-45% 0px -45% 0px" });
  sections.forEach(function (s) { io.observe(s); });
})();
