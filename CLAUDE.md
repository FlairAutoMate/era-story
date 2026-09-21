# Arbeidsregler for dette repoet

## Start alltid fra `origin/master`

```bash
git fetch origin && git checkout -B claude/<oppgave> origin/master
```

**Gjør dette først, hver gang, før du leser eller endrer noe.** Flere samtaler jobber i dette
repoet parallelt, og et git-arbeidstre husker sin egen branch mellom økter. Branchen du våkner på
er sannsynligvis utdatert.

Dette har allerede skjedd: 11. sept. 2026 ble en hel oppgave bygget på en branch som lå **33
commits bak master**. Det ble oppdaget ved flaks — en regenerert side fikk en gammel adresse
tilbake, og det synte i diffen. Hadde den blitt merget, ville den rullet tilbake fire merget PR-er.

Sjekk ved tvil: `git rev-list --count HEAD..origin/master` skal være `0`.

## Master går rett i produksjon

Vercel deployer `master` automatisk, ca. ett minutt etter merge. Ingen kjører `vercel --prod`.
**En merge er en publisering.** Alt som er feil på master er feil på era-app.no.

## Generert HTML skal aldri redigeres for hånd

| Fil | Bygges av |
| --- | --- |
| `boligeier/`, `styret/`, `handverker/`, `faghandel/`, `personvern/` | `python tools/build-pages.py` |
| `om-era/` | `python tools/build-om-era.py` (henter hodet fra `index.html`) |
| `partner/jotun/`, `investor/` | `python tools/build-partner-story.py` |

Endrer du `index.html`s hode eller meny, må `build-om-era.py` kjøres etterpå — ellers henger
`/om-era` igjen med den gamle versjonen.

`tools/rebase-deltas.py` er **arkivert** og skal ikke kjøres. Se README, «Oppdatere fra en ny
designeksport», for hvorfor og hva som gjelder i stedet.

## Sjekker før du er ferdig

```bash
python tools/check-demo-home.py
```

Obligatorisk etter endringer som berører `/boligeier`. Den fanger sprik i demoboligens data
(Myrerveien 46A), men **kan ikke se inn i en PNG** — grønn sjekk betyr at teksten stemmer, ikke at
skjermbildene er riktige.

`node qa-responsive.mjs http://localhost:8787 chromium all` for responsivitet og trykkflater.
Husregelen er 44 px; WCAG 2.5.8 (AA) krever 24 px.

## Påstandsdisiplin

Ingen oppdiktede tall, prosenter eller tidsbesparelser. Beskriv mekanismen i stedet. Funksjoner som
ikke er dokumentert tilgjengelige merkes «Planlagt» eller «I pilot».

**Ingen prosentsats ved siden av en motparts navn** på `/investor` og `/partner/*`. Sidene er
`noindex`, men de er åpne URL-er som blir videresendt — en sats knyttet til et navn er publisert før
motparten har sagt ja. Navnet hører hjemme i en statusliste, ikke i en betingelse.
