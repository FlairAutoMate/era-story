# ERA Property – styredashboard: teknisk dokumentasjon

Status per 9. september 2026 (oppdatert). Gren `claude/era-property-board-dashboard-653515`, [PR #57](https://github.com/FlairAutoMate/era-story/pull/57) mot `master`. Deployet og verifisert på Vercel.

**Lenker:** [PR #57](https://github.com/FlairAutoMate/era-story/pull/57) · [dashboard/](https://github.com/FlairAutoMate/era-story/tree/claude/era-property-board-dashboard-653515/dashboard) · [adapters.ts](https://github.com/FlairAutoMate/era-story/blob/claude/era-property-board-dashboard-653515/dashboard/src/data/adapters.ts) · [types.ts](https://github.com/FlairAutoMate/era-story/blob/claude/era-property-board-dashboard-653515/dashboard/src/domain/types.ts) · [roles.ts](https://github.com/FlairAutoMate/era-story/blob/claude/era-property-board-dashboard-653515/dashboard/src/access/roles.ts) · [e2e/run.mjs](https://github.com/FlairAutoMate/era-story/blob/claude/era-property-board-dashboard-653515/dashboard/e2e/run.mjs) · [qa/dashboard/](https://github.com/FlairAutoMate/era-story/tree/claude/era-property-board-dashboard-653515/qa/dashboard) (skjermbilder)

## 1. Sammendrag

Styredashboardet er en frontend-komplett, rollebasert applikasjon for borettslag og sameier, bygget som en egen Vite/React/TypeScript-app i `dashboard/` og servert på `/app` fra det eksisterende statiske repoet. Den dekker P0 og P1 fra produktbriefen: styrets oversikt, vedlikehold, saker og avvik, prosjekter med fellesprosjekt og private tilvalg, tilbudsforespørsel og sammenligning, beboere og kommunikasjon, dokumenter med ERA-tolkning, økonomi v1, beboer- og leverandørflyt, og ERA-assistent. Alt kjører mot typede adaptere med isolerte demo-data. Det finnes ingen backend for produktet i dag; kontrakten frontend trenger er definert og testet.

Appen er deployet og verifisert på faktisk Vercel-infrastruktur (ikke bare lokalt bygg), og alle sider er gjennomgått for et gjennomgående UX-mønster: kort- eller tabellvisninger som ellers ville vokse ukontrollert (Prosjekter, Vedlikehold, Tilbud, Beboere, Økonomi, Prosjektdetalj, Leverandør) har fått en «Vis liste»- eller «Vis alle»-veksling til en kompakt tabell.

Det viktigste å beslutte nå er hvor backend skal leve og hvem som eier datamodellen. Frontend er klar til å kobles på.

## 2. Hvorfor en egen app i dette repoet

`era-story` er en statisk markedsside uten byggesteg, uten komponentbibliotek og uten backend utover `api/lead.js`. Briefen forutsatte en eksisterende plattform med AppShell og designsystem. Den finnes ikke i noe repo vi har tilgang til; `Caelis` er et urelatert produkt. Valget ble derfor:

- Egen app i `dashboard/`, bygget til `app/` (gitignorert) og servert på `/app`. Markedssiden er urørt.
- Designtokens hentet fra den kjørende bolig-piloten på `pilot.era-app.no` (papir `#f3f0e9`, kort `#fbfaf6`, navy `#1b2a4a`, kobber `#a86d46`, radius 6 px, 44 px knapper, Inter/Inter Tight, bunnfaner på mobil). Styret og beboeren møter samme visuelle språk.
- Ingen Tailwind eller UI-bibliotek. Ett stilark med tokens, ca. 32 kB ukomprimert. Bundle er 380 kB / 117 kB gzip for hovedchunken, sidene lastes ved behov.

Flyttes dashboardet senere til et plattformrepo, er `dashboard/` selvstendig og kan flyttes som mappe.

## 3. Arkitektur

```
dashboard/
  src/domain/types.ts        Domenemodell (kontrakt)
  src/access/roles.ts        Rettigheter per rolle
  src/data/adapters.ts       DataAdapter-grensesnitt (det backend skal oppfylle)
  src/data/fixtureAdapter.ts Implementasjon mot demo-data, med tenant- og rolleskoping
  src/data/fixtures/         perrongen.ts (demo-tenant), solvang.ts (isolasjonstest), assistant.ts
  src/data/provider.tsx      DataProvider, useQuery, useMutation, sesjon
  src/shell/                 AppShell, ERA-assistent, global søk
  src/components/            UI-primitiver, domenekomponenter, RoleAwareGuard
  src/pages/                 Én fil per flate
  e2e/run.mjs                Playwright-QA
```

Prinsipper:

- **Komponenter kjenner ikke datakilden.** Alt går gjennom `DataAdapter`. Bytte til API betyr én ny fil som implementerer grensesnittet.
- **Skoping i adapteret, ikke i UI.** Hvert kall tar `Session` (`tenantId`, `role`, `unitId`, `supplierId`). Adapteret filtrerer på tenant, stripper kontaktfelt uten `residents:contact`, fjerner `privateQuote` for alle unntatt beboeren selv, leverandøren og ERA-admin, og begrenser leverandør til tildelte prosjekter. Backend må gjøre nøyaktig det samme; frontend-vakten `RoleAwareGuard` er kun UX.
- **Beregnede data er adapterets ansvar.** Prioriterte saker, statusoversikt og kalender beregnes i adapteret fra rådata. Det gjør at «Dette trenger styret nå» kan flyttes til server uten UI-endring.
- **URL er state.** Faner, filtre, valgt objekt og horisont ligger i søkeparametere. Alle visninger kan lenkes og lastes på nytt.
- **Ingen scroll på oversiktsflater.** AppShell er låst til viewport. Oversikten er et cockpit; lister klippes med «+ N til» som åpner lag. Detaljer er drawers med egen scroll. Målt til null vertikal scroll ved 1280×800, 1366×768, 1440×900 og 1920×1080.

## 4. Datamodell

`src/domain/types.ts` er kontrakten. Hovedobjekter:

| Objekt | Nøkkelfelt | Merknad |
|---|---|---|
| Tenant | id, kind, buildingCount, unitCount, isDemo | `isDemo` styrer «Demo-data»-merket |
| Building, Entrance, Unit | hierarki bygg → oppgang → bolig | 48 boliger i demo |
| BuildingPart | category, conditionGrade (TG 0–3), mapped | Ukartlagt del gir «Mangler grunnlag» |
| MaintenanceAction | status, priority, riskIfDelayed, cost (intervall + Confidence), basis | Kobles til avvik, dokumenter og prosjekt |
| Issue | severity, status, responsibility (felles/privat/uavklart), facts[] med Confidence, history, comments, tasks | `internal` på kommentar skjuler for beboer og leverandør |
| Project | stage (8 steg), budget/forecast/actual, sharedCost, privateAggregate, milestones, changeOrders, packages, fdvStatus | `hasPrivateUpgrades` slår på soilrør/bad-flyten |
| UnitParticipation | responseStatus, tier, readiness, scheduledWeek, privateQuote | `privateQuote` er sensitiv |
| QuoteRequest, Quote | scopeItems, lines[] (inngår / forbehold / inngår ikke), reservations, changeRisk, eraAssessment | Standardisert form gjør sammenligning mulig |
| Decision | status, meetingDate, quoteId | Vedtak er append-only i praksis |
| Resident, Message | segment (alle/bygg/oppgang/berørte/beboer), stats | Kontaktfelt krever rettighet |
| Document, DocumentFinding | status, analysisPct, missingMetadata, access, links, findings[] med location og confirmedBy | Menneskelig korrigering vinner over maskinell |
| BudgetLine | budget, approved, forecast, actual, scope felles/privat | Økonomi v1 |
| AssistantAnswer | conclusion, reasoning, sources, assumptions, missing, nextAction, actions | Assistenten skal aldri svare i fri tekst |

`Confidence` (`bekreftet`, `era_forslag`, `antakelse`, `mangler`) brukes gjennomgående og vises alltid som tekstmerke, aldri bare farge.

## 5. Tilgangsmodell

`src/access/roles.ts` definerer 22 rettigheter og sju roller. Utdrag:

| Rettighet | Styreleder | Styremedlem | Forretningsfører | Vaktmester | Beboer | Leverandør |
|---|---|---|---|---|---|---|
| board:read | ✓ | ✓ | ✓ | | | |
| board:decide | ✓ | | | | | |
| issues:write | ✓ | ✓ | | ✓ | | |
| quotes:request / quotes:decide | ✓ | | | | | |
| residents:contact | ✓ | | | | | |
| messages:send | ✓ | | ✓ | | | |
| documents:correct | ✓ | | | | | |
| private_quotes:read_own | | | | | ✓ | |
| supplier:read_assigned | | | | | | ✓ |

ERA-admin har alt pluss `tenant:switch` og `private_quotes:read_all`. Rollebytte i menyen er en demo-funksjon og må erstattes av ekte sesjon.

Enhetstestene bekrefter: styremedlem kan ikke registrere vedtak, beboer nektes alle styrekall, kontaktinfo strippes, styret ser aldri `privateQuote`, leverandør får `AccessDeniedError` på andres prosjekter, og ingen Solvang-data lekker inn i Perrongen.

## 6. Backend-gap og foreslått API

Ingenting i `DataAdapter` finnes server-side. Forslag til første API, gruppert etter prioritet:

**P0 – nødvendig for første styre**
- `GET /tenants/:id`, sesjon med `tenant_id` og `role` i token.
- `GET /buildings`, `/units`, `/building-parts`.
- `GET /maintenance-actions`, `GET /issues`, `POST /issues`, `POST /issues/:id/comments`, `PATCH /issues/:id/tasks/:taskId`.
- `GET /projects`, `POST /projects`, `GET /projects/:id/participation` (server stripper `privateQuote` etter rolle).
- `GET /documents`, `POST /documents/:id/findings/:fid/confirm`.
- `GET /board/summary`, `GET /board/priorities`, `GET /calendar`, `GET /activity` (beregnet server-side, samme form som i dag).
- `POST /assistant/ask` med `AssistantContext`, svar som `AssistantAnswer`.

**P1 – tilbud og gjennomføring**
- `GET/POST /quote-requests`, `GET /quotes`, `POST /decisions/:id/record`, `POST /projects/:id/change-orders/:coId/decide`.
- `GET /residents` (kontaktfelt bak rettighet), `GET/POST /messages`, `GET /messages/recipients?segment=`.
- Beboer: `GET /me/participation`, `POST /me/survey`, `POST /me/tier`, `POST /me/accept`.
- `GET /budget`.

**Krav uansett løsning**
- Radnivå-sikkerhet på `tenant_id` i databasen, ikke bare i applikasjonslaget.
- `privateQuote`, `email`, `phone` og `internal`-kommentarer filtreres på server.
- Vedtak, endringsordrer og aksept av private tilbud logges som hendelser (append-only).
- Dokumentlagring med tilgangsnivå (styret / alle beboere / privat / leverandør) og OCR-kø for analyse.

## 7. Testing og verifikasjon

| Nivå | Verktøy | Omfang | Status |
|---|---|---|---|
| Typer | `tsc --strict`, `noUncheckedIndexedAccess` | hele appen | grønt |
| Lint | eslint + typescript-eslint + react-hooks | `src/` | grønt |
| Enhet | vitest, 20 tester | rettigheter, tenant-isolasjon, private tilbud, soilrørflyt, beregnede data, tom/feil-modus | 20/20 |
| E2E | Playwright, 23 sjekker | roller, tenant, filtre og URL-state, tomme og feiltilstander, 390/1280/1440/1920 px, horisontal overflyt, null scroll på oversikten, full arbeidsflate ved 1920 px, mørkt tema (system/eksplisitt/persistens), assistentens kilder og antakelser, soilrør/bad ende til ende, vedtak og forespørsel, kort/liste-veksling (Prosjekter, Tilbud, Beboere/Meldinger), klipp med «vis alle» (Vedlikehold/Bygningsdeler, Leverandør/boligtabell), ingen døde knapper | 23/23 |

Kjør: `npm run dashboard:test`, deretter `npm --prefix dashboard run preview` og `npm run dashboard:e2e`. Skjermbilder havner i `qa/dashboard/`.

Demo-tilstander for QA via URL: `?rolle=`, `?tenant=perrongen|solvang`, `?tilstand=tom|feil|treg`.

## 8. Deploy

- `vercel.json`: `buildCommand: cd dashboard && npm ci && npm run build`, `outputDirectory: .`, rewrite `/app/:match* → /app`, immutable cache på `/app/assets/*`.
- `.vercelignore` utelater `dashboard/node_modules`, `dashboard/e2e` og tester.
- Fonter: Schibsted Grotesk og JetBrains Mono fra `/fonts`, Inter og Inter Tight fra Google Fonts. Ønskes alt selvhostet, legg woff2 i `fonts/` og oppdater `dashboard/index.html`.
- **Deployet og verifisert på faktisk Vercel-infrastruktur**, ikke bare lokalt. Tre reelle produksjonsfeil ble funnet og rettet underveis: manglende `@types/node` som ekte devDependency (lokal TS-oppløsning skjulte dette via en global `@types/node` på utviklermaskinen), `vite.config.ts` som importerte `defineConfig` fra `vite` i stedet for `vitest/config` (ga en typefeil bare på Vercels rene byggemiljø), og en SPA-rewrite som 404’et på alle underruter fordi rewrite-målet `/app/index.html` kolliderte med `cleanUrls`s automatiske indexstripping ved Vercels `check: true`-reverifisering. Løsningen var å endre rewrite-målet til `/app` (uten `index.html`-suffiks). Verifisert med `npx vercel curl` mot både manuell CLI-deploy og GitHub-trigget auto-deploy.
- **Nylig fullført, samme PR:** mørkt tema med System/Lys/Mørk-bryter, selvhostede fonter, mobilt formspråk justert til piller og avrundede kort som matcher bolig-appen, skrivebordets kortradius økt fra 12 til 16 px, en layoutfeil rettet der oversikten kastet bort 328 px i hver side ved 1920 px bredde, og en systematisk gjennomgang av alle sider for manglende «Vis liste»/«Vis alle»-veksling (se seksjon 1).

## 9. Risiko og avgrensninger

- **Demo-data kan forveksles med ekte.** Merket «Demo-data» vises alltid når `tenant.isDemo` er sant. Behold det til ekte tenant finnes.
- **Assistenten er regelstyrt.** Svarene i `fixtures/assistant.ts` er håndskrevne. Formen (kilder, antakelser, mangler) er kravet til en ekte modell, ikke innholdet.
- **Ingen innlogging.** Rollebytte er demo. Backend må levere sesjon; frontend leser `Session` fra provider og trenger ingen andre endringer.
- **Økonomi er v1.** Likviditet, felleskostnadseffekt, lån, tilskudd, fakturakontroll og benchmarking er merket «Kommer senere» og har ingen døde knapper.
- **Ytelse.** Fixture-adapteret klones i minnet per sidelast. Med API må `useQuery` få cache og deduplisering, for eksempel TanStack Query, hvis flere komponenter ber om samme ressurs.

## 10. Anbefalt rekkefølge videre

1. Beslutte hvor backend lever og at datamodellen i `types.ts` er utgangspunktet.
2. Sesjon og tenant (P0), deretter `board/summary`, `priorities`, `issues`, `projects`, `documents`.
3. Bytte `createFixtureAdapter` mot `createApiAdapter` i `provider.tsx`. Beholde fixture-adapteret for tester og demo.
4. Ekte assistent bak `POST /assistant/ask` med samme svarform.
5. Selvhostede fonter og Vercel-verifisering før første styre.
