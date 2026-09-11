# -*- coding: utf-8 -*-
"""Generates the audience subpages (/boligeier, /styret, /handverker, /faghandel) from one
template and one content dict. Run from the project root: python tools/build-pages.py"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(t):
    return html.escape(t, quote=True)


TAG_LABELS = {"customer": "Fra kunden", "doc": "Dokumentert", "ai": "ERA-forslag", "check": "Avklares på befaring", "board": "Styret", "pro": "Håndverker", "resident": "Beboer", "order": "Bestilling og levering", "pilot": "I pilot", "planned": "Planlagt", "illustration": "Illustrasjon av arbeidsflyt"}


def detail_card(title, meta, groups, note=None):
    """A scene's realistic product-view card: reuses .card/.row from the example section, with
    rows grouped under a small source tag (fra kunden / ERA-forslag / avklares på befaring / i pilot)
    so the visitor can see at a glance what's confirmed, suggested, or still to check."""
    body = []
    for tag, rows in groups:
        body.append(f'<div class="card-group"><span class="tag tag-{tag}">{esc(TAG_LABELS[tag])}</span>' + "".join(
            f'<div class="row"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows
        ) + '</div>')
    note_html = f'<p class="card-note">{esc(note)}</p>' if note else ""
    return (
        '<div class="card">'
        f'<div class="card-head"><span class="label">{esc(title)}</span><span class="meta">{esc(meta)}</span></div>'
        + "".join(body) + note_html +
        '<p class="card-fine">Eksempeldata, ikke reelle kundeopplysninger.</p>'
        '</div>'
    )



def dash(title, meta, kpis=(), groups=(), cols=(), footer=None, tag=None):
    """A wide, dashboard-like product view for the scene panel: a header, up to four KPI tiles,
    optional tagged row groups or side-by-side columns, and one short footer. Monospace only
    on small values. `tag` marks the whole view (e.g. illustration of a workflow)."""
    head_tag = f'<span class="tag tag-{tag}">{esc(TAG_LABELS[tag])}</span>' if tag else ""
    out = ['<div class="dash">',
           f'<div class="dash-head"><div><div class="dash-title">{esc(title)}</div><div class="dash-meta">{esc(meta)}</div></div>{head_tag}</div>']
    if kpis:
        out.append('<div class="kpis">' + "".join(
            f'<div class="kpi"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in kpis) + '</div>')
    for g_tag, rows in groups:
        out.append(f'<div class="dash-group dash-group-{g_tag}"><span class="tag tag-{g_tag}">{esc(TAG_LABELS[g_tag])}</span>' + "".join(
            f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows) + '</div>')
    if cols:
        out.append('<div class="dash-cols">' + "".join(
            f'<div class="dcol"><span class="tag tag-{c_tag}">{esc(TAG_LABELS[c_tag])}</span>' + "".join(
                f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows) + '</div>'
            for c_tag, rows in cols) + '</div>')
    if footer:
        out.append(f'<div class="dash-foot">{esc(footer)}</div>')
    out.append('</div>')
    return "".join(out)


SHY = "­"

# Long Norwegian compounds in a hero headline: at 320-390px the line is narrower than the word, and
# without a break point the browser cuts it mid-word. The soft hyphen puts the break at the seam.
SOFT_BREAKS = {
    "vedlikeholdsbehov": "vedlikeholds" + SHY + "behov",
    "Boligeierskap": "Bolig" + SHY + "eierskap",
}


def soften(text):
    """Insert soft hyphens at known compound seams. Only affects rendering when a line is too narrow."""
    for word, softened in SOFT_BREAKS.items():
        text = text.replace(word, softened)
    return text


# The one demo home used across every ERA Bolig screen on /boligeier. This is the fact sheet: the
# app screenshots must show these values, and the alt texts below are built from it so the two
# cannot drift apart. Three different values for the same home have already shipped by accident
# (6,8 mill. / 8,9 mill. / 6 250 000) — change a number here, re-export the screens, never the
# other way around. tools/check-demo-home.py fails if a stale value reappears in a generated page.
DEMO_HOME = {
    "address": "Myrerveien 46A",
    "city": "Oslo",
    "type": "enebolig",
    "area": "162 m²",
    "year": "1967",
    "condition": "God",
    "score": "78 av 100",
    "measure": "Fasadevask og maling",
    "cost": "85 000–140 000 kr",
    "value": "6 250 000 kr",
    "start": "april 2026",
    "duration": "2–3 uker",
    "pro": "Oslo Fasade AS",
}

# Values that shipped earlier and must never come back. Kept here so the fact sheet and the guard
# that enforces it live in the same place.
DEMO_HOME_STALE = ["1987", "80 000–120 000", "80 000 – 120 000", "6,8 mill", "8,9 mill",
                   "Myrveien", "Myreveien", "Borgveien"]


def phone(src, w, h, alt, size="md", eager=False, cap=None):
    """One ERA Bolig screen in a device frame. Never cropped: width/height come from the file, and
    each size class caps the width at the source resolution so nothing is upscaled and soft."""
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    cap_html = f'<p class="pw-phone-cap">{esc(cap)}</p>' if cap else ''
    return (f'<div class="pw-phone pw-phone--{size}">'
            f'<img src="{src}" width="{w}" height="{h}" alt="{esc(alt)}" {load} decoding="async">'
            f'{cap_html}</div>')


def ui(src, w, h, alt, cap=None):
    """A cropped piece of the app UI, shown as the card it is rather than inside a device frame."""
    cap_html = f'<p class="pw-phone-cap">{esc(cap)}</p>' if cap else ''
    return (f'<div class="pw-ui"><img src="{src}" width="{w}" height="{h}" alt="{esc(alt)}"'
            f' loading="lazy" decoding="async">{cap_html}</div>')


def app_section(eyebrow, title, lede, visual_html, points=(), alt_bg=False, flip=False, sid=None,
                dark=False, foot=None):
    """One product beat: a single message beside a single screen."""
    cls = "section appsec" + (" alt" if alt_bg else "") + (" dark" if dark else "") + (" appsec--flip" if flip else "")
    pts = ('<ul class="appsec-points">' + "".join(f'<li><b>{esc(t)}</b>{esc(d)}</li>' for t, d in points) + '</ul>') if points else ""
    foot_html = f'<p class="fine dark2">{esc(foot)}</p>' if foot else ""
    return (f'<section class="{cls}"' + (f' id="{sid}"' if sid else '') + '><div class="wrap">'
            f'<div class="appsec-text"><div class="label">{esc(eyebrow)}</div><h2>{esc(title)}</h2>'
            f'<p class="lede">{esc(lede)}</p>{pts}{foot_html}</div>'
            f'<div class="appsec-visual">{visual_html}</div>'
            '</div></section>')


def app_loop(eyebrow, title, steps, foot):
    """The whole loop in one row: five screens, five short labels, one grid so they stay aligned.
    Each step carries its own width/height: the screens are exported at different resolutions, and a
    hardcoded size would stretch them."""
    shots = "".join(
        f'<div class="apploop-shot"><img src="{src}" width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async"></div>'
        for _, _, src, alt, w, h in steps)
    labels = "".join(
        f'<div class="apploop-step"><span class="n">0{i+1}</span><b>{esc(t)}</b><span>{esc(d)}</span></div>'
        for i, (t, d, _, _, _, _) in enumerate(steps))
    return ('<section class="section alt" id="loopen"><div class="wrap wide">'
            f'<div class="label">{esc(eyebrow)}</div><h2>{esc(title)}</h2>'
            f'<div class="apploop">{shots}</div>'
            f'<div class="apploop-steps">{labels}</div>'
            f'<p class="fine dark2">{esc(foot)}</p>'
            '</div></section>')


AUDIENCES = {
    "boligeier": dict(
        key="owner", nav="Boligeier", title="ERA for boligeiere",
        label="For boligeier", hook="Boligeierskap uten gjetting.",
        lede="ERA forstår hva boligen din trenger, og hva som bør gjøres først. Tilstand, historikk, dokumentasjon og prioriteringer, samlet i én plan for hjemmet.",
        image="/assets/story/couple-sofa-v3.jpg", image_pos="55% 55%",
        app_hero=dict(src="/assets/story/app-hjem.png", w=853, h=1844, size="lg",
                      alt=f"ERA Bolig på mobil: forsiden for {DEMO_HOME['address']} med boligtype {DEMO_HOME['type']}, "
                          f"{DEMO_HOME['area']}, byggeår {DEMO_HOME['year']}, tilstand {DEMO_HOME['condition']} "
                          f"{DEMO_HOME['score']}, neste tiltak «{DEMO_HOME['measure']}» og estimert kostnad {DEMO_HOME['cost']}"),
        app_sections=[
            app_section(
                "Min bolig", "Alt om boligen. Ett sted.",
                "Ikke bare data fra registre. ERA bygger en levende boligprofil som utvikler seg når du legger til rom, dokumentasjon, arbeid og nye opplysninger.",
                phone("/assets/story/app-minbolig.png", 941, 1672,
                      f"ERA Bolig: Min bolig for {DEMO_HOME['address']} – {DEMO_HOME['type']} fra {DEMO_HOME['year']} på "
                      f"{DEMO_HOME['area']} med tilstand {DEMO_HOME['condition']} {DEMO_HOME['score']}, vedlikeholdstiltaket "
                      f"«{DEMO_HOME['measure']}» til {DEMO_HOME['cost']}, estimert verdi {DEMO_HOME['value']} og samlet dokumentasjon",
                      "lg"),
                alt_bg=True, flip=True, sid="slik"),
            app_section(
                "Kamera", "Vis ERA hva du ser.",
                "Ta et bilde av noe du lurer på. ERA analyserer det sammen med informasjonen den allerede har om boligen.",
                phone("/assets/story/app-kamera.png", 853, 1844,
                      "ERA Bolig: kameraet rettet mot avflassende maling på kledningen ved et vindu, med teksten «Ta et bilde – fokuser på problemet, så analyserer ERA det for deg» og valget «Analyser med ERA»",
                      "lg", cap="Eksempeldata · Myrerveien 46A"),
                foot="Du starter med det du faktisk ser, ikke med et skjema."),
            app_section(
                "Boligagent", "Ikke bare et AI-svar. Et svar om boligen din.",
                "ERA kombinerer det du spør om eller viser med tilgjengelig informasjon om boligens alder, historikk, tilstand og tidligere arbeid.",
                phone("/assets/story/app-agent.png", 853, 1844,
                      "ERA Bolig: brukeren spør «Kan du se på dette bildet?», og boligagenten svarer med det annoterte "
                      f"fotoet, to observasjoner, hva funnet betyr, et forslag og estimert kostnad {DEMO_HOME['cost']}",
                      "lg"),
                points=[("Hva jeg ser", "Avflassing av maling og slitasje rundt vinduet."),
                        ("Hva det betyr", "Vanlig for hus fra denne perioden. Ikke akutt, men bør følges opp."),
                        ("Mitt forslag", "Få fasaden vurdert av en fagperson og hent inn tilbud.")],
                alt_bg=True, flip=True, sid="boligagent"),
            app_section(
                "Prosjekt", "Fra anbefaling til gjennomføring.",
                "Når noe bør gjøres, kan ERA gjøre anbefalingen om til et konkret prosjekt – fra planlegging og tilbud til gjennomføring og dokumentasjon.",
                phone("/assets/story/app-prosjekt.png", 853, 1844,
                      f"ERA Bolig: prosjektet «{DEMO_HOME['measure']}» på {DEMO_HOME['address']} med estimert kostnad "
                      f"{DEMO_HOME['cost']}, planlagt oppstart {DEMO_HOME['start']}, fremdrift, håndverker og fem oppgaver",
                      "lg", cap="Eksempeldata"),
                points=[("Planlegging", "Omfang, oppstart og varighet."),
                        ("Tilbud", "Håndverker med vurderinger, klar for forespørsel."),
                        ("Gjennomføring", "Fem oppgaver fra stillas til sluttkontroll.")],
                foot="Fasadefunnet fra bildet er nå et prosjekt med kostnad, håndverker og oppgaver."),
            app_section(
                "Boligminne", "Alt som gjøres blir en del av boligen.",
                "Arbeid, dokumentasjon og historikk følger boligen videre – slik at du slipper å starte på nytt hver gang noe skal vedlikeholdes, vurderes eller forbedres.",
                ui("/assets/story/app-boligminne.png", 783, 645,
                   "ERA Bolig, boligminnet: tidslinjen 2020 nytt bad, 2022 varmepumpe, 2024 nytt tak og 2026 fasadevask og maling",
                   cap="Eksempeldata · Myrerveien 46A"),
                points=[("Det som er gjort", "Bad, varmepumpe og tak ligger med år og dokumentasjon."),
                        ("Det som kommer", "Fasadeprosjektet fra bildet står som planlagt.")],
                alt_bg=False, flip=True, sid="boligminne"),
            app_loop(
                "Hele loopen", "Fra spørsmål til ferdig dokumentert.",
                [("Boligen", "ERA kjenner den.", "/assets/story/app-hjem.png",
                  "ERA Bolig: forsiden for Myrerveien 46A med tilstand og neste tiltak", 853, 1844),
                 ("Kamera", "Vis ERA problemet.", "/assets/story/app-kamera.png",
                  "ERA Bolig: kameraet rettet mot avflassende maling ved et vindu", 853, 1844),
                 ("Boligagent", "Forstå hva det betyr.", "/assets/story/app-agent.png",
                  "ERA Bolig: boligagentens analyse av bildet med funn, betydning og forslag", 853, 1844),
                 ("Prosjekt", "Planlegg og gjennomfør.", "/assets/story/app-prosjekt.png",
                  "ERA Bolig: prosjektet «Fasadevask og maling» med kostnad, håndverker og oppgaver", 853, 1844),
                 ("Min bolig", "Dokumenter og husk.", "/assets/story/app-minbolig.png",
                  "ERA Bolig: Min bolig med nøkkeltall, vedlikeholdstiltak, estimert verdi og dokumentasjon", 941, 1672)],
                "Eksempeldata. Samme bolig, Myrerveien 46A, gjennom hele loopen."),
        ],
        gains=[
            ("Vit hva som haster", "Og hva som kan vente. Noen ganger er riktig råd å gjøre ingenting ennå."),
            ("Slutt på gjetting", "Kostnad, tid og forarbeid er regnet ut før du bestemmer deg."),
            ("Alt på ett sted", "Dokumentasjonen følger boligen, også til neste eier."),
            ("Dine data", "Lagret kryptert innenfor EU/EØS. Du bestemmer hvem som ser dem."),
        ],
        faq=[
            ("Må jeg ha tilstandsrapport?", "Nei. ERA starter med det du har. Jo mer du legger inn, jo mer presis blir planen."),
            ("Er ERA en markedsplass?", "Nei. ERA hjelper deg å ta riktig avgjørelse, også når den er å vente. Vi tjener ikke på at du pusser opp."),
            ("Hva skjer med dataene mine?", "De lagres kryptert innenfor EU/EØS og deles bare når du velger det: med håndverker, styret eller kjøper."),
            ("Hva koster ERA for boligeiere?", "ERA er gratis for de 300 boligeierne som deltar i betafasen. Du trenger ikke registrere betalingskort, og det er ingen binding. Eventuelle priser etter beta kommuniseres tydelig før noe endres."),
            ("Hvorfor er det bare 300 plasser?", "Vi begrenser betafasen for å kunne følge opp brukerne tett, forbedre ERA basert på reelle boligbehov og sikre kvalitet før en bredere lansering."),
        ],
        beta=dict(
            badge="Nå i kontrollert beta — åpnes for 300 boligeiere",
            note="Gratis for boligeiere i betaperioden. Begrenset antall plasser.",
            cta_primary="Søk om betatilgang", cta_secondary="Se hvordan ERA fungerer",
            heading="Bli en av 300 boligeiere som tester ERA",
            lede="ERA åpner nå en kontrollert betafase for 300 boligeiere. Som betabruker får du hjelp til å forstå, planlegge og gjennomføre vedlikehold og oppgraderinger i boligen, uten abonnement eller kostnad i betaperioden.",
            items=[
                "Ta bilde av et behov i boligen.",
                "Få analyse, oppgaveliste og prisestimat.",
                "Finn relevante produkter.",
                "Velg mellom å gjøre jobben selv eller få hjelp.",
                "Samle utført arbeid og dokumentasjon på boligen.",
                "Påminnelser om kommende vedlikehold.",
            ],
            cta="Søk om gratis betatilgang",
            fine="Ingen betalingskort. Ingen binding. Vi inviterer brukere fortløpende.",
        ),
        form_field="Adressen til boligen", form_label="Adresse", form_cta="Finn min bolig",
        done=("Takk. Vi finner boligen din.", "Vi sier fra når ERA er klar for adressen."),
        story="#boligeier",
    ),
    "styret": dict(
        key="board", nav="Styret", title="ERA for borettslag og sameier",
        label="For styret", hook="Fra vedlikeholdsbehov til ferdig jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler styret, boligeierne og håndverkerne rundt samme eiendom. Få hjelp til å forstå behovene, prioritere tiltak og følge arbeidet helt frem til dokumentert resultat.",
        hero_support="Styret skifter. Planen består.",
        image="/assets/story/block-bikes-v3.jpg", image_pos="50% 50%",
        hero_secondary=("Se hvordan det henger sammen", "/#styret"),
        hero_view=dash("Perrongen Borettslag", "200 boliger · 4 bygg · Eidsvoll · byggeår 1986",
                        kpis=[("Vedlikeholdsstatus", "72 / 100"), ("Neste 12 mnd", "4 tiltak"), ("Planlagt vedlikehold", "3,8 MNOK"), ("Risiko", "2 tiltak")],
                        footer="Eksempeleiendom og -tall. Illustrerer hvordan ERA samler styrets beslutningsgrunnlag."),
        app_sections=[
            app_section(
                "Planlegg vedlikehold", "Se hva som kommer – før det blir akutt.",
                "ERA samler tiltak, prioriteringer og kostnader i en levende vedlikeholdsplan som oppdateres når eiendommen endrer seg.",
                '<div class="appsec-dash">' + dash("10-årig vedlikeholdsplan", "Perrongen Borettslag",
                    groups=[("planned", [("2027 · Fasade", "1,2 MNOK"), ("2028 · Ventilasjon", "650 000 kr"), ("2029 · Soilrør", "4,8 MNOK"), ("2030 · Tak", "2,1 MNOK"), ("2031 · Vinduer", "1,8 MNOK")])],
                    footer="Eksempeldata. Tidspunkt og kostnad er anslag som oppdateres etter hvert som tilstand og pris avklares.") + '</div>',
                alt_bg=True, sid="vedlikeholdsplan"),
            app_section(
                "ERA hjelper styret prioritere", "Beslutningsstøtte, ikke en chatbot.",
                "Basert på vedlikeholdsplanen, registrert tilstand og risiko foreslår ERA hva styret bør prioritere først, med begrunnelse og kostnadsestimat.",
                '<div class="appsec-dash">' + dash("ERA Styre-agent", "«Hva bør styret prioritere de neste 24 månedene?»",
                    groups=[("ai", [("1. Soilrør", "Høy prioritet · estimert 4,2–5,0 MNOK"), ("2. Fasade", "Planlegg innen 18 måneder · estimert 1,0–1,3 MNOK"), ("3. Ventilasjon", "Bør kartlegges · estimert 80 000–120 000 kr")])],
                    footer="Eksempeldata. ERA foreslår og begrunner; styret vurderer og beslutter.") + '</div>',
                flip=True, sid="styre-agent"),
        ],
        scenes=dict(
            eyebrow="Fra behov til ferdig jobb", title="Én eiendom. Én sammenhengende vedlikeholdsflyt.",
            lede="Følg det samme fasadebehovet fra første funn til gjennomført og dokumentert arbeid. Beboerne er med hele veien: hver boligeier får egen boligoversikt, vedlikeholdsplan og påminnelser gjennom ERA for boligeiere.",
            items=[
                dict(nav="Oversikt", heading="Hva trenger bygget deres nå?",
                     text="Rapporter, tidligere arbeid og innmeldte behov gir styret ett samlet utgangspunkt.",
                     value="ERA skiller dokumenterte funn fra forslag som styret må vurdere.",
                     view=dash("Eiendomsoversikt", "Samlet utgangspunkt for styret",
                               kpis=[("Eiendom", "Perrongen Borettslag"), ("Boliger", "200 · 4 bygg"), ("Område", "Fasade"), ("Sist utført", "Malt 2012")],
                               groups=[("doc", [("Tilstandsrapport 2021", "Maling flasser på sør- og vestvegg"), ("Innmeldt behov", "Avskalling ved inngang B")]),
                                       ("ai", [("Forslag", "Befaring innen 12 måneder")])],
                               footer="Eksempeldata. ERA-forslag vurderes og besluttes av styret.")),
                dict(nav="Prioritering", heading="Fra rapport til neste steg.",
                     text="Det dokumenterte behovet omformes til et konkret tiltak i vedlikeholdsplanen.",
                     value="Styret ser hvorfor tiltaket foreslås, når det bør vurderes og hvilket grunnlag det bygger på.",
                     view=dash("Vedlikeholdsplan", "Forslag fra ERA, til styrets vurdering",
                               kpis=[("Foreslått tiltak", "Male sør- og vestvegg"), ("Anbefalt år", "2027"), ("Kostnadsintervall", "1,0–1,3 mill"), ("Status", "Til vurdering")],
                               groups=[("doc", [("Funn", "Maling flasser, sør- og vestvegg · rapport 2021"), ("Egen oppgave i totalplanen", "Tak · 2031")]),
                                       ("ai", [("Grunnlag", "Rapport 2021 og innmeldt avskalling"), ("Per bolig", "ca. 5 000–6 500 kr")])],
                               footer="Eksempeldata. Styret vurderer og beslutter; ERA foreslår.")),
                dict(nav="Beslutning", heading="Et tydelig behov. Et tydelig oppdrag.",
                     text="Tiltaket tas videre som arbeidsbeskrivelse og beslutningsgrunnlag for styret.",
                     value="Samme informasjon gjenbrukes uten at prosjektet må bygges opp på nytt.",
                     view=dash("Oppdragsgrunnlag", "Fasade 2027 · fra vedlikeholdsplanen", tag="illustration",
                               cols=[("doc", [("Omfang", "Sør- og vestvegg, vask, sparkling, 2 strøk"), ("Vedlegg", "Bilder og rapport"), ("Ønsket tid", "Mai–juni 2027")]),
                                     ("board", [("Forutsetninger", "Stillas, adkomst inngang B"), ("Beslutning", "Styremøte 14. mars")]),
                                     ("pro", [("Tilbud", "3 mottatt på samme omfang"), ("Spenn", "1,05–1,25 mill")])],
                               footer="Eksempeldata. Sammenligning av tilbud vises som illustrasjon av arbeidsflyten.")),
                dict(nav="Gjennomføring", heading="Samme prosjekt. Alle vet hva som skjer.",
                     text="Styret, håndverkeren og beboerne møter samme prosjekt, med informasjon tilpasset sin rolle.",
                     value="Hver rolle ser det som gjelder dem. Beboerne ser fellesarbeidet, ikke styrets saksbehandling.",
                     view=dash("Fasade 2027", "Tre roller, samme prosjekt",
                               cols=[("board", [("Fremdrift", "Uke 2 av 6, i rute"), ("Avklaring", "Farge på beslag, svar innen fredag")]),
                                     ("pro", [("Arbeidsgrunnlag", "Omfang, bilder og avtalt tid"), ("Dokumentasjon", "Bilder legges inn underveis")]),
                                     ("resident", [("Når", "Stillas ved inngang B, uke 20–25"), ("Praktisk", "Balkonger ryddes før 12. mai")])],
                               footer="Eksempeldata. Varsling til beboere vises som illustrasjon av arbeidsflyten.")),
                dict(nav="Dokumentasjon", heading="Jobben er ferdig. Historikken lever videre.",
                     text="Utført arbeid, bilder og produkter samles på eiendommen, og vedlikeholdsplanen oppdateres.",
                     value="Neste styre starter med historikken, ikke fra null.",
                     view=dash("Dokumentasjon", "Fasade 2027",
                               kpis=[("Fasade", "Ferdigstilt"), ("Utført arbeid", "Sør- og vestvegg, 2 strøk"), ("Produkter", "Maling og grunning, dokumentert"), ("Vedlikeholdsplan", "Oppdatert")],
                               groups=[("doc", [("Bilder", "18 før og etter"), ("Utført av", "Malermester Berg AS")]),
                                       ("ai", [("Foreslått neste fasadekontroll", "2032")]),
                                       ("illustration", [("Påminnelse", "Fasadekontroll 2032")])],
                               footer="Eksempeldata. En ryddig logg, ikke en garanti. Taket står som egen oppgave i totalplanen.")),
            ],
        ),
        aside=dict(
            label="Beboerverdi", heading="Verdi for styret. Hjelp til hver bolig.",
            text="Styret får oversikt over felles vedlikehold. Boligeieren får relevant informasjon om fellesarbeidet, og hjelp til å følge opp egen bolig med dokumentasjon, vedlikeholdsplan og påminnelser. Fellesareal og privat bolig holdes adskilt: privat boligdokumentasjon deles ikke automatisk med styret.",
            link="Se ERA for boligeiere →", href="/boligeier",
        ),
        gains=[
            ("Forstå hva bygget trenger", "Eiendommens dokumentasjon og innmeldte behov blir grunnlag for foreslåtte tiltak, prioritering og vedlikeholdsplan."),
            ("Ta tiltakene videre", "Styret vurderer underlaget, beslutter og følger opp arbeidet med håndverkeren."),
            ("Bevar resultatet", "Utført arbeid dokumenteres, beboerne informeres og historikken følger eiendommen videre."),
        ],
        faq=[
            ("Passer ERA for små sameier?", "Ja. Et sameie med fire seksjoner har de samme spørsmålene som ett med førti. Planen skalerer."),
            ("Erstatter ERA forretningsfører?", "Nei. ERA holder orden på bygget, ikke regnskapet. Forretningsføreren kan få tilgang til planen."),
            ("Vi har allerede et styresystem. Hvor passer ERA inn?", "ERA samler oppfølgingen av eiendommen fra vedlikeholdsbehov til gjennomført og dokumentert arbeid. I en demo ser vi på hvordan dere jobber i dag, og hvor ERA kan bidra i arbeidsflyten deres."),
            ("Hvem eier dataene?", "Eiendommen. Styret bestemmer hvem som ser dem. Ved styreskifte følger alt med."),
        ],
        closing=dict(
            heading="Hva er neste tiltak for deres eiendom?",
            lede="Se hvordan ERA kan hjelpe dere fra første vurdering til ferdig dokumentert arbeid, med styret, boligeierne og håndverkeren i samme flyt.",
        ),
        intents=[
            ("demo", "Book en demo", "Takk. Vi tar kontakt for å avtale en demo.", "Du hører fra oss med forslag til tidspunkt."),
            ("interest", "Meld interesse", "Takk. Vi ser på eiendommen.", "Vi tar kontakt med et forslag til plan, klart til neste møte."),
        ],
        form_field="Adressen til bygget", form_label="Adresse", form_cta="Book en demo",
        done=("Takk. Vi tar kontakt for å avtale en demo.", "Du hører fra oss med forslag til tidspunkt."),
        story="#styret",
    ),
    "handverker": dict(
        key="pro", nav="Håndverker", title="ERA for håndverkere",
        label="For håndverkere", hook="Fra kundens boligbehov til din neste jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler boligeiere, styrer og håndverkere. Ta kundens behov videre til befaring, tilbud og gjennomføring, og la dokumentasjonen følge boligen når jobben er ferdig.",
        hero_support="Du kan faget. ERA hjelper deg med flyten rundt jobben.",
        image="/assets/story/painter-v3.jpg", image_pos="30% 50%",
        hero_secondary=("Følg et oppdrag", "#slik"),
        scenes=dict(
            eyebrow="Fra henvendelse til ferdig jobb", title="Ett prosjekt. Fem hendelser.",
            lede="Følg det samme maleprosjektet fra kundens henvendelse til dokumentert overlevering. Kunden beskriver og godkjenner; du vurderer, utfører og dokumenterer.",
            items=[
                dict(nav="Oppdrag", heading="Se hva kunden trenger. Før du drar.",
                     text="Kundens beskrivelse, bilder og tilgjengelig boliginformasjon følger henvendelsen.",
                     value="Du vurderer jobben og forbereder befaringen på et bedre grunnlag.",
                     view=dash("Oppdragsgrunnlag", "Male stue · fra kundens henvendelse",
                               kpis=[("Adresse", "Borgveien 14"), ("Rom", "Stue, 2 vegger"), ("Bilder", "4 vedlagt"), ("Ønsket tid", "Uke 38–40")],
                               groups=[("ai", [("Anslått flate", "ca. 42 m²")]),
                                       ("check", [("Forbehandling", "Sjekkes på befaring")])],
                               footer="Eksempeldata. Bare det kunden har delt vises; ERA-forslaget er et utgangspunkt, ikke en fasit.")),
                dict(nav="Tilbud", heading="Ta befaringen videre til et tydelig tilbud.",
                     text="Mål, bilder og notater samles på oppdraget. ERA hjelper deg å strukturere arbeidsbeskrivelsen og kalkylen.",
                     value="Du vurderer mengder, pris og tilbud før det sendes.",
                     view=dash("Tilbudsutkast", "Male stue · bygget på befaringsnotatene",
                               kpis=[("Omfang", "Vegger, 2 strøk"), ("Forbehandling", "Lett sparkling"), ("Ønsket tid", "Uke 38–40"), ("Kundens estimat", "ca. 6 800 kr")],
                               groups=[("customer", [("Materialer", "Ligger klart i planen")]),
                                       ("ai", [("Kalkyle", "Strukturert fra mål og notater, du justerer")])],
                               footer="Eksempeldata. Tilbudet sendes først når du har godkjent det.")),
                dict(nav="Avtale", heading="Avklart med kunden. Klart for oppstart.",
                     text="Avtalt omfang, materialbehov og prosjektinformasjon holdes samlet, så du og kunden vet hva som skal gjøres.",
                     value="Produkter og mengder kommer fra planen. Kunden velger levering.",
                     view=dash("Arbeidsgrunnlag", "Male stue · godkjent av kunde",
                               kpis=[("Omfang", "Vegger, 2 strøk"), ("Avtalt oppstart", "Uke 38"), ("Materialpris", "ca. 1 900 kr"), ("Status", "Godkjent")],
                               groups=[("ai", [("Produkter fra planen", "2 × maling 10 L, 1 × sparkel 5 kg, 2 ruller")]),
                                       ("order", [("Bestilling", "Én bestilling fra planen, uavhengig av kjede"), ("Levering", "Kjøres hjem, hentes i butikk, eller du henter")]),
                                       ("pilot", [("Betaling i ERA", "Avtalt beløp og betalingsstatus")])],
                               footer="Eksempeldata. Betaling i ERA er i pilot.")),
                dict(nav="Endring", heading="Kunden vil også male taket.",
                     text="Endringen beskrives med pris og konsekvens for fremdriften, og sendes til kunden for godkjenning før ekstraarbeidet starter.",
                     value="Kunden ser alltid forskjellen på foreslått og godkjent.",
                     view=dash("Endringsordre", "Male stue · tillegg til opprinnelig omfang",
                               kpis=[("Opprinnelig omfang", "Vegger, 2 strøk"), ("Foreslått tillegg", "Tak, 1 strøk"), ("Prisendring", "+ ca. 1 800 kr"), ("Status", "Venter godkjenning")],
                               groups=[("customer", [("Kundens ønske", "Også male taket, samme uke")]),
                                       ("check", [("Fremdrift", "+ 1 dag, avklares med kunden")])],
                               footer="Eksempeldata. Godkjent endring oppdaterer arbeidsgrunnlaget.")),
                dict(nav="Overlevering", heading="Din jobb blir en del av boligens historie.",
                     text="Bilder, produktinformasjon og utført arbeid samles i en ryddig overlevering som kunden beholder i boligen.",
                     value="Arbeidet ditt er synlig for fremtidig oppfølging, med ditt navn på.",
                     view=dash("Overlevering", "Male stue · ferdigstilt",
                               kpis=[("Utført", "Vegger og tak, 2 strøk"), ("Bilder", "6 lagt til"), ("Produkter", "Maling, sparkel, ruller"), ("Status", "Overlevert")],
                               groups=[("doc", [("Boligens historikk", "Utført arbeid, med ditt navn på")]),
                                       ("pilot", [("Betaling i ERA", "Avtalt beløp og om det er gjort opp")])],
                               footer="Eksempeldata. En ryddig logg, ikke en sertifisering eller garanti.")),
            ],
        ),
        roles=[
            ("Boligeier", "Beskriver behovet, og tar stilling til tilbud og endringer underveis."),
            ("Håndverker", "Vurderer, utfører og dokumenterer jobben fra befaring til overlevering."),
            ("Styret", "Følger opp og godkjenner når oppdraget gjelder fellesareal, ikke egen bolig."),
        ],
        roles_note="Ved private oppdrag er boligeieren kunden. Ved fellesarbeid er det styret som bestiller og godkjenner på vegne av sameiet eller borettslaget.",
        gains=[
            ("Forstå oppdraget", "Se kundens behov, bilder og tilgjengelig boliginformasjon før befaringen."),
            ("Ha kontroll på jobben", "Ta underlaget videre til kalkyle, tilbud, avtale og avklarte endringer."),
            ("Overlever med dokumentasjonen på plass", "Samle informasjon underveis, og knytt ferdig arbeid til riktig bolig eller eiendom."),
        ],
        faq=[
            ("Koster det noe å melde interesse?", "Nei. Meld interesse, så tar vi kontakt med vilkårene som gjelder i ditt område når ERA rulles ut der."),
            ("Konkurrerer jeg med mange?", "Kunden ber om tilbud på et beskrevet oppdrag. Du ser omfanget før du bruker tid."),
            ("Hva med dokumentasjon etter jobben?", "Bilder og beskrivelse legges i boligens historikk, og du bygger overleveringen mens du jobber."),
            ("Vi bruker allerede et ordresystem. Hvor passer ERA inn?", "ERA kobler håndverkerens arbeidsflyt til kundens bolig og vedlikeholdsbehov. Relevant informasjon følger oppdraget inn, og dokumentasjonen fra arbeidet følger boligen videre. I en demo ser vi på hvor ERA kan bidra i arbeidsflyten deres."),
        ],
        closing=dict(
            heading="Mer tid til faget. Bedre kontroll på jobben.",
            lede="Se hvordan ERA knytter kundens behov til arbeidsflyten din, fra første henvendelse til ferdig dokumentert oppdrag.",
        ),
        intents=[
            ("interest", "Meld interesse", "Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
            ("demo", "Be om demo", "Takk. Vi tar kontakt for å avtale en demo.", "Du hører fra oss med forslag til tidspunkt."),
        ],
        form_field="Firmanavn eller organisasjonsnummer", form_label="Firma", form_cta="Meld interesse",
        done=("Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
        story="#handverker",
    ),
    "faghandel": dict(
        key="partner", nav="Faghandel", title="ERA for faghandel",
        label="For faghandel", hook="Behovet er beregnet før kunden går i butikken.",
        lede="Riktig produkt, riktig mengde, riktig tid, i én bestilling. Fra boliger og fra hele borettslag. Uavhengig av kjede.",
        image="/assets/story/materials-floor-v3.jpg", image_pos="50% 50%",
        scenes=dict(
            eyebrow="Fra behov til bestilling", title="Behovet er beregnet før kunden går i butikken.",
            lede="Følg ett prosjekt fra beregnet behov til bestilling hos dere, med samme eksempel gjennom alle stegene.",
            items=[
                dict(nav="Behov", heading="ERA beregner behovet.",
                     text="Flate, tilstand og forarbeid gir mengder: 2 × 10 liter maling, 1 × 5 kg sparkel, ruller, pensler, maskering.",
                     value="Kunden trenger ikke regne selv, mengdene følger prosjektet.",
                     view=dash("Beregnet behov", "Male stue · 42 m²",
                               kpis=[("Maling", "2 × 10 L"), ("Sparkel", "1 × 5 kg"), ("Ruller", "2 stk"), ("Maskering", "2 ruller")],
                               footer="Eksempeldata. Mengdene er beregnet for 42 m², to strøk.")),
                dict(nav="Levering", heading="Kunden velger levering.",
                     text="Kjøres hjem, hentes i butikk, eller håndverkeren henter. Kunden bestemmer, dere leverer.",
                     value="Ingen ekstra dialog om levering, valget er tatt før bestillingen når dere.",
                     view=dash("Levering", "Bestilling · Male stua",
                               kpis=[("Valgt levering", "Kjøres hjem"), ("Alternativ", "Hentes i butikk"), ("Alternativ", "Håndverker henter")],
                               footer="Eksempeldata. Kunden bestemmer, dere leverer.")),
                dict(nav="Bestilling", heading="Bestillingen kommer til dere.",
                     text="Riktige varelinjer, riktig mengde, riktig tidspunkt. Hele prosjektet, ikke én boks.",
                     value="Bestillingen er nesten skrevet før kunden har valgt farge.",
                     view=dash("Bestilling · Male stua", "Levering: kjøres hjem",
                               kpis=[("Maling", "2 × 10 L"), ("Sparkel", "1 × 5 kg"), ("Ruller", "2 stk"), ("Pensler", "3 stk")],
                               footer="Eksempeldata. Mengder beregnet for 42 m², to strøk.")),
                dict(nav="Prognose", heading="Neste prosjekt er kjent.",
                     text="Planlagte fasader, tak og vinduer gir prognose. Også når det er 24 seksjoner i et borettslag.",
                     value="Dere kan planlegge lager og bemanning etter det som faktisk kommer.",
                     view=dash("Prognose", "Vedlikeholdsplaner i porteføljen",
                               groups=[("doc", [("Neste 12 mnd", "3 fasadeprosjekter, 1 borettslag · 24 seksjoner")]),
                                       ("ai", [("Forventet volum", "Maling, stillas, tettemidler")])],
                               footer="Eksempeldata. Prognosen bygger på styrenes vedlikeholdsplaner.")),
            ],
        ),
        gains=[
            ("Kvalifisert etterspørsel", "Bestillingen oppstår fra et faktisk behov i boligen, ikke fra inspirasjon."),
            ("Færre feilkjøp og returer", "Mengdene er regnet ut. Kunden kjøper riktig første gang."),
            ("Større kurv", "Hele prosjektet i én bestilling, med forarbeid og verktøy."),
            ("Prognose", "Vedlikeholdsplaner forteller hva som skal kjøpes neste år."),
        ],
        faq=[
            ("Er ERA knyttet til én kjede?", "Nei. ERA kobler behov til partnere uavhengig av kjede. Kunden velger hvor bestillingen går."),
            ("Hvordan får vi bestillingene?", "Vi finner en bestillingsflyt som passer dere. Ta kontakt, så viser vi hvordan."),
            ("Hva med borettslag?", "Styrets vedlikeholdsplan gir store, planlagte bestillinger. Fasade, tak og vinduer, år for år."),
        ],
        form_field="Kjede eller butikk", form_label="Butikk", form_cta="Bli partner",
        done=("Takk. Vi tar kontakt.", "Vi tar kontakt og viser hvordan beregnede behov blir bestillinger hos dere."),
        story="#partnere",
    ),
}

ORDER = ["boligeier", "styret", "handverker", "faghandel"]


SITE = "https://era-story.vercel.app"


def head_meta(path, title, description):
    """Sharing metadata + cookieless Vercel analytics (enable Web Analytics once in the dashboard)."""
    return f'''<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ERA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{SITE}/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:locale" content="nb_NO">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{SITE}/og.jpg">
<script defer src="/_vercel/insights/script.js"></script>'''


MENU = [("/", "Historien"), ("/boligeier", "Boligeier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/om-era", "Om ERA"), ("/personvern", "Personvern")]


def nav_html(current, cta_label, cta_href):
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if h == "/" + current else ""}>{esc(l)}</a>' for h, l in MENU if h != "/personvern")
    panel = "".join(f'<a href="{h}" data-menu-close="1">{esc(l)}<span>→</span></a>' for h, l in MENU)
    return f'''<nav class="nav" aria-label="Hovedmeny">
  <div class="pill">
    <a class="brand" href="/">era<span>.</span></a>
    <div class="links">{links}</div>
    <div class="right"><a class="cta" href="{cta_href}">{cta_label}</a><button type="button" class="menu-btn" data-menu-toggle="1" aria-label="Åpne menyen" aria-expanded="false">☰</button></div>
  </div>
  <div class="menu-panel" hidden>{panel}</div>
</nav>'''


def page(slug, a):
    cur = ' aria-current="page"'
    beta = a.get("beta")
    nav_links = "".join(
        f'<a href="/{s}"{cur if s == slug else ""}>{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER
    )
    def step_li(i, step):
        h, t = step[0], step[1]
        detail = ""
        if len(step) > 2:
            label, html = step[2]
            detail = f'<details class="step-detail"><summary>{esc(label)} <span class="chev" aria-hidden="true">⌄</span></summary>{html}</details>'
        return f'<li><span class="n">0{i+1}</span><div><h3>{esc(h)}</h3><p>{esc(t)}</p>{detail}</div></li>'
    steps = "".join(step_li(i, s) for i, s in enumerate(a.get("steps", [])))
    steps_label = a.get("steps_label", "Slik fungerer det")
    steps_title = a.get("steps_title", "Fire steg. Ingen gjetting.")
    steps_intro = f'<p class="steps-intro">{esc(a["steps_intro"])}</p>' if a.get("steps_intro") else ""
    scenes_section = ""
    if a.get("scenes"):
        sc = a["scenes"]
        items = sc["items"]
        tabs = "".join(
            f'<button type="button" role="tab" id="tab-{i+1}" aria-selected="{"true" if i == 0 else "false"}" aria-controls="scene-{i+1}" tabindex="{0 if i == 0 else -1}"><span class="n">0{i+1}</span><span class="t">{esc(it["nav"])}</span></button>'
            for i, it in enumerate(items))
        def scene_nav(i):
            prev = f'<button type="button" class="scene-prev" data-dir="-1">← Forrige</button>' if i > 0 else '<span></span>'
            if i < len(items) - 1:
                nxt = f'<button type="button" class="scene-next" data-dir="1">Neste: {esc(items[i+1]["nav"])} →</button>'
            else:
                nxt = f'<a class="scene-next" href="#skjema">{esc(a["form_cta"])}</a>'
            return f'<div class="scene-nav">{prev}{nxt}</div>'
        panels = "".join(
            f'<div class="scene" role="tabpanel" id="scene-{i+1}" aria-labelledby="tab-{i+1}"{"" if i == 0 else " hidden"}>'
            f'<div class="scene-text"><div class="label">Steg {i+1} · {esc(it["nav"])}</div><h3>{esc(it["heading"])}</h3><p>{esc(it["text"])}</p>'
            f'<p class="scene-value">{esc(it["value"])}</p></div>'
            f'<div class="scene-view">{it["view"]}</div>{scene_nav(i)}</div>'
            for i, it in enumerate(items))
        scenes_section = (
            '<section class="section scenes" id="slik"><div class="wrap wide">'
            f'<div class="label">{esc(sc["eyebrow"])}</div><h2>{esc(sc["title"])}</h2><p class="steps-intro">{esc(sc["lede"])}</p>'
            f'<div class="stepnav" role="tablist" aria-label="{len(items)} steg" style="grid-template-columns: repeat({len(items)}, minmax(0, 1fr))">{tabs}</div>'
            f'<div class="scene-panel">{panels}</div>'
            '</div></section>'
        )
    steps_section = scenes_section or (
        '<section class="section" id="slik">'
        f'<div class="label">{esc(steps_label)}</div><h2>{esc(steps_title)}</h2>{steps_intro}'
        f'<ol class="steps">{steps}</ol></section>'
        if a.get("steps") else ""
    )
    if beta:
        hero_secondary = (beta["cta_secondary"], "#slik")
    else:
        hero_secondary = a.get("hero_secondary", ("Se det i historien →", "/" + a["story"]))
    aside_section = ""
    if a.get("aside"):
        ad = a["aside"]
        aside_section = (
            '<section class="section"><div class="wrap narrow aside">'
            f'<div class="label">{esc(ad["label"])}</div><h2>{esc(ad["heading"])}</h2>'
            f'<p class="aside-text">{esc(ad["text"])}</p>'
            f'<a class="link dark" href="{ad["href"]}">{esc(ad["link"])}</a>'
            '</div></section>'
        )
    roles_section = ""
    if a.get("roles"):
        roles_html = "".join(f'<div class="role"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in a["roles"])
        roles_note = f'<p class="fine dark2">{esc(a["roles_note"])}</p>' if a.get("roles_note") else ""
        roles_section = (
            '<section class="section alt"><div class="wrap">'
            '<div class="label">Roller</div><h2>Hvem gjør hva.</h2>'
            f'<div class="roles">{roles_html}</div>{roles_note}'
            '</div></section>'
        )
    features_section = ""
    if a.get("features"):
        features_html = "".join(f'<details><summary>{esc(t)}</summary><p>{esc(txt)}</p></details>' for t, txt in a["features"])
        features_section = (
            '<section class="section" id="funksjoner"><div class="wrap narrow">'
            '<div class="label">Underveis</div><h2>Funksjonene du bruker.</h2>'
            f'<div class="faq features">{features_html}</div>'
            '</div></section>'
        )
    closing = a.get("closing", {})
    closing_head = closing.get("heading", a["hook"])
    closing_lede = closing.get("lede", a["lede"])
    closing_note = f'<p class="fine">{esc(closing["note"])}</p>' if closing.get("note") else ""
    intents = a.get("intents") or []
    intent_toggle = ""
    intents_attr = ""
    if intents:
        intent_toggle = '<div class="intent" role="group" aria-label="Hva ønsker du?">' + "".join(
            f'<button type="button" data-intent="{k}" data-label="{esc(lbl)}" aria-pressed="{"true" if i == 0 else "false"}">{esc(lbl)}</button>'
            for i, (k, lbl, _h, _s) in enumerate(intents)
        ) + '</div>'
        intents_attr = ' data-intents="' + esc(json.dumps({k: [h, sub] for k, _l, h, sub in intents}, ensure_ascii=False)) + '"'
    intent_field = f'<input type="hidden" name="intent" value="{intents[0][0]}">' if intents else ""
    gains = "".join(f'<div class="gain"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in a["gains"])
    example_section = ""
    if a.get("example"):
        ex = a["example"]
        rows = "".join(f'<div class="row"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in ex["rows"])
        example_section = (
            '<section class="section"><div class="example"><div class="card">'
            f'<div class="card-head"><span class="label">{esc(ex["title"])}</span><span class="meta">{esc(ex["meta"])}</span></div>'
            f'{rows}</div><div class="example-text"><h2>Slik ser det ut.</h2><p>{esc(ex["note"])}</p></div></div></section>'
        )
    faq = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in a["faq"])
    beta_section = ""
    if beta:
        beta_items = "".join(f"<li>{esc(it)}</li>" for it in beta["items"])
        beta_section = (
            '<section class="section dark beta"><div class="wrap narrow">'
            f'<h2>{esc(beta["heading"])}</h2>'
            f'<p class="lede light">{esc(beta["lede"])}</p>'
            f'<ul class="beta-items">{beta_items}</ul>'
            f'<a class="btn" href="#skjema">{esc(beta["cta"])}</a>'
            f'<p class="fine">{esc(beta["fine"])}</p>'
            '</div></section>'
        )
    others = [s for s in ORDER if s != slug]
    other_links = " · ".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in others)
    done_head, done_sub = a["done"]
    hero_mod, hero_wrap, hero_visual = "", "hero-plain", ""
    hero_media = ('<div class="hero-media"><img src="' + a["image"] + '" srcset="' + a["image"][:-4]
                  + '-m.jpg 1400w, ' + a["image"] + ' 3000w" sizes="100vw" alt="" style="object-position: '
                  + a["image_pos"] + '"></div>')
    ah = a.get("app_hero")
    if ah:
        # On this page the product IS the app, so the hero shows the app, not a photo of a house.
        hero_mod, hero_wrap, hero_media = " hero--product", "hero-grid", ""
        hero_visual = '<div class="hero-visual">' + phone(ah["src"], ah["w"], ah["h"], ah["alt"], ah.get("size", "lg"), eager=True) + '</div>'
    elif a.get("hero_view"):
        # A dashboard-style KPI card floats over the property photo (kept, unlike app_hero above)
        # so the hero still shows the physical asset alongside the decision-support view of it.
        hero_visual = '<div class="hero-dash">' + a["hero_view"] + '</div>'
    product_story = "".join(a.get("app_sections", []))
    is_svg = a["image"].endswith(".svg")
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(a["title"])} — ERA</title>
<meta name="description" content="{esc(a["lede"])}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/" + slug, a["title"] + " — ERA", a["lede"])}
<link rel="preload" href="/fonts/d09f6137-d0ab-46d2-a3bf-0d7be812fb75.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body data-audience="{a["key"]}">
{nav_html(slug, esc(a["form_cta"]), "#skjema")}

<header class="hero{hero_mod}">
  {hero_media}
  <div class="{hero_wrap}">
  <div class="hero-text">
    <div class="label">{esc(a["label"])}</div>
    <h1>{soften(esc(a["hook"]))}</h1>{f'<div class="beta-badge">{esc(beta["badge"])}</div><p class="beta-note">{esc(beta["note"])}</p>' if beta else ''}
    <p class="lede">{esc(a["lede"])}</p>{f'<p class="hero-support">{esc(a["hero_support"])}</p>' if a.get("hero_support") else ''}
    <div class="hero-actions"><a class="btn" href="#skjema">{esc(beta["cta_primary"] if beta else a["form_cta"])}</a><a class="link" href="{hero_secondary[1]}">{esc(hero_secondary[0])}</a></div>
  </div>
  {hero_visual}
  </div>
</header>

<main>
  {product_story}

  {steps_section}

  {aside_section}

  {roles_section}

  {features_section}

  {beta_section}

  <section class="section alt">
    <div class="wrap">
      <div class="label">Det får {"dere" if a["key"] in ("board", "partner") else "du"}</div>
      <h2>Gevinsten</h2>
      <div class="gains">{gains}</div>
    </div>
  </section>

  {example_section}

  <section class="section alt">
    <div class="wrap narrow">
      <div class="label">Spørsmål</div>
      <h2>Det folk lurer på.</h2>
      <div class="faq">{faq}</div>
    </div>
  </section>

  <section class="section dark" id="skjema">
    <div class="wrap narrow">
      <div class="brand big">era<span>.</span></div>
      <h2>{esc(closing_head)}</h2>
      <p class="lede light">{esc(closing_lede)}</p>
      {intent_toggle}
      <form id="era-lead" class="lead" data-audience="{a["key"]}"{intents_attr}>
        {intent_field}
        <div class="lead-pill">
          <label class="sr" for="lead-value">{esc(a["form_field"])}</label>
          <div class="lead-value-wrap">
            <input id="lead-value" name="value" type="text" autocomplete="off" required minlength="3" maxlength="200" placeholder="{esc(a["form_field"])}">
            <span id="lead-typewriter" aria-hidden="true"></span>
            <span class="field-label" aria-hidden="true">{esc(a["form_label"])}</span>
          </div>
          <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
          <button type="submit">{esc(a["form_cta"])}</button>
        </div>
      </form>
      <div class="done" role="status" aria-live="polite" hidden>
        <div class="check"><svg width="20" height="16" viewBox="0 0 20 16" fill="none"><path d="M2 8L7.5 13.5L18 2" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div><b>{esc(done_head)}</b><span>{esc(done_sub)}</span></div>
      </div>
      <div class="err" hidden></div>
      <p class="fine">Ingen binding. Dataene lagres kryptert i Norge og brukes bare til å ta kontakt.</p>
      {closing_note}
    </div>
  </section>
</main>

<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>
<script src="/pages.js" defer></script>
</body>
</html>
'''


PRIVACY_DESC = "Hva ERA lagrer når du bruker skjemaene på denne siden, hvor det lagres, hvor lenge, og hvordan du får det slettet."


def privacy_page():
    """Honest to what the site actually does today: one form, one private store in the EU, no cookies."""
    sections = [
        ("Hva vi samler inn", [
            "Når du sender inn skjemaet på historien eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede eller butikk), hvilken målgruppe du leste som (boligeier, styret, håndverker eller faghandel), om du ba om en demo, tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
            "Vi samler ikke inn navn, e-post eller telefonnummer gjennom skjemaet i dag, og vi lagrer ikke IP-adressen din.",
        ]),
        ("Hvorfor", [
            "For å ta kontakt om ERA for den adressen, eiendommen eller virksomheten du meldte inn. Ikke til noe annet. Vi selger eller deler ikke opplysningene.",
        ]),
        ("Hvor og hvor lenge", [
            "Opplysningene lagres kryptert hos vår driftsleverandør Vercel, i et privat lager i Frankfurt (EU/EØS). Bare ERA technologies AS har tilgang.",
            "Vi sletter innsendingen senest tolv måneder etter at den kom inn, eller så snart du ber om det.",
        ]),
        ("Informasjonskapsler og analyse", [
            "Siden setter ingen informasjonskapsler. Vi bruker Vercel Web Analytics, som teller sidevisninger uten cookies og uten å identifisere deg. Derfor trenger vi ikke et samtykkebanner.",
        ]),
        ("Dine rettigheter", [
            "Du kan når som helst be om innsyn i, retting av eller sletting av det du har sendt inn. Send oss en melding via skjemaet på siden med «personvern» først i teksten, så svarer vi. Behandlingsansvarlig er ERA technologies AS, Oslo.",
        ]),
    ]
    body = "".join(f'<section class="pv"><h2>{esc(h)}</h2>{"".join(f"<p>{esc(p)}</p>" for p in ps)}</section>' for h, ps in sections)
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Personvern — ERA</title>
<meta name="description" content="{esc(PRIVACY_DESC)}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/personvern", "Personvern — ERA", PRIVACY_DESC)}
<link rel="preload" href="/fonts/d09f6137-d0ab-46d2-a3bf-0d7be812fb75.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body class="light">
{nav_html("personvern", "Til historien", "/")}
<main class="doc">
  <div class="wrap narrow">
    <div class="label">Personvern</div>
    <h1>Din bolig. Dine data.</h1>
    <p class="lede dark">ERA lagrer boligens historie for deg, ikke om deg. Her står nøyaktig hva denne nettsiden gjør med det du sender inn.</p>
    <p class="fine dark">Sist oppdatert 4. september 2026.</p>
    {body}
  </div>
</main>
<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>
<script src="/pages.js" defer></script>
</body>
</html>
'''


for slug in ORDER:
    d = os.path.join(ROOT, slug)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(page(slug, AUDIENCES[slug]))
    print("wrote", slug)
os.makedirs(os.path.join(ROOT, "personvern"), exist_ok=True)
with open(os.path.join(ROOT, "personvern", "index.html"), "w", encoding="utf-8") as f:
    f.write(privacy_page())
print("wrote personvern")
