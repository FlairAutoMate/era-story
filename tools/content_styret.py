# -*- coding: utf-8 -*-
"""Product content for /styret (ERA Styret). Called by tools/build-pages.py as render(H, a) and
inserted between the hero and the scenes section (#slik). H is the helpers namespace (see its
docstring in build-pages.py); a is the audience dict (cta_primary = pilot sameie entry,
cta_secondary = «Book en gjennomgang» → #skjema).

Sections, in order: #produktet (one board dashboard window, eight widgets), #funksjoner (one
tabbed window, five function areas, each tab = grouped checklist + one small product surface),
#tilvalg (the soilrør scenario) and #verdi (uten/med ERA + the page's two CTAs). Example data is
the shared Borgveien 14 set; every window carries the «Eksempeldata» chip. Status: ERA Styret is
«I pilot»; tilbudssammenligning and beboervarsling stay «Illustrasjon av arbeidsflyt»;
fakturagrunnlag (betaling i ERA) is «I pilot». No numbers beyond the example data."""

TILVALG_TEXT = (
    "Borettslaget skal skifte soilrør. ERA sender samme prosjektgrunnlag til kvalifiserte VVS-partnere. "
    "Hver boligeier kan samtidig få tilbud på privat oppgradering av badet. Fellesarbeidet, individuelle "
    "tilvalg, fremdrift, kostnader og dokumentasjon holdes adskilt – men gjennomføres i én koordinert flyt."
)

OFFER_HEADERS = ["Tilbyder", "Pris", "Omfang", "Forbehold", "Oppstart"]
OFFER_ROWS = [
    ["Malermester Berg AS", "1,05 mill", "Samme", "Stillas", "Uke 20"],
    ["Tilbyder B", "1,18 mill", "Samme", "Stillas", "Mai–juni"],
    ["Tilbyder C", "1,25 mill", "Samme", "Stillas", "Mai–juni"],
]


def _offers_table(H):
    """The three-offer comparison. .pw-table--stack collapses it to blocks when its widget is
    narrower than 480px (container query in product.css), so one markup serves every width."""
    return H.table(OFFER_HEADERS, OFFER_ROWS, num_cols=(1,), chosen=(0,))


def render(H, a):
    parts = []
    # The illustration note rides as the legend's trailing note (its own flex item) rather than
    # inside the inline-flex legend item, so it wraps onto its own line at 320px instead of overflowing.
    status_legend = H.legend(
        [("pilot", "ERA Styret"), "illustration"],
        note="tilbudssammenligning og beboervarsling",
    )

    # ---- 1. Produktet: ett styredashboard, åtte widgeter ----
    # DOM order alternates one-column (N) and two-column (W) widgets so the dense .pw-dashboard grid
    # fills every row at two, three and four columns: N W N W N W N W.
    helse = H.widget(
        "Eiendommens helsetilstand",
        H.ring_row(67, "<b>67 av 100</b>" + H.note("Bygger på det som er dokumentert om eiendommen."),
                   label="Eiendommens helsetilstand 67 av 100")
        + H.legend([
            ("warn", None, "2 høy risiko"),
            ("wait", None, "4 middels"),
            ("ok", None, "8 ok"),
            ("check", None, "1 ikke vurdert"),
        ]),
    )
    budsjett = H.widget(
        "Budsjett og kostnadsprognose",
        H.kpis([
            ("Kostnadsintervall", "1,0–1,3 mill", "fasade 2027", "mono"),
            ("Per seksjon", "ca. 42–54 000 kr", "24 seksjoner", "mono"),
        ])
        + H.rows([("Likviditetsbehov 2027", "Til styrets vurdering", "ai")]),
        wide=True,
    )
    tiltak = H.widget(
        "Kritiske og kommende tiltak",
        H.rows([
            ("Fasade sør/vest", "Befaring innen 12 mnd", "ai"),
            ("Tak", "Egen oppgave 2031"),
            ("Vinduer", "Tetningslister høst 2026"),
        ]),
    )
    tilbud = H.widget("Aktive tilbud", _offers_table(H), wide=True, tag="illustration")
    beslutning = H.widget(
        "Neste styrebeslutning",
        H.status_rows([("Neste", "Fasade 2027 · styremøte 14. mars", "now")])
        + H.rows([("Grunnlag", "Funn, ERA-forslag og kostnad", "ok", "Klart")]),
    )
    prosjekter = H.widget(
        "Pågående prosjekter",
        H.rows([("Fasade 2027", "Uke 2 av 6", "ok", "I rute")])
        + H.progress(33)
        + H.rows([
            ("Utføres av", "Malermester Berg AS"),
            ("Stillas", "Inngang B · uke 20–25"),
            ("Bilder fra arbeidet", "Legges inn underveis"),
        ]),
        wide=True,
    )
    avvik = H.widget(
        "Avvik som krever behandling",
        H.rows([
            ("Farge på beslag", "Svar innen fredag", "wait", "Venter"),
            ("Inngang B", "Avskalling · lagt til i omfanget", "ok", "Behandlet"),
        ]),
    )
    meldinger = H.widget(
        "Meldinger til beboerne",
        H.msgs([("Stillas ved inngang B, uke 20–25. Balkonger ryddes før 12. mai.", "Styret til beboerne · Fasade 2027")])
        + H.rows([("Mottakere", "24 seksjoner")]),
        wide=True, tag="illustration",
    )
    dashboard = H.window(
        "ERA Styret", "Borgveien 14 · 24 seksjoner",
        body_html=H.dashboard([helse, budsjett, tiltak, tilbud, beslutning, prosjekter, avvik, meldinger]),
        foot="Eksempeldata. Tall, datoer og priser viser arbeidsflyten, ikke en reell eiendom. Samme fasadesak vises i flere faser samtidig.",
    )
    parts.append(H.section(
        status_legend + dashboard, id="produktet", wide=True,
        eyebrow="ERA Styret", title="Styrets operative arbeidsflate for hele eiendommen.",
        lede="ERA Styret samler vedlikeholdsplan, beslutningsgrunnlag, økonomi, leverandører, fremdrift, dokumentasjon og kommunikasjon med beboerne rundt samme eiendom.",
    ))

    # ---- 2. Funksjonsområder: ett vindu, fem faner ----
    def panel(items, surface_title, surface_html, below_html="", surface_tag=None):
        return H.grid([H.widget("Funksjoner", H.checklist(items)), H.widget(surface_title, surface_html, tag=surface_tag)]) + below_html

    oversikt = panel(
        [
            "Eiendom, bygg, seksjoner og fellesarealer",
            "Tilstandsrapporter og tidligere arbeid",
            "Innmeldte behov",
            "Risiko og prioritet",
            "5-, 10- og 20-års vedlikeholdsplan",
            "Påminnelser og periodiske kontroller",
        ],
        "Vedlikeholdsplan · Borgveien 14",
        H.timeline([
            ("2021", "Tilstandsrapport", "Takstmann Berg AS · maling flasser på sør- og vestvegg", "done", "doc"),
            ("2027", "Male sør- og vestvegg", "Anbefalt år · 1,0–1,3 mill", "next", "ai"),
            ("2031", "Tak", "Egen oppgave i totalplanen", "later"),
            ("2032", "Neste fasadekontroll", "Periodisk kontroll etter utført arbeid", "later", "ai"),
        ])
        + H.rows([("Innmeldt behov", "Avskalling ved inngang B", "resident")]),
    )
    beslutning_tab = panel(
        [
            "Tiltak rangert etter risiko, kostnad og anbefalt tidspunkt",
            "Kostnadsestimat, også per seksjon",
            "Budsjett og likviditetsbehov",
            "Beslutningsgrunnlag til styremøtet",
            "Vedtak og ansvar",
            "Dokumentert skille mellom faglige funn, ERA-forslag og styrets beslutninger",
        ],
        "Beslutningsgrunnlag · Fasade 2027",
        H.rows([("Funn", "Maling flasser på sør- og vestvegg · rapport 2021")], group_tag="doc")
        + H.rows([("Anbefalt år", "2027"), ("Kostnadsintervall", "1,0–1,3 mill · ca. 42–54 000 kr per seksjon")], group_tag="ai")
        + H.rows([("Vedtak", "Styremøte 14. mars"), ("Ansvar", "Styreleder")], group_tag="board"),
    )
    tilbud_tab = panel(
        [
            "Strukturert tilbudsforespørsel",
            "Samme arbeidsgrunnlag til alle leverandører",
            "Bilder, mål, dokumentasjon og ønsket fremdrift",
            "Sammenligning av pris, omfang, forbehold og tidspunkt",
            "Valg av leverandør",
            "Kontrakt og oppstart",
        ],
        "Forespørsel · Fasade 2027",
        H.rows([
            ("Omfang", "Sør- og vestvegg, vask, sparkling, 2 strøk"),
            ("Vedlegg", "Bilder og rapport 2021"),
            ("Ønsket tid", "Mai–juni 2027"),
            ("Sendt til", "3 leverandører, samme grunnlag"),
        ]),
        below_html=H.widget(
            "Tilbud · Fasade 2027",
            _offers_table(H) + H.note("Tre tilbud på samme omfang, spenn 1,05–1,25 mill. Valgt: Malermester Berg AS."),
            tag="illustration",
        ),
    )
    gjennomforing = panel(
        [
            "Fremdriftsplan og milepæler",
            "Bilder fra arbeidet",
            "Endringsordre og tillegg",
            "Avvik",
            "Godkjenning",
            ("Fakturagrunnlag", "pilot"),
        ],
        "Gjennomføring · Fasade 2027",
        H.rows([("Fremdrift", "Uke 2 av 6", "ok", "I rute")])
        + H.progress(33)
        + H.rows([
            ("Milepæl", "Stillas opp uke 20"),
            ("Bilder", "18 lagt inn"),
            ("Endringsordre", "Ingen"),
            ("Fakturagrunnlag", "Betaling i ERA", "pilot"),
        ]),
    )
    beboerne = panel(
        [
            "Informasjon før, under og etter prosjektet",
            "Påminnelser og varsler",
            "Tilgang til relevant felles dokumentasjon",
            "Egen ERA Bolig-profil for hver boligeier",
            "Privat boligdokumentasjon holdes adskilt fra styrets informasjon",
        ],
        "Beboerne · Fasade 2027",
        H.msgs([("Stillas ved inngang B, uke 20–25. Balkonger ryddes før 12. mai.", "Styret til beboerne")])
        + H.rows([("Privat bolig", "Deles ikke automatisk med styret", "doc")]),
        surface_tag="illustration",
    )
    funksjoner = H.window(
        "ERA Styret", "Funksjonsområder",
        tabs=[
            ("oversikt", "Oversikt og vedlikeholdsplan", oversikt),
            ("beslutning", "Beslutning og økonomi", beslutning_tab),
            ("tilbud", "Tilbud og leverandører", tilbud_tab),
            ("gjennomforing", "Gjennomføring", gjennomforing),
            ("beboerne", "Beboerne", beboerne),
        ],
        numbered=True,
        equalize=False,  # panel heights differ; the tab strip sits above, so nothing shifts
        foot="Eksempeldata. Samme fasadesak i alle fem områdene.",
    )
    parts.append(H.section(
        funksjoner + status_legend, id="funksjoner", alt=True, wide=True,
        eyebrow="Funksjonsområder", title="Fem områder. Én eiendom.",
        lede="Samme eiendom hele veien: fra oversikt og plan til beslutning, tilbud, gjennomføring og beboerne.",
    ))

    # ---- 3. Fellesarbeid og private tilvalg ----
    scenario = H.scenario(
        "Soilrør i borettslaget", TILVALG_TEXT,
        [
            ("Fellesarbeid", [
                ("Tiltak", "Soilrør · 24 seksjoner"),
                ("Grunnlag", "Samme prosjektgrunnlag til kvalifiserte VVS-partnere"),
                ("Beslutning", "Styret beslutter"),
            ]),
            ("Individuelle tilvalg", [
                ("Tilbud", "Privat oppgradering av badet"),
                ("Til hvem", "Hver boligeier, samtidig"),
                ("Avtale og kostnad", "Privat · holdes adskilt fra fellesarbeidet"),
            ]),
            ("Én koordinert flyt", [
                ("Fremdrift", "Felles og privat holdes adskilt"),
                ("Kostnader og dokumentasjon", "Adskilt per avtale"),
                ("Gjennomføring", "Samtidig, i én koordinert flyt"),
            ]),
        ],
        tag="illustration",
    )
    parts.append(H.section(
        scenario, id="tilvalg",
        eyebrow="Fellesarbeid og tilvalg", title="Fellesarbeid og private tilvalg i én flyt.",
    ))

    # ---- 4. Tid og kvalitet ----
    compare = H.compare(
        "Uten ERA", [
            "Dokumenter i mapper og e-post",
            "Flere møter for å forstå behovet",
            "Ulike beskrivelser sendt til leverandørene",
            "Tilbud som er vanskelige å sammenligne",
            "Manuell oppfølging av fremdrift og avvik",
            "Historikk som forsvinner når styret skiftes",
        ],
        "Med ERA", [
            "Ett samlet eiendomsgrunnlag",
            "Prioriterte tiltak og klart beslutningsgrunnlag",
            "Samme forespørsel til alle leverandører",
            "Sammenlignbare tilbud",
            "Løpende fremdrift og dokumentasjon",
            "Vedlikeholdsplanen består når styret skiftes",
        ],
    )
    primary_label, primary_href = a["cta_primary"]
    secondary_label, secondary_href = a["cta_secondary"]
    ctas = H.cta_row([
        H.cta(primary_label, primary_href, "gold"),
        H.cta(secondary_label, secondary_href, "ghost"),
    ])
    parts.append(H.section(
        compare + ctas, id="verdi", alt=True,
        eyebrow="Tid og kvalitet", title="Mindre styrearbeid. Raskere vei til et forsvarlig vedtak.",
        lede="Det ERA tar bort, og det styret får i stedet.",
    ))

    return "".join(parts)
