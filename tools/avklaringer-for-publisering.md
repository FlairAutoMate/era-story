# Avklaringer før publisering

Sjekkliste for produktoppdateringen av era-app.no (10. september 2026). Hvert punkt er noe
nettsiden **påstår i dag**, som ingen i arbeidet kunne verifisere ut fra kildene i dette repoet.
Ingenting her er en feil i koden — det er påstander som må bekreftes av et menneske før lansering.

Kolonnen **Eier**: `produkt` = ERA produkt/ledelse, `juridisk` = personvern og avtaler,
`teknisk` = pilotteamet på pilot.era-app.no (eget kodebase, se `tools/pilot-entry-spec.md`).

Rekkefølge: 1 statusmatrisen (styrer alt annet), 2 pilotinngangen, 3 personvern, 4 per side.

---

## 1. Statusmatrisen

Alle statusetikettene på tvers av sidene kommer herfra. Endres én av dem, må den endres alle
steder — de er gjentatt i produktvinduer, legender og arkitekturdiagrammet.

| Det som står | Hvor | Eier | Trygg reserve |
|---|---|---|---|
| **ERA Bolig · «Kontrollert beta»** — åpen for 300 boligeiere, gratis i betaperioden, uten betalingskort og uten binding | Forsiden `#hva`, /boligeier (hero, beta-seksjon, avslutning), /om-era `#arkitektur` | produkt | «I pilot» hvis de 300 plassene eller gratisperioden ikke er vedtatt |
| **ERA Styret · «I pilot»** | Forsiden `#hva`, /styret, /om-era | produkt | «Under utvikling» |
| **ERA Håndverker · «I pilot»** | Forsiden `#hva`, /handverker, /om-era | produkt | «Under utvikling» |
| **Faghandelsdashbordene · «Under utvikling»** (sentralt dashboard og forhandlerdashboard) | /faghandel `#dashboard` | produkt | Behold — dette er den mest forsiktige etiketten som finnes |
| **Betaling i ERA · «I pilot»** — inkludert fakturagrunnlag og utbetaling | Forsiden `#hva`, /boligeier, /handverker, /om-era | produkt | «Planlagt» |
| **Energi og forbedringer · «Planlagt»** (etterisolering, varmepumpe) | Forsiden (detaljpanelet «Se planen»), /boligeier | produkt | Behold |
| **Tilbudssammenligning og beboervarsling · «Illustrasjon av arbeidsflyt»** | Forsiden `#hva`, /styret | produkt | Behold |

**«Tilgjengelig nå» brukes ikke noe sted.** Det er et bevisst valg: ingenting på siden påstår å
være allment tilgjengelig i dag. Skal noe få den etiketten, må det avklares eksplisitt.

---

## 2. Pilotinngangen (pilot.era-app.no)

Piloten ligger **ikke** i dette repoet. Full spesifikasjon: `tools/pilot-entry-spec.md` (kapittel 9
der har de tekniske detaljene). Det som blokkerer publisering av markedssiden:

| # | Punkt | Eier | Status i dag |
|---|---|---|---|
| P1 | `entry=partner` og `entry=board-demo` finnes ikke i piloten. Markedssiden ruter derfor «Utforsk partnerskap med ERA» til `/faghandel#skjema` og «Book en gjennomgang» til `/styret#skjema`. Når piloten støtter verdiene, byttes de to CTA-ene til pilotlenker. | teknisk | Håndtert med egne skjemaer, ingen død lenke |
| P2 | Piloten må tåle ukjent eller manglende `entry` (nøytral rollevelger, aldri feil) fra dag én. | teknisk | Uavklart |
| P3 | De tre lenkene som er i bruk — `?entry=homeowner`, `?entry=sameie`, `?entry=contractor` — må faktisk lande på riktig registrering. **Testes mot piloten før lansering.** | teknisk | Uavklart |
| P4 | `SITE` i `tools/build-pages.py` er `https://era-story.vercel.app`. Pilotens «Tilbake til era-app.no» forutsetter at målgruppesidene ligger på `era-app.no`. | produkt | Uavklart |
| P5 | Markedssiden sender ingen analysehendelse når en pilot-CTA klikkes. Foreslått: `eraTrack('era_pilot_cta_clicked', { entry })`. | teknisk | Ikke implementert (bevisst — navnene må stemme med pilotens) |

---

## 3. Personvern

`/personvern` er skrevet om fordi den motsa seg selv: den sa at opplysningene brukes «til å ta
kontakt», samtidig som den sa at verken navn, e-post eller telefon samles inn.

| # | Det som står nå | Eier | Merknad |
|---|---|---|---|
| J1 | Formålet er omskrevet: innsendingen registrerer interesse for en adresse, eiendom eller virksomhet og hjelper ERA å prioritere hvor tjenesten åpnes. Kontakt kan bare tas der det finnes en offentlig eller registrert kontaktvei, eller hvis avsenderen selv tar kontakt. | juridisk | **Må leses av noen med juridisk ansvar.** Dette er den eneste formuleringen som er sann gitt at skjemaet ikke har kontaktfelt |
| J2 | «hos vår driftsleverandør Vercel, i et privat lager innenfor EU/EØS (Frankfurt)» — står **bare** på /personvern | juridisk | Alle andre sider sier kun «kryptert innenfor EU/EØS». Bekreft at Frankfurt fortsatt stemmer |
| J3 | Ny seksjon «Registrering i ERA-piloten»: piloten er en egen tjeneste med egne personvernvilkår, og denne siden dekker den ikke | juridisk | **Mangler lenke.** Se `<!-- AVKLAR: lenke til pilotens personvernerklæring -->` i `privacy_page()` i `tools/build-pages.py` |
| J4 | «Vi sletter innsendingen senest tolv måneder etter at den kom inn» | juridisk | Uendret fra før, men bekreft at rutinen finnes |
| J5 | Hvilke data piloten samler inn, hvor de lagres og hvor lenge | juridisk + teknisk | Ikke beskrevet noe sted. Ikke dikt opp — hent fra pilotens faktiske oppsett |

---

## 4. Per side: funksjoner som er navngitt uten å være dokumentert tilgjengelige

Alle punktene under står i et produktvindu merket «Eksempeldata», og de fleste ligger under en
statusetikett. Listen finnes for at produkt skal kunne si «ja, dette gjør vi» eller «nei, ta det ut».

### Forsiden (`#hva`)

| Det som står | Eier | Trygg reserve |
|---|---|---|
| ERA Bolig-vinduet: «Stue · Vegg slitt, ingen skader» merket **Dokumentert** | produkt | Merk «Fra kunden», eller ta raden ut |
| ERA Bolig-vinduet: «Fasade · Maling flasser» merket **Felles** (ansvarsmerke, ikke kildemerke) | produkt | Bekreft at «Felles» kan stå ved siden av kildemerkene, ellers bruk «Dokumentert» |
| ERA Håndverker-vinduet: «Tilbudsutkast · Sendes når du har godkjent» | produkt | Bekreft at ERA lager et tilbudsutkast håndverkeren godkjenner |
| ERA Håndverker-vinduet: «Fakturagrunnlag · Godkjent tilbud, endringsordre og overlevering» | produkt | Merket «I pilot». Bekreft at grunnlaget faktisk bygges slik |

### /boligeier

| Det som står | Eier | Trygg reserve |
|---|---|---|
| «Bilder og dokumenter analyseres og kan knyttes til riktig rom og bygningsdel» | produkt | «Bilder og dokumenter kan legges inn og knyttes til rom og bygningsdel» |
| «Påminnelsene følger vedlikeholdsplanen og sesongen» — sesongbaserte påminnelser | produkt | Fjern «og sesongen» |
| «Felles tiltak kommer fra borettslagets plan i ERA Styret» — krever at koblingen finnes | produkt | Fjern raden til koblingen er live |
| Vedlikeholdsindeksen «67 av 100» og fordelingen 2 / 4 / 8 / 1 | produkt | Behold som eksempeldata; bekreft at en indeks faktisk beregnes |
| KPI «Dokumenter · 16» (1 tilstandsrapport + 3 FDV + 12 kvitteringer) | produkt | Regnestykket er internt konsistent; bekreft at telleren finnes |

### /styret

| Det som står | Eier | Trygg reserve |
|---|---|---|
| «Sist utført: Malt 2012» og tilbudet «Tilbyder B · 1,18 mill» | produkt | Nye faktapåstander om eksempeleiendommen. Enten tas de inn i det delte eksempeldatasettet, eller de erstattes med verdier som allerede er avtalt |
| «Kostnad per seksjon» og «Likviditetsbehov 2027» merket ERA-forslag | produkt | Bekreft at ERA regner per seksjon |
| Beslutningsgrunnlag til styremøtet, vedtak og ansvar | produkt | Merket «I pilot» |

### /handverker

| Det som står | Eier | Trygg reserve |
|---|---|---|
| Kalkylens rader «Innkjøpspris», «Påslag», «Margin» (uten tall — «fra prisliste», «ditt påslag», «beregnes») | produkt | Formuleringen er bevisst tallfri. Bekreft at kalkylen har disse feltene |
| «Samsvarsdokumentasjon» i dokumentasjonssteget | produkt | Ta ut hvis ERA ikke håndterer samsvarserklæringer |
| «Automatisk oppdatering av boligens historikk» | produkt | «Dokumentasjonen føres tilbake til boligens historikk» |

### /faghandel

| Det som står | Eier | Trygg reserve |
|---|---|---|
| Hele det sentrale dashbordet og forhandlerdashbordet | produkt | Merket **Under utvikling**. Bekreft at dette er retningen, ikke bare en idé |
| «Avvik mellom anbefalt og kjøpt produkt», «Kampanjeeffekt», «Forhandlerprestasjon», «Konvertering» — vist som etiketter uten tall | produkt | Merket «Under utvikling» |
| Ny h2 «Mengden, leveringen og bestillingen. Og det som kommer neste år.» | produkt | Erstattet en overskrift som var ordrett lik sidens H1. Bekreft stemmen |

### /om-era

| Det som står | Eier | Trygg reserve |
|---|---|---|
| «Dokumentasjon og FDV» og «Bildeanalyse» i arkitekturdiagrammet, merket **Kontrollert beta** | produkt | De er merket fordi de listes som ERA Bolig-funksjoner. Bekreft at de hører til betaen |
| «Boligdata og historikk lagres én gang i eiendomsmodellen … i stedet for å kopiere informasjon mellom separate siloer» | teknisk | Bekreft at arkitekturen faktisk er slik |
| «Privat boliginformasjon deles ikke automatisk med styret eller håndverkeren» | teknisk + juridisk | **Viktig påstand.** Bekreft at tilgangsstyringen fungerer slik i dag |

---

## 5. Endringer i eksisterende innhold som bør godkjennes

Dette er tekst og design som fantes fra før, og som er endret i denne runden.

| Endring | Hvorfor | Eier |
|---|---|---|
| Forsiden: «Vedtaket tar ti minutter, ikke to møter.» → «Styret vedtar på ett samlet grunnlag, ikke på tre ulike beskrivelser.» | Den gamle setningen var en udokumentert tidsbesparelse, som resten av oppdateringen eksplisitt avviser | produkt |
| Forsiden: «1,2 millioner» → «1,0–1,3 mill» | Samme fasadeprosjekt hadde to ulike tall på samme side etter at produktvinduet kom inn | produkt |
| Småtekstfargen `#8A8579` → `#6E6A5E` (og statusbrikkenes tekst mørknet) | Målt kontrast var 3,07–3,68:1 mot WCAG AA-kravet 4,5:1. Ny farge måler 4,51–5,40:1 på alle flatene våre | produkt (design) |
| Hero-tekstspalten vokser til 960 px på skjermer over 1440 px | Ellers ble målet smalere enn ordet «vedlikeholdsbehov», som da brakk midt i ordet på /styret | produkt (design) |
| Menyetiketten «Historien» → «Hva ERA gjør» på alle sider | Samme lenke het to forskjellige ting | produkt |
| Nav-knappen på /styret: «Registrer sameie» → «Registrer eiendom» | Den gamle utelot borettslag, som er den vanligste formen | produkt |
| /personvern sin nav-knapp: «Hva ERA gjør» → «Til forsiden» | Siden hadde to identiske lenker ved siden av hverandre | produkt |
| /boligeier har ikke lenger et kontaktskjema | All CTA går til pilotregistreringen. Betyr at siden ikke lenger samler leads | produkt |
| /faghandel har ikke lenger «Gevinsten» | Den nye «Verdi»-seksjonen dekker det samme; oppdraget forbyr å gjenta samme forklaring | produkt |

---

## 6. Kjente, aksepterte svakheter

Ikke feil som stopper publisering, men som bør stå oppført.

- **Fire 404-er på forsiden i utviklingsmodus**: `image-slot`-elementene for rørlegger, elektriker,
  hele boligen og årstidsbildene har `src="{{ … }}"` i markupen, så nettleseren ber om en bokstavelig
  `{{ }}`-URL før skriptet fyller inn verdien. Forsvinner når fotoene foreligger og `src` settes fast.
- **`/_vercel/insights/script.js` gir 404 lokalt.** Den finnes bare på Vercel. Ikke en feil.
- **Menypunktet «Partnere» (Jotun) vises på forsiden og /om-era, men ikke på undersidene.** Det er
  bevisst: lenken filtreres bort på `era-app.no`, så menyen er lik i produksjon. På
  forhåndsvisningsdomenet er den ikke det.
- **Detaljknappene i historien** («Se planen», «Se produktvalg», «Se dokumentasjonen») var 42 px
  høye og er hevet til 44 px i denne runden.
