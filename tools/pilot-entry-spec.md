# Pilotinngang — spesifikasjon for pilot.era-app.no

Utkast · 10. september 2026 · gjelder pilotappen (eget kodebase, ikke dette repoet).
Skrevet fra markedssiden slik at ordlyd, lenker og designtokens er de samme begge steder.
Kildene som er brukt: `pages.css`, `product.css`, `tools/build-pages.py` (tekst per målgruppe),
`index.html` (finale og analyse) og `api/lead.js`. Alt som ikke kan leses ut av disse filene er
merket **Avklares** og samlet i kapittel 9.

Innhold

1. Mål
2. Innganger
3. URL-parameter `entry`
4. Terminologi
5. Designtokens
6. Tilgjengelighet
7. Personvern
8. Akseptansekriterier
9. Avklaringer

---

## 1. Mål

Pilotinngangen skal oppleves som samme produkt som era-app.no. Den som trykker «Start som
boligeier» på markedssiden skal ikke merke at de bytter system: samme farger, samme skrift,
samme radier, samme ord for de samme tingene, og en tydelig vei tilbake.

Konkret:

- **Visuelt**: pilotens inngangs-, innloggings-, registrerings- og kontaktskjermer bruker
  tokens fra kapittel 5 (Schibsted Grotesk, gull #D4B17A, navy #131E3A, 22 px kort, 999 px piller).
  Dagens Inter / kobber / 6 px-radius fases ut, se migrasjonsnotatet i 5.7.
- **Språklig**: produktnavn, flyt, statusetiketter og skjemaetiketter er identiske med
  markedssiden (kapittel 4). Ingen nye løfter, ingen nye tall.
- **Flyt**: `entry`-parameteren som markedssiden allerede sender, forhåndsvelger riktig rolle,
  overlever innlogging og registrering, og «Tilbake til era-app.no» fører til riktig målgruppeside.

Omfang: inngangssiden (rollevelger), rammen rundt innlogging og registrering, og de to
kontaktflytene som ikke gir konto (partner, demo). Arbeidsflatene bak innlogging arver bare
tokens, ikke denne spesifikasjonen.

---

## 2. Innganger

Seks innganger, i denne rekkefølgen. De tre første gir konto, de to siste er kontaktflyter,
og «Logg inn» ligger øverst til høyre som tekstlenke.

| # | Inngang | Etikett på kort / knapp | Én linje under rollen | Åpner | Status | `entry` |
|---|---|---|---|---|---|---|
| 1 | Boligeier | Kort «ERA Bolig» · handling «Start som boligeier» | Forstå boligen. Se hva som bør gjøres. Få hjelp til å gjennomføre det. | Registrering i ERA Bolig | Kontrollert beta | `homeowner` |
| 2 | Borettslag og sameie | Kort «ERA Styret» · handling «Registrer borettslag eller sameie» | Fra vedlikeholdsbehov til beslutning, tilbud og ferdig dokumentert arbeid. | Registrering i ERA Styret | I pilot | `sameie` |
| 3 | Håndverker | Kort «ERA Håndverker» · handling «Start som håndverker» | Jobben er forstått før forespørselen kommer. | Registrering i ERA Håndverker | I pilot | `contractor` |
| 4 | Innlogging | Tekstlenke «Logg inn» | Har du tilgang fra før, logger du inn her. | Eksisterende konto, riktig arbeidsflate | – | beholder mottatt verdi |
| 5 | **Ny:** Faghandel og partner | Kort «ERA for faghandel» · handling «Utforsk partnerskap med ERA» | Fra boligbehov til riktig produkt i riktig butikk. | Partnerkontakt, **ikke** konto | Under utvikling | `partner` (foreslått) |
| 6 | **Ny:** Book demo for styret | Kort «Book en gjennomgang» · handling «Book en gjennomgang» | En gjennomgang av ERA Styret med oss, før dere registrerer eiendommen. | Demoforespørsel, **ikke** konto | I pilot | `board-demo` (foreslått) |

Linjene i rad 1, 2, 3 og 5 er markedssidens løftelinjer og skal stå ordrett. Linjene i rad 4
og 6 er nye og må godkjennes (Avklares, A1).

Merknader per inngang:

- **Boligeier.** Registreringssteget kan gjenta betafaktaene fra markedssiden, ordrett og ikke
  mer: «Nå i kontrollert beta — åpnes for 300 boligeiere», «Gratis for boligeiere i
  betaperioden. Begrenset antall plasser.», «Ingen betalingskort. Ingen binding. Vi inviterer
  brukere fortløpende.» Ingen priser etter beta.
- **Borettslag og sameie.** Sekundærhandling på kortet: «Book en gjennomgang» → inngang 6.
- **Håndverker.** ERA Håndverker rulles ut område for område. Bekreftelsen etter registrering
  bruker markedssidens ordlyd: «Takk. Du er registrert.» / «Vi tar kontakt når det er ferdig
  beskrevne oppdrag i ditt område.»
- **Faghandel og partner.** Faghandel er ikke en fjerde app og får aldri en pilotkonto. Kortet
  fører til et kontaktskjema. Dashbordene for kjede og forhandler er «Under utvikling».
- **Book demo for styret.** Skjema med feltet «Adressen til bygget», hensikt `demo`.
  Bekreftelse: «Takk. Vi tar kontakt for å avtale en demo.» / «Du hører fra oss med forslag
  til tidspunkt.»

### 2.1 Skisse av inngangssiden

```
[← Tilbake til era-app.no]                                          [Logg inn]

  PILOT · ERA                                   (eyebrow, .label-stil)
  Velkommen til ERA.                            (h1, se 6.1 for variant)
  Tre arbeidsflater. Én sammenhengende eiendom. (lede)

  ┌ ERA Bolig ──────────┐ ┌ ERA Styret ─────────┐ ┌ ERA Håndverker ─────┐
  │ BOLIGEIER            │ │ BORETTSLAG OG SAMEIE │ │ HÅNDVERKER           │
  │ Forstå boligen. …    │ │ Fra vedlikeholds… │ │ Jobben er forstått … │
  │ [Kontrollert beta]   │ │ [I pilot]            │ │ [I pilot]            │
  │ Start som boligeier →│ │ Registrer borettslag…│ │ Start som håndverker→│
  └──────────────────────┘ └──────────────────────┘ └──────────────────────┘

  ┌ ERA for faghandel ────────────────┐ ┌ Book en gjennomgang ─────────────┐
  │ FAGHANDEL OG PARTNER               │ │ STYRET                            │
  │ Fra boligbehov til riktig produkt… │ │ En gjennomgang av ERA Styret …    │
  │ [Under utvikling]                  │ │ [I pilot]                         │
  │ Utforsk partnerskap med ERA →      │ │ Book en gjennomgang →             │
  └────────────────────────────────────┘ └───────────────────────────────────┘

  Personvern for piloten · © 2026 ERA technologies AS · Oslo
```

Kortanatomi (ovenfra): eyebrow med rollen, h2 med produktnavnet, løftelinjen, statusetikett
(`.pw-tag--beta` / `--pilot` / `--dev`), handlingstekst med «→». Hele kortet er én lenke
(kapittel 6). Under 900 px stables kortene i én kolonne i samme rekkefølge; ingen kort skjules.

---

## 3. URL-parameter `entry`

### 3.1 Verdier

| `entry` | Rolle | Finnes i dag | Markedssiden lenker fra | Mål i piloten | Tilbake-lenke |
|---|---|---|---|---|---|
| `homeowner` | Boligeier | Ja | `/boligeier` (alle CTA) og forsidens produktkort via `/boligeier` | Registrering, ERA Bolig | `/boligeier` |
| `sameie` | Styret | Ja | `/styret` (primær CTA) | Registrering, ERA Styret | `/styret` |
| `contractor` | Håndverker | Ja | `/handverker` (primær CTA) | Registrering, ERA Håndverker | `/handverker` |
| `partner` | Faghandel | Nei, foreslått | I dag ingen: `/faghandel` sender til eget skjema `/faghandel#skjema` | Partnerkontakt | `/faghandel` |
| `board-demo` | Styret (demo) | Nei, foreslått | I dag ingen: `/styret` sender til eget skjema `/styret#skjema` (hensikt `demo`) | Demoforespørsel | `/styret` |
| mangler eller ukjent | – | – | – | Nøytral rollevelger | `/` (forsiden) |

Markedssiden lenker til `https://pilot.era-app.no/register?entry=<verdi>` med vanlig
`<a href>` i samme fane og `rel="noopener"`. De to foreslåtte verdiene tas i bruk på
markedssiden først når piloten bekrefter at de er støttet (Avklares, A2). Piloten bør likevel
tåle dem fra dag én: ukjent verdi gir nøytral velger, aldri feil.

### 3.2 Oppførsel

1. **Tolkning.** Les `entry`, trim, små bokstaver, sjekk mot listen over. Alt annet behandles
   som «mangler». Råverdien skrives aldri inn i DOM, tittel eller logg; bare den oppslåtte nøkkelen.
2. **Gyldig verdi.** Kortet for rollen får `aria-current="true"` og valgt utseende (navy flate,
   gull understrek, som `.pw-tab[aria-selected="true"]`). Etter første tegning: kortet rulles til
   midten av viewporten og får fokus. Ved `prefers-reduced-motion: reduce` rulles det uten
   animasjon (`behavior: 'auto'`). Ingen automatisk videresending: ett trykk bekrefter valget, så
   den som kom inn med feil rolle kan velge om.
3. **Manglende eller ukjent verdi.** Nøytral velger: ingen `aria-current`, ingen rulling, h1
   «Velg hvordan du vil bruke ERA.».
4. **Parameteren følger med.** `entry` legges på alle interne videresendinger i kjeden
   inngang → `/login` → `/register` → bekreftelse → første skjerm. Som reserve for steg der
   tredjepart kan miste spørrestrengen: lagre `sessionStorage['era.entry']` ved landing, les
   den hvis URL-en mangler verdien, slett etter bruk. Rekkefølge: URL foran lagret verdi.
5. **Ny konto** får rolle og arbeidsflate fra `entry`. **Eksisterende konto** beholder sin rolle;
   `entry` forkastes stille etter innlogging.
6. **«Logg inn»** peker til `/login?entry=<verdi>` når verdien finnes.
7. **Tilbake-lenken** «← Tilbake til era-app.no» ligger øverst til venstre på inngang,
   innlogging, registrering og de to kontaktskjemaene. Minst 44 × 44 px, samme fane, mål etter
   tabellen i 3.1. Vises ikke inne i arbeidsflatene etter innlogging.

### 3.3 Analysehendelser

Markedssiden sender egendefinerte hendelser til Vercel Web Analytics med
`window.va('event', { name, … })`, navngitt `era_story_landed`, `era_story_started`,
`era_story_25`, `era_story_50`, `era_story_75`, `era_story_completed` og
`find_home_cta_viewed`, `find_home_cta_clicked`, `find_home_started`, `find_home_completed`.
Piloten speiler mønsteret med prefikset `era_pilot_`:

| Hendelse | Når | Data |
|---|---|---|
| `era_pilot_landed` | Inngangssiden er lastet | `{ entry }` (nøkkel eller `"none"`) |
| `era_pilot_role_selected` | Trykk på et rollekort | `{ entry, preselected: true\|false }` |
| `era_pilot_register_started` | Første felt i registreringen får fokus | `{ entry }` |
| `era_pilot_register_completed` | Konto opprettet | `{ entry }` |
| `era_pilot_login_started` / `era_pilot_login_completed` | Innlogging startet / fullført | `{ entry }` |
| `era_pilot_partner_started` / `era_pilot_partner_completed` | Partnerskjema åpnet / sendt | – |
| `era_pilot_demo_started` / `era_pilot_demo_completed` | Demoskjema åpnet / sendt | – |
| `era_pilot_back_clicked` | Tilbake-lenken trykket | `{ entry }` |

Regler, som på markedssiden: snake_case, fortid, hver milepæl maks én gang per økt, aldri kast
feil (pakk inn i `try`), aldri personopplysninger i nyttelasten (ingen adresse, navn, e-post
eller råverdi av `entry`). Hvilket analyseverktøy piloten bruker er uavhengig av navnene (Avklares, A3).

---

## 4. Terminologi

### 4.1 Produkt og flyt

| Begrep | Riktig | Merknad |
|---|---|---|
| Arbeidsflatene | **ERA Bolig**, **ERA Styret**, **ERA Håndverker** | Alltid slik skrevet når produktet navngis. Sidetitler som «ERA for boligeiere» er greit som titler. |
| Faghandel | «ERA for faghandel» er «en integrert handels- og distribusjonsflate i ERA-systemet» | Ikke en fjerde app. Aldri «ERA Faghandel». |
| Produktlinje | «Tre arbeidsflater. Én sammenhengende eiendom.» | Brukes som lede på inngangssiden. |
| Underlinje | «ERA Bolig hjelper boligeieren forstå og handle. ERA Styret gjør behov om til planer og beslutninger. ERA Håndverker gjør forespørselen om til tilbud, gjennomføring og dokumentert resultat.» | Kan stå under produktkortene på bred skjerm. |
| Flyten | **Forstå → prioritere → planlegge → bestille → gjennomføre → dokumentere** | Alltid denne rekkefølgen og ordlyden. Vises som chip-kjede (`.pw-flow`). |
| Roller i løpende tekst | boligeier, styret, håndverker, faghandel | Små bokstaver. |
| Sidetittel | «Velkommen — ERA», «Logg inn — ERA», «Registrer deg — ERA» | Markedssiden bruker `{tittel} — ERA` med tankestrek. |

### 4.2 Statusetiketter

Bare disse fem tilgjengelighetsetikettene finnes: **Tilgjengelig nå**, **Kontrollert beta**,
**I pilot**, **Under utvikling**, **Planlagt**. I tillegg kildeetikettene **Dokumentert**,
**ERA-forslag**, **Fra kunden**, **Avklares på befaring**, **Illustrasjon av arbeidsflyt**,
**Bestilling og levering**. Ingenting er «Tilgjengelig nå» i dag.

| Hva | Etikett | CSS-klasse |
|---|---|---|
| ERA Bolig | Kontrollert beta (300 boligeiere, gratis i betaperioden, uten kort og binding) | `.pw-tag--beta` |
| ERA Styret | I pilot (registrering finnes, demo tilbys) | `.pw-tag--pilot` |
| ERA Håndverker | I pilot (rulles ut område for område) | `.pw-tag--pilot` |
| Betaling i ERA, utbetaling og fakturagrunnlag | I pilot | `.pw-tag--pilot` |
| Energi og forbedringer | Planlagt | `.pw-tag--planned` |
| Faghandelens dashbord (sentralt og forhandler) | Under utvikling | `.pw-tag--dev` |
| Tilbudssammenligning og beboervarsling (styret) | Illustrasjon av arbeidsflyt | `.pw-tag--illustration` |

### 4.3 Eksempeldata

Alle skjermer som viser data som kan forveksles med ekte kundedata (demo-leietaker,
forhåndsvisning i registreringen, tomtilstander med innhold) merkes med chipen
**«Eksempeldata»** (`.pw-chip`) i tittellinjen, eller fotnoten «Eksempeldata, ikke reelle
kundeopplysninger.» Bruk markedssidens eksempel så alle flater viser samme eiendom:
Borgveien 14 · borettslag, 24 seksjoner; boligeierens jobb «Male stue, 42 m²», ca. 6 800 kr.

### 4.4 Skjemaetiketter og bekreftelser

Nøyaktig ordlyd fra markedssidens skjemaer. `autocomplete` er et forslag.

| Rolle | Feltetikett | `autocomplete` | Knapp | Bekreftelse (overskrift / underlinje) |
|---|---|---|---|---|
| Boligeier | Adressen til boligen | `street-address` | Finn min bolig | Takk. Vi finner boligen din. / Vi sier fra når ERA er klar for adressen. |
| Styret, registrering | Adressen til bygget | `street-address` | Registrer borettslag eller sameie | Takk. Vi ser på eiendommen. / Vi tar kontakt med et forslag til plan, klart til neste møte. |
| Styret, demo | Adressen til bygget | `street-address` | Book en gjennomgang | Takk. Vi tar kontakt for å avtale en demo. / Du hører fra oss med forslag til tidspunkt. |
| Håndverker | Firmanavn eller organisasjonsnummer | `organization` | Start som håndverker | Takk. Du er registrert. / Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område. |
| Faghandel og partner | Kjede, produsent eller butikk | `organization` | Utforsk partnerskap med ERA | Takk. Vi tar kontakt. / Vi tar kontakt og viser hvordan beregnede behov blir bestillinger hos dere. |

Adressefeltene for boligeier og styret har på markedssiden Kartverket-autofullføring
(Geonorge `adresser/v1/sok`, seks treff, `role="combobox"`). Piloten bør bruke samme kilde så
adressen skrives likt begge steder.

Feilmeldinger, ordrett: «Skriv inn litt mer, så finner vi riktig sted.» (for kort verdi),
«Noe gikk galt hos oss. Prøv igjen om et øyeblikk.» (serverfeil), «Ingen kontakt med serveren.
Sjekk nettet og prøv igjen.» (nettverksfeil). Under sending står knappen «Sender…».

### 4.5 Språkregler

Bokmål, kort og konkret. Overskrifter i setningsform med punktum til slutt, som markedssiden
(«Boligeierskap uten gjetting.», «Velkommen til ERA.»). Ingen utropstegn. Sitattegn «». Skilletegn ·. Tynn mellomrom i tall: «6 800 kr», «42 m²», «2 × 10 L».
Intervaller med tankestrek: «uke 38–40». Ingen påstander om tid spart eller prosent; beskriv
mekanismen (hva som gjenbrukes, hva som slippes).

Datalagring: markedssiden sier bare «kryptert innenfor EU/EØS». Piloten bruker samme formulering
bare hvis den er sann for piloten (Avklares, A5); aldri «i Norge» eller stedsnavn utenfor
personvernsiden.

---

## 5. Designtokens

Alle verdier er hentet fra `pages.css` (`:root`) og `product.css`. Piloten kan kopiere
`product.css` uendret (klasseprefiks `.pw-`, ingen globale resets) og legge `:root`-variablene
fra `pages.css` i sitt eget tema.

### 5.1 Farger

| Token | Hex | Bruk |
|---|---|---|
| `--navy` | `#0F1830` | Mørke seksjoner, sidebakgrunn i mørkt tema, meta `theme-color` |
| `--navy-2` / `--ink` | `#131E3A` | Brødtekst, navy-knapper, valgte faner, tekst på gull |
| `--navy-3` | `#26344F` | Hover på navy-knapper, dempet navy |
| `--warm` | `#F7F4EE` | Krem: tekst på navy, lys bakgrunn |
| `--paper` | `#FFFDF9` | Sidebakgrunn (lys), kortbakgrunn |
| `--sand` | `#F1EDE4` | Alternerende seksjoner, chips, dempede grupper |
| `--line` | `#E3DDD0` | Kantlinjer på kort og felt |
| hairline | `#EFEAE0` | Skillelinjer i rader, tittellinjer |
| `--gold` | `#D4B17A` | Primærknapp (flate), fokusring, aktiv markering. **Aldri som tekst på lys bakgrunn.** |
| `--gold-2` | `#B0935F` | Eyebrows og små etiketter på lys bakgrunn (arv fra nettsiden; under AA for løpende tekst) |
| gull mørk | `#7A6238` | Gulltekst under 18 px der AA kreves (ca. 5,8:1 mot papir) |
| `--muted` | `#5E6472` | Sekundærtekst |
| `--muted-2` | `#8A8579` | Etiketter, meta, fotnoter |
| muted-3 | `#9A968C` | Juridisk fottekst, «senere»-tilstander |
| good | `#3E7B4F` / `#4C8A63` | Bekreftelse, fremdrift ok |
| danger | `#C0483A` | Feil, høy risiko |

Gull brukes som flate med navy tekst (`#131E3A` på `#D4B17A`), ikke omvendt. Hover på gull:
`#E2C48F`.

### 5.2 Skrift

| Rolle | Font | Merknad |
|---|---|---|
| UI og brødtekst | `'Schibsted Grotesk', system-ui, sans-serif` | `-webkit-font-smoothing: antialiased` |
| Tall, meta, id-er, kontekst | `'JetBrains Mono', monospace` | `font-variant-numeric: tabular-nums` i tabeller |
| Håndskrift | `'Caveat'` | Bare i historien; ikke i piloten |

Filene ligger i markedssidens `fonts.css` + `/fonts/*.woff2`; piloten bør selv-hoste de samme
filene (ingen ekstern fontkall). Preload den første Schibsted-filen som markedssiden gjør.

Typeskala (fra `pages.css`):

| Element | Verdi |
|---|---|
| h1 | `clamp(38px, 5.4vw, 72px)`, 800, `letter-spacing: -0.03em`, `line-height: 1.04`, `text-wrap: balance`. Appskjermer kan bruke `clamp(36px, 5vw, 60px)` (`.doc h1`). |
| h2 | `clamp(30px, 3.8vw, 50px)`; kortoverskrift 20 px 800 `-0.02em` (`.pw-card-head h3`) |
| Lede | `clamp(17px, 2vw, 22px)`, 500, `line-height: 1.4`, farge `--muted` (lys) eller `rgba(247,244,238,0.85)` (navy) |
| Eyebrow (`.label`) | 12 px 700 uppercase `letter-spacing: 0.14em`, farge `--gold-2` |
| Brødtekst | 14–16,5 px, `line-height: 1.45–1.55` |
| Etikett (`.pw-tag`) | 10,5 px 700 uppercase `0.06em`, radius 999 px |
| Inputtekst | **16 px** (aldri mindre) |

### 5.3 Radier og flater

| Element | Radius | Øvrig |
|---|---|---|
| Piller: knapper, faner, chips, tags, meny | 999 px | |
| Store kort, vinduer, menypanel | 22 px (16 px under 900 px for `.pw`) | Bakgrunn `--paper` eller `#FFFFFF`, kant `1px solid --line`, skygge `0 10px 40px rgba(19,30,58,0.05)` (panel) / `0 30px 80px rgba(19,30,58,0.12)` (vindu) |
| Fliser: KPI, grupper, widgets, menyrader | 12–14 px | Bakgrunn `#FFFFFF`, kant `--line` |
| Mellomstore kort (roller, gevinster) | 16–20 px | |
| Inputfelt | 999 px i pille-skjema; 12–14 px i vanlige skjemaer | Kant `--line`, fokusring som under |

### 5.4 Komponenter

| Komponent | Spesifikasjon |
|---|---|
| Primærknapp (`.btn`) | Høyde 46 px, padding `0 22px`, radius 999, bakgrunn `--gold`, tekst `--navy-2`, 700, 15 px; hover `#E2C48F` |
| Navy-knapp (`.pw-cta`, `.scene-next`) | Min-høyde 44 px, padding `0 20px`, bakgrunn `#131E3A`, tekst `#F7F4EE`, 700, 14,5 px; hover `#26344F` |
| Ghost-knapp (`.pw-cta--ghost`) | Transparent, kant `--line`, tekst `--ink`; hover `--sand` |
| Tekstlenke (`.link`) | Min-høyde 44 px, 600, 15 px, farge `--gold` på navy / `--gold-2` på lys; hover `#fff` / `--ink` |
| Toppmeny (`.pill`) | Høyde 58 px, radius 999, blur 18 px, `rgba(15,24,48,0.55)` på mørk / `rgba(255,253,248,0.85)` på lys, `top: max(14px, env(safe-area-inset-top))` |
| Rollekort | Som `.pw-card--tile`: padding `22px 24px`, radius 22, `#FFFFFF`, kant `--line`; valgt: bakgrunn `#131E3A`, tekst `#F7F4EE`, `box-shadow: inset 0 -3px 0 #D4B17A` |
| Statusetikett | `.pw-tag--beta` (gullramme), `--pilot` / `--planned` / `--illustration` (`#E7E0D3` / `#7A6238`), `--dev` (`#EFEAE0` / `#5E6472`) |
| Bekreftelse (`.done`) | Kort 22 px, grønn sirkel 40 px `#3E7B4F` med hvit hake, `role="status" aria-live="polite"` |
| Feilmelding (`.err`) | 13,5 px, `#C0483A` på lys / `rgba(247,244,238,0.8)` på navy, rett under feltet |
| Fottekst (`.fine`) | 12,5 px, `--muted-2` |

### 5.5 Fokus, bevegelse, brytpunkter

- Fokus: `outline: 2px solid #D4B17A; outline-offset: 3px` på alle interaktive elementer
  (`:focus-visible`). Radius 6 px på fokusringen rundt inputfelt er greit; ellers følger ringen
  elementets radius.
- Overganger 150–180 ms `ease-out`; panelinngang `translateY(4px)` → 0 på 180 ms. Ved
  `prefers-reduced-motion: reduce`: `transition: none; animation: none`, `scroll-behavior: auto`,
  ingen skrivemaskin-plassholder, ingen pulserende knapper.
- Brytpunkter som markedssiden: 899 px (mobilkomposisjon, hamburger), 560 px (rader stables),
  389 px (én kolonne), 350 px (sekundær CTA i toppmenyen skjules). Landskap under 520 px høyde:
  stram typografi, skjul sidebilder.
- Mobil først fra 320 px. `100dvh` med `100vh` som reserve. `viewport-fit=cover` og
  `safe-area-inset-*` på faste elementer.
- Aldri horisontal rulling og ingen indre `overflow-x`-beholdere: rutenett med
  `repeat(auto-fit, minmax(min(100%, Npx), 1fr))` eller `minmax(0, 1fr)`, `overflow-wrap: anywhere`
  på lange strenger, `max-width: 100%` på bilder. Minst 44 × 44 px trykkflate på alt interaktivt.

### 5.6 Ikon og merke

Merket er «era» med gull punktum: `<span class="brand">era<span>.</span></span>` (800,
`-0.03em`, punktumet i `--gold`). Samme `favicon.svg` og `theme-color #0F1830` som markedssiden.

### 5.7 Migrasjon fra dagens pilottokens

Fra en tidligere gjennomgang bruker piloten i dag papir `#f3f0e9`, kort `#fbfaf6`, navy
`#1b2a4a`, kobber `#a86d46`, grønn `#5b7a4b`, rød `#a85a3d`, radius 6 px, 44 px knapper,
Inter / Inter Tight og fanelinje nederst på mobil. Bytt slik:

| I dag | Bytt til | Merknad |
|---|---|---|
| Papir `#f3f0e9` | `#F7F4EE` (side) / `#FFFDF9` (kort) | To nyanser, ikke én |
| Kort `#fbfaf6` | `#FFFFFF` på papir, `#FFFDF9` på krem | |
| Navy `#1b2a4a` | `#131E3A` (tekst, knapper) / `#0F1830` (mørke flater) | |
| Kobber `#a86d46` | `#D4B17A` som flate, `#B0935F` for eyebrows, `#7A6238` for gulltekst | Kobber som tekstfarge forsvinner helt |
| Grønn `#5b7a4b` | `#3E7B4F` (`#4C8A63` for fremdrift) | |
| Rød `#a85a3d` | `#C0483A` | |
| Radius 6 px | 999 px piller, 22 px kort, 12–14 px fliser | 6 px bare på fokusring rundt input |
| Inter / Inter Tight | Schibsted Grotesk / JetBrains Mono | Selv-hostet, samme filer som markedssiden |
| 44 px knapper | Behold; primær 46 px, gull | |
| Fanelinje nederst (mobil) | Behold inne i arbeidsflatene, med nye tokens: papir, hairline-topp, navy ikoner, gull aktiv, `env(safe-area-inset-bottom)`, minst 44 px per fane | **Ikke** på inngang, innlogging, registrering og kontaktskjemaer; de ligger utenfor app-skallet |

Gjør migrasjonen i én runde for skjermene i denne spesifikasjonen, så inngangen ikke står med
to visuelle språk samtidig. Skjermene bak innlogging kan følge etter.

---

## 6. Tilgjengelighet

### 6.1 Struktur

- `<html lang="no">`. Én h1 per side: «Velkommen til ERA.» når `entry` er gyldig, «Velg hvordan
  du vil bruke ERA.» ellers (punktum til slutt, som markedssidens overskrifter). Kortene bruker h2 (produktnavn); ingen h3 uten h2 over seg.
- Landemerker: `<header>` (tilbake, logg inn), `<main>` (h1, kort), `<footer>` (personvern).
  Toppmenyen: `<nav aria-label="Hovedmeny">` som på markedssiden.
- Rollekort er `<a href="/register?entry=…">`, aldri `div`/`span` med klikk. Hele kortet er
  lenken; `aria-labelledby="<h2-id> <handling-id>"` gir navnet «ERA Bolig, Start som boligeier»,
  `aria-describedby` peker på løftelinjen. Knapper som gjør noe på siden er `<button type="button">`.
- Forhåndsvalgt kort: `aria-current="true"`. Bare ett kort om gangen.
- Tabrekkefølge: hopp-lenke «Til innholdet» (valgfritt) → «Tilbake til era-app.no» → «Logg inn»
  → kortene i visuell rekkefølge → «Personvern for piloten». Ingen `tabindex` over 0.

### 6.2 Skjemaer

- Synlig `<label>` for hvert felt (eller `.sr`-etikett og synlig plassholder, som markedssiden).
  Inputtekst 16 px. Min-høyde 44 px. `autocomplete` etter tabellen i 4.4. Honningkrukke
  (`name="website"`, `tabindex="-1"`, `aria-hidden="true"`, visuelt skjult) i kontaktskjemaene.
- Feil: rett under feltet, `aria-describedby` fra feltet, `aria-invalid="true"`, tekst fra 4.4.
  Serverfeil i en `role="alert"`-beholder. Fokus flyttes til første felt med feil.
- Bekreftelse i `role="status" aria-live="polite"`; skjemaet skjules (`hidden`), ikke fjernes.
- Sende-knappen låses under sending (`disabled`, «Sender…») og låses opp ved feil.
- Adresseforslag: `role="combobox"`, `aria-autocomplete="list"`, `aria-expanded`,
  `aria-activedescendant`, piltaster, Enter, Escape, lukk ved blur.

### 6.3 Visuelt

- Fokusring `2px solid #D4B17A`, offset 3 px, på alt interaktivt, også kort.
- Kontrast: tekst mot bakgrunn minst 4,5:1; `#D4B17A` og `#B0935F` bare som flate eller eyebrow.
- Dekorativ grafikk `alt=""`; informative bilder får beskrivende `alt`. Ikke tekst i bilder.
- Ingen informasjon bare i farge: status har alltid etikett-tekst.
- `prefers-reduced-motion` respekteres (5.5). Ingen autoplay.
- Fungerer fra 320 px til 1920 px uten horisontal rulling; 200 % zoom uten tap av innhold.

---

## 7. Personvern

- Inngangssiden lenker til pilotens egne personvernvilkår, «Personvern for piloten», i bunnen og
  ved siden av registreringsknappen. Lenken har minst 44 px trykkflate. URL: Avklares (A5).
- Markedssidens `/personvern` beskriver bare markedssidens skjemaer (ett felt, privat lager i
  EU/EØS, sletting senest etter tolv måneder, ingen cookies, Vercel Web Analytics) og omtaler
  piloten som en egen tjeneste med egne vilkår. Den dekker **ikke** det piloten samler inn.
- Det som ikke kan leses ut av markedssiden og derfor ikke skal antas:

| Punkt | Status |
|---|---|
| Hvilke opplysninger piloten samler inn ved registrering (navn, e-post, telefon, adresse, organisasjonsnummer, innloggingsmetode) | Avklares |
| Hvor pilotens data lagres, og om formuleringen «kryptert innenfor EU/EØS» er sann for piloten | Avklares |
| Lagringstid for konto, for ufullførte registreringer og for partner-/demohenvendelser | Avklares |
| Behandlingsansvarlig (markedssiden: ERA technologies AS, Oslo) og kontaktvei for innsyn og sletting | Avklares |
| Cookies og analyse i piloten (markedssiden setter ingen cookies; samtykkebanner unødvendig der) | Avklares |
| Hvor partner- og demohenvendelser fra piloten havner. Markedssidens `POST /api/lead` tar bare `audience`, `value`, `email?`, `intent`, `website`, `page`, merker alt `source: "era-story"` og har ingen CORS-hoder, så piloten kan ikke poste dit fra nettleseren i dag | Avklares |

Inntil disse er avklart skal inngangssiden ikke love noe om lagring. Nøytral setning som er
sann uansett: «Ingen binding. Du kan be om sletting når som helst.» bare hvis piloten faktisk
tilbyr sletting på forespørsel (A5).

---

## 8. Akseptansekriterier

Inngang og parameter

- [ ] `/register?entry=homeowner` forhåndsvelger «ERA Bolig», kortet har `aria-current="true"`, får fokus og står i viewporten.
- [ ] `/register?entry=sameie` forhåndsvelger «ERA Styret» på samme måte.
- [ ] `/register?entry=contractor` forhåndsvelger «ERA Håndverker» på samme måte.
- [ ] `/register?entry=partner` åpner partnerkontakt (ikke konto) med feltet «Kjede, produsent eller butikk».
- [ ] `/register?entry=board-demo` åpner demoskjema med feltet «Adressen til bygget» og hensikt `demo`.
- [ ] `/register` uten `entry`, og med `entry=foo`, `entry=HOMEOWNER%20`, `entry=<script>`: nøytral velger, h1 «Velg hvordan du vil bruke ERA.», ingen feil, ingen råverdi i DOM.
- [ ] `entry` står i URL-en etter `/login` → `/register` og etter bekreftelsessteget; ny konto får rollen fra `entry`; eksisterende konto beholder sin rolle.
- [ ] «Logg inn» beholder `entry` i lenken når verdien finnes.

Tilbake-lenke

- [ ] «← Tilbake til era-app.no» finnes øverst til venstre på inngang, innlogging, registrering og begge kontaktskjemaer, minst 44 × 44 px.
- [ ] Målet følger 3.1: `homeowner` → `/boligeier`, `sameie` og `board-demo` → `/styret`, `contractor` → `/handverker`, `partner` → `/faghandel`, ellers `/`.
- [ ] Åpner i samme fane.

Skjerm og betjening

- [ ] 320, 360, 390, 768, 1024, 1440 og 1920 px: ingen horisontal rulling, ingen avkuttet tekst, kortene i én kolonne under 900 px.
- [ ] Alle interaktive elementer minst 44 × 44 px; inputtekst 16 px.
- [ ] Hele siden kan betjenes med tastatur i rekkefølgen i 6.1; fokusring synlig på alle elementer; Escape lukker menyer og forslag.
- [ ] Nøyaktig én h1 per side, h2 på kortene, ingen sprang i nivå.
- [ ] Rollekort og handlinger er `<a>` eller `<button>`; skjermleser leser «ERA Bolig, Start som boligeier, lenke, gjeldende».
- [ ] `prefers-reduced-motion: reduce`: ingen overganger, ingen animert rulling, ingen skrivemaskin.
- [ ] Dekorativ grafikk har `alt=""`.

Innhold

- [ ] Produktnavn, løftelinjer, statusetiketter, feltetiketter, knappetekster, bekreftelser og feilmeldinger er ordrett som i kapittel 2 og 4.
- [ ] Ingen «Tilgjengelig nå». ERA Bolig «Kontrollert beta», ERA Styret og ERA Håndverker «I pilot», faghandel «Under utvikling».
- [ ] Ingen tall, priser, prosenter eller tidsbesparelser utover markedssidens eksempeldata; eksempeldata er merket «Eksempeldata».
- [ ] Ingen utropstegn; «»-sitattegn; tynn mellomrom i tall.

Analyse og personvern

- [ ] `era_pilot_landed` sendes med `entry`-nøkkel eller `"none"`; `era_pilot_role_selected` med `preselected`; øvrige hendelser etter 3.3; ingen personopplysninger i nyttelast.
- [ ] Lenke «Personvern for piloten» finnes på inngang og registrering.
- [ ] Ingen påstand om lagringssted før A5 er avklart.

---

## 9. Avklaringer

| # | Punkt | Hvem |
|---|---|---|
| A1 | Ny tekst som ikke finnes på markedssiden: «Har du tilgang fra før, logger du inn her.» (innlogging) og «En gjennomgang av ERA Styret med oss, før dere registrerer eiendommen.» (demo). Godkjenn eller erstatt. | ERA |
| A2 | `entry=partner` og `entry=board-demo` finnes ikke i piloten i dag. Markedssiden sender faghandel til `/faghandel#skjema` og «Book en gjennomgang» til `/styret#skjema` inntil piloten bekrefter støtte. Hvem sier fra når de kan tas i bruk? | Pilotteam |
| A3 | Pilotens analyseverktøy. Markedssiden bruker Vercel Web Analytics egendefinerte hendelser. Navnene i 3.3 gjelder uansett verktøy. | Pilotteam |
| A4 | Domene for tilbake-lenken. Markedssidens `canonical` er i dag `https://era-story.vercel.app`; denne spesifikasjonen forutsetter `https://era-app.no`. Bekreft at målgruppesidene ligger på era-app.no før lansering. | ERA |
| A5 | Personvern for piloten: hvilke data, hvor de lagres (og om «kryptert innenfor EU/EØS» er sant), lagringstid, behandlingsansvarlig, cookies og analyse, URL til vilkårene, og hvor partner-/demohenvendelser fra piloten lagres. Ikke dikt opp; hent fra pilotens faktiske oppsett. | Pilotteam + ERA |
| A6 | Styrets demo-etikett: markedssidens skjema bruker «Book en demo» som hensiktsknapp i dag, mens CTA-rutingen sier «Book en gjennomgang». Velg én etikett for begge steder. | ERA |
| A7 | Faghandelens feltetikett: `tools/build-pages.py` har i dag «Kjede eller butikk»; terminologien i denne spesifikasjonen sier «Kjede, produsent eller butikk». Oppdater generatoren eller spesifikasjonen så de er like. | ERA (markedssiden) |
| A8 | Ingen automatisk videresending forbi rollevelgeren ved gyldig `entry` (ett trykk bekrefter). Hvis pilotteamet heller vil hoppe rett til registrering, må tilbake-lenken og «velg annen rolle» finnes på registreringssteget. | Pilotteam |
| A9 | Skal piloten få en «Se produktet i bruk»-forhåndsvisning på inngangssiden (produktvindu med Borgveien 14 og chipen «Eksempeldata»)? Ikke et krav; hvis ja, bruk `product.css` uendret. | ERA |
