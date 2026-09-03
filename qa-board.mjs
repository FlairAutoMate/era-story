// QA for the audience reading paths: chapter 11 (styret), chapter 8 (håndverker), chapter 7 (partner),
// the journey, and the four finale variants (owner, board, pro, partner).
import { chromium } from "file:///C:/Users/mcspa/Documents/ERA/node_modules/playwright/index.mjs";
const url = process.argv[2] ?? "http://localhost:8787/";
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
const p = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errs = [];
p.on("pageerror", (e) => errs.push(e.message));
await p.goto(url, { waitUntil: "networkidle" });
await p.waitForTimeout(1500);
const at = async (id, f) => {
  const [y, h] = await p.evaluate((i) => { const s = document.getElementById(i); return [s.getBoundingClientRect().top + scrollY, s.offsetHeight]; }, id);
  await p.evaluate((v) => scrollTo({ top: v, behavior: "instant" }), y + (h - 900) * f);
  await p.waitForTimeout(800);
};
const finaleText = async () => p.evaluate(() => { const s = document.getElementById("start"); return [...s.querySelectorAll("h2, span, a")].map((e) => e.textContent.trim()).filter((t) => t && t.length < 90).slice(0, 6); });
const out = {};
await at("handverker", 0.85); await p.screenshot({ path: "qa/pro-08.png" });
await at("reisen", 0.9); await p.screenshot({ path: "qa/pro-13.png" });
await at("start", 0.9); out.owner = await finaleText();
await at("handverker", 0.85); await p.click("a[data-pro]"); await p.waitForTimeout(1200); await at("start", 0.9); out.pro = await finaleText(); await p.screenshot({ path: "qa/finale-pro.png" });
await p.click('nav a[href="#partnere"]'); await p.waitForTimeout(1200); await at("start", 0.9); out.partner = await finaleText(); await p.screenshot({ path: "qa/finale-partner.png" });
await p.click('nav a[href="#styret"]'); await p.waitForTimeout(1200); await at("start", 0.9); out.board = await finaleText();
await p.click('nav a[href="#boligeier"]'); await p.waitForTimeout(1200); await at("start", 0.9); out.ownerAgain = await finaleText();
console.log(JSON.stringify({ errs, out }, null, 1));
await browser.close();
