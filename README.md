# ERA Scroll Story

Statisk landingsside bygget fra Claude Design-eksporten «ERA Scroll Story». Ingen byggesteg: `index.html` + `js/` (dc-runtime, image-slot) + `vendor/` (React UMD) + `assets/` + `fonts/`.

Lokalt: `python -m http.server 8787` og åpne http://localhost:8787/. Visuell QA: `node qa-scroll.mjs`.

Deploy: `npx vercel --prod`.

## Historiens dramaturgi (3 · 5 · 7)

- **Tre faser** bærer historien og skinnen: Forstå boligen (02–04) → Gjennomfør tiltak (05–09) → Dokumenter verdien (10, 05b). Fasen står som eyebrow i scenene, og 02 sier tidlig at ERA er en AI-drevet boligplattform.
- **Fem hendelser** i én kjede rundt paret og stua: behovet (01) → plan og estimat (05) → produkter og valg (06–07) → bestilling og gjennomføring (08) → ferdig og dokumentert (09–10). «Hele boligen» ligger etter «Hukommelse» som overgang til styret.
- **Detaljer på forespørsel**: «Se planen» (05), «Se produktvalg» (07) og «Se dokumentasjonen» (10) er knapper (`data-detail`) som åpner et panel inline på desktop og som bunnark på mobil. Innholdet ligger i HTML også når det er lukket. Funksjoner som ikke er dokumentert tilgjengelige er merket «Planlagt» (energi og forbedringer) eller «I pilot» (betaling i ERA).

## Om ERA — egen side

`/om-era` er Om ERA-filmen som egen side (13 scener: bro fra ett bygg til alle boliger, den fragmenterte boligen, den agentiske sløyfen, «fra et bilde», gjør det selv / få hjelp i én scene, lukk sløyfen, hvor kundereisen starter, teknologi, agent, aktørene, visjon, menneskene, finale med kapittelets sluttfraser). Forsiden lenker dit fra split-scenen («Hvorfor ERA finnes →»), finalen, skinnen, mobilmenyen og bunnteksten.

- Scenene ligger i `tools/om-era-template.html`. `python tools/build-om-era.py` setter dem sammen med forsidens hode, meny, skinne, finale, bunntekst og skript til `om-era/index.html`. Rediger malen, ikke den bygde filen.
- Én scroll-motor for begge sider: skriptet i `index.html` sjekker `body[data-page="om-era"]` for skinne-kapitler, kapittelkart, finale-timing og finalehøyde. Endringer i skriptet må følges av `build-om-era.py`.
- Etter en ny designeksport: `rebase-deltas.py` → `build-om-era.py` → `build-pages.py`. Merk at komprimeringen 2026-09-05 (05c fjernet, 20+21 slått sammen, nye scenehøyder) ikke ligger i `rebase-deltas.py` ennå.

Alle bilder er utskiftbare `<image-slot id="…" src="…">` uten innbakt tekst/UI. Portrettene (`team-*`) er plassholdere til foto foreligger; sett `src` i `teamDefs` i skriptet.

Visuell QA: `node qa-om.mjs http://localhost:8787/om-era` (skjermbilder til `qa/om-era/`).
## Responsivitet og nettleser-QA

Siden er bygget mobile-first fra 320 px og opp. Faste regler som ligger i `index.html` (`<style>` i `<helmet>`) og `pages.css`:

- Sticky-scener bruker `100dvh` med `100vh` som fallback (`.era-vh`), så de fyller det synlige vinduet på iOS. `#start`-ankeret følger samme høyde.
- `viewport-fit=cover`; meny og fast CTA respekterer `safe-area-inset-*`.
- Historien bytter til mobilkomposisjon under 900 px (samme bruddpunkt som undersidenes hamburger). Under 520 px høyde (liggende mobil) slår `html.era-short` inn: sidebilder og flytende kort skjules, typografien strammes.
- Alle lenker og knapper har minst 44 px trykkflate (`.era-link`, bunntekst, skinne, pill). Inputtekst er 16 px.
- Mobilmenyen låser bakgrunnsscroll, lukkes med Escape og ved trykk utenfor.
- Flytende brikker (kaos, fragmentert bolig, lukk sløyfen) klemmes inn i viewporten.

QA-skript (krever `node_modules` med Playwright og motorene `npx playwright install chromium firefox webkit`):

- `node qa-responsive.mjs http://localhost:8787 chromium,firefox,webkit all` — alle ruter × 14 viewporter × motor. Rapporterer horisontal overflyt, elementer utenfor viewporten, avkuttet/overlappende tekst, trykkflater under 44 px, inputtekst under 16 px og konsollfeil. Rapport i `qa/responsive/`.
- `node qa-tablet.mjs` — ett skjermbilde per scene på iPad portrett/landskap, liggende mobil og 768 px.
- `node qa-a11y.mjs` — tab-rekkefølge, fokusmarkering, menylås/Escape/klikk utenfor, skjemavalidering.
- `node qa-om.mjs` — Om ERA-kapittelet scene for scene.

Ikke testet automatisk (krever ekte enheter): Safari på iPhone/iPad med dynamisk adressefelt, Samsung Internet, autofyll. WebKit-motoren i Playwright dekker Safari-rendering.

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
