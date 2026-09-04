// Tablet / landscape spot checks for the story: one frame per scene at a representative progress.
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
const url = process.argv[2] ?? "http://localhost:8787/";
const out = process.argv[3] ?? "qa/tablet";
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
for (const [name, w, h] of [["ipad-p", 820, 1180], ["ipad-l", 1180, 820], ["phone-l", 844, 390], ["tab-768", 768, 1024]]) {
  const page = await browser.newPage({ viewport: { width: w, height: h }, hasTouch: true });
  await page.goto(url, { waitUntil: "networkidle" }); await page.waitForTimeout(1000);
  const secs = await page.evaluate(() => [...document.querySelectorAll("section")].map((s) => [s.getAttribute("data-screen-label").slice(0, 2), s.getBoundingClientRect().top + scrollY, s.offsetHeight]));
  for (const [num, y, hh] of secs) {
    await page.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), Math.round(y + Math.max(0, hh - h) * 0.72));
    await page.waitForTimeout(350);
    await page.screenshot({ path: `${out}/${name}-${num}.png` });
  }
  await page.close();
}
await browser.close();
console.log("done");
