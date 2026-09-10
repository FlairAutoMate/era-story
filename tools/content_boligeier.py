# -*- coding: utf-8 -*-
"""Product content for /boligeier (ERA Bolig). Called by tools/build-pages.py as render(H, a) and
inserted between the hero and the scenes section. H is the helpers namespace (see its docstring in
build-pages.py); a is the audience dict. Sections: #produktet (one app window with seven tabs),
Funksjoner (four feature groups) and «Dette sparer ERA deg for». Example data is the shared
Borgveien 14 set; the window carries the «Eksempeldata» chip."""


def render(H, a):
    parts = []

    # ---- 1. Produktet: ett vindu, sju faner ----
    oversikt = (
        H.kpis([
            ("Vedlikeholdsindeks", "67", "basert på det som er dokumentert", "mono"),
            ("Nå", "1 tiltak", "Stua males"),
            ("Neste", "1 tiltak", "Vinduer · tetningslister"),
            ("Dokumenter", "16", "rapport, FDV og kvitteringer"),
        ])
        + H.grid([
            H.widget("Prioritering", H.status_rows([
                ("Nå", "Stua males", "now"),
                ("Neste", "Vinduer · tetningslister"),
                ("Senere", "Bad", "later"),
            ])),
            H.widget("Påminnelser", H.rows([
                ("Vinduer · tetningslister", "Høst 2026"),
                ("Fasade · felles", "Befaring innen 12 mnd", "board", "Felles"),
            ]) + H.note("Påminnelsene følger vedlikeholdsplanen og sesongen.")),
        ])
    )

    tilstand = (
        H.ring_row(67, '<b>Vedlikeholdsindeks 67</b>' + H.note("Bygger på tilstandsrapport, FDV, kvitteringer og bilder. Endres når du legger inn mer."), label="Vedlikeholdsindeks 67 av 100")
        + H.grid([
            H.rows([
                ("Stue", "Vegg slitt, ingen skader"),
                ("Vinduer", "Nordan · garanti til 2029"),
            ], group_tag="doc"),
            H.rows([
                ("Overflatebehandling stue", "Innen 12 mnd"),
            ], group_tag="ai"),
            H.rows([
                ("Fasade", "Maling flasser · befaring innen 12 mnd"),
            ], group_tag="board", group_label="Felles · styret"),
            H.widget("Risiko og manglende dokumentasjon", H.rows([
                ("Bad", "Dokumentasjon delvis", "wait", "Ufullstendig"),
            ]) + H.note("Deler uten dokumentasjon vises her, så du vet hva som mangler.")),
        ])
    )

    tiltak = (
        H.kpis([
            ("Vegg", "42 m²", None, "mono"),
            ("Forbehandling", "Lett sparkling"),
            ("Strøk", "2", None, "mono"),
            ("Tid", "1–2 dager"),
            ("Estimert", "ca. 6 800 kr", "med håndverker", "accent"),
        ])
        + H.cols([
            ("ai", [
                ("Hvorfor anbefales det", "Veggen er slitt, uten skader (tilstandsrapport 2021). ERA foreslår overflatebehandling innen 12 mnd."),
                ("Materialer", "ca. 1 900 kr · 2 × 10 L interiørmaling, 1 × 5 kg sparkel, 2 ruller, 3 pensler, 2 ruller maskering"),
            ]),
        ])
        + H.grid([
            H.widget("Fra deg", H.rows([
                ("Farge", "Sjøgrønn 0398"),
                ("Ønsket tid", "Uke 38–40"),
                ("Bilder", "4 vedlagt"),
            ])),
            H.widget("Veivalg", H.flow(["Gjør det selv", "Få hjelp"], arrows=False)
                     + H.note("Materialene er beregnet og kan bestilles. Eller jobben går til håndverker, ferdig beskrevet.")),
        ])
    )

    plan = (
        H.timeline([
            ("2026", "Stua malt", "Dokumentert · 6 bilder, produkter og kvittering", "done"),
            ("Høst 2026", "Vinduer · tetningslister", "Neste tiltak · påminnelse følger", "next"),
            ("2027", "Fasade · felles", "Male sør- og vestvegg · styret beslutter", "later", "board"),
            ("2031", "Tak · felles", "Egen oppgave i borettslagets totalplan", "later", "board"),
            ("Senere", "Energi og forbedringer", "Vises i planen når funksjonen er klar", "later", "planned"),
        ])
        + H.note("Felles tiltak kommer fra borettslagets plan i ERA Styret. Private tiltak er dine.")
    )

    dokumenter = H.grid([
        H.rows([
            ("Tilstandsrapport", "2021 · Takstmann Berg AS"),
            ("FDV", "3 dokumenter"),
            ("Kvitteringer", "12"),
            ("Bilder", "24"),
            ("Garantier", "Vinduer · Nordan, til 2029"),
        ], group_tag="doc"),
        H.widget("Legg til", H.rows([
            ("Import", "Tilstandsrapport, FDV, kvitteringer og bilder", "beta"),
            ("Fra", "E-post, mapper og telefon"),
        ]) + H.note("Bilder og dokumenter analyseres og kan knyttes til riktig rom og bygningsdel.")),
    ])

    prosjekter = (
        H.table(["Jobb", "Fag", "Når", "Detaljer"], [
            ["Male stue", "Maler", "Uke 38", "Overlevert · 6 bilder"],
            ["Lekkasje under kjøkkenvask", "Rørlegger", "Denne uken", "2 bilder og video"],
            ["Ny kurs til kjøkken", "Elektriker", "Uke 40", "1 kurs · 16 A"],
        ], chosen=(0,))
        + H.grid([
            H.widget("Male stue · avtale", H.rows([
                ("Omfang", "Vegger og tak, 2 strøk"),
                ("Avtalt oppstart", "Uke 38"),
                ("Farge", "Sjøgrønn 0398"),
                ("Endringsordre", "Tak, +ca. 1 800 kr, +1 dag · godkjent"),
            ])),
            H.widget("Male stue · overlevering", H.rows([
                ("Status", "Overlevert", "ok", "Ferdig"),
                ("Utført av", "Håndverker, med navn på jobben"),
                ("Bilder", "6"),
                ("Produkter", "Maling, sparkel, ruller"),
            ]) + H.rows([
                ("Betaling i ERA", "Avtalt beløp og betalingsstatus"),
            ], group_tag="pilot")),
        ])
    )

    historikk = (
        H.timeline([
            ("2021", "Tilstandsrapport", "Takstmann Berg AS", "done"),
            ("2024", "Kvittering Byggmakker", "8 420 kr · 14.05.2024", "done"),
            ("2026", "Stua malt", "2 strøk · 6 bilder · produkter og FDV", "done"),
            ("2029", "Garanti vinduer utløper", "Nordan", "later"),
        ])
        + H.note("Historikken følger boligen ved eierskifte.")
    )

    window = H.window(
        "ERA Bolig", "Borgveien 14 · eksempelbolig",
        tabs=[
            ("oversikt", "Oversikt", oversikt),
            ("tilstand", "Tilstand", tilstand),
            ("tiltak", "Tiltak", tiltak),
            ("plan", "Vedlikeholdsplan", plan),
            ("dokumenter", "Dokumenter", dokumenter),
            ("prosjekter", "Prosjekter", prosjekter),
            ("historikk", "Historikk", historikk),
        ],
        side=True,
        equalize=False,  # panel heights differ a lot; the tab strip sits above, so nothing shifts
        foot="Eksempeldata. Tall, datoer og priser viser arbeidsflyten, ikke en reell bolig.",
    )
    legend = H.legend([
        ("beta", "åpen for 300 boligeiere"),
        ("pilot", "betaling i ERA"),
        ("planned", "energi og forbedringer"),
    ])
    parts.append(H.section(
        legend + window, id="produktet", wide=True,
        eyebrow="ERA Bolig", title="Boligen din, samlet og forstått.",
        lede="ERA Bolig gir deg én løpende oversikt over boligens tilstand, historikk, dokumentasjon og kommende behov. Du ser hva som bør gjøres, hva som kan vente og hvordan du kommer videre.",
    ))

    # ---- 2. Funksjoner ----
    groups = H.groups([
        ("Forstå boligen", "Det du har liggende blir en boligprofil.", [
            "Digital boligprofil med rom, bygningsdeler og installasjoner",
            "Import av tilstandsrapport, FDV, kvitteringer og bilder",
            "AI-analyse av bilder og dokumenter",
            "Vedlikeholdsindeks",
            "Risiko og manglende dokumentasjon",
        ]),
        ("Vit hva som bør gjøres", "Og hva som kan vente.", [
            "Prioritering: nå, neste og senere",
            "Personlig vedlikeholdsplan",
            "Sesongbaserte påminnelser",
            "Kostnadsestimat",
            "Forventet tidsbruk",
            "Forklaring på hvorfor tiltaket anbefales",
        ]),
        ("Gjennomfør tiltaket", "Fra et bilde til en jobb som kan prises.", [
            "Ta bilde eller beskriv behovet",
            "Få arbeidsbeskrivelse",
            "Få beregnet materialer og mengder",
            "Se relevante produkter",
            "Velg mellom gjør-det-selv og håndverker",
            "Motta og sammenligne tilbud",
            ("Bestille produkt eller tjeneste", "pilot"),
        ]),
        ("Bevar verdien", "Alt som er gjort, blir værende i boligen.", [
            "Bilder før, under og etter",
            "Kvitteringer",
            "Produkter og FDV",
            "Garantier",
            "Utførende håndverker",
            "Kostnad og dato",
            "Historikk som følger boligen ved eierskifte",
        ]),
    ])
    groups_legend = H.legend([
        ("beta", "funksjonene videreutvikles sammen med de første 300 boligeierne"),
        ("pilot", "bestilling med betaling i ERA"),
    ])
    parts.append(H.section(
        groups + groups_legend, alt=True,
        eyebrow="Funksjoner", title="Fire ting ERA Bolig gjør for deg.",
        lede="Samme bolig hele veien: fra det du har liggende til en bolig som husker hva som er gjort.",
    ))

    # ---- 3. Dette sparer ERA deg for ----
    saves = H.saves(
        x_items=[
            "Leting etter dokumenter i e-post og mapper",
            "Manuell vurdering av hva som haster",
            "Flere runder for å forklare behovet til håndverkere",
            "Feilkjøp og feilberegnede mengder",
            "Manglende dokumentasjon etter utført arbeid",
        ],
        fromto_items=[
            "Fra spredt informasjon til ett forståelig beslutningsgrunnlag.",
            "Fra en løs idé til et strukturert prosjekt som kan prises.",
            "Fra utført jobb til oppdatert bolighistorikk uten en ny dokumentasjonsrunde.",
        ],
    )
    parts.append(H.section(
        saves,
        eyebrow="Konkret verdi", title="Dette sparer ERA deg for.",
        lede="Ingen prosenter. Bare det som faller bort, og det som kommer i stedet.",
    ))

    return "".join(parts)
