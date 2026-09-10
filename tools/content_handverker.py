# -*- coding: utf-8 -*-
"""Product content for /handverker (ERA Håndverker). Called by tools/build-pages.py as render(H, a)
and inserted between the hero and the scenes section (id="prosjekt"). H is the helpers namespace
(see its docstring in build-pages.py); a is the audience dict.

Sections, in order:
  #produktet  eyebrow ERA Håndverker · one dashboard window «Malermester Berg AS · innboks» with
              seven status widgets (innboks, tilbud, avtaler, prosjekter, endringer, dokumentasjon,
              faktura/utbetaling).
  #flyt       the ten-step job flow (H.flow chain + one window with ten tabs, «Male stue ·
              Borgveien 14»). The hero's secondary link points here.
  #verdi      six result cards (title + mechanism, no numbers).
  #roller     six roles inside the contractor company + the page CTAs.

Status: ERA Håndverker is «I pilot» (rolled out area by area); «Betaling i ERA» incl. utbetaling
and fakturagrunnlag is «I pilot». Example data is the shared Borgveien 14 set; every window carries
the «Eksempeldata» chip. No numbers beyond the example data."""

PRO_URL = "https://pilot.era-app.no/register?entry=contractor"

STEPS = [
    ("innboks", "Innboks", "Innboks"),
    ("befaring", "Befaring", "befaring"),
    ("kalkyle", "Kalkyle", "kalkyle"),
    ("tilbud", "Tilbud", "tilbud"),
    ("kontrakt", "Kontrakt", "kontrakt"),
    ("planlegging", "Planlegging", "planlegging"),
    ("gjennomforing", "Gjennomføring", "gjennomføring"),
    ("endringer", "Endringer", "endringer"),
    ("dokumentasjon", "Dokumentasjon", "dokumentasjon"),
    ("fakturering", "Fakturering", "fakturering og utbetaling"),
]


def _step_nav(H, i):
    """Prev/next buttons inside a panel; pages.js moves the tablist via data-dir."""
    prev = (f'<button type="button" class="pw-cta pw-cta--ghost" data-dir="-1">← {H.esc(STEPS[i - 1][1])}</button>'
            if i > 0 else "")
    nxt = (f'<button type="button" class="pw-cta pw-cta--ghost" data-dir="1">Neste: {H.esc(STEPS[i + 1][1])} →</button>'
           if i < len(STEPS) - 1 else "")
    if not (prev or nxt):
        return ""
    return f'<div class="pw-cta-row">{prev}{nxt}</div>'


def render(H, a):
    parts = []
    primary_label, primary_href = a.get("cta_primary", ("Start som håndverker", PRO_URL))
    secondary_label, secondary_href = a.get("cta_secondary", ("Se hvordan en jobb flyter gjennom ERA", "#flyt"))

    # ---- 1. Produktet: håndverkerdashboardet (innboks) ----
    innboks = H.widget(
        "Nye kvalifiserte forespørsler",
        H.kpi("Til vurdering", "3", "med adresse, bilder, mål og ønsket tid", "mono")
        + H.rows([
            ("Male stue, 42 m²", "Borgveien 14 · uke 38–40", "customer"),
            ("Fasade, sør- og vestvegg", "Borgveien 14 · felles", "board"),
            ("Tak, 1 strøk", "Tillegg til Male stue", "customer"),
        ]),
        wide=True,
    )
    tilbud = H.widget(
        "Tilbud som venter",
        H.kpi("Utkast", "1", "bygget av kalkylen", "mono")
        + H.rows([
            ("Male stue", "Utkast", "wait", "Utkast"),
            ("Kundens estimat", "ca. 6 800 kr"),
            ("Sendes", "Når du har godkjent det"),
        ]),
    )
    avtaler = H.widget(
        "Avtaler som skal signeres",
        H.kpi("Til signering", "1", "digital aksept", "mono")
        + H.rows([
            ("Male stue", "Digital aksept", "wait", "Venter"),
            ("Oppstart", "Uke 38"),
            ("Omfang", "Vegger, 2 strøk · 42 m²"),
        ]),
    )
    prosjekter = H.widget(
        "Prosjekter i arbeid",
        H.kpi("Pågår", "1", "Fasade 2027 · Borgveien 14", "good")
        + H.progress(33, "good")
        + H.rows([
            ("Fremdrift", "Uke 2 av 6", "ok", "I rute"),
            ("Stillas", "Inngang B · uke 20–25"),
            ("Avklaring", "Farge på beslag, svar innen fredag"),
        ]),
    )
    endringer = H.widget(
        "Endringer som krever godkjenning",
        H.kpi("Venter godkjenning", "1", "sendt til kunden", "accent")
        + H.rows([
            ("Male stue", "Tak, 1 strøk", "wait", "Venter"),
            ("Pris og tid", "+ca. 1 800 kr · +1 dag"),
            ("Godkjennes", "Av kunden, før arbeidet starter"),
        ]),
    )
    dokumentasjon = H.widget(
        "Dokumentasjon som mangler",
        H.kpi("Mangler", "2", "etterbilder tak", "warn")
        + H.rows([
            ("Etterbilder tak", "0 av 2", "warn", "Mangler"),
            ("Vegger, før og etter", "6 bilder", "ok", "Komplett"),
        ]),
    )
    faktura = H.widget(
        "Faktura eller utbetaling som venter",
        H.kpi("Venter", "1", "avtalt beløp", "mono")
        + H.rows([
            ("Male stue", "Avtalt beløp", "pilot"),
            ("Fakturagrunnlag", "Fra arbeidsgrunnlaget"),
            ("Utbetaling", "Status vises på jobben"),
        ]),
    )
    dashboard = H.window(
        "ERA Håndverker", "Malermester Berg AS · innboks",
        body_html=H.dashboard([innboks, tilbud, avtaler, prosjekter, endringer, dokumentasjon, faktura]),
        foot="Eksempeldata. Samme malejobb vises i flere steg, slik at hvert felt i innboksen får et eksempel.",
    )
    legend = H.legend([
        ("pilot", "ERA Håndverker rulles ut område for område"),
        ("pilot", "betaling i ERA, med fakturagrunnlag og utbetaling"),
    ])
    parts.append(H.section(
        legend + dashboard, id="produktet", wide=True,
        eyebrow="ERA Håndverker", title="Fra kvalifisert forespørsel til dokumentert og betalt jobb.",
        lede="ERA Håndverker gir deg et komplett arbeidsgrunnlag og én sammenhengende flyt for befaring, kalkyle, tilbud, kontrakt, gjennomføring, dokumentasjon og betaling.",
    ))

    # ---- 2. Hele flyten: ti steg, én jobb ----
    p_innboks = (
        H.panel_lead("Du starter ikke med «Hva koster det å pusse opp?». Du starter med et behov som allerede er strukturert.")
        + H.grid([
            H.widget("Forespørsel", H.rows([
                ("Adresse", "Borgveien 14"),
                ("Fagområde", "Maler"),
                ("Beskrivelse", "«Vi vil male stua»"),
                ("Ønsket tidspunkt", "Uke 38–40"),
                ("Bilder", "4"),
                ("Kunden ønsker", "Direkte tilbud", "customer"),
            ])),
            H.widget("Fra boligen", H.rows([
                ("Mål", "ca. 42 m²", "ai"),
                ("Bolighistorikk", "Stue: vegg slitt, ingen skader (2021)", "doc"),
                ("Materialbehov", "2 × 10 L maling, 1 × 5 kg sparkel", "ai"),
            ])),
        ])
    )
    p_befaring = (
        H.panel_lead("Mål, bilder og bolighistorikk ligger i forespørselen, så du avgjør om befaring trengs. Notatene legges rett på saken.")
        + H.widget("Befaringsnotat · Borgveien 14", H.kpis([
            ("Mål", "42 m²", "bekreftet på befaring", "mono"),
            ("Forbehandling", "Lett sparkling"),
            ("Bilder", "4 → 6", "2 nye fra befaringen", "mono"),
            ("Farge", "Sjøgrønn 0398", "fra kunden"),
        ]))
    )
    p_kalkyle = (
        H.panel_lead("Mengder og materialer fra forespørselen ligger allerede i kalkylen. Du justerer timer, priser, påslag og forbehold.")
        + H.grid([
            H.widget("Kalkyle · Male stue", H.rows([
                ("Timer og roller", "Maler 12 t", "ai"),
                ("Materialer og mengder", "2 × 10 L, 1 × 5 kg", "ai"),
                ("Innkjøpspris", "Fra din prisliste"),
                ("Påslag", "Din sats"),
                ("Margin", "Beregnes"),
            ]) + H.note("Forslagene kommer fra arbeidsgrunnlaget. Du justerer før tilbudet bygges.")),
            H.widget("Til tilbudet", H.rows([
                ("Forbehold", "Tilkomst · fra befaringen"),
                ("Alternativer", "1 eller 2 strøk"),
                ("Tilvalg", "Tak, 1 strøk"),
            ])),
        ])
    )
    p_tilbud = (
        H.panel_lead("Gjenbruk informasjonen fra forespørselen i kalkylen og tilbudet. Mindre dobbeltarbeid og raskere svar til kunden.")
        + H.kpis([
            ("Pris", "ca. 6 800 kr", "materialer ca. 1 900 kr", "accent"),
            ("Oppstart", "Uke 38", "innenfor ønsket uke 38–40"),
            ("Forbehold", "Tilkomst"),
            ("Tilvalg", "Tak, 1 strøk", "+ca. 1 800 kr"),
        ])
        + H.grid([
            H.widget("Tilbud · Male stue", H.rows([
                ("Status", "Generert fra arbeidsgrunnlaget", "wait", "Utkast"),
                ("Bygget av", "Kalkylen og befaringsnotatet"),
                ("Sendes", "Når du har godkjent det"),
            ])),
            H.widget("Tilbudet inneholder", H.checklist([
                "Omfang: vegger, 2 strøk, lett sparkling",
                "Pris, materialer og fremdrift",
                "Forbehold og alternativer",
                "Tilvalg: tak, 1 strøk",
            ])),
        ])
    )
    p_kontrakt = (
        H.panel_lead("Kunden aksepterer digitalt. Oppgaver, ansvar og milepæler er avtalt før oppstart.")
        + H.grid([
            H.widget("Kontrakt · Male stue", H.rows([
                ("Digital aksept", "Kunden godkjenner i ERA Bolig", "wait", "Venter"),
                ("Grunnlag", "Tilbud, kalkyle og arbeidsgrunnlag"),
                ("Oppgaver og ansvar", "Fordelt mellom deg og kunden"),
            ])),
            H.widget("Milepæler", H.timeline([
                ("Uke 38", "Oppstart", "Avtalt med kunden", "next"),
                ("Uke 38", "Vegger, 2 strøk", "1–2 dager", "later"),
                ("Uke 38", "Overlevering", "Bilder, produkter og dokumentasjon", "later"),
            ])),
        ])
    )
    p_planlegging = (
        H.panel_lead("Materialer bestilles fra samme grunnlag, og oppstarten legges i planen.")
        + H.grid([
            H.widget("Materialbestilling", H.rows([
                ("Maling", "2 × 10 L · Sjøgrønn 0398"),
                ("Sparkel", "1 × 5 kg"),
                ("Ruller og pensler", "2 ruller, 3 pensler"),
                ("Maskering", "2 ruller"),
                ("Levering", "Håndverker henter", "order"),
            ])),
            H.widget("Plan", H.rows([
                ("Oppstart", "Uke 38"),
                ("Varighet", "1–2 dager"),
                ("Kundens ønske", "Uke 38–40", "customer"),
            ])),
        ])
    )
    p_gjennomforing = (
        H.panel_lead("Bilder, sjekkliste og kundedialog ligger på jobben mens du utfører den.")
        + H.grid([
            H.widget("Sjekkliste", H.rows([
                ("Lett sparkling", "Utført", "ok", "Utført"),
                ("Strøk 1", "Utført", "ok", "Utført"),
                ("Strøk 2", "I dag", "wait", "Pågår"),
                ("Bilder underveis", "Legges til fra telefonen"),
            ])),
            H.widget("Kundedialog", H.msgs([
                ("Kan dere også male taket?", "Kunden"),
                ("Ja. Jeg sender en endringsordre med pris og tid.", "Deg", True),
            ])),
        ])
    )
    p_endringer = (
        H.panel_lead("Endringen beskrives med pris og konsekvens for fremdriften, og kunden godkjenner før arbeidet starter.")
        + H.grid([
            H.widget("Endringsordre · tak, 1 strøk", H.rows([
                ("Pris", "+ca. 1 800 kr"),
                ("Fremdrift", "+1 dag"),
                ("Status", "Godkjent av kunden", "ok", "Godkjent"),
            ]) + H.note("Fra «Venter godkjenning» til «Godkjent». Arbeidsgrunnlaget oppdateres med tillegget.")),
            H.widget("Avvik", H.rows([
                ("Meldes", "Med bilde og beskrivelse, på jobben"),
                ("Kunden ser", "Foreslått og godkjent, hver for seg"),
            ])),
        ])
    )
    p_dokumentasjon = (
        H.panel_lead("Overleveringen bygges mens du jobber. Når jobben er ferdig, er dokumentasjonen det også.")
        + H.kpis([
            ("Bilder", "6", "før og etter", "mono"),
            ("Utførte oppgaver", "Vegger og tak, 2 strøk"),
            ("Produkter", "Maling, sparkel, ruller"),
            ("Status", "Overlevert", None, "good"),
        ])
        + H.rows([
            ("FDV", "Maling, dokumentert"),
            ("Garantier og samsvar", "Legges ved jobben"),
            ("Kostnader", "Avtalt beløp og godkjent endringsordre"),
            ("Boligens historikk", "Oppdateres automatisk, med ditt navn på"),
        ], group_tag="doc")
    )
    p_fakturering = (
        H.panel_lead("Fakturagrunnlaget bygges fra arbeidsgrunnlaget, og betalingsstatus vises på jobben.")
        + H.rows([
            ("Fakturagrunnlag", "Avtalt beløp og godkjent endringsordre"),
            ("Utbetaling", "Status vises på jobben"),
            ("Regnskap", "Grunnlaget kan hentes ut"),
        ], group_tag="pilot")
        + H.note("Betaling i ERA, med fakturagrunnlag og utbetaling, er i pilot.")
    )
    panels = [p_innboks, p_befaring, p_kalkyle, p_tilbud, p_kontrakt, p_planlegging, p_gjennomforing, p_endringer, p_dokumentasjon, p_fakturering]
    tabs = [(tid, label, panel + _step_nav(H, i)) for i, ((tid, label, _f), panel) in enumerate(zip(STEPS, panels))]
    flow = H.flow([f for _t, _l, f in STEPS], active=0)
    flow_window = H.window(
        "ERA Håndverker", "Male stue · Borgveien 14",
        tabs=tabs,
        dense=True,  # ten numbered tabs: ≤560px only the numbers show and each panel names its step
        equalize=False,  # ten panels of very different height; the tab strip sits above, so nothing shifts
        foot="Eksempeldata. «Male stue, 42 m²» på Borgveien 14 fulgt gjennom alle ti stegene.",
    )
    parts.append(H.section(
        flow + flow_window, id="flyt", alt=True, wide=True,
        eyebrow="Hele flyten", title="Én jobb. Ti steg. Samme grunnlag hele veien.",
        lede="Følg «Male stue, 42 m²» fra forespørsel til utbetaling. Hvert steg bygger på det forrige.",
    ))

    # ---- 3. Konkret verdi ----
    results = H.results([
        ("Færre tomme og useriøse forespørsler", "Forespørselen kommer med adresse, bilder, mål og ønsket tid – og fra en boligeier som allerede har fått et estimat."),
        ("Færre unødvendige befaringer", "Mål, bilder og bolighistorikk ligger i forespørselen, så du kan vurdere om befaring trengs før du kjører."),
        ("Raskere kalkulasjon", "Mengder og materialer fra kundens plan går rett inn i kalkylen. Du justerer, du starter ikke fra null."),
        ("Raskere tilbud til kunden", "Tilbudet bygges av kalkylen og arbeidsgrunnlaget, og sendes når du har godkjent det."),
        ("Bedre kontroll på materialer og margin", "Innkjøp, påslag, tilvalg og endringer ligger i samme sak som tilbudet."),
        ("Raskere dokumentasjon, fakturering og betaling", "Bilder, produkter og utførte oppgaver samles underveis; fakturagrunnlaget og boligens historikk oppdateres fra samme sak. Betaling i ERA:", "pilot"),
    ], cols=3)  # six cards as 3 × 2 in the normal wrap
    parts.append(H.section(
        results, id="verdi",
        eyebrow="Konkret verdi", title="Hva du sparer, og hvorfor.",
        lede="Ingen prosenter. Bare det som gjenbrukes, og det du slipper å gjøre på nytt.",
    ))

    # ---- 4. Roller i bedriften + CTA ----
    roles = H.roles([
        ("Daglig leder", "Pipeline, kapasitet, omsetning og lønnsomhet."),
        ("Kalkulatør", "Arbeidsgrunnlag, kalkyle og tilbud."),
        ("Prosjektleder", "Fremdrift, ansvar, endringer og avvik."),
        ("Utførende", "Oppgaver, bilder, sjekklister og dokumentasjon."),
        ("Kundeansvarlig", "Dialog, godkjenninger og status."),
        ("Regnskap", "Fakturagrunnlag og betalingsstatus."),
    ], cols=3)  # 3 × 2 like #verdi
    roles_legend = H.legend([("pilot", "fakturagrunnlag og betalingsstatus")])
    ctas = H.cta_row([
        H.cta(primary_label, primary_href, "gold"),
        H.cta(secondary_label, secondary_href, "ghost"),
    ])
    parts.append(H.section(
        roles + roles_legend + ctas, id="roller", alt=True,
        eyebrow="I bedriften din", title="Hva hver i bedriften får.",
        lede="Én sak, flere innganger. Alle jobber i samme arbeidsgrunnlag.",
    ))

    return "".join(parts)
