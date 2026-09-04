// Renders tools/og-source.html to og.jpg (1200x630) for social sharing previews.
// Run: node tools/render-og.mjs (needs the local static server running so /fonts.css and
// /assets/story/... resolve; point --base at a different origin if needed).
import { chromium } from "playwright";
const base = process.argv[2] ?? "http://localhost:8855";
const browser = await chromium.launch({ executablePath: "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe" });
const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
await page.goto(`${base}/tools/og-source.html`, { waitUntil: "load" });
await page.waitForTimeout(300);
await page.screenshot({ path: "og.jpg", type: "jpeg", quality: 92 });
await page.close();
await browser.close();
console.log("written og.jpg");
