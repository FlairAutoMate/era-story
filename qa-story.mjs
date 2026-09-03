// Full-story QA: one screenshot per chapter at a representative progress, desktop + mobile, composed into contact sheets.
import { chromium } from "file:///C:/Users/mcspa/Documents/ERA/node_modules/playwright/index.mjs";
import { mkdirSync } from "node:fs";
const url = process.argv[2] ?? "http://localhost:8787/";
mkdirSync("qa/story", { recursive: true });
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
for (const [name, vp] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) {
  const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: "networkidle" }); await page.waitForTimeout(1500);
  const secs = await page.evaluate(() => [...document.querySelectorAll("section")].map((s) => [s.getAttribute("data-screen-label"), s.getBoundingClientRect().top + scrollY, s.offsetHeight]));
  let n = 0;
  for (const [label, y, h] of secs) {
    for (const f of h > vp.height * 1.5 ? [0.3, 0.8] : [0.5]) {
      await page.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), Math.round(y + Math.max(0, h - vp.height) * f));
      await page.waitForTimeout(700);
      await page.screenshot({ path: `qa/story/${name}-${String(n++).padStart(2, "0")}-${label.slice(0, 2)}-${f}.png` });
    }
  }
  await page.close();
}
await browser.close();
console.log("done");
