// Om ERA-kapittelet: skjermbilder per scene ved flere scroll-posisjoner. Bruk: node qa-om.mjs [url] [utmappe] [seksjonsnr,…] [brøker,…] [d|m]
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
const url = process.argv[2] ?? "http://localhost:8791/";
const out = process.argv[3] ?? "qa/om-era";
const only = process.argv[4] ? process.argv[4].split(",") : null;
const fracs = (process.argv[5] ?? "0.03,0.25,0.5,0.75,0.97").split(",").map(Number);
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
for (const [name, vp] of [["d", { width: 1440, height: 900 }], ["m", { width: 390, height: 844 }]]) {
  if (process.argv[6] && process.argv[6] !== name) continue;
  const page = await browser.newPage({ viewport: vp, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: "networkidle" }); await page.waitForTimeout(1200);
  const secs = await page.evaluate(() => [...document.querySelectorAll("section")].map((s) => [s.getAttribute("data-screen-label"), s.getBoundingClientRect().top + scrollY, s.offsetHeight]));
  for (const [label, y, h] of secs) {
    const num = label.slice(0, 2);
    if (only && !only.includes(num)) continue;
    for (const f of h > vp.height * 1.5 ? fracs : [0.5]) {
      await page.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), Math.round(y + Math.max(0, h - vp.height) * f));
      await page.waitForTimeout(450);
      await page.screenshot({ path: `${out}/${name}-${num}-${f}.png` });
    }
  }
  await page.close();
}
await browser.close();
console.log("done");
