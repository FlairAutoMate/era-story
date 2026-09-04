# ERA Scroll Story

Statisk landingsside bygget fra Claude Design-eksporten «ERA Scroll Story». Ingen byggesteg: `index.html` + `js/` (dc-runtime, image-slot) + `vendor/` (React UMD) + `assets/` + `fonts/`.

Lokalt: `python -m http.server 8787` og åpne http://localhost:8787/. Visuell QA: `node qa-scroll.mjs`.

Deploy: `npx vercel --prod`.

## Mottak av leads

Feltet i finalen sender `POST /api/lead` med `{ audience, value }`. Funksjonen (`api/lead.js`) lagrer ett JSON-dokument per lead i det private Vercel Blob-lageret `era-leads` under `leads/<målgruppe>/<dato>/`. Ingenting sendes videre.

- Målgruppe (`owner`, `board`, `pro`, `partner`) settes av hvilken historielenke besøkende fulgte sist.
- Honeypot-feltet `website` stopper enkle roboter. Verdier under tre tegn avvises.
- Hent ut leads: `npm run leads` (tabell) eller `npm run leads:csv`. Krever `BLOB_READ_WRITE_TOKEN` i `.env.local` (`npx vercel env pull .env.local`).
- Lageret administreres i Vercel-dashbordet under Storage, eller med `npx vercel blob`.

## Undersider per målgruppe

`/boligeier`, `/styret`, `/handverker`, `/faghandel` genereres av `python tools/build-pages.py` fra én innholdsstruktur (hook, verdiforslag, fire steg, gevinst, eksempel, spørsmål, skjema). Delt stil i `pages.css`, fonter i `fonts.css`, skjema i `pages.js` (samme `/api/lead`). Endre tekst i generatoren og kjør den på nytt.

## Oppdatere fra en ny designeksport

1. Pakk ut den frittstående eksporten (bilder til `assets/story/*-v2.*`, fonter til `fonts/`, malen til `base.html` med ressurskart i `<head>`).
2. `python tools/rebase-deltas.py base.html index.html` legger ERAs egne endringer oppå (meny og bunntekst til undersidene, målgruppetekster, finale med skjema, dyplenker, firmanavn).
3. `python tools/build-pages.py`, deretter `node qa-story.mjs` og `node qa-board.mjs`.

Siste base ligger i `tools/base-export-2026-09-04.html`.
