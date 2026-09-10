# -*- coding: utf-8 -*-
"""Product content for /faghandel (ERA for faghandel). Called by tools/build-pages.py as render(H, a)
and inserted between the hero and the scenes section (#slik). H is the helpers namespace (see its
docstring in build-pages.py); a is the audience dict. Sections: #produktet (what the faghandel surface
is, where it enters the ERA flow), #dashboard (one window, two tabs: sentralt dashboard for the chain
and forhandlerdashboard for the single store) and #verdi (value for faghandelen and for the customer,
plus the page's two CTAs). Faghandel is not a fourth app: «ERA for faghandel» is an integrated
handels- og distribusjonsflate; both dashboards are «Under utvikling». Example data is the shared
Borgveien 14 set (Male stue 42 m², 2 × 10 L, fasade 2027 …); the window carries the «Eksempeldata»
chip and everything without example data stays a label with a «Under utvikling» tag.

The hero's secondary link points to #dashboard, so that id must stay on the window section."""

FLOW = ["Forstå", "prioritere", "planlegge", "bestille", "gjennomføre", "dokumentere"]


def render(H, a):
    parts = []
    primary_label, primary_href = a["cta_primary"]
    secondary_label, secondary_href = a["cta_secondary"]

    # ---- 1. Produktet: hva flaten er, og hvor den kommer inn i flyten ----
    line = ('<p class="steps-intro">'
            + H.esc("Faghandel er ikke en egen app, men en integrert handels- og distribusjonsflate i ERA-systemet.")
            + '</p>')
    legend = H.legend([("dev", "kjede- og forhandlerdashboard")])
    flow = H.flow(FLOW, active="bestille")
    flow_note = H.note("Faghandelen møter kunden ved «bestille». Behov, produkter og mengder er beregnet i planen før det.")
    parts.append(H.section(
        line + legend + flow + flow_note, id="produktet",
        eyebrow="ERA for faghandel", title="Fra boligbehov til riktig produkt i riktig butikk.",
        lede="ERA beregner behov, produkter og mengder før kunden går i butikken. Kunden kan velge levering, klikk og hent eller at håndverkeren henter materialene.",
    ))

    # ---- 2. Dashboard: ett vindu, to nivåer ----
    sentralt = (
        H.note("For kjede, produsent eller sentral markedsorganisasjon.")
        + H.kpis([
            ("Fasadeprosjekter", "3", "neste 12 mnd", "mono"),
            ("Borettslag", "1", "24 seksjoner", "mono"),
            ("Neste store tiltak", "Fasade 2027", "1,0–1,3 mill"),
            ("Produktkategorier", "5", "fra vedlikeholdsplanene", "mono"),
        ])
        # Widget order and the two wide widgets are chosen so the grid fills 4, 3 and 2 columns
        # without holes (12 cells: 8 single + 2 wide). Wide ones lead their row.
        + H.dashboard([
            H.widget("Produktkategorier", H.flow(["Maling", "Grunning", "Sparkel", "Stillas", "Tettemidler"], arrows=False)
                     + H.rows([
                         ("Maling, grunning, stillas", "Fasade 2027 · sør- og vestvegg", "ai"),
                         ("Tettemidler", "Vinduer · tetningslister, høst 2026", "ai"),
                         ("Sparkel", "Male stue, 42 m²"),
                     ]), wide=True),
            H.widget("Etterspørsel per geografi", H.rows([
                ("Neste 12 mnd", "3 fasadeprosjekter"),
                ("Borettslag", "1 · 24 seksjoner"),
                ("Per område", "Kommune og bydel", "dev"),
            ])),
            H.widget("Kommende vedlikeholdsbehov", H.timeline([
                ("2027", "Fasade", "Male sør- og vestvegg · 1,0–1,3 mill", "next"),
                ("2031", "Tak", "Egen oppgave i totalplanen", "later"),
            ])),
            H.widget("Fremtidige volumprognoser", H.rows([
                ("Fasade 2027", "Maling og stillas", "ai"),
                ("Tak 2031", "Egen oppgave i totalplanen"),
            ])),
            H.widget("Sesong og vær", H.rows([
                ("Utendørs maling", "Mai–september"),
                ("Fasade 2027", "Ønsket tid mai–juni"),
            ])),
            H.widget("Avvik mellom anbefalt og kjøpt produkt", H.rows([
                ("Male stue", "Anbefalt 2 × 10 L · kjøpt 2 × 10 L", "ok", "Ingen avvik"),
            ]), wide=True),
            # The four metrics that exist only as labels: four tiles ≥900px, one condensed wide
            # widget below (keeps the mobile panel shorter without dropping the information).
            H.widget("Beregnet salgsverdi", H.rows([
                ("Grunnlag", "Beregnes fra vedlikeholdsplaner", "dev"),
            ]), cls="pw-desk"),
            H.widget("Konvertering", H.rows([
                ("Anbefalt → kjøpt", "Fra ERA-forslag til bestilling", "dev"),
            ]), cls="pw-desk"),
            H.widget("Kampanjeeffekt", H.rows([
                ("Måles mot", "Beregnet behov", "dev"),
            ]), cls="pw-desk"),
            H.widget("Forhandlerprestasjon", H.rows([
                ("Per forhandler", "Levering og avvik", "dev"),
            ]), cls="pw-desk"),
            H.widget("Måltall under utvikling", H.rows([
                ("Beregnet salgsverdi", "Beregnes fra vedlikeholdsplaner", "dev"),
                ("Konvertering", "Anbefalt → kjøpt", "dev"),
                ("Kampanjeeffekt", "Måles mot beregnet behov", "dev"),
                ("Forhandlerprestasjon", "Levering og avvik", "dev"),
            ]), cls="pw-mob", wide=True),
        ])
    )

    forhandler = (
        H.note("For den enkelte butikk.")
        + H.kpis([
            ("Nytt prosjekt", "Male stue", "42 m² · Borgveien 14"),
            ("Varelinjer", "5", "beregnet i ERA", "mono"),
            ("Materialer", "ca. 1 900 kr", "tilbud til kunden", "accent"),
            ("Levering", "Kjøres hjem", "valgt av kunden"),
        ])
        # 12 cells (6 single + 3 wide), ordered so 4-, 3- and 2-column layouts fill without holes.
        + H.dashboard([
            H.widget("Produkt og mengde", H.kpis([
                ("Flate", "42 m²", "stue", "mono"),
                ("Strøk", "2", None, "mono"),
                ("Maling", "2 × 10 L", "ca. 1 300 kr", "mono"),
                ("Øvrig materiell", "ca. 600 kr", "sparkel, ruller, pensler, maskering"),
            ]), wide=True),
            H.widget("Nye kundeprosjekter", H.rows([
                ("Male stue, 42 m²", "Borgveien 14"),
                ("Ønsket tid", "Uke 38–40", "customer"),
                ("Farge", "Sjøgrønn 0398", "customer"),
            ])),
            H.widget("Lagerstatus", H.rows([
                ("Interiørmaling 10 L", "2 × 10 L", "ok", "På lager"),
                ("Sparkel 5 kg", "1 × 5 kg", "ok", "På lager"),
                ("Lagersystem", "Kobles per butikk", "dev"),
            ])),
            H.widget("Handlelister", H.table(["Produkt", "Mengde"], [
                ["Interiørmaling", "2 × 10 L"],
                ["Sparkel", "1 × 5 kg"],
                ["Ruller", "2"],
                ["Pensler", "3"],
                ["Maskering", "2 ruller"],
            ], num_cols=(1,)) + H.note("Beregnet for 42 m², to strøk og lett sparkling."), wide=True),
            H.widget("Klikk og hent · levering · håndverkerhenting",
                     H.flow(["Klikk og hent", "Kjøres hjem", "Håndverker henter"], active="Kjøres hjem", arrows=False)
                     + H.status_rows([("Valgt", "Kjøres hjem", "now")])
                     + H.rows([
                         ("Leveres til", "Borgveien 14"),
                         ("Før oppstart", "Uke 38", "customer"),
                     ]), wide=True),
            H.widget("Tilbud til kunden", H.rows([
                ("Materialer", "ca. 1 900 kr"),
                ("Maling", "ca. 1 300 kr"),
                ("Øvrig materiell", "ca. 600 kr"),
            ])),
            H.widget("Mersalgsforslag", H.rows([
                ("Forslag", "Prøvefarge · maskeringstape", "ai"),
                ("Grunnlag", "Farge og forarbeid i planen"),
            ])),
            H.widget("Kommende lokal etterspørsel", H.rows([
                ("Borettslag", "1 · fasade 2027"),
                ("Tiltak", "Male sør- og vestvegg"),
                ("Materiell", "Maling, grunning, stillas", "ai"),
            ])),
            H.widget("Avvik som må dokumenteres", H.rows([
                ("Male stue", "Anbefalt og kjøpt like", "ok", "Ingen avvik"),
                ("Registrering", "Per bestilling", "dev"),
            ])),
        ])
    )

    window = H.window(
        "ERA for faghandel", "Kjede · forhandler",
        tabs=[
            ("sentralt", "Sentralt dashboard", sentralt),
            ("forhandler", "Forhandlerdashboard", forhandler),
        ],
        chips=("Under utvikling", "Eksempeldata"),
        equalize=False,  # the tab strip sits above the panels, so a height change never shifts the tabs
        foot="Eksempeldata. Dashboardene er under utvikling; prosjekter, mengder og priser viser arbeidsflyten, ikke reelle kunder.",
    )
    dash_legend = H.legend([
        ("dev", "begge dashboardene"),
        ("ai", "forslag fra ERA, til vurdering"),
        ("customer", "valgt av kunden"),
    ])
    parts.append(H.section(
        dash_legend + window, id="dashboard", wide=True,
        eyebrow="To nivåer", title="Ett dashboard for kjeden. Ett for butikken.",
        lede="Kjeden ser etterspørsel og prognoser på tvers av butikker. Butikken ser prosjektene som er på vei inn, med produkt, mengde og levering allerede valgt.",
    ))

    # ---- 3. Verdi: for faghandelen og for kunden, så sidens to CTA-er ----
    groups = H.groups([
        ("For faghandelen", "Etterspørselen er beregnet før den når dere.", [
            "Kvalifisert etterspørsel fra faktiske boligbehov",
            "Riktig mengde gir færre feilkjøp og returer",
            "Hele prosjektet gir større handlekurv",
            "Kunden sendes til riktig forhandler",
            "Bedre kundelojalitet gjennom boligens livsløp",
            "Vedlikeholdsplaner gir tidligere og mer presise prognoser",
            "Dokumentert kobling mellom anbefaling, kjøp og gjennomført tiltak",
        ]),
        ("For kunden", "Færre ting å ta feil på.", [
            "Riktig produkt",
            "Riktig mengde",
            "Riktig butikk",
            "Riktig levering",
            "Mindre usikkerhet",
            "Færre ekstraturer",
        ]),
    ])
    ctas = H.cta_row([
        H.cta(primary_label, primary_href, "gold"),
        H.cta(secondary_label, secondary_href, "ghost"),
    ])
    parts.append(H.section(
        groups + ctas, id="verdi", alt=True,
        eyebrow="Verdi", title="Riktig produkt, riktig mengde, riktig butikk.",
    ))

    return "".join(parts)
