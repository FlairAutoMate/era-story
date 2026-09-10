# ERA Scroll Story

Statisk landingsside bygget fra Claude Design-eksporten «ERA Scroll Story». Ingen byggesteg: `index.html` + `js/` (dc-runtime, image-slot) + `vendor/` (React UMD) + `assets/` + `fonts/`.

Lokalt: `python -m http.server 8787` og åpne http://localhost:8787/. Visuell QA: `node qa-scroll.mjs`.

Deploy: `npx vercel --prod`.

## Historiens dramaturgi (3 · 5 · 7)

- **Tre faser** bærer historien og skinnen: Forstå boligen (02–04) → Gjennomfør tiltak (05–09) → Dokumenter verdien (10, 05b). Fasen står som eyebrow i scenene, og 02 sier tidlig at ERA er en AI-drevet boligplattform.
- **Fem hendelser** i én kjede rundt paret og stua: behovet (01) → plan og estimat (05) → produkter og valg (06–07) → bestilling og gjennomføring (08) → ferdig og dokumentert (09–10). «Hele boligen» ligger etter «Hukommelse» som overgang til styret.
- **Detaljer på forespørsel**: «Se planen» (05), «Se produktvalg» (07) og «Se dokumentasjonen» (10) er knapper (`data-detail`) som åpner et panel inline på desktop og som bunnark på mobil. Innholdet ligger i HTML også når det er lukket. Funksjoner som ikke er dokumentert tilgjengelige er merket «Planlagt» (energi og forbedringer) eller «I pilot» (betaling i ERA).
- **Kamera-beatet i 05**: mellom «Vi vil male stua.» og «ERA forstår rommet.» ligger «Du tar ett bilde.» Gullrammen som allerede tennes på veggen leser da som kameraets ramme, og «Vegg · 42 m²» som ERAs måling fra bildet. Det gjør kamera → agent → prosjekt → hukommelse synlig i hovedhistorien.

### Scenehøyder og mobil — les dette før du endrer `heights`

Hver sticky-scene er `height: {{ h_* }}` med en `.era-vh`-child på `100dvh`, og `H(d, f)` gir mobil en kortere variant. **Blir en seksjon kortere enn viewporten, blir `prog`-verdien permanent 0** — scenen animerer aldri, og alt som henger på den slutter å virke.

Det var tilfellet for døren: `H(180, 0.55)` ga 99vh mot et 100dvh-barn, altså −8px scroll-distanse på 390×844. Døren åpnet seg aldri på mobil, hele navigasjonen lå på `opacity: 0` (men var fortsatt trykkbar), fremdriftslinjen vistes aldri, og `era_story_started` / `find_home_cta_viewed` fyrte aldri. Faktoren er nå 0.95. **Hold enhver mobilfaktor over ~1.1× viewporthøyden.**

`navShown` har derfor en sikring: navigasjonen vises også når `scrollY > 0.6 × vh`, slik at en tilsvarende regnefeil ikke kan skjule CTA-en igjen.

- **Historieprogresjon** regnes som snittet av scenenes egen `prog`, ikke dokument-scroll — én sticky-scene kan eie fem viewporter, så scroll-prosent er misvisende. Den styrer både fremdriftslinjen på mobil og `era_story_25/50/75`.
- **Dør-cue-en** («Scroll for å utforske ERA» / «Sveip opp») låses via `state.cueSeen` når historien har startet, så den ikke kommer tilbake hvis man scroller opp igjen.

## Om ERA — egen side

`/om-era` er Om ERA-filmen som egen side (13 scener: bro fra ett bygg til alle boliger, den fragmenterte boligen, den agentiske sløyfen, «fra et bilde», gjør det selv / få hjelp i én scene, lukk sløyfen, hvor kundereisen starter, teknologi, agent, aktørene, visjon, menneskene, finale med kapittelets sluttfraser). Forsiden lenker dit fra split-scenen («Hvorfor ERA finnes →»), finalen, skinnen, mobilmenyen og bunnteksten.

- Sidens `h1` er broscenens overskrift «Et agentisk system for hele boligens livsløp.» i `tools/om-era-template.html`. Siden hadde tidligere ingen `h1` i det hele tatt — forsidens ligger i dør-scenen, som ikke er med i dette bygget.
- Scenene ligger i `tools/om-era-template.html`. `python tools/build-om-era.py` setter dem sammen med forsidens hode, meny, skinne, finale, bunntekst og skript til `om-era/index.html`. Rediger malen, ikke den bygde filen.
- Én scroll-motor for begge sider: skriptet i `index.html` sjekker `body[data-page="om-era"]` for skinne-kapitler, kapittelkart, finale-timing og finalehøyde. Endringer i skriptet må følges av `build-om-era.py`.
- Etter en ny designeksport: `rebase-deltas.py` → `build-om-era.py` → `build-pages.py`. Merk at komprimeringen 2026-09-05 (05c fjernet, 20+21 slått sammen, nye scenehøyder) ikke ligger i `rebase-deltas.py` ennå.

Alle bilder er utskiftbare `<image-slot id="…" src="…">` uten innbakt tekst/UI. Portrettene (`team-*`) er plassholdere til foto foreligger; sett `src` i `teamDefs` i skriptet.

Visuell QA: `node qa-om.mjs http://localhost:8787/om-era` (skjermbilder til `qa/om-era/`).
## ERA Partner Story — /partner/<slug>

En egen, gjenbrukbar historieform for kommersielle partnersamtaler (`ERA × Jotun` er den første), helt separat fra den offentlige ERA-storyen og undersidene. Delt design (`pages.css`), egen komponentvokabular (`partner.css`: cinematisk scene, split, flow-diagram, crossfade-overgang, nummerert reveal, konvergens) og en lett reveal-motor (`js/partner-story.js`, IntersectionObserver) i stedet for den offentlige storyens skreddersydde scroll-motor — en partnerside skal ikke kreve endringer i `index.html`s script for å eksistere.

- Bygges av `tools/build-partner-story.py` (`python tools/build-partner-story.py`) fra en `PARTNERS`-dict med gjenbrukbare scene-typer (`hero`, `scene`, `split`, `transition`, `flow`, `dash`, `reveal_list`, `converge`, `steps_grid`). Ny partner = ny dict-oppføring i `PARTNERS`, ikke ny malkode.
- Alle bilder gjenbrukes fra `assets/story/`. Ingen nye plassholdere.
- Egen, diskret meny (`ERA × <partner>` + Oversikt/B2C/Distribusjon/Innsikt/Pilot + «Tilbake til ERA»), ikke lenket inn i den offentlige toppmenyen.
- `noindex,nofollow` og utelatt fra `sitemap.xml` — møtespesifikt innhold, ikke en offentlig lansert side.
- Påstandsdisiplin følges gjennomgående: `TAG_LABELS` skiller Dokumentert/ERA-forslag/Fremtidsbilde/I pilot, og produktkort er tydelig merket `DEMO_PRODUCT_DATA`.

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

### Produktflater på /boligeier

Boligeiersiden viser ERA Bolig med ekte appskjermer i stedet for å forklare produktet med tekst. Rekkefølgen følger loopen: **hero** (appens forside med tilstand, neste tiltak og estimat) → **Min bolig** → **Kamera** → **ERA-assistenten** → **Prosjekt** → **Boligminne** → **hele loopen**.

- Innholdet ligger i `app_hero` og `app_sections` i målgruppedicten. Byggerne er `phone()` (skjerm i enhetsramme), `ui()` (utsnitt av et enkelt kort, uten ramme), `app_section()` (ett budskap ved siden av én skjerm) og `app_loop()` (fem skjermer i ett rutenett med etiketter).
- Har en side `app_hero`, bytter heroen fotografiet med appen (`.hero--product`, tekst til venstre og skjerm til høyre). Uten `app_hero` er heroen som før — wrapperen `.hero-plain` er `display: contents` og endrer ingenting.
- **Skjermbilder skaleres aldri opp.** Størrelsesklassene i `.pw-phone` (`--sm` 236px, `--md` 300px, `--lg` 420px) og `.pw-ui` (400px) er satt etter kildeoppløsningen. Alle flater ligger i dag på 2,03× eller bedre. Legger du inn et nytt bilde, sjekk `naturalWidth` mot visningsbredden før du velger klasse.
- Gløden bak enheten (`.pw-phone::before`) er begrenset horisontalt. Et pseudoelement teller med i `scrollWidth`, og en bleed på 18 % ga 423px dokument på en 390px skjerm.
- **Loop-stripen bygges i HTML** av de samme fem skjermene som seksjonene bruker, ikke av et bakt komposittbilde. Da kan den ikke drifte fra seksjonene når en skjerm byttes. Under 900px skjules stripen: fem telefoner ved siden av hverandre blir ~65px brede og uleselige, og skjermene er allerede vist i lesbar størrelse i seksjonene over.
- **Én demobolig per side.** `/boligeier` bruker **Myrerveien 46A** gjennomgående; de andre målgruppesidene bruker Borgveien 14. Ikke bland dem på samme side.
- **Åpent (sept. 2026):** boligens byggeår er 1967, men skjermbildene viser 1987 (Hjem i statraden, assistenten i både analysen og «Hva det betyr»). Årstallet er derfor midlertidig ute av alt-teksten og av punktet «Hva det betyr», så siden ikke motsier bildet ved siden av. Samtidig oppgir Hjem 6,8 mill. kr og Boligminne 8,9 mill. kr for samme bolig — derfor brukes bare Boligminne-*kortet*, ikke hele den skjermen. Begge løses av to nye eksporter.

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
- **Hendelser:** `era_story_landed/started/25/50/75/completed` og `find_home_cta_viewed/cta_clicked/started/completed`, sendt via `eraTrack()`. Milepælene bygger på historieprogresjon, ikke dokument-scroll. Fram til september 2026 fyrte `era_story_started` og `find_home_cta_viewed` aldri på mobil — se scenehøydene over.
- **Personvern:** `/personvern` genereres av `tools/build-pages.py` og beskriver nøyaktig det siden gjør. Oppdater den hvis skjemaet eller lagringen endres.
- **Delingsbilde:** `og.jpg` rendres fra `tools/og-source.html` (1200 × 630) med Playwright.

## ERA Property – styredashboard (/app)

Rollebasert dashboard for borettslag og sameier, bygget som en egen Vite/React/TypeScript-app i `dashboard/` og servert på `/app`. Designtokens speiler ERA bolig-appen (papir, kort, navy, kobber, radius 6 px, 44 px knapper, bunnfaner på mobil). Markedssiden `/styret` er uendret.

- Utvikling: `npm run dashboard:dev` (http://localhost:5178/app/). Fontene serveres fra repo-roten via en liten Vite-plugin.
- Bygg: `npm run dashboard:build` skriver til `app/` (gitignorert). Vercel kjører samme kommando (`buildCommand` i `vercel.json`) og har SPA-rewrite for `/app/*`.
- Test: `npm run dashboard:test` (vitest: tilgang, tenant-isolasjon, private tilbud, soilrørflyt) og `npm run dashboard:e2e` mot `npm --prefix dashboard run preview` (Playwright: roller, filtre/URL-state, tomme og feiltilstander, 390/1280/1440/1920 px, overflyt, assistentens kilder, soilrør/bad ende til ende). Skjermbilder i `qa/dashboard/`.

Demo-styring via URL ved første last: `?rolle=styreleder|styremedlem|forretningsforer|vaktmester|beboer|leverandor|era_admin`, `?tenant=perrongen|solvang`, `?tilstand=tom|feil|treg`. Rollen kan også byttes i menyen («Vis som»).

### Arkitektur

- `src/domain/types.ts` – domenemodell (eiendom, bygningsdeler, tiltak, avvik, prosjekter, tilbud, beboere, meldinger, dokumenter, økonomi, deltakelse per bolig med private tilvalg).
- `src/access/roles.ts` – rettigheter per rolle. Frontend skjuler, adapteret håndhever.
- `src/data/adapters.ts` – kontrakten mot backend. `fixtureAdapter.ts` implementerer den mot `fixtures/perrongen.ts` (demo-tenant) og `fixtures/solvang.ts` (kun for isolasjonstest). Alle kall tar `Session`, så tenant- og rolleskoping skjer i adapteret.
- `src/shell/` – AppShell låst til viewport-høyde (venstremeny, topplinje med aktivt borettslag og rolle, global søk, bunnfaner på mobil) og ERA-assistenten som felt i bunnlinjen; svaret åpner som lag med konklusjon, begrunnelse, kilder, antakelser, mangler og neste handling.
- Uten scroll: oversikten er et cockpit (tre saker fast til venstre, firefanet panel til høyre, «+ N til» åpner fullvisning i lag; kortstokk med sveip på mobil). Tabeller i Vedlikehold, Saker, Dokumenter og Beboere klippes med «+ N til». Tilbudssammenligningen er gruppert i pris, omfang og risiko med festet beslutningslinje. Prosjektets boligliste skjules bak «Vis liste». Min bolig er en veiviser med ett steg om gangen.
- Mørkt tema: System/Lys/Mørk-bryter i sidemenyen (`src/shell/theme.tsx`), lagres i `localStorage` og settes som `data-theme` på `<html>`. Følger enhetens `prefers-color-scheme` som standard. Alle farger er tokens i `src/styles/app.css`; navy er delt i `--navy` (tekst, lysere i mørkt tema) og `--navy-solid` (knapper/paneler, mørk i begge temaer) slik at hvit tekst på navy-flater alltid er lesbar.
- Selvhostede fonter: Inter og Inter Tight ligger i `fonts/` og lastes via `fonts-inter.css`, samme mønster som Schibsted Grotesk i `fonts.css`.
- `src/pages/` – Oversikt (Mission Control), Vedlikehold, Saker, Prosjekter og prosjektdetalj, Tilbud (forespørsel og sammenligning), Beboere og meldinger, Dokumenter med ERA-funn, Økonomi, Min bolig (beboer), Mine oppdrag (leverandør).

### Backend-gap

Repoet har ingen backend for dette produktet (kun `api/lead.js`). Alt i `DataAdapter` mangler server-side: tenant og sesjon, bygg/oppganger/boliger, bygningsdeler, vedlikeholdstiltak, avvik med historikk og oppgaver, prosjekter med milepæler og endringsordrer, deltakelse per bolig og private tilbud, tilbudsforespørsler og standardiserte tilbud, vedtak, beboere og kontaktinfo, meldinger med status, dokumenter med AI-funn og korrigering, budsjettlinjer, aktivitet og assistentsvar. Fixtures er isolert i `src/data/fixtures/` og importeres bare av `fixtureAdapter.ts`; `tenant.isDemo` gir «Demo-data»-merket i topplinjen.
