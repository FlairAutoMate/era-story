// Responsive/cross-browser audit: every route × viewport × engine.
// Reports horizontal overflow, elements poking outside the viewport, clipped text,
// overlapping text blocks, tap targets under 44 px, inputs under 16 px and console errors.
// Usage: node qa-responsive.mjs [url] [engines=chromium,firefox,webkit] [viewports=all|quick] [routes]
import { chromium, firefox, webkit } from "playwright";
import { writeFileSync, mkdirSync } from "node:fs";

const base = process.argv[2] ?? "http://localhost:8787";
const engines = (process.argv[3] ?? "chromium").split(",");
const vpSet = process.argv[4] ?? "all";
const routes = (process.argv[5] ?? "/,/boligeier,/styret,/handverker,/faghandel,/personvern").split(",");
const ALL = [[320, 568], [360, 800], [375, 812], [390, 844], [414, 896], [768, 1024], [820, 1180], [1024, 768], [1280, 800], [1440, 900], [1920, 1080], [812, 375], [844, 390], [1180, 820]];
const QUICK = [[320, 568], [390, 844], [768, 1024], [1440, 900], [844, 390]];
const viewports = vpSet === "quick" ? QUICK : ALL;
const launchers = { chromium, firefox, webkit };
mkdirSync("qa/responsive", { recursive: true });

const AUDIT = () => {
  const vw = innerWidth, vh = innerHeight, out = [];
  const vis = (el) => { const cs = getComputedStyle(el); if (cs.display === "none" || cs.visibility === "hidden") return false; let e = el; while (e && e !== document.body) { const c = getComputedStyle(e); if (parseFloat(c.opacity) < 0.5 || c.display === "none" || c.visibility === "hidden") return false; e = e.parentElement; } return true; };
  const inView = (r) => r.bottom > 0 && r.top < vh && r.width > 0 && r.height > 0;
  const txt = (el) => (el.innerText || el.value || el.getAttribute("aria-label") || "").trim().replace(/\s+/g, " ").slice(0, 60);
  if (document.documentElement.scrollWidth > vw + 1) out.push({ kind: "overflow-x", detail: `scrollWidth ${document.documentElement.scrollWidth} > ${vw}` });
  const textEls = [...document.querySelectorAll("h1,h2,h3,p,a,button,span,div,li,summary,label,input")];
  const blocks = [];
  for (const el of textEls) {
    if (!vis(el)) continue;
    const r = el.getBoundingClientRect();
    if (!inView(r)) continue;
    const t = txt(el);
    const ownText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const clipped = (() => { let e = el.parentElement; while (e && e !== document.body) { const c = getComputedStyle(e); if (c.overflow !== "visible" || c.overflowX !== "visible") { const cr = e.getBoundingClientRect(); if (r.right <= cr.left + 1 || r.left >= cr.right - 1) return true; return r.left < cr.left - 1 || r.right > cr.right + 1; } e = e.parentElement; } return false; })();
    if (ownText && !clipped && (r.left < -1 || r.right > vw + 1)) out.push({ kind: "outside-viewport", detail: `${el.tagName} "${t}" left=${Math.round(r.left)} right=${Math.round(r.right)}` });
    const cs = getComputedStyle(el);
    if (ownText && cs.overflow !== "visible" && cs.whiteSpace === "nowrap" && el.scrollWidth > el.clientWidth + 2 && !el.id.includes("typewriter")) out.push({ kind: "clipped-text", detail: `${el.tagName} "${t}" scroll=${el.scrollWidth} client=${el.clientWidth}` });
    if (/^(H1|H2|H3|P)$/.test(el.tagName) && t && ownText) blocks.push({ el, r, t });
    if (/^(A|BUTTON|SUMMARY)$/.test(el.tagName) || (el.tagName === "INPUT" && el.type !== "hidden")) {
      if (el.getAttribute("aria-hidden") === "true" || el.tabIndex < 0) continue;
      const pill = el.tagName === "INPUT" ? el.closest(".lead-pill, form > div") : null; const pr = pill ? pill.getBoundingClientRect() : r;
      if (pr.width > 0 && (pr.width < 44 || pr.height < 44) && !(pr.height >= 40 && pr.width >= 100)) {
        const kids = el.closest("footer, nav") ? "nav/footer" : "content";
        out.push({ kind: "tap-target", detail: `${el.tagName} "${t}" ${Math.round(r.width)}×${Math.round(r.height)} (${kids})` });
      }
    }
    if (el.tagName === "INPUT" && el.type !== "hidden" && parseFloat(cs.fontSize) < 16) out.push({ kind: "input-font", detail: `${el.name || el.id} ${cs.fontSize}` });
  }
  for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) {
    const a = blocks[i], b = blocks[j];
    if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
    const ix = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left), iy = Math.min(a.r.bottom, b.r.bottom) - Math.max(a.r.top, b.r.top);
    if (ix > 8 && iy > 8) out.push({ kind: "overlap", detail: `"${a.t}" × "${b.t}" (${Math.round(ix)}×${Math.round(iy)})` });
  }
  return out;
};

const results = {};
for (const eng of engines) {
  const browser = await launchers[eng].launch();
  for (const [w, h] of viewports) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, hasTouch: w < 900, isMobile: eng !== "firefox" && w < 900 });
    const page = await ctx.newPage();
    const errs = [];
    page.on("pageerror", (e) => errs.push("pageerror: " + e.message));
    page.on("console", (m) => { if (m.type() === "error" && !/404|Expected length|insights/.test(m.text())) errs.push("console: " + m.text().slice(0, 160)); });
    for (const route of routes) {
      const key = `${eng} ${w}×${h} ${route}`;
      const found = new Map();
      try {
        await page.goto(base + route, { waitUntil: "networkidle", timeout: 30000 });
        await page.waitForTimeout(800);
        const stops = route === "/"
          ? await page.evaluate(() => [...document.querySelectorAll("section")].flatMap((s) => { const y = s.getBoundingClientRect().top + scrollY, hh = s.offsetHeight, ex = Math.max(0, hh - innerHeight); return ex > innerHeight ? [y + ex * 0.25, y + ex * 0.6, y + ex * 0.97] : [y + ex * 0.5]; }))
          : await page.evaluate(() => { const H = document.documentElement.scrollHeight - innerHeight, a = []; for (let y = 0; y <= H; y += innerHeight * 0.8) a.push(y); a.push(H); return a; });
        for (const y of stops) {
          await page.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), Math.round(y));
          await page.waitForTimeout(220);
          for (const it of await page.evaluate(AUDIT)) { const k = it.kind + "|" + it.detail; if (!found.has(k)) found.set(k, { ...it, y: Math.round(y) }); }
        }
        if (route === "/" && w < 900) {
          await page.evaluate(() => scrollTo({ top: innerHeight * 3, behavior: "instant" })); await page.waitForTimeout(400);
          const btn = page.locator("[data-menu-toggle]").first();
          if (await btn.count()) { await btn.click(); await page.waitForTimeout(300); for (const it of await page.evaluate(AUDIT)) { const k = "menu:" + it.kind + "|" + it.detail; if (!found.has(k)) found.set(k, { ...it, kind: "menu:" + it.kind }); } await btn.click(); }
        }
      } catch (e) { found.set("nav", { kind: "error", detail: e.message.slice(0, 200) }); }
      for (const e of errs.splice(0)) found.set("err:" + e, { kind: "console", detail: e });
      results[key] = [...found.values()];
    }
    await ctx.close();
  }
  await browser.close();
}
writeFileSync(`qa/responsive/report-${engines.join("-")}.json`, JSON.stringify(results, null, 1));
const counts = {};
for (const [k, v] of Object.entries(results)) for (const it of v) { counts[it.kind] = (counts[it.kind] || 0) + 1; }
console.log("summary", JSON.stringify(counts));
for (const [k, v] of Object.entries(results)) if (v.length) { console.log("\n== " + k); for (const it of v.slice(0, 25)) console.log(`  [${it.kind}] ${it.detail}${it.y != null ? " @" + it.y : ""}`); if (v.length > 25) console.log(`  … +${v.length - 25}`); }
