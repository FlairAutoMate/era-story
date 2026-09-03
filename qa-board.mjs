// QA for the board (styret) reading path: chapter 11, the journey, both finale variants, the priority cloud.
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
await at("styret", 0.85); await p.screenshot({ path: "qa/board-11.png" });
await at("reisen", 0.9); await p.screenshot({ path: "qa/board-13.png" });
await at("start", 0.9); await p.screenshot({ path: "qa/board-finale-owner.png" });
await at("styret", 0.85); await p.click("a[data-board]"); await p.waitForTimeout(1500);
await at("start", 0.9); await p.screenshot({ path: "qa/board-finale-board.png" });
await at("prioriter", 0.2); await p.screenshot({ path: "qa/board-04.png" });
console.log("errors", errs);
await browser.close();
