/**
 * Ende-til-ende-QA for styredashboardet. Krever at `vite preview` kjører (npm run preview) eller
 * pass inn base-URL: `node e2e/run.mjs http://localhost:5179/app`.
 *
 * Sjekker: rolletilgang, tenant-isolasjon, filtre/URL-state, tomme og feiltilstander, mobil 390,
 * laptop 1280, desktop 1440/1920, horisontal overflyt, skjulte primærhandlinger, assistentens
 * kilder/antakelser og soilrør/bad-flyten. Skjermbilder til ../qa/dashboard/.
 */
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:5179/app").replace(/\/$/, "");
const outDir = path.resolve(here, "../../qa/dashboard");
fs.mkdirSync(outDir, { recursive: true });

const exe = ["C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1234/chrome-win64/chrome.exe", "C:/Users/mcspa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe"].find((p) => fs.existsSync(p));
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
const results = [];
const fail = (name, msg) => results.push({ name, ok: false, msg });
const pass = (name, msg = "") => results.push({ name, ok: true, msg });

async function page(viewport, url, opts = {}) {
  const ctx = await browser.newContext({ viewport, locale: "nb-NO", ...(opts.mobile ? { isMobile: true, hasTouch: true } : {}) });
  const p = await ctx.newPage();
  const errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  p.on("console", (m) => m.type() === "error" && !/favicon|fonts.googleapis|ERR_/.test(m.text()) && errors.push(m.text()));
  await p.goto(base + url, { waitUntil: "networkidle" });
  await p.waitForTimeout(500);
  return { p, ctx, errors };
}

async function overflow(p) {
  return p.evaluate(() => document.documentElement.scrollWidth > Math.max(document.documentElement.clientWidth, innerWidth) + 1);
}

async function check(name, fn) {
  try {
    await fn();
  } catch (e) {
    fail(name, e.message.split("\n")[0]);
  }
}

/* ---------- 1. Styreleder ser alt ---------- */
await check("styreleder: oversikt", async () => {
  const { p, ctx, errors } = await page({ width: 1440, height: 900 }, "/?rolle=styreleder&tenant=perrongen");
  const cards = await p.locator('[data-testid="priority-cards"] .deck').count();
  if (cards < 1 || cards > 3) throw new Error(`priority cards: ${cards}`);
  const ctxText = await p.locator('[data-testid="active-context"]').innerText();
  if (!/Perrongen/.test(ctxText) || !/Styreleder/.test(ctxText)) throw new Error("aktiv kontekst mangler: " + ctxText);
  if (!(await p.locator('[data-testid="create-primary"]').isVisible())) throw new Error("primærhandling skjult");
  if (await overflow(p)) throw new Error("horisontal overflyt");
  const vscroll = await p.evaluate(() => { const m = document.querySelector("main"); return m ? m.scrollHeight - m.clientHeight : 0; });
  if (vscroll > 2) throw new Error(`oversikten scroller vertikalt: ${vscroll} px`);
  await p.locator('[role="tab"]', { hasText: "Kommende" }).click();
  await p.waitForTimeout(200);
  if (!p.url().includes("panel=kommende")) throw new Error("panelfane ikke i URL");
  await p.screenshot({ path: path.join(outDir, "desktop-1440-oversikt.png"), fullPage: true });
  if (errors.length) throw new Error("konsoll: " + errors[0]);
  pass("styreleder: oversikt", `${cards} prioriterte saker`);
  await ctx.close();
});

/* ---------- 1b. Cockpit fyller arbeidsflaten på brede skjermer ---------- */
await check("oversikt: fyller arbeidsflaten ved 1920 px", async () => {
  const { p, ctx } = await page({ width: 1920, height: 1080 }, "/?rolle=styreleder");
  const w = await p.evaluate(() => document.querySelector(".content").getBoundingClientRect().width);
  if (w < 1500) throw new Error(`content bare ${Math.round(w)}px bred ved 1920 px viewport (kappet for smalt)`);
  if (await overflow(p)) throw new Error("horisontal overflyt ved 1920 px");
  pass("oversikt: fyller arbeidsflaten ved 1920 px", `content ${Math.round(w)}px`);
  await ctx.close();
});

/* ---------- 2. Styremedlem mangler admin ---------- */
await check("styremedlem: ingen admin-handlinger", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/beboere?rolle=styremedlem");
  if (await p.locator('[data-testid="new-message"]').count()) throw new Error("styremedlem kan sende melding");
  const head = await p.locator('[data-testid="residents-table"] thead').innerText();
  if (/E-post|Telefon/.test(head)) throw new Error("styremedlem ser kontaktinfo");
  await p.goto(base + "/prosjekter/prj-fasade?fane=tilbud&rolle=styremedlem", { waitUntil: "networkidle" });
  await p.waitForTimeout(500);
  if (await p.locator('[data-testid="co-approve"]').count()) throw new Error("styremedlem kan godkjenne endringsordre");
  if (await p.locator('[data-testid="decide-approve"]').count()) throw new Error("styremedlem kan vedta");
  pass("styremedlem: ingen admin-handlinger");
  await ctx.close();
});

/* ---------- 3. Beboer får ikke styredata ---------- */
await check("beboer: ingen styredata", async () => {
  const { p, ctx } = await page({ width: 1280, height: 800 }, "/?rolle=beboer");
  await p.waitForURL(/min-bolig/);
  await p.waitForSelector('[data-testid="resident-shared"]', { timeout: 8000 });
  for (const u of ["/saker", "/okonomi", "/tilbud", "/beboere", "/vedlikehold"]) {
    await p.goto(base + u, { waitUntil: "networkidle" });
    await p.waitForTimeout(300);
    const denied = await p.locator(".state.denied").count();
    if (!denied) throw new Error(`beboer fikk tilgang til ${u}`);
  }
  const nav = await p.locator(".sidenav").innerText();
  if (/Økonomi|Tilbud|Beboere/.test(nav)) throw new Error("beboer ser styremeny");
  await p.screenshot({ path: path.join(outDir, "laptop-1280-beboer.png"), fullPage: true });
  pass("beboer: ingen styredata");
  await ctx.close();
});

/* ---------- 4. Leverandør ser bare tildelte ---------- */
await check("leverandør: bare tildelte prosjekter", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/?rolle=leverandor");
  await p.waitForURL(/leverandor/);
  const n = await p.locator('[data-testid="supplier-project"]').count();
  if (n !== 1) throw new Error(`leverandør ser ${n} prosjekter`);
  const text = await p.locator('[data-testid="supplier-project"]').innerText();
  if (!/soilrør/i.test(text) || /Fasaderehabilitering/.test(text)) throw new Error("feil prosjekt for leverandør");
  await p.goto(base + "/prosjekter/prj-fasade", { waitUntil: "networkidle" });
  await p.waitForTimeout(300);
  if (!(await p.locator(".state.denied").count())) throw new Error("leverandør åpnet fasadeprosjektet");
  pass("leverandør: bare tildelte prosjekter");
  await ctx.close();
});

/* ---------- 5. Tenant-isolasjon ---------- */
await check("tenant-isolasjon", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/saker?rolle=era_admin&tenant=solvang");
  const t = await p.locator('[data-testid="issue-table"]').innerText().catch(() => p.locator("main").innerText());
  if (/AV-31|soilrør/i.test(t)) throw new Error("Perrongen-data lekker til Solvang");
  if (!/Solvang/.test(t)) throw new Error("Solvang-data mangler");
  await p.goto(base + "/saker?tenant=perrongen", { waitUntil: "networkidle" });
  await p.waitForTimeout(400);
  const t2 = await p.locator("main").innerText();
  if (/Solvang/.test(t2)) throw new Error("Solvang-data lekker til Perrongen");
  pass("tenant-isolasjon");
  await ctx.close();
});

/* ---------- 6. Filtre og URL-state ---------- */
await check("filtre og URL-state", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/vedlikehold?rolle=styreleder");
  await p.selectOption('[data-testid="filter-status"]', "krever_beslutning");
  await p.waitForTimeout(300);
  if (!p.url().includes("status=krever_beslutning")) throw new Error("URL oppdateres ikke");
  const rows = await p.locator('[data-testid="maintenance-table"] tbody tr').count();
  if (rows !== 3) throw new Error(`forventet 3 tiltak, fikk ${rows}`);
  await p.reload({ waitUntil: "networkidle" });
  await p.waitForTimeout(400);
  if ((await p.locator('[data-testid="maintenance-table"] tbody tr').count()) !== 3) throw new Error("filter overlever ikke reload");
  await p.locator('[data-testid="maintenance-table"] tbody tr').first().focus();
  await p.keyboard.press("Enter");
  await p.waitForSelector('[role="dialog"]');
  if (!p.url().includes("tiltak=")) throw new Error("åpent objekt ikke i URL");
  await p.keyboard.press("Escape");
  await p.waitForTimeout(300);
  if (await p.locator('[role="dialog"]').count()) throw new Error("Escape lukker ikke drawer");
  await p.goto(base + "/saker?alvor=kritisk", { waitUntil: "networkidle" });
  await p.waitForTimeout(300);
  if ((await p.locator('[data-testid="issue-table"] tbody tr').count()) !== 1) throw new Error("saksfilter fra URL feiler");
  await p.goto(base + "/saker?bygg=b-c", { waitUntil: "networkidle" });
  await p.waitForTimeout(300);
  if (!/Flere filtre \(1\)/.test(await p.locator('[data-testid="more-filters"]').innerText())) throw new Error("skjult filter telles ikke");
  await p.locator('[data-testid="more-filters"]').click();
  await p.waitForSelector('[role="dialog"]');
  await p.keyboard.press("Escape");
  await p.screenshot({ path: path.join(outDir, "desktop-1440-saker.png"), fullPage: true });
  pass("filtre og URL-state");
  await ctx.close();
});

/* ---------- 7. Tomme og feiltilstander ---------- */
await check("tom tilstand", async () => {
  const { p, ctx } = await page({ width: 1280, height: 800 }, "/?rolle=styreleder&tilstand=tom");
  const states = await p.locator(".state").count();
  if (states < 2) throw new Error("tomme tilstander vises ikke");
  const txt = await p.locator(".state").first().innerText();
  if (txt.length < 40) throw new Error("tom tilstand forklarer ikke");
  await p.screenshot({ path: path.join(outDir, "laptop-1280-tom.png"), fullPage: true });
  pass("tom tilstand");
  await ctx.close();
});
await check("feiltilstand låser ikke siden", async () => {
  const { p, ctx } = await page({ width: 1280, height: 800 }, "/?rolle=styreleder&tilstand=feil");
  if (!(await p.locator(".state.error").count())) throw new Error("feiltilstand vises ikke");
  if (!(await p.locator(".sidenav").isVisible())) throw new Error("AppShell borte");
  if (!(await p.locator(".topbar").isVisible())) throw new Error("topplinje borte");
  await p.screenshot({ path: path.join(outDir, "laptop-1280-feil.png"), fullPage: true });
  pass("feiltilstand låser ikke siden");
  await ctx.close();
});

/* ---------- 8. Responsivt uten overflyt ---------- */
const routes = ["/", "/vedlikehold", "/saker", "/prosjekter", "/prosjekter/prj-soil?fane=boliger", "/prosjekter/prj-fasade?fane=tilbud", "/tilbud/qr-tak", "/beboere", "/dokumenter", "/okonomi"];
for (const [w, h, label, mobile] of [[390, 844, "mobil-390", true], [1280, 800, "laptop-1280", false], [1440, 900, "desktop-1440", false], [1920, 1080, "desktop-1920", false]]) {
  await check(`viewport ${label}`, async () => {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, locale: "nb-NO", ...(mobile ? { isMobile: true, hasTouch: true } : {}) });
    const p = await ctx.newPage();
    const errs = [];
    p.on("pageerror", (e) => errs.push(e.message));
    const bad = [];
    for (const r of routes) {
      await p.goto(base + r + (r.includes("?") ? "&" : "?") + "rolle=styreleder", { waitUntil: "networkidle" });
      await p.waitForTimeout(400);
      if (await overflow(p)) bad.push(r);
      const small = await p.evaluate(() => Array.from(document.querySelectorAll("button, a")).filter((el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && (r.height < 24 || r.width < 24); }).map((el) => el.textContent?.trim().slice(0, 30) || el.getAttribute("aria-label")));
      if (mobile && small.length > 12) bad.push(`${r} små trykkflater: ${small.slice(0, 3).join(", ")}`);
      if (r === "/" || r === "/prosjekter/prj-soil?fane=boliger" || r === "/tilbud/qr-tak") await p.screenshot({ path: path.join(outDir, `${label}${r.replace(/[^a-z0-9]+/gi, "-")}.png`), fullPage: true });
    }
    if (mobile) {
      await p.goto(base + "/?rolle=styreleder", { waitUntil: "networkidle" });
      if (!(await p.locator(".bottomnav").isVisible())) throw new Error("bunnfaner mangler på mobil");
      if (!(await p.locator('[data-testid="priority-stack"]').isVisible())) throw new Error("kortstokk mangler på mobil");
      await p.locator(".bottomnav .fab").click();
      await p.waitForTimeout(300);
      if (!(await p.locator('[data-testid="era-assistant"]').isVisible())) throw new Error("assistent åpner ikke på mobil");
      await p.screenshot({ path: path.join(outDir, `${label}-assistent.png`) });
    }
    if (bad.length) throw new Error("overflyt/berøring: " + bad.join(" | "));
    if (errs.length) throw new Error("pageerror: " + errs[0]);
    pass(`viewport ${label}`, `${routes.length} ruter uten overflyt`);
    await ctx.close();
  });
}

/* ---------- 9. Assistent med kilder og antakelser ---------- */
await check("assistent viser kilder og antakelser", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/tilbud/qr-tak?rolle=styreleder");
  await p.locator('[data-testid="ask-era"]').click();
  await p.locator(".suggest button", { hasText: "Sammenlign" }).first().click();
  await p.waitForSelector('[data-testid="era-answer"]', { timeout: 8000 });
  const ctxText = await p.locator(".assist-ctx").innerText();
  if (!/Styreleder/.test(ctxText) || !/Takomlegging/.test(ctxText)) throw new Error("assistent mangler kontekst: " + ctxText);
  if (!(await p.locator('[data-testid="era-sources"] li').count())) throw new Error("ingen kilder");
  if (!(await p.locator('[data-testid="era-assumptions"] li').count())) throw new Error("ingen antakelser");
  await p.screenshot({ path: path.join(outDir, "desktop-1440-assistent.png"), fullPage: true });
  pass("assistent viser kilder og antakelser");
  await ctx.close();
});

/* ---------- 10. Soilrør/bad ende til ende ---------- */
await check("soilrør/bad-flyt ende til ende", async () => {
  const { p, ctx } = await page({ width: 1280, height: 900 }, "/min-bolig?rolle=beboer");
  await p.waitForSelector('[data-testid="resident-total"]', { timeout: 8000 });
  const before = await p.locator('[data-testid="resident-total"]').innerText();
  await p.locator(".steps li").nth(1).click();
  await p.locator('[data-testid="pkg-komplett"]').click();
  await p.locator('[data-testid="choose-tier"]').click();
  await p.waitForTimeout(700);
  const after = await p.locator('[data-testid="resident-total"]').innerText();
  if (before === after) throw new Error("kostnad endret seg ikke ved pakkevalg");
  await p.locator(".steps li").nth(2).click();
  await p.locator('[data-testid="accept-quote"]').click();
  await p.locator('[role="alertdialog"] button', { hasText: "Aksepter" }).click();
  await p.waitForTimeout(700);
  const quoteCard = await p.locator('[data-testid="resident-quote"]').innerText();
  if (!/Akseptert/.test(quoteCard)) throw new Error("aksept ikke registrert");
  // Styret ser status, ikke tilbudet.
  await p.goto(base + "/prosjekter/prj-soil?fane=boliger&rolle=styreleder", { waitUntil: "networkidle" });
  await p.waitForSelector('[data-testid="unit-summary"]', { timeout: 8000 });
  const summary = await p.locator('[data-testid="unit-summary"]').innerText();
  if (!/har svart/i.test(summary)) throw new Error("styret mangler svaroversikt");
  await p.locator('[data-testid="toggle-list"]').click();
  await p.waitForTimeout(200);
  const table = await p.locator('[data-testid="units-table"]').innerText();
  if (/Servantskap|Downlights|terrazzo/.test(table)) throw new Error("privat tilbud lekker til styret");
  if (!/Komplett baderom/.test(table)) throw new Error("styret ser ikke valgt pakke");
  await p.locator('[role="tab"]', { hasText: "Oversikt" }).click();
  await p.waitForTimeout(300);
  const split = await p.locator('[data-testid="cost-split"]').innerText();
  if (!/Felles kostnad/i.test(split) || !/Private tilvalg/i.test(split)) throw new Error("kostnadsdeling mangler");
  await p.screenshot({ path: path.join(outDir, "laptop-1280-soil-styret.png"), fullPage: true });
  // Leverandøren ser tilvalg og tilgang.
  await p.goto(base + "/leverandor?rolle=leverandor", { waitUntil: "networkidle" });
  await p.waitForTimeout(500);
  const sup = await p.locator('[data-testid="supplier-units"]').innerText();
  if (!/Komplett baderom/.test(sup)) throw new Error("leverandør ser ikke pakkevalg");
  pass("soilrør/bad-flyt ende til ende");
  await ctx.close();
});

/* ---------- 11. Beslutning og tilbudsforespørsel ---------- */
await check("vedtak og tilbudsforespørsel", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/prosjekter/prj-fasade?fane=tilbud&rolle=styreleder");
  await p.locator('[data-testid="co-approve"]').click();
  await p.locator('[role="alertdialog"] button', { hasText: "Godkjenn" }).click();
  await p.waitForTimeout(700);
  if (await p.locator('[data-testid="co-approve"]').count()) throw new Error("endringsordre fortsatt åpen");
  await p.goto(base + "/tilbud/ny?prosjekt=prj-soil", { waitUntil: "networkidle" });
  await p.locator('[data-testid="qr-next-1"]').click();
  await p.locator('[data-testid="qr-next-2"]').click();
  await p.locator(".check input").first().check();
  await p.locator('[data-testid="qr-next-3"]').click();
  await p.locator('[data-testid="qr-send"]').click();
  await p.waitForURL(/\/tilbud\/qr-/);
  await p.waitForSelector(".state, [data-testid=\"quote-comparison\"]", { timeout: 8000 });
  if (!/Sendt|Ingen tilbud mottatt/.test(await p.locator("main").innerText())) throw new Error("forespørsel ikke opprettet");
  // Melding til beboere
  await p.goto(base + "/beboere?ny=1&prosjekt=prj-soil&segment=berorte", { waitUntil: "networkidle" });
  await p.locator('[data-testid="suggest-text"]').click();
  await p.waitForTimeout(200);
  await p.locator('[data-testid="send-message"]').click();
  await p.waitForTimeout(700);
  if (!/Melding sendt/.test(await p.locator(".toasts").innerText().catch(() => ""))) throw new Error("melding ikke sendt");
  pass("vedtak og tilbudsforespørsel");
  await ctx.close();
});

/* ---------- 11b. Prosjekter: kort/liste-veksling ---------- */
await check("prosjekter: vis liste veksler til kompakt tabell", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/prosjekter?rolle=styreleder");
  await p.waitForSelector('[data-testid="toggle-list"]', { timeout: 8000 });
  const label = await p.locator('[data-testid="toggle-list"]').innerText();
  if (!/^Vis liste \(\d+\)$/.test(label)) throw new Error(`uventet knappetekst: ${label}`);
  await p.locator('[data-testid="toggle-list"]').click();
  await p.waitForSelector('[data-testid="projects-table"]', { timeout: 4000 });
  if (!p.url().includes("liste=1")) throw new Error("listevisning ikke i URL");
  await p.reload({ waitUntil: "networkidle" });
  await p.waitForSelector('[data-testid="projects-table"]', { timeout: 8000 });
  if (!/^Vis kort$/.test(await p.locator('[data-testid="toggle-list"]').innerText())) throw new Error("knapp viser ikke 'Vis kort' i listevisning");
  await p.locator('[data-testid="toggle-list"]').click();
  await p.waitForTimeout(200);
  if (await p.locator('[data-testid="projects-table"]').count()) throw new Error("tabellen forsvinner ikke ved tilbake til kort");
  pass("prosjekter: vis liste veksler til kompakt tabell");
  await ctx.close();
});

/* ---------- 12. Ingen døde knapper ---------- */
await check("alle knapper har handling eller er deaktivert", async () => {
  const { p, ctx } = await page({ width: 1440, height: 900 }, "/okonomi?rolle=styreleder");
  const dead = await p.evaluate(() => Array.from(document.querySelectorAll("button")).filter((b) => !b.disabled && !b.onclick && !b.closest("form") && b.type !== "submit" && !b.getAttribute("aria-pressed") && !b.getAttribute("role")).length);
  // React binder handlere via delegasjon, så `onclick` er alltid null; sjekk i stedet at «Kommer senere» ikke er knapper.
  const coming = await p.locator(".coming").count();
  const comingButtons = await p.locator("button.coming").count();
  if (coming < 3 || comingButtons > 0) throw new Error("«Kommer senere» er ikke tydelig deaktivert");
  await p.screenshot({ path: path.join(outDir, "desktop-1440-okonomi.png"), fullPage: true });
  pass("alle knapper har handling eller er deaktivert", `${dead} knapper sjekket`);
  await ctx.close();
});

/* ---------- 13. Mørkt tema: system, eksplisitt valg, overlever reload ---------- */
await check("tema: system, eksplisitt valg og persistens", async () => {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, locale: "nb-NO", colorScheme: "dark" });
  const p = await ctx.newPage();
  await p.goto(base + "/?rolle=styreleder", { waitUntil: "networkidle" });
  await p.waitForTimeout(400);
  const sysBg = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (sysBg === "rgb(243, 240, 233)") throw new Error("følger ikke system (dark) som standard");
  const topbarBg = await p.evaluate(() => getComputedStyle(document.querySelector(".topbar")).backgroundColor);
  if (/243, 240, 233/.test(topbarBg)) throw new Error("topplinjen henger igjen i lys bakgrunn i mørkt tema");
  await p.locator('[data-testid="theme-light"]').click();
  await p.waitForTimeout(200);
  const lightBg = await p.evaluate(() => getComputedStyle(document.body).backgroundColor);
  if (lightBg !== "rgb(243, 240, 233)") throw new Error("eksplisitt lys overstyrer ikke mørk systeminnstilling");
  await p.reload({ waitUntil: "networkidle" });
  await p.waitForTimeout(300);
  const afterReload = await p.evaluate(() => ({ attr: document.documentElement.getAttribute("data-theme"), stored: localStorage.getItem("era-theme") }));
  if (afterReload.attr !== "light" || afterReload.stored !== "light") throw new Error("temavalg overlever ikke reload");
  await p.locator('[data-testid="theme-system"]').click();
  await p.waitForTimeout(200);
  if (await p.evaluate(() => document.documentElement.hasAttribute("data-theme"))) throw new Error("system fjerner ikke data-theme");
  pass("tema: system, eksplisitt valg og persistens");
  await ctx.close();
});

await browser.close();
const okAll = results.every((r) => r.ok);
for (const r of results) console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}${r.msg ? " · " + r.msg : ""}`);
console.log(`\n${results.filter((r) => r.ok).length}/${results.length} passerte. Skjermbilder i ${outDir}`);
process.exit(okAll ? 0 : 1);
