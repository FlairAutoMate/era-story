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
