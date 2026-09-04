# ERA Scroll Story

Statisk landingsside bygget fra Claude Design-eksporten «ERA Scroll Story». Ingen byggesteg: `index.html` + `js/` (dc-runtime, image-slot) + `vendor/` (React UMD) + `assets/` + `fonts/`.

Lokalt: `python -m http.server 8787` og åpne http://localhost:8787/. Visuell QA: `node qa-scroll.mjs`.

Deploy: `npx vercel --prod`.

## Om ERA-kapittelet

Etter «Din bolig. Vårt bygg.» og personvern-blokken følger siste akt, `#om-era` (seksjonene 15–28 i `index.html`): bro fra ett bygg til alle boliger, den fragmenterte boligen, den agentiske sløyfen, «fra et bilde» (se → forstå → vurdere), veivalget, gjør det selv / få hjelp, lukk sløyfen, hvor kundereisen starter, teknologi (fem evner), fra assistent til agent, aktørene, visjon og menneskene bak ERA. Finalen (`29`) åpner med kapittelets sluttfraser før logo og skjema; ankeret `#start` ligger nå der skjemaet er synlig.

Alle bilder er utskiftbare `<image-slot id="…" src="…">` uten innbakt tekst/UI: `about-hero`, `about-bridge`, `fragmented-home`, `loop-home`, `photo-observation`, `diy-commerce`, `tradesperson`, `completed-work`, `property-intelligence`, `agentic-future-0..3`, `ecosystem`, samt `finale-neighbourhood` (`data-story-image`). Inntil endelig foto foreligger peker de på eksisterende bilder i `assets/story/`. Portrettene (`team-lars`, `team-ragnvald`, `team-thomas`, `team-magnus`, `team-eskild`, `team-william`) er nøytrale plassholdere; sett `src` i `teamDefs` i skriptet når bildene er klare (samme utsnitt, 4:5).

Visuell QA av kapittelet: `node qa-om.mjs http://localhost:8787/` (skjermbilder til `qa/om-era/`).

## Mottak av leads

Feltet i finalen sender `POST /api/lead` med `{ audience, value }`. Funksjonen (`api/lead.js`) lagrer ett JSON-dokument per lead i det private Vercel Blob-lageret `era-leads` under `leads/<målgruppe>/<dato>/`. Ingenting sendes videre.

- Målgruppe (`owner`, `board`, `pro`, `partner`) settes av hvilken historielenke besøkende fulgte sist.
- Honeypot-feltet `website` stopper enkle roboter. Verdier under tre tegn avvises.
- Hent ut leads: `npm run leads` (tabell) eller `npm run leads:csv`. Krever `BLOB_READ_WRITE_TOKEN` i `.env.local` (`npx vercel env pull .env.local`).
- Lageret administreres i Vercel-dashbordet under Storage, eller med `npx vercel blob`.

## Undersider per målgruppe

`/boligeier`, `/styret`, `/handverker`, `/faghandel` genereres av `python tools/build-pages.py` fra én innholdsstruktur (hook, verdiforslag, fire steg, gevinst, eksempel, spørsmål, skjema). Delt stil i `pages.css`, fonter i `fonts.css`, skjema i `pages.js` (samme `/api/lead`). Endre tekst i generatoren og kjør den på nytt.

## Nye bilder som venter på foto

Kapitlene «Hele boligen» (05b), «Flere behov» (05c) og «Få hjelp» (08) bruker tre motiver som ennå ikke er fotografert: hele boligen, rørlegger og elektriker. De hentes fra `window.__resources` i `<head>` (nøklene `wholeHome`, `plumber`, `electrician`). Så lenge nøkkelen er tom vises en ERA-stilt placeholder med etiketten `BILDE · …`; legg inn stien til fotoet, så forsvinner etiketten av seg selv. Markørposisjonene i 05b ligger i `wholeSpotDefs` i skriptet og justeres når fotoet foreligger.

## Oppdatere fra en ny designeksport

1. Pakk ut den frittstående eksporten (bilder til `assets/story/*-v2.*`, fonter til `fonts/`, malen til `base.html` med ressurskart i `<head>`).
2. `python tools/rebase-deltas.py base.html index.html` legger ERAs egne endringer oppå (meny og bunntekst til undersidene, målgruppetekster, finale med skjema, dyplenker, firmanavn).
3. `python tools/build-pages.py`, deretter `node qa-story.mjs` og `node qa-board.mjs`.

Siste base ligger i `tools/base-export-2026-09-04.html`.

## Varsling, analyse og personvern

- **E-postvarsel per lead:** sett `RESEND_API_KEY` og `LEAD_NOTIFY_TO` (kommaseparert) med `npx vercel env add`. Uten disse lagres leads stille. `LEAD_NOTIFY_FROM` kan settes når et domene er verifisert hos Resend.
- **Lagring:** privat Vercel Blob-lager `era-leads-eu` i Frankfurt (EU/EØS).
- **Analyse:** `/_vercel/insights/script.js` er lagt inn på alle sider. Slå på Web Analytics én gang i Vercel-dashbordet (prosjekt → Analytics), ellers gjør skriptet ingenting.
- **Personvern:** `/personvern` genereres av `tools/build-pages.py` og beskriver nøyaktig det siden gjør. Oppdater den hvis skjemaet eller lagringen endres.
- **Delingsbilde:** `og.jpg` rendres fra `tools/og-source.html` (1200 × 630) med Playwright.
