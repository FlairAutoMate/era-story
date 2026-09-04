// QA for the audience paths: a fresh load per deep link, then the finale's wording; plus a
// desktop screenshot of the håndverker chapter. Chapter CTAs now lead to the audience pages,
// so the audience state is exercised through the deep links (/#styret etc.).
import { chromium } from "playwright";
const base = (process.argv[2] ?? "http://localhost:8787/").replace(/\/$/, "");
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
const errs = [];
const out = {};
for (const [name, hash] of [["owner", ""], ["board", "#styret"], ["pro", "#handverker"], ["partner", "#partnere"]]) {
  const p = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  p.on("pageerror", (e) => errs.push(name + ": " + e.message));
  await p.goto(base + "/" + hash, { waitUntil: "load" });
  await p.waitForTimeout(1500);
  const landed = hash ? await p.evaluate((id) => Math.round(document.getElementById(id).getBoundingClientRect().top), hash.slice(1)) : 0;
  const [y, h] = await p.evaluate(() => { const s = document.getElementById("start").closest("section"); return [s.getBoundingClientRect().top + scrollY, s.offsetHeight]; });
  await p.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), y + (h - 900) * 0.9);
  await p.waitForTimeout(900);
  out[name] = { landed, finale: await p.evaluate(() => { const box = document.getElementById("era-lead").closest('div[style*="max-width: 560px"]'); return [box.querySelector("h2").textContent.trim(), document.getElementById("era-lead-value").placeholder, document.querySelector("#era-lead button").textContent.trim()]; }) };
  if (name === "pro") { const [y2, h2] = await p.evaluate(() => { const s = document.getElementById("handverker"); return [s.getBoundingClientRect().top + scrollY, s.offsetHeight]; }); await p.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), y2 + (h2 - 900) * 0.85); await p.waitForTimeout(800); await p.screenshot({ path: "qa/pro-08.png" }); }
  await p.close();
}
console.log(JSON.stringify({ errs, out }, null, 1));
await browser.close();
