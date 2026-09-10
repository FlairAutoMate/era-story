# ERA Scroll Story

Statisk landingsside bygget fra Claude Design-eksporten «ERA Scroll Story». Ingen byggesteg: `index.html` + `js/` (dc-runtime, image-slot) + `vendor/` (React UMD) + `assets/` + `fonts/`.

Lokalt: `python -m http.server 8787` og åpne http://localhost:8787/. Visuell QA: `node qa-scroll.mjs`.

Deploy: `npx vercel --prod`.

## Historiens dramaturgi

- **Seks kapitler** i skinnen: Hjemmet → Selve produktet (`#hva`) → Forstå boligen (`#ser`) → Gjennomfør tiltak → Dokumenter verdien → Hele eiendommen. Fasen står som eyebrow i scenene, og 02 sier tidlig at ERA er en AI-drevet boligplattform.
- **Produktseksjonen (02b, `id="hva"`)** ligger rett etter «ERA samler boligen» og før «Forstå boligen». Det er en statisk seksjon (samme mønster som `#data` og team-seksjonen — padding, ikke sticky), som viser de tre arbeidsflatene som ekte produktvinduer med felles eksempeldata, flytkjeden ERA Bolig → ERA Styret → ERA Håndverker → boligens historikk, og en statuslegende. Merk: den gamle seksjon 03 heter nå `id="ser"`; `#hva` er produktseksjonen, og det er dit menyens «Hva ERA gjør» peker.
- **Produktetiketter i historien**: `.pw-where`-brikker i scene 03, 05, 07, 08, 10 og 11 («I ERA Bolig», «Sendt til ERA Håndverker», «Oppdatert i boligens historikk», «Synlig for ERA Styret») gjør male-stue-eksempelet til en demonstrasjon av produktet, ikke bare en fortelling.
- **Finalen** har en pilotlenke per målgruppe (`finPilotHref` / `finPilotLabel` i `finaleByAudience`) ved siden av adresseskjemaet.
- **Fem hendelser** i én kjede rundt paret og stua: behovet (01) → plan og estimat (05) → produkter og valg (06–07) → bestilling og gjennomføring (08) → ferdig og dokumentert (09–10). «Hele boligen» ligger etter «Hukommelse» som overgang til styret.
- **Detaljer på forespørsel**: «Se planen» (05), «Se produktvalg» (07) og «Se dokumentasjonen» (10) er knapper (`data-detail`) som åpner et panel inline på desktop og som bunnark på mobil. Innholdet ligger i HTML også når det er lukket. Funksjoner som ikke er dokumentert tilgjengelige er merket «Planlagt» (energi og forbedringer) eller «I pilot» (betaling i ERA).

## Om ERA — egen side

Sidens H1 er «Et agentisk system for hele boligens livsløp.» (scene 15). Etter den fragmenterte boligen ligger `#arkitektur` — «Produktarkitektur», en statisk seksjon som viser de tre arbeidsflatene over én bolig- og eiendomsmodell, de integrerte tjenestene rundt (faghandel, betaling, dokumentasjon og FDV, bildeanalyse — hver med statusetikett), tre forklaringer (én kilde ikke kopier · rollebasert tilgang · hvorfor systemet kalles agentisk) og flytkjeden. Skinnen har sju kapitler. Ordet «agentisk» brukes bevisst få steder, og alltid koblet til en konkret handling.

`/om-era` er Om ERA-filmen som egen side (13 scener: bro fra ett bygg til alle boliger, den fragmenterte boligen, den agentiske sløyfen, «fra et bilde», gjør det selv / få hjelp i én scene, lukk sløyfen, hvor kundereisen starter, teknologi, agent, aktørene, visjon, menneskene, finale med kapittelets sluttfraser). Forsiden lenker dit fra split-scenen («Hvorfor ERA finnes →»), finalen, skinnen, mobilmenyen og bunnteksten.

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

## Produktflater og `product.css`

Alle «ERA-programvareflater» — produktvinduene på forsiden, app-flatene på målgruppesidene og
arkitekturdiagrammet på Om ERA — bygges av ett delt vokabular i `product.css` (klasseprefiks `.pw-`).
Filen lastes av `index.html` (og dermed `/om-era`) og av alle genererte sider. Toppen av filen har en
kommentarblokk med bruksmønster for hver komponent — **les den før du skriver ny markup**, og utvid
vokabularet i stedet for å lage engangsstiler per side.

- **Vindu**: `.pw` med `.pw-bar` (era-merke, app-brikke, kontekst, «Eksempeldata»-brikke), så enten
  `.pw-tabs`/`.pw-panel` eller `.pw-body`, og eventuelt `.pw-foot`.
- **Innhold**: `.pw-dashboard`/`.pw-widget`, `.pw-kpis`, `.pw-rows`, `.pw-status-list`, `.pw-timeline`,
  `.pw-table`, `.pw-flow`, `.pw-msgs`, `.pw-progress`, `.pw-ring`, `.pw-tag` (status- og kildemerker).
- **Sideblokker**: `.pw-cards`, `.pw-chain`, `.pw-groups`, `.pw-compare`, `.pw-results`, `.pw-roles`,
  `.pw-saves`, `.pw-legend`, `.pw-scenario`, `.pw-arch`, `.pw-where` (produktetikett i historien).
- **Mobil**: `.pw-desk` skjuler sekundære widgeter under 900 px (forsidens kort viser de fire første),
  `.pw-mob` er motsatt. Ingen komponent scroller horisontalt; brede tabeller stables i stedet.

`pages.js` initialiserer **alle** `[role="tablist"]` på siden med samme oppførsel (piltaster, Home/End,
roving tabindex, `.is-past`, `.is-entering`, forrige/neste via `[data-dir]`, og høydeutjevning når
panelbeholderen er `.scene-panel` eller har `data-equalize`). `window.eraInitTabs` er eksponert for
faneflater som legges til senere. Forsiden bruker ikke `pages.js` — den har sin egen scroll-motor.

Eksempeldataene er felles for hele siden (Borgveien 14 · 24 seksjoner · male stue 42 m² · fasade 2027).
Hver flate som kan forveksles med ekte kundedata er merket «Eksempeldata».

## Responsivitet og nettleser-QA

Siden er bygget mobile-first fra 320 px og opp. Faste regler som ligger i `index.html` (`<style>` i `<helmet>`) og `pages.css`:

- Sticky-scener bruker `100dvh` med `100vh` som fallback (`.era-vh`), så de fyller det synlige vinduet på iOS. `#start`-ankeret følger samme høyde.
- `viewport-fit=cover`; meny og fast CTA respekterer `safe-area-inset-*`.
- Historien bytter til mobilkomposisjon under 900 px (samme bruddpunkt som undersidenes hamburger). Under 520 px høyde (liggende mobil) slår `html.era-short` inn: sidebilder og flytende kort skjules, typografien strammes.
- Alle lenker og knapper har minst 44 px trykkflate (`.era-link`, bunntekst, skinne, pill). Inputtekst er 16 px.
- Mobilmenyen låser bakgrunnsscroll, lukkes med Escape og ved trykk utenfor.
- Flytende brikker (kaos, fragmentert bolig, lukk sløyfen) klemmes inn i viewporten.

QA-skript (krever `node_modules` med Playwright og motorene `npx playwright install chromium firefox webkit`):

- `node qa-responsive.mjs http://localhost:8787 chromium,firefox,webkit all "/,/boligeier,/styret,/handverker,/faghandel,/om-era,/personvern"` — alle ruter × 14 viewporter × motor. Uten siste argument utelates `/om-era`. Rapporterer horisontal overflyt, elementer utenfor viewporten, avkuttet/overlappende tekst, trykkflater under 44 px, inputtekst under 16 px og konsollfeil. Rapport i `qa/responsive/`.
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

`/boligeier`, `/styret`, `/handverker`, `/faghandel` genereres av `python tools/build-pages.py` fra én innholdsstruktur (hook, verdiforslag, steg, gevinst, eksempel, spørsmål, skjema). Delt stil i `pages.css`, fonter i `fonts.css`, skjema i `pages.js` (samme `/api/lead`). Endre tekst i generatoren og kjør den på nytt.

**Produktseksjonene ligger i egne moduler.** Hver side har `product_module="content_<slug>"`, og `build-pages.py` kaller `render(H, a)` i `tools/content_<slug>.py` og setter resultatet inn rett etter heroen. `H` er byggerne (`window`, `dashboard`, `kpis`, `rows`, `status_rows`, `timeline`, `table`, `flow`, `groups`, `compare`, `results`, `roles`, `saves`, `legend`, `scenario`, `msgs`, `widget`, `cols`, `checklist`, `section`, `tag`, `note` …), `a` er målgruppedicten. Alt tekstinnhold escapes av byggerne; bare parametre som slutter på `_html` tar ferdig markup. Legg til en ny seksjon i modulen, ikke i generatoren.

**CTA-ruting** — én tabell, brukt av hero, meny, avslutning og fanenavigasjon:

| Side | Primær | Sekundær |
|---|---|---|
| `/boligeier` | «Start som boligeier» → `https://pilot.era-app.no/register?entry=homeowner` | «Se produktet i bruk» → `#produktet` |
| `/styret` | «Registrer borettslag eller sameie» → `…?entry=sameie` | «Book en gjennomgang» → `#skjema` |
| `/handverker` | «Start som håndverker» → `…?entry=contractor` | «Se hvordan en jobb flyter gjennom ERA» → `#flyt` |
| `/faghandel` | «Utforsk partnerskap med ERA» → `#skjema` | «Se dashboardet for kjede og forhandler» → `#dashboard` |

Faghandel sendes aldri til pilotinngangen — den har ingen konto. Eksterne lenker er `rel="noopener"` i samme fane.

**Avslutningen er ulik per side:** `/boligeier` har *ikke* lenger et kontaktskjema (all CTA går til piloten), `/styret` og `/handverker` har pilotknapp + skjema med hensiktsvalg, `/faghandel` har bare partnerskjemaet. `/faghandel` har heller ingen «Gevinsten»-seksjon — den nye «Verdi»-seksjonen dekker det samme, og oppdraget forbyr å gjenta samme forklaring.

Menyen er lik på alle sider: Hva ERA gjør · Boligeier · Styret · Håndverker · Faghandel · Om ERA (Personvern bare i mobilpanelet og bunnteksten). Etiketten «Historien» er ute overalt.

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
- **Ordlyd om lagring:** markedsføringssidene sier bare «kryptert innenfor EU/EØS». Frankfurt og Vercel nevnes utelukkende på `/personvern`. «i Norge» skal ikke forekomme.
- **Analyse:** `/_vercel/insights/script.js` er lagt inn på alle sider. Slå på Web Analytics én gang i Vercel-dashbordet (prosjekt → Analytics), ellers gjør skriptet ingenting.
- **Personvern:** `/personvern` genereres av `tools/build-pages.py` og beskriver nøyaktig det siden gjør. Oppdater den hvis skjemaet eller lagringen endres. Formålsteksten er skrevet om (siden påsto tidligere at opplysningene brukes til å ta kontakt, samtidig som den sa at ingen kontaktopplysninger samles inn), og seksjonen «Registrering i ERA-piloten» forklarer at piloten er en egen tjeneste med egne vilkår — lenken dit mangler, se `AVKLAR`-kommentaren i `privacy_page()`.
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

## Før publisering

- `tools/avklaringer-for-publisering.md` — sjekklisten over alt nettsiden påstår som et menneske må bekrefte: statusmatrisen, pilotinngangen, personvern, og funksjoner navngitt per side. Gå gjennom den før lansering.
- `tools/pilot-entry-spec.md` — spesifikasjon for pilotinngangen på `pilot.era-app.no`. Piloten ligger **ikke** i dette repoet; markedssiden lenker bare til den.
- Kjør begge generatorene (`python tools/build-pages.py && python tools/build-om-era.py`) som siste steg. De er idempotente: en ny kjøring skal ikke endre noe.
