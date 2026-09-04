// Keyboard + form flow: tab order reaches nav, menu, form; Escape closes the menu; validation messages appear.
import { chromium } from "playwright";
const base = process.argv[2] ?? "http://localhost:8787";
const browser = await chromium.launch();
const out = {};
for (const route of ["/", "/styret"]) {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 }, hasTouch: true });
  await page.goto(base + route, { waitUntil: "networkidle" }); await page.waitForTimeout(800);
  if (route === "/") await page.evaluate(() => scrollTo({ top: innerHeight * 2.5, behavior: "instant" }));
  await page.waitForTimeout(400);
  const seq = [];
  for (let i = 0; i < 8; i++) { await page.keyboard.press("Tab"); seq.push(await page.evaluate(() => { const a = document.activeElement; return a.tagName + ":" + (a.textContent || a.getAttribute("aria-label") || "").trim().slice(0, 18) + ":" + getComputedStyle(a).outlineStyle; })); }
  await page.locator("[data-menu-toggle]").click(); await page.waitForTimeout(200);
  const opened = await page.evaluate(() => ({ expanded: document.querySelector("[data-menu-toggle]").getAttribute("aria-expanded"), bodyOverflow: getComputedStyle(document.body).overflow }));
  await page.keyboard.press("Escape"); await page.waitForTimeout(200);
  const closedEsc = await page.evaluate(() => document.querySelector("[data-menu-toggle]").getAttribute("aria-expanded"));
  await page.locator("[data-menu-toggle]").click(); await page.waitForTimeout(200);
  await page.mouse.click(200, 700); await page.waitForTimeout(200);
  const closedOutside = await page.evaluate(() => ({ expanded: document.querySelector("[data-menu-toggle]").getAttribute("aria-expanded"), bodyOverflow: getComputedStyle(document.body).overflow }));
  // form: empty submit → browser validation blocks; short value → our message
  await page.evaluate(() => { const f = document.getElementById("era-lead"); f.scrollIntoView({ block: "center" }); });
  await page.waitForTimeout(500);
  const input = page.locator("#era-lead input[name=value]");
  await input.fill("ab");
  await page.evaluate(() => { const f = document.getElementById("era-lead"); f.noValidate = true; f.requestSubmit(); });
  await page.waitForTimeout(400);
  const msg = await page.evaluate(() => (document.querySelector(".err:not([hidden])") || document.querySelector('[role="status"]') || {}).textContent || document.body.innerText.match(/Skriv inn litt mer[^\n]*/)?.[0] || "");
  await input.fill("Kirkeveien 44, Bergen");
  await page.evaluate(() => document.getElementById("era-lead").requestSubmit());
  await page.waitForTimeout(1200);
  const after = await page.evaluate(() => document.body.innerText.match(/(Noe gikk galt|Ingen kontakt|Takk\.)[^\n]*/)?.[0] || "");
  const inputFont = await input.evaluate((el) => getComputedStyle(el).fontSize);
  out[route] = { tabSeq: seq, opened, closedEsc, closedOutside, shortValueMsg: msg.trim().slice(0, 60), submitResult: after.slice(0, 60), inputFont };
  await page.close();
}
await browser.close();
console.log(JSON.stringify(out, null, 1));
