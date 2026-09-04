// Visual QA: load the page in headless Chromium, capture console errors and screenshots at
// a set of scroll positions. `node qa-scroll.mjs [url]` → qa/*.png
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const url = process.argv[2] ?? "http://localhost:8787/";
mkdirSync("qa", { recursive: true });
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [];
page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") errors.push(`${m.type()}: ${m.text().slice(0, 200)}`); });
page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
page.on("requestfailed", (r) => errors.push("requestfailed: " + r.url()));
await page.goto(url, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
const total = await page.evaluate(() => document.documentElement.scrollHeight);
const stops = [0, 0.03, 0.06, 0.1, 0.14, 0.2, 0.26, 0.32, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.97];
for (const s of stops) {
  await page.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), Math.round((total - 900) * s));
  await page.waitForTimeout(500);
  await page.screenshot({ path: `qa/scroll-${String(Math.round(s * 100)).padStart(2, "0")}.png` });
}
const rootInfo = await page.evaluate(() => ({ root: !!document.getElementById("dc-root"), xdc: !!document.querySelector("x-dc"), h: document.documentElement.scrollHeight, slots: [...document.querySelectorAll("image-slot")].map((s) => [s.id, s.getAttribute("src") ? "src" : "placeholder"]) }));
console.log(JSON.stringify({ total, rootInfo, errors: [...new Set(errors)] }, null, 1));
await browser.close();
