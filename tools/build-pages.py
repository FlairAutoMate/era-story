# -*- coding: utf-8 -*-
"""Generates the audience subpages (/boligeier, /styret, /handverker, /faghandel) from one
template and one content dict. Run from the project root: python tools/build-pages.py"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(t):
    return html.escape(t, quote=True)


TAG_LABELS = {"customer": "Fra kunden", "doc": "Dokumentert", "ai": "ERA-forslag", "check": "Avklares på befaring", "board": "Styret", "pro": "Håndverker", "resident": "Beboer", "order": "Bestilling og levering", "pilot": "I pilot", "planned": "Planlagt", "illustration": "Illustrasjon av arbeidsflyt", "missing": "Mangler"}


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


def next_steps_section(eyebrow, title, lede, cards, sid, foot=None):
    """A full-width three-card section for what comes after ERA has identified a need: not a
    fourth product screen, just a short next-step link per path (insurance, financing, execution).
    Deliberately non-promissory copy — see the cards passed in."""
    cards_html = "".join(
        f'<div class="nstep"><h3>{esc(h)}</h3>' + (f'<span class="nstep-tag">{esc(tag[0])}</span>' if tag else "") + f'<p>{esc(t)}</p>'
        + (f'<a class="link" href="{href}">{esc(link_text)} →</a>' if href else "")
        + '</div>'
        for h, t, link_text, href, *tag in cards)
    foot_html = f'<p class="fine dark2">{esc(foot)}</p>' if foot else ""
    return (f'<section class="section" id="{sid}"><div class="wrap">'
            f'<div class="label">{esc(eyebrow)}</div><h2>{esc(title)}</h2>'
            f'<p class="lede dark">{esc(lede)}</p>'
            f'<div class="nsteps">{cards_html}</div>{foot_html}'
            '</div></section>')


def app_loop(eyebrow, title, steps, foot, cols=5):
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
            f'<div class="apploop{" apploop--4" if cols == 4 else ""}">{shots}</div>'
            f'<div class="apploop-steps{" apploop-steps--4" if cols == 4 else ""}">{labels}</div>'
            f'<p class="fine dark2">{esc(foot)}</p>'
            '</div></section>')


PRIORITY_LABELS = {"high": "Høy prioritet", "med": "Middels prioritet", "low": "Lav prioritet"}


def priority_dot(level):
    return f'<span class="pdot pdot-{level}" aria-hidden="true"></span>'


def maintenance_plan_view(title, meta, kpis, rows, footer):
    """The 10-year plan view: a dot-coded priority timeline plus filter-style KPI counts,
    built from the same .dash/.kpi/.drow parts as dash() so it stays visually consistent."""
    kpi_html = '<div class="kpis">' + "".join(
        f'<div class="kpi"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in kpis) + '</div>'
    row_html = '<div class="dash-group plan-rows">' + "".join(
        f'<div class="drow plan-row"><span>{priority_dot(level)}{esc(year)} · {esc(name)}</span>'
        f'<b>{esc(cost)}<i class="plan-pri">{esc(PRIORITY_LABELS[level])}</i></b></div>'
        for year, name, cost, level in rows) + '</div>'
    return (f'<div class="dash"><div class="dash-head"><div><div class="dash-title">{esc(title)}</div>'
            f'<div class="dash-meta">{esc(meta)}</div></div></div>{kpi_html}{row_html}'
            f'<div class="dash-foot">{esc(footer)}</div></div>')


def styre_agent_view(question, answer_lede, picks, footer, title="ERA Styre-agent", meta="Beslutningsstøtte basert på eiendomsdata"):
    """The ERA Styre-agent view: a question bubble, a short answer, and a numbered priority list."""
    picks_html = "".join(
        f'<div class="agent-pick"><span class="agent-n">{i+1}</span>'
        f'<div><b>{esc(name)}</b><span>{esc(detail)}</span></div></div>'
        for i, (name, detail) in enumerate(picks))
    return (
        '<div class="dash agent-dash">'
        f'<div class="dash-head"><div><div class="dash-title">{esc(title)}</div>'
        f'<div class="dash-meta">{esc(meta)}</div></div></div>'
        f'<div class="agent-q">{esc(question)}</div>'
        f'<div class="agent-a"><p>{esc(answer_lede)}</p>{picks_html}</div>'
        f'<div class="dash-foot">{esc(footer)}</div></div>'
    )


def offer_comparison_view(title, meta, offers, recommended, footer):
    """The offer-comparison view: three vendor rows with an initial-circle avatar, price and
    lead time, one marked as ERA's recommendation."""
    rows = "".join(
        f'<div class="offer-row{" offer-row--rec" if name == recommended else ""}">'
        f'<span class="agent-n offer-av">{esc(name[0])}</span>'
        f'<div class="offer-main"><b>{esc(name)}</b><span>{esc(scope)}</span></div>'
        f'<div class="offer-price"><b>{esc(price)}</b><span>{esc(weeks)}</span></div>'
        + (f'<span class="offer-tag">Anbefalt</span>' if name == recommended else "")
        + '</div>'
        for name, scope, price, weeks in offers)
    return (f'<div class="dash offer-dash"><div class="dash-head"><div><div class="dash-title">{esc(title)}</div>'
            f'<div class="dash-meta">{esc(meta)}</div></div></div>'
            f'<div class="offer-rows">{rows}</div>'
            f'<div class="dash-foot">{esc(footer)}</div></div>')


def resident_notice_view(title, meta, recipients, body, checklist, footer):
    """The resident-notification view: a message preview plus a short 'what happens next'
    checklist, reusing the agent-bubble look for the message body."""
    check_html = "".join(f'<li>{esc(item)}</li>' for item in checklist)
    return (
        '<div class="dash notice-dash">'
        f'<div class="dash-head"><div><div class="dash-title">{esc(title)}</div>'
        f'<div class="dash-meta">{esc(meta)}</div></div></div>'
        f'<div class="kpis"><div class="kpi"><span>Varsel sendes til</span><b>{esc(recipients)}</b></div></div>'
        f'<div class="agent-q notice-msg">{esc(body)}</div>'
        f'<div class="notice-next"><span class="notice-next-label">Hva skjer videre?</span><ul>{check_html}</ul></div>'
        f'<div class="dash-foot">{esc(footer)}</div></div>'
    )


def completion_view(title, meta, kpis, docs, footer):
    """The project-completion view: a done badge, outcome KPIs, and a document chip row."""
    kpi_html = '<div class="kpis">' + "".join(
        f'<div class="kpi"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in kpis) + '</div>'
    doc_html = '<div class="doc-chips">' + "".join(
        f'<span class="doc-chip">{esc(d)}</span>' for d in docs) + '</div>'
    return (
        '<div class="dash">'
        '<div class="dash-head"><div><span class="done-badge">✓ Prosjektet er ferdig</span>'
        f'<div class="dash-title" style="margin-top:8px">{esc(title)}</div>'
        f'<div class="dash-meta">{esc(meta)}</div></div></div>'
        f'{kpi_html}{doc_html}'
        f'<div class="dash-foot">{esc(footer)}</div></div>'
    )


def budget_view(title, meta, kpis, rows, financing_note, footer):
    """The budget view: cost-per-year KPIs plus a short, deliberately non-promissory financing
    note — same restrained tone as the boligeier next-steps cards, styled like the agent card."""
    kpi_html = '<div class="kpis">' + "".join(
        f'<div class="kpi"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in kpis) + '</div>'
    row_html = '<div class="dash-group">' + "".join(
        f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows) + '</div>'
    return (
        '<div class="dash"><div class="dash-head"><div><div class="dash-title">' + esc(title) +
        f'</div><div class="dash-meta">{esc(meta)}</div></div></div>'
        f'{kpi_html}{row_html}'
        f'<div class="agent-a"><p>{esc(financing_note)}</p></div>'
        f'<div class="dash-foot">{esc(footer)}</div></div>'
    )


def building_overview_view(title, meta, buildings, footer):
    """The property-map view: one status card per building, so the board sees where attention
    is needed before diving into any single maintenance item."""
    cards = "".join(
        f'<div class="bldg-card{" bldg-card--risk" if risk else ""}">'
        f'<div class="bldg-name">{esc(name)}</div><div class="bldg-meta">{esc(units)}</div>'
        f'<div class="bldg-score"><b>{esc(score)}</b><span>vedlikeholdsstatus</span></div>'
        f'<div class="bldg-tasks">{esc(tasks)}</div>'
        + ('<span class="bldg-flag">Krever oppfølging</span>' if risk else '')
        + '</div>'
        for name, units, score, tasks, risk in buildings)
    return (f'<div class="dash"><div class="dash-head"><div><div class="dash-title">{esc(title)}</div>'
            f'<div class="dash-meta">{esc(meta)}</div></div></div>'
            f'<div class="bldg-grid">{cards}</div>'
            f'<div class="dash-foot">{esc(footer)}</div></div>')


AUDIENCES = {
    "boligeier": dict(
        key="owner", nav="Huseier", title="ERA for huseiere",
        meta="Hjemmets AI-agent for boligeiere. ERA kjenner hjemmet ditt, oppdager hva som bør gjøres først og samler tilstand, historikk og dokumentasjon i én plan.",
        label="For boligeiere", hook="Å eie hjem uten gjetting.",
        lede="ERA forstår hva hjemmet ditt trenger, og hva som bør gjøres først. Tilstand, historikk, dokumentasjon og prioriteringer, samlet i én plan for hjemmet.",
        image="/assets/story/couple-sofa-v3.jpg", image_pos="55% 55%",
        app_hero=dict(src="/assets/story/app-hjem.png", w=935, h=1683, size="lg",
                      alt=f"ERA Bolig på mobil: forsiden for {DEMO_HOME['address']} med boligtype {DEMO_HOME['type']}, "
                          f"{DEMO_HOME['area']}, byggeår {DEMO_HOME['year']}, tilstand {DEMO_HOME['condition']} "
                          f"{DEMO_HOME['score']}, neste tiltak «{DEMO_HOME['measure']}», estimert kostnad "
                          f"{DEMO_HOME['cost']} og estimert verdi {DEMO_HOME['value']}"),
        app_sections=[
            app_section(
                "Min bolig", "Alt om hjemmet. Ett sted.",
                "Ikke bare data fra registre. ERA bygger en levende hjemmeprofil som utvikler seg når du legger til rom, dokumentasjon, arbeid og nye opplysninger.",
                phone("/assets/story/app-minbolig.png", 853, 1844,
                      f"ERA Bolig: Min bolig for {DEMO_HOME['address']} – {DEMO_HOME['type']} fra {DEMO_HOME['year']} på "
                      f"{DEMO_HOME['area']} med tilstand {DEMO_HOME['condition']} {DEMO_HOME['score']}, neste prosjekt "
                      f"«{DEMO_HOME['measure']}» til {DEMO_HOME['cost']} med oppstart {DEMO_HOME['start']} og "
                      f"{DEMO_HOME['pro']}, estimert verdi {DEMO_HOME['value']} og samlet dokumentasjon",
                      "lg"),
                alt_bg=True, flip=True, sid="slik"),
            app_section(
                "Kamera", "Vis ERA hva du ser.",
                "Ta et bilde av noe du lurer på. ERA analyserer det sammen med informasjonen den allerede har om hjemmet.",
                phone("/assets/story/app-kamera.png", 853, 1844,
                      "ERA Bolig: kameraet rettet mot avflassende maling på kledningen ved et vindu, med teksten «Ta et bilde – fokuser på problemet, så analyserer ERA det for deg» og valget «Analyser med ERA»",
                      "lg", cap="Eksempeldata · Myrerveien 46A"),
                foot="Du starter med det du faktisk ser, ikke med et skjema."),
            app_section(
                "Boligagent", "Ikke bare et AI-svar. Et svar om hjemmet ditt.",
                "ERA kombinerer det du spør om eller viser med tilgjengelig informasjon om hjemmets alder, historikk, tilstand og tidligere arbeid.",
                phone("/assets/story/app-agent.png", 853, 1844,
                      f"ERA Bolig, boligagenten for {DEMO_HOME['address']}: fotoet av huset er merket av med fasade og tak "
                      "til oppfølging og takrenner og grunnmur i god stand, etterfulgt av «Hva jeg ser» med de fire "
                      f"punktene, «Hva det betyr» for en bolig fra {DEMO_HOME['year']}, og forslaget «{DEMO_HOME['measure']}» "
                      f"med estimert kostnad {DEMO_HOME['cost']}, oppstart {DEMO_HOME['start']} og {DEMO_HOME['pro']}",
                      "lg"),
                points=[("Hva jeg ser", "Fasade og tak bør følges opp. Takrenner og grunnmur er i god stand."),
                        ("Hva det betyr", f"Hjemmet er fra {DEMO_HOME['year']}. Det gjør fasade, tak og el-anlegg verdt å se nærmere på."),
                        ("Mitt forslag", f"«{DEMO_HOME['measure']}» med kostnad, oppstart og en håndverker som kan gjøre jobben.")],
                alt_bg=True, flip=True, sid="boligagent"),
            next_steps_section(
                "Visualiser og velg · Planlagt", "Se det. Velg det. Få det gjort.",
                "Med ERA skal du kunne visualisere hjemmet ditt med ulike farger, produkter og løsninger, og se hvordan resultatet kan bli før du bestemmer deg. Når du har funnet løsningen du ønsker, velger du selv hvordan du vil gå videre – alt hjemme fra sofaen.",
                cards=[
                    ("Gjør jobben selv", "ERA hjelper deg med riktige produkter og mengder. Gjennomfør kjøpet direkte hjemmefra – hent ferdig pakkede varer i butikken, eller få alt levert på døren.", None, None, "Planlagt"),
                    ("Få noen til å gjøre jobben", "Be om tilbud fra en anbefalt håndverker gjennom ERA. Motta og godkjenn tilbudet på telefonen – håndverkeren kjøper inn riktige produkter og gjennomfører jobben.", None, None),
                ],
                sid="visualiser",
                foot="Visualisering og kjøp direkte i ERA er planlagt og ikke tilgjengelig ennå. Tilbud fra håndverker er en del av prosjektflyten."),
            app_section(
                "Prosjekt", "Fra anbefaling til gjennomføring.",
                "Når noe bør gjøres, kan ERA gjøre anbefalingen om til et konkret prosjekt – fra planlegging og tilbud til gjennomføring og dokumentasjon.",
                phone("/assets/story/app-prosjekt.png", 935, 1683,
                      f"ERA Bolig: prosjektet «{DEMO_HOME['measure']}» på {DEMO_HOME['address']} med estimert kostnad "
                      f"{DEMO_HOME['cost']}, oppstart {DEMO_HOME['start']} og varighet {DEMO_HOME['duration']}, "
                      f"{DEMO_HOME['pro']} som utførende, status planlagt og fremdriften kartlagt, tilbud og utføres",
                      "lg", cap="Eksempeldata"),
                points=[("Kartlagt", f"Omfang, kostnad, oppstart og varighet ligger klart: {DEMO_HOME['cost']}, {DEMO_HOME['start']}, {DEMO_HOME['duration']}."),
                        ("Tilbud", f"{DEMO_HOME['pro']} med 4,8 av 32 vurderinger, klar for forespørsel."),
                        ("Utføres", "Fremdriften følger prosjektet til det er ferdig og dokumentert.")],
                foot="Fasadefunnet fra agenten er nå et prosjekt med kostnad, håndverker og fremdrift."),
            next_steps_section(
                "Neste steg · Delvis planlagt", "Når hjemmet trenger mer enn en påminnelse.",
                "ERA kobler det dokumenterte behovet med riktige muligheter for gjennomføring – enten det gjelder forsikring, finansiering eller kvalifiserte fagfolk.",
                cards=[
                    ("Forsikring", "Sjekk om forholdet kan være relevant for forsikringen din, og finn frem nødvendig dokumentasjon.",
                     "Avklar dekning", "#boligagent", "Planlagt"),
                    ("Finansiering", "Få oversikt over forventet kostnad og mulige finansieringsalternativer før du starter prosjektet.",
                     "Se muligheter", "#boligagent", "Planlagt"),
                    ("Gjennomføring", "Gå videre til kvalifisert håndverker med samme dokumentasjon, bilder og prosjektgrunnlag.",
                     "Innhent tilbud", "/handverker"),
                ],
                sid="neste-steg",
                foot="Forsikring og finansiering er planlagt og ikke tilgjengelig ennå. ERA gir grunnlag for å vurdere alternativer. ERA gir ikke forsikrings- eller lånetilsagn, og lover ikke dekning, godkjenning eller vilkår."),
            app_section(
                "Boligminne", "Alt som gjøres blir en del av hjemmet.",
                "Arbeid, dokumentasjon og historikk følger hjemmet videre – slik at du slipper å starte på nytt hver gang noe skal vedlikeholdes, vurderes eller forbedres.",
                ui("/assets/story/app-boligminne.png", 783, 645,
                   "ERA Bolig, boligminnet: tidslinjen 2020 nytt bad, 2022 varmepumpe, 2024 nytt tak og 2026 fasadevask og maling",
                   cap="Eksempeldata · Myrerveien 46A"),
                points=[("Det som er gjort", "Bad, varmepumpe og tak ligger med år og dokumentasjon."),
                        ("Det som kommer", "Fasadeprosjektet fra bildet står som planlagt.")],
                alt_bg=False, flip=True, sid="boligminne"),
            app_loop(
                "Hele loopen", "Fra spørsmål til ferdig dokumentert.",
                [("Hjemmet", "ERA kjenner det.", "/assets/story/app-hjem.png",
                  "ERA Bolig: forsiden for Myrerveien 46A med tilstand og neste tiltak", 935, 1683),
                 ("Kamera", "Vis ERA problemet.", "/assets/story/app-kamera.png",
                  "ERA Bolig: kameraet rettet mot avflassende maling ved et vindu", 853, 1844),
                 ("Boligagent", "Forstå hva det betyr.", "/assets/story/app-agent.png",
                  "ERA Bolig: boligagentens analyse av huset med funn, betydning og forslag", 853, 1844),
                 ("Prosjekt", "Planlegg og gjennomfør.", "/assets/story/app-prosjekt.png",
                  "ERA Bolig: prosjektet «Fasadevask og maling» med kostnad, håndverker og fremdrift", 935, 1683),
                 ("Min bolig", "Dokumenter og husk.", "/assets/story/app-minbolig.png",
                  "ERA Bolig: Min bolig med nøkkeltall, neste prosjekt, estimert verdi og dokumentasjon", 853, 1844)],
                "Eksempeldata. Samme hjem, Myrerveien 46A, gjennom hele loopen."),
        ],
        gains=[
            ("Vit hva som haster", "Og hva som kan vente. Noen ganger er riktig råd å gjøre ingenting ennå."),
            ("Slutt på gjetting", "Kostnad, tid og forarbeid er regnet ut før du bestemmer deg."),
            ("Alt på ett sted", "Dokumentasjonen følger hjemmet, også til neste eier."),
            ("Dine data", "Lagret kryptert innenfor EU/EØS. Du bestemmer hvem som ser dem."),
        ],
        # FAQ-en er kategoriavklarende forst, kjopsnar etterpa. De seks forste staar apent;
        # resten ligger bak «Se alle sporsmal». Rekkefolgen er bevisst: tvilen om hva ERA *er*
        # ryddes for sporsmal om data, handling og pris.
        faq=[
            ("Hva er ERA?",
             "ERA er hjemmets AI-agent. Den bygger kunnskap om hjemmet, oppdager relevante behov og hjelper deg fra "
             "spørsmål til ferdig jobb."),
            ("Hva er forskjellen på ERA og Boligmappa?",
             "Boligmappa er først og fremst et sted for dokumentasjon og historikk knyttet til hjemmet. ERA bygger videre "
             "på samme type kunnskap om hjemmet, men bruker den aktivt: Hva vet vi? → Hva betyr det? → Hva bør gjøres? → Skal "
             "ERA hjelpe deg få det gjort? ERA skal derfor være hjemmets agent, ikke bare hjemmets arkiv."),
            ("Gjelder ERA for leilighet og borettslag, eller bare enebolig?",
             "Begge deler. Den signerte piloten er et borettslag med 69 leiligheter. Bor du i borettslag eller sameie, "
             "får du din egen oversikt over hjemmet, vedlikeholdsplan og påminnelser, samtidig som styret kan bruke ERA for "
             "fellesarealene."),
            ("Hva er forskjellen på ERA og Mittanbud?",
             "Mittanbud blir relevant når du allerede vet at du trenger en håndverker. ERA kan starte tidligere, og hjelpe "
             "deg forstå behovet og vurdere hva som bør gjøres. Deretter velger du:",
             [("Gjør det selv — ", "ERA hjelper med plan, produkter og veiledning."),
              ("Få hjelp av proff — ", "behovet er allerede beskrevet, så du slipper å starte prosessen på nytt.")]),
            ("Hva vet ERA om hjemmet mitt?",
             "ERA starter med det som allerede finnes eller kan hentes inn om hjemmet, og lærer mer etter hvert som du "
             "legger til bilder, dokumenter og informasjon. ERA skiller mellom tre ting:",
             [("Dokumentert — ", "vi vet hvor informasjonen kommer fra."),
              ("ERA-forslag — ", "ERA gjør en vurdering og forklarer hvorfor."),
              ("Mangler — ", "ERA sier fra når informasjonen ikke finnes.")]),
            ("Kan ERA hjelpe meg å gjøre det selv eller finne en proff?",
             "Ja. ERA utvikles for begge veier. Vil du gjøre jobben selv, kan ERA hjelpe med plan → produkter → mengder → "
             "handleliste → veiledning. Vil du heller ha hjelp, kan det samme behovet brukes videre mot en proff."),
            ("Hva koster ERA?",
             "ERA er gratis for huseiere de første tolv månedene. Ingen betalingskort og ingen binding."),

            # ── bak «Se alle spørsmål» ──
            ("Hva er forskjellen på ERA og ChatGPT?",
             "En generell AI kjenner ikke hjemmet ditt. ERA bygger en vedvarende hukommelse rundt ditt konkrete hjem — med "
             "hjemmedata, bilder, dokumentasjon, historikk og det som blir gjort over tid. Derfor kan et spørsmål som «Hva "
             "bør jeg følge opp nå?» besvares i kontekst av akkurat ditt hjem."),
            ("Må jeg ha tilstandsrapport?",
             "Nei. ERA starter med det du har. Jo mer du legger inn, jo mer presis blir planen."),
            ("Må jeg legge inn alt selv?",
             "Nei. Målet er at du skal kunne starte med adressen, og at ERA bygger hjemmeprofilen gradvis. Du skal ikke "
             "måtte fylle ut et langt skjema før ERA blir nyttig."),
            ("Kan jeg ta et bilde og spørre ERA?",
             "Ja. Bilder er en viktig del av ERA-opplevelsen. Du skal kunne vise ERA noe du lurer på, og få hjelp til å "
             "forstå hva du ser i sammenheng med resten av hjemmet. For eksempel:",
             ["«Hva bør jeg gjøre med denne veggen?»",
              "«Bør dette følges opp?»",
              "«Hva trenger jeg hvis jeg vil fikse dette selv?»"]),
            ("Kan ERA hente tilbud fra håndverkere?",
             "ERA har fundamentet for reisen fra behov i hjemmet til konkret arbeid, tilbud, valg av utførende, gjennomføring "
             "og dokumentasjon. Målet er at du skal kunne gå fra «dette bør gjøres» til «få hjelp av proff» uten å "
             "beskrive hele behovet på nytt."),
            ("Får ERA betalt når jeg kjøper noe?",
             "ERA kan få betalt fra partnere når du velger å kjøpe et produkt eller en tjeneste gjennom ERA. Det endrer "
             "ikke at du bestemmer hva du vil gjøre og hvem du vil bruke."),
            ("Hva skjer etter de første tolv månedene?",
             "Prismodellen er ikke fastsatt ennå. Du binder deg ikke til noe, og endringer kommuniseres tydelig før de "
             "trer i kraft."),
            ("Hvorfor er det bare 300 plasser?",
             "Vi begrenser betafasen for å kunne følge opp brukerne tett, forbedre ERA basert på reelle behov i hjemmet og "
             "sikre kvalitet før en bredere lansering."),
            ("Hva skjer når jeg søker om betatilgang?",
             "Du oppgir adressen til hjemmet. Vi sier fra når ERA er klar for den. Ingen binding, og dataene lagres "
             "kryptert i EU/EØS og brukes bare til å ta kontakt."),
            ("Hva skjer når jobben er ferdig?",
             "Resultatet skal tilbake til hjemmet. Bilder, dokumentasjon og relevant historikk gjør hjemmeprofilen bedre, "
             "slik at neste prosjekt ikke starter fra null. Hjemmet husker. Du slipper."),
            ("Følger informasjonen hjemmet over tid?",
             "Det er selve ideen. ERA bygger en digital hukommelse rundt hjemmet, slik at tidligere arbeid, dokumentasjon "
             "og historikk kan gi bedre beslutninger senere."),
            ("Hva skjer med dataene mine?",
             "Du bestemmer hvem som får tilgang. Data om hjemmet deles ikke med håndverkere, partnere eller andre bare "
             "fordi de finnes i ERA. Deling skjer når det er relevant og du velger det. Lagret kryptert innenfor EU/EØS."),
            ("Kan jeg slette alt?",
             "Ja. Du kan når som helst be om innsyn i, retting av eller sletting av det du har sendt inn, også e-posten. "
             "Send en melding via skjemaet med «personvern» først i teksten, så ordner vi det."),
            ("Hvem står bak ERA?",
             "ERA technologies AS, med base i Oslo. Teamet har bakgrunn fra eiendom, bygg, faghandel, teknologi og "
             "finans. Du finner menneskene og hvorfor ERA finnes under Om ERA."),
        ],
        beta=dict(
            badge="Nå i kontrollert beta — åpnes for 300 huseiere",
            note="Gratis de første tolv månedene. Begrenset antall plasser.",
            cta_primary="Søk om betatilgang", cta_secondary="Se hvordan ERA fungerer",
            heading="Bli en av 300 huseiere som tester ERA",
            lede="ERA åpner nå en kontrollert betafase for 300 huseiere. Som betabruker får du hjelp til å forstå, planlegge og gjennomføre vedlikehold og oppgraderinger i hjemmet, uten abonnement eller kostnad de første tolv månedene.",
            items=[
                "Ta bilde av et behov i hjemmet.",
                "Få analyse, oppgaveliste og prisestimat.",
                "Finn relevante produkter.",
                "Velg mellom å gjøre jobben selv eller få hjelp.",
                "Samle utført arbeid og dokumentasjon på hjemmet.",
                "Påminnelser om kommende vedlikehold.",
            ],
            cta="Søk om gratis betatilgang",
            fine="Ingen betalingskort. Ingen binding. Vi inviterer brukere fortløpende.",
        ),
        form_field="Adressen til hjemmet", form_label="Adresse", form_cta="Finn mitt hjem",
        done=("Takk. Vi finner hjemmet ditt.", "Vi sier fra når ERA er klar for adressen."),
        story="#boligeier",
    ),
    "styret": dict(
        key="board", nav="Styret", title="ERA for borettslag og sameier",
        label="For styret", hook="Fra vedlikeholdsbehov til ferdig jobb.",
        lede="ERA er en AI-drevet plattform som kobler styret, eierne og håndverkerne rundt samme eiendom. Få hjelp til å forstå behovene, prioritere tiltak og følge arbeidet helt frem til dokumentert resultat.",
        hero_support="Styret skifter. Planen består.",
        image="/assets/story/block-bikes-v3.jpg", image_pos="50% 50%",
        hero_secondary=("Se hvordan det henger sammen", "/#styret"),
        hero_view=dash("Perrongen Borettslag", "200 hjem · 4 bygg · Eidsvoll · byggeår 1986",
                        kpis=[("Vedlikeholdsstatus", "72 / 100"), ("Neste 12 mnd", "4 tiltak"), ("Planlagt, 10 år", "10,55 MNOK"), ("Risiko", "2 tiltak")],
                        footer="Eksempeleiendom og -tall. Illustrerer hvordan ERA samler styrets beslutningsgrunnlag."),
        app_sections=[
            app_section(
                "Eiendommen samlet", "Fire bygg. Én status.",
                "Før styret går inn i ett enkelt tiltak, ser dere hvor det trengs mest – bygg for bygg, ikke bare for eiendommen som helhet.",
                '<div class="appsec-dash">' + building_overview_view(
                    "Bygningsoversikt", "Perrongen Borettslag · byggeår 1986",
                    buildings=[("Bygg A", "52 hjem", "68/100", "3 tiltak", True),
                               ("Bygg B", "48 hjem", "81/100", "2 tiltak", False),
                               ("Bygg C", "50 hjem", "74/100", "3 tiltak", False),
                               ("Bygg D", "50 hjem", "62/100", "4 tiltak", True)],
                    footer="Eksempeldata. Status per bygg bygger på tilstandsrapporter og innmeldte behov.") + '</div>',
                sid="eiendomskart"),
            app_section(
                "Planlegg vedlikehold", "Se hva som kommer – før det blir akutt.",
                "ERA samler tiltak, prioriteringer og kostnader i en levende vedlikeholdsplan som oppdateres når eiendommen endrer seg.",
                '<div class="appsec-dash">' + maintenance_plan_view(
                    "10-årig vedlikeholdsplan", "Perrongen Borettslag",
                    kpis=[("Alle tiltak", "12"), ("Høy prioritet", "3"), ("Middels", "6"), ("Lav", "3")],
                    rows=[("2027", "Fasade", "1,2 MNOK", "high"),
                          ("2028", "Ventilasjon", "650 000 kr", "med"),
                          ("2029", "Soilrør", "4,8 MNOK", "high"),
                          ("2030", "Tak", "2,1 MNOK", "med"),
                          ("2031", "Vinduer", "1,8 MNOK", "low")],
                    footer="Eksempeldata. Tidspunkt og kostnad er anslag som oppdateres etter hvert som tilstand og pris avklares.") + '</div>',
                alt_bg=True, sid="vedlikeholdsplan"),
            app_section(
                "Budsjett", "Hva koster planen – og hvordan finansieres den?",
                "ERA regner ut hva vedlikeholdsplanen betyr i kroner, år for år og per hjem, slik at styret kan vurdere fond, felleskostnader og finansiering med samme tall.",
                '<div class="appsec-dash">' + budget_view(
                    "Budsjett 2027–2031", "Perrongen Borettslag · 200 hjem",
                    kpis=[("Totalt planlagt", "10,55 MNOK"), ("Snitt per år", "1,06 MNOK"), ("Snitt per hjem/år", "5 275 kr"), ("Fellesgjeld i dag", "0 kr")],
                    rows=[("2027 · Fasade", "1,2 MNOK"), ("2028 · Ventilasjon", "650 000 kr"),
                          ("2029 · Soilrør", "4,8 MNOK"), ("2030 · Tak", "2,1 MNOK"), ("2031 · Vinduer", "1,8 MNOK")],
                    financing_note="Mindre tiltak kan dekkes av vedlikeholdsfond og løpende felleskostnader. For de største tiltakene (som soilrør i 2029) kan styret vurdere felleslån. ERA gir tallgrunnlaget for vurderingen – ikke lånetilsagn eller anbefalt bank.",
                    footer="Eksempeldata. Finansiering besluttes av styret og generalforsamlingen, ikke av ERA.") + '</div>',
                flip=True, sid="budsjett"),
            app_section(
                "ERA hjelper styret prioritere", "Beslutningsstøtte, ikke en chatbot.",
                "Basert på vedlikeholdsplanen, registrert tilstand og risiko foreslår ERA hva styret bør prioritere først, med begrunnelse og kostnadsestimat.",
                '<div class="appsec-dash">' + styre_agent_view(
                    "Hva bør styret prioritere de neste 24 månedene?",
                    "Basert på tilstand, alder på komponenter og vedlikeholdsplanen anbefaler ERA at dere prioriterer:",
                    picks=[("Soilrør", "Høy risiko for følgeskader · estimert 4,2–5,0 MNOK"),
                           ("Fasade", "Planlegg innen 18 måneder · estimert 1,0–1,3 MNOK"),
                           ("Ventilasjon", "Bør kartlegges · estimert 80 000–120 000 kr")],
                    footer="Eksempeldata. ERA foreslår og begrunner; styret vurderer og beslutter.") + '</div>',
                alt_bg=True, flip=True, sid="styre-agent"),
            app_section(
                "Sammenlign tilbud", "Tre tilbud. Samme grunnlag. Én oversikt.",
                "Når tiltaket er besluttet, samler ERA inn tilbud på samme arbeidsbeskrivelse, slik at styret sammenligner pris og fremdrift direkte, uten regneark.",
                '<div class="appsec-dash">' + offer_comparison_view(
                    "Fasade 2027 · tilbud", "3 tilbud på samme omfang",
                    offers=[("Mestergruppen", "Fasade og utvendig maling", "2 350 000 kr", "8 uker"),
                            ("Proff Malerservice", "Fasade, balkonger og detaljer", "2 480 000 kr", "10 uker"),
                            ("Fargerike Prosjekt", "Totalleveranse", "2 690 000 kr", "9 uker")],
                    recommended="Mestergruppen",
                    footer="Eksempeldata. ERA sammenstiller tilbudene; styret velger leverandør.") + '</div>',
                sid="tilbud"),
            app_section(
                "Varsle beboerne", "Styret varsler. Beboerne vet hva som skjer.",
                "Når arbeidet er avtalt, varsler ERA alle eierne samtidig, med det de faktisk trenger å vite – og en åpning for å melde egne behov i samme prosjekt.",
                '<div class="appsec-dash">' + resident_notice_view(
                    "Send varsel til beboere", "Fasade 2027 · alle seksjoner",
                    recipients="200 hjem",
                    body="Styret planlegger overflatebehandling og maling av fasader, balkonger og fellesarealer fra mai 2027. Du får mer informasjon om tidsplan og tilgang, og kan melde behov for egen balkong i samme prosjekt.",
                    checklist=["Beboere får varsel i app og e-post",
                               "Spørsmål samles i én tråd til styret",
                               "Beboere kan melde interesse for tilleggsarbeid",
                               "Styret får oversikt over svar og spørsmål"],
                    footer="Eksempeldata. Varsling og svar vises som illustrasjon av beboerflyten.") + '</div>',
                alt_bg=True, flip=True, sid="beboerflyt"),
            app_section(
                "Eieren ser det også", "Ikke bare et varsel. Egen oppfølging.",
                "Det samme fasadeprosjektet dukker opp i eierens egen ERA-app, sammen med resten av hjemmet deres. Fellesareal og privat hjem holdes adskilt: privat dokumentasjon om hjemmet deles ikke automatisk med styret.",
                phone("/assets/story/app-minbolig.png", 853, 1844,
                      "ERA Bolig, boligeierens Min bolig-side: viser egen bolig med tilstand og neste prosjekt, samt fellesprosjektet fra styret",
                      "md"),
                points=[("For eieren", "Eget hjem, dokumentasjon og vedlikeholdsplan – pluss fellesprosjekter fra styret."),
                        ("For styret", "Ingen ekstra jobb. Samme varsel gjør fellesprosjektet synlig i eierens app.")],
                foot="Eksempeldata. Skjermbilde fra ERA for huseiere.", sid="boligeier-visning"),
            app_section(
                "Fra ferdig til dokumentert", "Jobben er ferdig. Historikken lever videre.",
                "Når arbeidet er utført, oppdaterer ERA vedlikeholdsplanen automatisk og samler dokumentasjon, bilder og kostnad på eiendommen – klart for neste styre.",
                '<div class="appsec-dash">' + completion_view(
                    "Fasade 2027", "Overflatebehandling og maling",
                    kpis=[("Totalkostnad", "2 350 000 kr"), ("Avvik fra estimat", "−5 %"), ("Varighet", "8 uker, i rute"), ("Beboere informert", "100 %")],
                    docs=["Sluttrapport (PDF)", "Bilder før/etter (18)", "FDV-dokumentasjon", "Oppdatert tilstandsrapport"],
                    footer="Eksempeldata. Dokumentasjonen lagres på eiendommen og oppdaterer vedlikeholdsplanen.") + '</div>',
                alt_bg=True, sid="dokumentasjon"),
            next_steps_section(
                "Oppsummert", "Forstå. Gjennomfør. Dokumenter.",
                "Tre steg, samme eiendom, hver gang: ERA hjelper styret forstå hva som trengs, gjennomføre riktig tiltak med riktig leverandør, og dokumentere resultatet slik at neste styre starter med historikken, ikke fra null.",
                cards=[
                    ("Forstå", "Tilstand, risiko og innmeldte behov samlet i én bygningsoversikt og vedlikeholdsplan.", None, None),
                    ("Gjennomfør", "Fra prioritering og budsjett til sammenlignede tilbud og varslede beboere.", None, None),
                    ("Dokumenter", "Utført arbeid, kostnad og bilder lagres på eiendommen og oppdaterer planen.", None, None),
                ],
                sid="oppsummering"),
        ],
        scenes=dict(
            eyebrow="Fra behov til ferdig jobb", title="Én eiendom. Én sammenhengende vedlikeholdsflyt.",
            lede="Følg det samme fasadebehovet fra første funn til gjennomført og dokumentert arbeid. Beboerne er med hele veien: hver eier får egen oversikt over hjemmet, vedlikeholdsplan og påminnelser gjennom ERA for huseiere.",
            items=[
                dict(nav="Oversikt", heading="Hva trenger bygget deres nå?",
                     text="Rapporter, tidligere arbeid og innmeldte behov gir styret ett samlet utgangspunkt.",
                     value="ERA skiller dokumenterte funn fra forslag som styret må vurdere.",
                     view=dash("Eiendomsoversikt", "Samlet utgangspunkt for styret",
                               kpis=[("Eiendom", "Perrongen Borettslag"), ("Hjem", "200 · 4 bygg"), ("Område", "Fasade"), ("Sist utført", "Malt 2012")],
                               groups=[("doc", [("Tilstandsrapport 2021", "Maling flasser på sør- og vestvegg"), ("Innmeldt behov", "Avskalling ved inngang B")]),
                                       ("ai", [("Forslag", "Befaring innen 12 måneder")])],
                               footer="Eksempeldata. ERA-forslag vurderes og besluttes av styret.")),
                dict(nav="Prioritering", heading="Fra rapport til neste steg.",
                     text="Det dokumenterte behovet omformes til et konkret tiltak i vedlikeholdsplanen.",
                     value="Styret ser hvorfor tiltaket foreslås, når det bør vurderes og hvilket grunnlag det bygger på.",
                     view=dash("Vedlikeholdsplan", "Forslag fra ERA, til styrets vurdering",
                               kpis=[("Foreslått tiltak", "Male sør- og vestvegg"), ("Anbefalt år", "2027"), ("Kostnadsintervall", "1,0–1,3 mill"), ("Status", "Til vurdering")],
                               groups=[("doc", [("Funn", "Maling flasser, sør- og vestvegg · rapport 2021"), ("Egen oppgave i totalplanen", "Tak · 2031")]),
                                       ("ai", [("Grunnlag", "Rapport 2021 og innmeldt avskalling"), ("Per hjem", "ca. 5 000–6 500 kr")])],
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
            label="Beboerverdi", heading="Samme prosjekt, sett fra eierens app.",
            text="Nysgjerrig på hvordan eieren opplever den andre siden av samme prosjekt – eget hjem, egen dokumentasjon, egne påminnelser?",
            link="Se ERA for huseiere →", href="/boligeier",
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
            ("Er ERA et nytt FDV-system?", "Nei. Et FDV-system organiserer og dokumenterer informasjon. ERA bruker informasjonen til å forstå eiendommen, oppdage relevante behov og vise styret hva som bør gjøres videre. Målet er ikke bare å lagre hva som har skjedd."),
            ("Hva koster ERA for borettslaget?", "Gratis de første tolv månedene, både for styret og for beboerne. Prismodellen etter det er ikke fastsatt ennå."),
            ("Hvem eier dataene?", "Eiendommen. Styret bestemmer hvem som ser dem. Ved styreskifte følger alt med."),
        ],
        closing=dict(
            heading="Hva er neste tiltak for deres eiendom?",
            lede="Se hvordan ERA kan hjelpe dere fra første vurdering til ferdig dokumentert arbeid, med styret, eierne og håndverkeren i samme flyt.",
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
        label="For håndverkere", hook="Fra kundens behov til din neste jobb.",
        lede="ERA er en AI-drevet plattform som kobler huseiere, styrer og håndverkere. Ta kundens behov videre til befaring, tilbud og gjennomføring, og la dokumentasjonen følge hjemmet når jobben er ferdig.",
        hero_support="Du kan faget. ERA hjelper deg med flyten rundt jobben.",
        image="/assets/story/painter-v3.jpg", image_pos="30% 50%",
        hero_secondary=("Følg et oppdrag", "#slik"),
        scenes=dict(
            eyebrow="Fra henvendelse til ferdig jobb", title="Ett prosjekt. Fem hendelser.",
            lede="Følg det samme maleprosjektet fra kundens henvendelse til dokumentert overlevering. Kunden beskriver og godkjenner; du vurderer, utfører og dokumenterer.",
            items=[
                dict(nav="Oppdrag", heading="Se hva kunden trenger. Før du drar.",
                     text="Kundens beskrivelse, bilder og tilgjengelig informasjon om hjemmet følger henvendelsen.",
                     value="Du vurderer jobben og forbereder befaringen på et bedre grunnlag.",
                     view=dash("Oppdragsgrunnlag", "Male stue · fra kundens henvendelse",
                               kpis=[("Adresse", "Myrerveien 14"), ("Rom", "Stue, 2 vegger"), ("Bilder", "4 vedlagt"), ("Ønsket tid", "Uke 38–40")],
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
                dict(nav="Overlevering", heading="Din jobb blir en del av hjemmets historie.",
                     text="Bilder, produktinformasjon og utført arbeid samles i en ryddig overlevering som kunden beholder i hjemmet.",
                     value="Arbeidet ditt er synlig for fremtidig oppfølging, med ditt navn på.",
                     view=dash("Overlevering", "Male stue · ferdigstilt",
                               kpis=[("Utført", "Vegger og tak, 2 strøk"), ("Bilder", "6 lagt til"), ("Produkter", "Maling, sparkel, ruller"), ("Status", "Overlevert")],
                               groups=[("doc", [("Hjemmets historikk", "Utført arbeid, med ditt navn på")]),
                                       ("pilot", [("Betaling i ERA", "Avtalt beløp og om det er gjort opp")])],
                               footer="Eksempeldata. En ryddig logg, ikke en sertifisering eller garanti.")),
            ],
        ),
        roles=[
            ("Huseier", "Beskriver behovet, og tar stilling til tilbud og endringer underveis."),
            ("Håndverker", "Vurderer, utfører og dokumenterer jobben fra befaring til overlevering."),
            ("Styret", "Følger opp og godkjenner når oppdraget gjelder fellesareal, ikke eget hjem."),
        ],
        roles_note="Ved private oppdrag er huseieren kunden. Ved fellesarbeid er det styret som bestiller og godkjenner på vegne av sameiet eller borettslaget.",
        gains=[
            ("Forstå oppdraget", "Se kundens behov, bilder og tilgjengelig informasjon om hjemmet før befaringen."),
            ("Ha kontroll på jobben", "Ta underlaget videre til kalkyle, tilbud, avtale og avklarte endringer."),
            ("Overlever med dokumentasjonen på plass", "Samle informasjon underveis, og knytt ferdig arbeid til riktig hjem eller eiendom."),
        ],
        faq=[
            ("Koster det noe å melde interesse?", "Nei. Meld interesse, så tar vi kontakt med vilkårene som gjelder i ditt område når ERA rulles ut der."),
            ("Konkurrerer jeg med mange?", "Kunden ber om tilbud på et beskrevet oppdrag. Du ser omfanget før du bruker tid."),
            ("Hva med dokumentasjon etter jobben?", "Bilder og beskrivelse legges i hjemmets historikk, og du bygger overleveringen mens du jobber."),
            ("Vi bruker allerede et ordresystem. Hvor passer ERA inn?", "ERA kobler håndverkerens arbeidsflyt til kundens hjem og vedlikeholdsbehov. Relevant informasjon følger oppdraget inn, og dokumentasjonen fra arbeidet følger hjemmet videre. I en demo ser vi på hvor ERA kan bidra i arbeidsflyten deres."),
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
        lede="Riktig produkt, riktig mengde, riktig tid, i én bestilling. Fra hjem og fra hele borettslag. Uavhengig av kjede.",
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
            ("Kvalifisert etterspørsel", "Bestillingen oppstår fra et faktisk behov i hjemmet, ikke fra inspirasjon."),
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


MENU = [("/historie", "Historien"), ("/boligeier", "Huseier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/ny/om-era", "Om ERA"), ("/personvern", "Personvern")]


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


def scenes_html(sc, cta_label, cta_href="#skjema", item_label="Steg"):
    """The tabbed walkthrough (numbered tabs, one panel per step). Shared by the audience pages and /ny;
    pages.js drives it from the markup alone."""
    items = sc["items"]
    tabs = "".join(
        f'<button type="button" role="tab" id="tab-{i+1}" aria-selected="{"true" if i == 0 else "false"}" aria-controls="scene-{i+1}" tabindex="{0 if i == 0 else -1}"><span class="n">0{i+1}</span><span class="t">{esc(it["nav"])}</span></button>'
        for i, it in enumerate(items))
    def scene_nav(i):
        prev = f'<button type="button" class="scene-prev" data-dir="-1">← Forrige</button>' if i > 0 else '<span></span>'
        if i < len(items) - 1:
            nxt = f'<button type="button" class="scene-next" data-dir="1">Neste: {esc(items[i+1]["nav"])} →</button>'
        else:
            nxt = f'<a class="scene-next" href="{cta_href}">{esc(cta_label)}</a>'
        return f'<div class="scene-nav">{prev}{nxt}</div>'
    panels = "".join(
        f'<div class="scene" role="tabpanel" id="scene-{i+1}" aria-labelledby="tab-{i+1}"{"" if i == 0 else " hidden"}>'
        f'<div class="scene-text"><div class="label">{esc(item_label)} {i+1} · {esc(it["nav"])}</div><h3>{esc(it["heading"])}</h3><p>{esc(it["text"])}</p>'
        f'<p class="scene-value">{esc(it["value"])}</p></div>'
        f'<div class="scene-view">{it["view"]}</div>{scene_nav(i)}</div>'
        for i, it in enumerate(items))
    return (
        '<section class="section scenes" id="slik"><div class="wrap wide">'
        f'<div class="label">{esc(sc["eyebrow"])}</div><h2>{esc(sc["title"])}</h2><p class="steps-intro">{esc(sc["lede"])}</p>'
        f'<div class="stepnav" role="tablist" aria-label="{len(items)} steg" style="grid-template-columns: repeat({len(items)}, minmax(0, 1fr))">{tabs}</div>'
        f'<div class="scene-panel">{panels}</div>'
        '</div></section>'
    )


def footer_html():
    return f'''<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Å eie hjem uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/historie#hva">Hva ERA gjør</a><a href="/ny/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/historie">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>'''


FAQ_VISIBLE = 7


def faq_html(items, visible=FAQ_VISIBLE):
    """FAQ-en er en del av produktforklaringen, ikke bare en hjelpefunksjon.

    Et element er (spørsmål, svar) eller (spørsmål, svar, punkter). Et punkt er enten en streng
    eller (ledetekst, tekst) — brukt der strukturen bærer meningen, som skillet mellom
    Dokumentert, ERA-forslag og Mangler.

    Bare de første `visible` vises. Resten ligger bak «Se alle spørsmål»: fjorten åpne spørsmål
    over folden leses som en støttefunksjon, ikke som en forklaring. Løsningen er ren HTML —
    <details> trenger ingen JavaScript, virker uten den, og er tastaturnavigerbar av seg selv.
    """
    def one(it):
        q, ans = it[0], it[1]
        bullets = it[2] if len(it) > 2 else None
        body = "<p>" + esc(ans) + "</p>"
        if bullets:
            lis = []
            for b in bullets:
                if isinstance(b, (tuple, list)) and len(b) == 2:
                    lis.append("<li><b>" + esc(b[0]) + "</b>" + esc(b[1]) + "</li>")
                else:
                    lis.append("<li>" + esc(b) + "</li>")
            body += '<ul class="faq-points">' + "".join(lis) + "</ul>"
        return "<details><summary>" + esc(q) + "</summary>" + body + "</details>"

    head = "".join(one(it) for it in items[:visible])
    rest = items[visible:]
    if not rest:
        return head
    return (head + '<details class="faq-more"><summary>Se alle spørsmål</summary>'
            '<div class="faq">' + "".join(one(it) for it in rest) + "</div></details>")


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
    scenes_section = scenes_html(a["scenes"], a["form_cta"]) if a.get("scenes") else ""
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
    faq = faq_html(a["faq"])
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
<meta name="description" content="{esc(a.get("meta", a["lede"]))}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/" + slug, a["title"] + " — ERA", a.get("meta", a["lede"]))}
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
      <p class="fine">Ingen binding. Dataene lagres kryptert i EU/EØS og brukes bare til å ta kontakt.</p>
      {closing_note}
    </div>
  </section>
</main>

{footer_html()}
<script src="/pages.js" defer></script>
</body>
</html>
'''


PRIVACY_DESC = "Hva ERA lagrer når du bruker skjemaene på denne siden, hvor det lagres, hvor lenge, og hvordan du får det slettet."


def privacy_page():
    """Honest to what the site actually does today: the address form (and on the front page an optional e-mail), the Kartverket address search, one private store in the EU, no cookies."""
    sections = [
        ("Hva vi samler inn", [
            "Når du sender inn skjemaet på historien eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede eller butikk), hvilken målgruppe du leste som (huseier, styret, håndverker eller faghandel), om du ba om en demo, tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
            "På forsiden gjelder noe mer. Velger du et forslag i adressesøket, lagrer vi også det Kartverket returnerer for den adressen: postnummer og sted, kommune, gårds-, bruks-, feste- og seksjonsnummer og et koordinatpunkt. Velger du ikke et forslag, lagrer vi bare teksten du skrev.",
            "Etter at du har sendt inn adressen på forsiden, kan du også legge igjen e-postadressen din. Det er valgfritt. E-posten lagres som en egen post som er knyttet til innsendingen med en intern id.",
            "Vi samler ikke inn navn eller telefonnummer, og vi lagrer ikke IP-adressen din. Unntaket er kontaktskjemaet for meglere og partnere (/partnere): der skriver du selv navn, firma, e-post og en melding, og vi lagrer det for å kunne svare deg. Det brukes ikke til nyhetsbrev.",
        ]),
        ("Adressesøket hos Kartverket", [
            "Når du skriver i et adressefelt, sender nettleseren din det du har skrevet (fra tre tegn) til Kartverkets åpne adresse-API (Geonorge), som svarer med forslag. Kartverket mottar da teksten og IP-adressen din, slik som ved enhver nettforespørsel, og er selv ansvarlig for sin behandling av det. ERA lagrer ikke det du skriver før du trykker send.",
        ]),
        ("Hvorfor", [
            "For å ta kontakt om ERA for den adressen, eiendommen eller virksomheten du meldte inn, og for å sende deg en invitasjon til ERA hvis du har lagt igjen e-post. Ikke til noe annet. Vi selger eller deler ikke opplysningene.",
        ]),
        ("Hvor og hvor lenge", [
            "Opplysningene lagres kryptert hos vår driftsleverandør Vercel, i et privat lager i Frankfurt (EU/EØS). Bare ERA technologies AS har tilgang.",
            "Vi sletter innsendingen, og e-posten som hører til den, senest tolv måneder etter at den kom inn, eller så snart du ber om det.",
        ]),
        ("Informasjonskapsler og analyse", [
            "Siden setter ingen informasjonskapsler. Vi bruker Vercel Web Analytics, som teller sidevisninger uten cookies og uten å identifisere deg. Derfor trenger vi ikke et samtykkebanner.",
            "På forsiden teller vi også hendelser som at et adresseforslag ble valgt eller at en e-post ble sendt inn. Hendelsene inneholder verken adressen eller e-posten.",
        ]),
        ("Dine rettigheter", [
            "Du kan når som helst be om innsyn i, retting av eller sletting av det du har sendt inn, også e-posten. Send oss en melding via skjemaet på siden med «personvern» først i teksten, så svarer vi. Behandlingsansvarlig er ERA technologies AS, Oslo.",
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
    <h1>Ditt hjem. Dine data.</h1>
    <p class="lede dark">ERA lagrer hjemmets historie for deg, ikke om deg. Her står nøyaktig hva denne nettsiden gjør med det du sender inn.</p>
    <p class="fine dark">Sist oppdatert 2. oktober 2026.</p>
    {body}
  </div>
</main>
<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Å eie hjem uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/historie#hva">Hva ERA gjør</a><a href="/ny/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/historie">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>
<script src="/pages.js" defer></script>
</body>
</html>
'''


NY_DESC = "Hjemmets AI-agent. ERA kjenner hjemmet ditt, oppdager hva som bør gjøres og hjelper deg få det gjort. Spør om hjemmet eller ta et bilde."


def lead_form_html(suffix, a, done, label=None, placeholder=None):
    """One address form. pages.js binds every form.lead, so a page can carry several as long as the
    input ids are unique. The field shows a static example instead of the typewriter, so it never
    looks empty; `label` puts a visible instruction above it."""
    lab = (f'<label class="lead-label" for="lead-value-{suffix}">{esc(label)}</label>' if label
           else f'<label class="sr" for="lead-value-{suffix}">{esc(a["form_field"])}</label>')
    ph = placeholder or a["form_field"]
    return f'''<form id="era-lead-{suffix}" class="lead" data-audience="{a["key"]}" data-follow="email">
        {lab}
        <div class="lead-pill">
          <div class="lead-value-wrap">
            <input id="lead-value-{suffix}" name="value" type="text" autocomplete="off" required minlength="3" maxlength="200" placeholder="{esc(ph)}">
            <span class="field-label" aria-hidden="true">{esc(a["form_label"])}</span>
          </div>
          <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
          <button type="submit">Finn hjemmet mitt</button>
        </div>
      </form>
      <div class="done done--follow" role="status" aria-live="polite" hidden>
        <div class="check"><svg width="20" height="16" viewBox="0 0 20 16" fill="none"><path d="M2 8L7.5 13.5L18 2" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div class="done-body">
          <b data-done-title>{esc(done[0])}</b>
          <span data-done-sub>{esc(done[1])}</span>
          <span data-done-note>Vi inviterer brukere fortløpende. Legg igjen e-post, så sier vi fra når det er din tur.</span>
          <form class="follow" data-follow-form novalidate hidden>
            <label class="sr" for="follow-email-{suffix}">E-post</label>
            <div class="follow-row">
              <input id="follow-email-{suffix}" name="email" type="email" autocomplete="email" inputmode="email" maxlength="200" placeholder="E-post">
              <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
              <button type="submit">Si fra til meg</button>
            </div>
            <small>Valgfritt. Brukes bare til å invitere deg til ERA. Du kan be om sletting når som helst.</small>
            <span class="follow-err" role="alert" hidden></span>
          </form>
        </div>
      </div>
      <div class="err" hidden></div>'''


def ny_nav(base="", current=True):
    """The /ny menu is the homeowner's: no audience pages, no partners. The other audiences live in the
    footer. `base` is "" on /ny and "/ny" on the pages next to it, so the in-page anchors still work."""
    items = [(base + "#produkt", "Produkt"), (base + "#slik", "Slik fungerer det"), ("/ny/om-era", "Om ERA")]
    links = "".join(f'<a href="{h}"{" aria-current=" + chr(34) + "page" + chr(34) if h == "/ny/om-era" and base and current else ""}>{esc(l)}</a>' for h, l in items)
    panel = "".join(f'<a href="{h}" data-menu-close="1">{esc(l)}<span>→</span></a>' for h, l in items)
    return f'''<nav class="nav" aria-label="Hovedmeny">
  <div class="pill">
    <a class="brand" href="/">era<span>.</span></a>
    <div class="links">{links}</div>
    <div class="right"><a class="cta" href="{base}#adresse">Finn hjemmet mitt</a><button type="button" class="menu-btn" data-menu-toggle="1" aria-label="Åpne menyen" aria-expanded="false">☰</button></div>
  </div>
  <div class="menu-panel" hidden>{panel}</div>
</nav>'''


def ny_footer(base=""):
    return f'''<footer class="foot" data-nav="light">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Hjemmets AI-agent</div></div>
    <div class="cols">
      <div><b>ERA</b><a href="{base}#produkt">Produkt</a><a href="{base}#slik">Slik fungerer det</a><a href="/ny/om-era">Om ERA</a><a href="/personvern">Personvern</a></div>
      <div><b>For profesjonelle</b><a href="/styret">Borettslag og sameier</a><a href="/handverker">Håndverkere</a><a href="/faghandel">Faghandel</a><a href="/partnere">Meglere og partnere</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>'''


def cine(src, body, sid=None, cls="", pos="50% 50%", tag="section"):
    """A cinematic section: one of the story photographs behind a dark wash, with a short message on
    top. The photograph carries the feeling; the message and the product carry the meaning."""
    stem = src[:-4]
    img = (f'<img src="{src}" srcset="{stem}-m.jpg 1400w, {src} 3000w" sizes="100vw" alt="" '
           f'loading="lazy" decoding="async" style="object-position: {pos}">')
    return (f'<{tag} class="cine {cls}" data-nav="dark"' + (f' id="{sid}"' if sid else '') + '>'
            f'<div class="cine-media">{img}</div><div class="cine-body">{body}</div></{tag}>')


def app_flow(eyebrow, title, steps, foot, sid, lede=None):
    """The journey as one horizontal flow. The steps keep their order and numbers; the screens are
    sized by how much they explain (the agent largest), so the eye reads a flow instead of five equal
    phones. On a desktop the steps wake one by one as the section scrolls into view, and when the last
    one is awake a line is drawn back to the first: everything returns to the home. On a phone it is a
    swipeable row and every step is awake."""
    items = "".join(
        f'<li class="flow-step flow-step--{size}"><div class="flow-shot"><img src="{src}" width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async"></div>'
        f'<div class="flow-cap"><span class="n">0{i+1}</span><b>{esc(t)}</b><span>{esc(d)}</span></div></li>'
        for i, (t, d, src, alt, w, h, size) in enumerate(steps))
    return (f'<section class="section alt flow" id="{sid}" data-nav="light"><div class="wrap wide">'
            f'<h2>{esc(title)}</h2>'
            + (f'<p class="flow-lede">{esc(lede)}</p>' if lede else '') +
            f'<ol class="flow-track" tabindex="0" aria-label="Reisen i fem steg. Sveip sideveis for å se alle.">{items}</ol>'
            '<div class="flow-return" aria-hidden="true"><span class="flow-return-line"></span><span class="flow-return-label">Tilbake til hjemmet</span></div>'
            f'<p class="flow-hint">Sveip for å se alle fem</p>'
            f'<p class="fine dark2">{esc(foot)}</p></div></section>')


def knows_view(title, eyebrow, rows, foot, photo=None):
    """What ERA knows, what it only suggests and what is missing, as an editorial list rather than a
    dashboard card. rows: (kind, label, value, tag[, feed]) with kind doc / ai / miss; `feed` names the
    scattered document that lights up when it has been read into this row."""
    lis = "".join(
        f'<li class="k-{kind}"' + (f' data-feed="{feed[0]}"' if feed else '') + '><span class="k-mark" aria-hidden="true"></span>'
        f'<div><b>{esc(label)}</b><span>{esc(value)}</span></div><em>{esc(tag)}</em></li>'
        for kind, label, value, tag, *feed in rows)
    pic = (f'<div class="knows-photo"><img src="{photo}" alt="" loading="lazy" decoding="async"><span>{esc(title)}</span></div>' if photo else "")
    return (f'<div class="knows"><div class="knows-eyebrow">{esc(eyebrow)}</div><h3>{esc(title)}</h3>{pic}'
            f'<ul class="knows-rows">{lis}</ul><p class="knows-foot">{esc(foot)}</p></div>')


# The documents that lie scattered around a home, and where each ends up. Percent positions inside the
# stage: start (scattered) and end (tidy grid). Rotation in degrees.
SCATTER_DOCS = [
    ("Tilstandsrapport 2021", (18, 22, -9), (24, 30), "byggeaar"),
    ("Kvittering tak", (80, 18, 7), (50, 30), None),
    ("FDV-dokumenter", (50, 64, -5), (76, 30), None),
    ("Bilder", (84, 74, 11), (24, 72), None),
    ("E-post med håndverker", (24, 82, 6), (50, 72), "sistarbeid"),
    ("Garanti", (66, 40, -12), (76, 72), None),
]


def docs_scatter():
    chips = "".join(
        f'<span class="doc-fly" style="--x:{s[0]}%;--y:{s[1]}%;--r:{s[2]}deg;--x2:{e[0]}%;--y2:{e[1]}%;--i:{i}"'
        + (f' data-feeds="{feed}"' if feed else '') + f'>{esc(t)}</span>'
        for i, (t, s, e, feed) in enumerate(SCATTER_DOCS))
    return (f'<div class="docs-scatter" aria-hidden="true">{chips}</div>'
            '<p class="docs-cap">Spredt i dag. Samlet i hjemmet.</p>')


# The people behind ERA: bios and tags as the story's "Menneskene bak ERA" chapter has them (index.html,
# teamDefs). The four leads' titles follow the brief of 2 Oct 2026. /investor keeps its own titles.
NY_TEAM = [
    ("Lars-Henrik Sand", "Founder · Managing Partner · Vision & AI Architect", True, "team-lars.jpg",
     "17+ års erfaring i skjæringspunktet mellom eiendom, teknologi og marked. Har jobbet med digitale løsninger og markedsføring for mer enn 400 boligprosjekter og en rekke ledende aktører i eiendomsmarkedet.",
     "Eiendom · AI · Produkt · Teknologi · Strategi"),
    ("Ragnvald Løhren", "Co-Founder · Managing Partner · Finance & Strategy", True, "team-ragnvald.jpg",
     "Erfaring fra finans, investeringer og forretningsutvikling, blant annet fra Storebrand og VentureLab. Ansvar for ERAs finansielle strategi, forretningsutvikling og kapital.",
     "Finans · Strategi · Investering · M&A"),
    ("Thomas Floden", "Partner · CTO", True, "team-thomas.jpg",
     "Teknologigründer med erfaring fra SaaS, AI, systemarkitektur og digitale plattformer. Leder den teknologiske utviklingen av ERA og arkitekturen bak plattformen.",
     "Teknologi · AI · SaaS · Systemarkitektur"),
    ("Eskild Løken Ugland", "Partner · Styremedlem", True, "team-eskild-v2.jpg",
     "25+ års erfaring fra bolig, bygg og faghandel. Tidligere salgs- og markedsdirektør i Block Watne, og senere kjedesjef for Mal Proff og Mesterfarge i Mestergruppen. Bidrar særlig med bransjekunnskap, distribusjon og kommersiell utvikling.",
     "Bolig · Bygg · Faghandel · Distribusjon · Salg"),
    ("Markus Frost", "Styreleder", False, "team-markus.jpg", "Leder ERAs styrearbeid.", ""),
    ("Magnus Stensrud", "Daglig leder / Sales", False, "team-magnus-v4.jpg",
     "Lang erfaring fra salg, salgsledelse og kundereiser, blant annet fra Elkjøp.", ""),
    ("Andreas Løhren", "Legal & Regulatory · Styremedlem", False, "team-andreas.jpg",
     "Bakgrunn fra offentlig forvaltning, EU/EØS, digitalisering og regulatoriske problemstillinger.", ""),
    ("William Lente", "Digital Growth & Design", False, "team-william.jpg",
     "Bakgrunn fra digital markedsføring, leadgenerering, web og design.", ""),
]


def team_html():
    """The whole team, every person the same size. The portraits are the trust."""
    def card(name, role, lead, photo, bio, tags):
        shot = f'<img src="/assets/story/{photo}" alt="{esc(name)} – {esc(role)}" loading="lazy" decoding="async">'
        return (f'<article class="team-card team-card--lead">'
                f'<div class="team-shot">{shot}</div><h3>{esc(name)}</h3><div class="team-role">{esc(role)}</div>'
                f'<p>{esc(bio)}</p>' + (f'<div class="team-tags">{esc(tags)}</div>' if tags else "") + '</article>')
    return '<div class="team-all">' + "".join(card(*p) for p in NY_TEAM) + '</div>'


CHECK_SVG = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M2.5 7.5l3 3 6-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def how_it_works():
    """Slik fungerer ERA: three big steps on a light surface, each with one small visual. A thin line
    is drawn from 1 to 2 to 3 as the section scrolls into view."""
    pin = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 14s5-4.2 5-8a5 5 0 10-10 0c0 3.8 5 8 5 8z" stroke="currentColor" stroke-width="1.4"/><circle cx="8" cy="6" r="1.8" stroke="currentColor" stroke-width="1.4"/></svg>'
    chk = '__CHECK__'
    def shot(src, alt):
        return (f'<div class="how-visual how-visual--app"><img src="{src}" width="853" height="1844" alt="{esc(alt)}" loading="lazy" decoding="async"></div>')
    v1 = shot("/assets/story/app-minbolig.png", "ERA Bolig: Min bolig med boligprofil, neste prosjekt og dokumentasjon")
    v2 = shot("/assets/story/app-kamera.png", "ERA Bolig: kameraet rettet mot avflassende maling, klart til å analysere bildet")
    v3 = shot("/assets/story/app-prosjekt.png", "ERA Bolig: prosjektet med plan, valget mellom å gjøre det selv eller be om tilbud, og fremdrift")
    steps = [(v1, "Finn hjemmet", "Skriv inn adressen din. ERA starter med det som allerede finnes av hjemmedata, dokumentasjon og historikk."),
             (v2, "Vis eller spør", "Ta et bilde eller beskriv hva du lurer på. ERA bruker hjemmets kontekst sammen med det du viser den."),
             (v3, "Få det gjort", "Få forslag og en plan. Gjør det selv, eller be om tilbud fra proff. Resultatet lagres på hjemmet.")]
    items = "".join(f'<li>{v}<div class="how-cap"><span class="how-n">{i+1}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></div></li>' for i, (v, t, d) in enumerate(steps))
    return ('<section class="section how" id="slik" data-nav="light" data-reveal><div class="wrap wide">'
            '<div class="label">Slik fungerer ERA</div><h2>Fra adresse til ferdig jobb.</h2>'
            '<p class="how-lede">Tre enkle steg. ERA kobler hjemmedata, bildene dine og fagkunnskap, og hjelper deg hele veien fra idé til ferdig jobb.</p>'
            f'<ol class="how-steps">{items}</ol><span class="how-line" aria-hidden="true"></span></div></section>').replace('__CHECK__', CHECK_SVG)


def reise_sofa():
    """Customer journey 1: it often starts on the sofa. One quote, one ERA notification."""
    body = ('<div class="reise-text"><h2>Det starter ofte i sofaen.</h2>'
            '<p class="cine-lede">ERA følger med på hjemmet og minner deg på det som bør vurderes.</p>'
            '<p class="reise-say">«Vi burde male stua.»</p></div>'
            '<div class="reise-note" aria-hidden="true"><b>ERA</b><span>Tid for å vurdere ny maling?</span><em>Det er en stund siden sist.</em></div>')
    return cine("/assets/story/couple-reminder-v5.jpg", body, sid="sofaen", cls="cine--reise cine--sofa", pos="50% 55%").replace('<section class="cine', '<section data-reveal class="cine', 1)


def reise_bilde():
    """Customer journey 2: take a photo, ERA makes the plan. Four things, not six panels."""
    rows = [("Hva ERA ser", "Maling som flasser på veggen"), ("Forslag", "Maling og farge som passer hjemmet"),
            ("Plan", "Forarbeid, sparkling, grunning og strøk"), ("Handleliste", "Produkter og mengde")]
    lis = "".join(f'<li style="--i:{i}"><span>{esc(k)}</span><b>{esc(v)}</b></li>' for i, (k, v) in enumerate(rows))
    body = ('<div class="reise-text"><h2>Ta et bilde. ERA lager planen.</h2>'
            '<p class="cine-lede">ERA bruker det du viser den sammen med det den allerede vet om hjemmet.</p>'
            '<p class="cine-fine">Eksempel. Produktforslag og handleliste er under utvikling.</p></div>'
            '<div class="reise-card" aria-hidden="false"><div class="reise-card-head"><b>era.</b><span>Myrerveien 46A</span></div>'
            f'<ul class="reise-rows">{lis}</ul>'
            '<div class="reise-paths"><span>Gjør det selv</span><span>Få tilbud fra proff</span></div></div>')
    return cine("/assets/story/couple-wall-v5.jpg", body, sid="bilde", cls="cine--reise cine--bilde", pos="40% 50%").replace('<section class="cine', '<section data-reveal class="cine', 1)


def valget():
    """One plan, two ways. A dark navy surface; ERA in the middle. The plan splits in two."""
    left = ["Produkter", "Mengder", "Fremgangsmåte", "Handleliste"]
    right = ["Behovet er allerede beskrevet", "Få tilbud", "Velg", "Følg jobben"]
    li = lambda xs: "".join(f'<li>{esc(x)}</li>' for x in xs)
    return ('<section class="valget" id="valget" data-nav="dark" data-reveal><div class="wrap wide">'
            '<h2>Én plan. To veier.</h2>'
            '<p class="valget-lede">ERA lager en konkret plan. Du bestemmer hvordan det blir gjort.</p>'
            '<div class="valget-grid">'
            f'<div class="valget-col valget-col--l"><div class="valget-photo"><img src="/assets/story/materials-floor-v3-m.jpg" alt="" loading="lazy" decoding="async"></div><h3>Gjør det selv</h3><ul>{li(left)}</ul></div>'
            '<div class="valget-core" aria-hidden="true"><span>era<i>.</i></span></div>'
            f'<div class="valget-col valget-col--r"><div class="valget-photo"><img src="/assets/story/painter-v3-m.jpg" alt="" loading="lazy" decoding="async"></div><h3>Få hjelp av proff</h3><ul>{li(right)}</ul></div>'
            '</div><p class="cine-fine">Produktforslag og tilbud i ERA er under utvikling.</p></div></section>')


def reise_ferdig():
    """Customer journey 3: the same couple back on the sofa. Only the status arrives."""
    st = ["Ferdig", "Dokumentert", "Lagret på hjemmet"]
    lis = "".join(f'<li style="--i:{i}"><span>{CHECK_SVG}</span>{esc(t)}</li>' for i, t in enumerate(st))
    body = ('<div class="reise-text"><h2>Ferdig.<br>Og hjemmet husker det.</h2>'
            '<p class="cine-lede">Neste gang starter ERA med historikken, ikke fra null.</p></div>'
            f'<div class="reise-card reise-card--done"><ul class="reise-done">{lis}</ul></div>')
    return cine("/assets/story/couple-done-v5.jpg", body, sid="ferdig", cls="cine--reise cine--ferdig", pos="50% 50%").replace('<section class="cine', '<section data-reveal class="cine', 1)


# Three scenes from the old story, in a short form. Each one starts when it scrolls into view
# ([data-reveal] -> .is-in) and plays once. Without JS or with reduced motion they stand in their final state.
SEE_SPOTS = [
    # name, line 1, line 2 (label, value, tone), x%, y%, card side
    ("Tak og beslag", ("Alder og tetting", "Bør kontrolleres"), ("Ansvar", "Felles", "mid"), 66, 24, "right"),
    ("Fasade", ("Status", "Bør følges opp"), ("Maling", "Flasser", "mid"), 72, 52, "left"),
    ("Bad", ("Dokumentasjon", "Delvis"), ("Rehabilitering nå", "Ikke anbefalt", "calm"), 84, 76, "left"),
]


def scene_see():
    """ERA reads the building: three places light up one at a time, each with what is known and who is
    responsible. Example data, as the old story had it."""
    spots = "".join(
        f'<div class="see-spot see-spot--{side}" style="--x:{x}%;--y:{y}%;--i:{i}"><span class="see-dot"></span>'
        f'<div class="see-card"><b>{esc(name)}</b><div><span>{esc(a[0])}</span><i>{esc(a[1])}</i></div>'
        f'<div><span>{esc(b[0])}</span><i class="tone-{b[2]}">{esc(b[1])}</i></div></div></div>'
        for i, (name, a, b, x, y, side) in enumerate(SEE_SPOTS))
    rows = "".join(f'<li><b>{esc(n)}</b><span>{esc(a[1])}</span></li>' for n, a, b, x, y, side in SEE_SPOTS)
    bx, by = SEE_SPOTS[-1][3], SEE_SPOTS[-1][4]
    body = ('<div class="see-spots" aria-hidden="true">' + spots + f'<span class="see-line" style="--x:{bx}%;--y:{by}%"></span></div>'
            '<div class="cine-text see-text"><div class="label">Fra bilde til forslag</div><h2>Se hva hjemmet trenger.</h2>'
            '<p class="cine-lede">Ta et bilde. ERA kobler det du ser til resten av hjemmet.</p>'
            '<p class="see-sub">Fasadens tilstand, dokumentasjon, alder og tidligere arbeid kan vurderes i samme kontekst.</p>'
            f'<ul class="see-list">{rows}</ul>'
            '<p class="see-sources"><b>ERA bruker</b> bildene dine, byggeår og materialer, tidligere arbeid og kvitteringer, og fagkunnskap.</p>'
            '<ul class="see-areas" aria-label="Områder ERA ser på">' + "".join(f'<li>{t}</li>' for t in ("Tak", "Takrenner", "Fasade", "Vinduer", "Bad", "Ventilasjon", "Kjøkken", "Uteområde")) + '</ul>'
            '<a class="link see-cta" href="#adresse">Start med adressen din →</a>'
            '<p class="cine-fine">Eksempeldata.</p></div>')
    return cine("/assets/story/roof-detail-v3.jpg", body, sid="ser", cls="cine--see", pos="60% 50%").replace('<section class="cine', '<section data-reveal class="cine', 1)


def home_page():
    """/: the homeowner-first front page (the old story now lives at /historie).
    The rhythm is cinematic, product, flow, cinematic, product, action: the photographs carry the
    feeling, the real app screens carry the meaning, and the address field is the only action.
    Other audiences keep their own pages and live in the footer."""
    a = AUDIENCES["boligeier"]
    h = DEMO_HOME
    minbolig_alt = (f"ERA Bolig: Min bolig for {h['address']} – {h['type']} fra {h['year']} på {h['area']} med tilstand "
                    f"{h['condition']} {h['score']}, neste prosjekt «{h['measure']}» til {h['cost']} med oppstart {h['start']} og "
                    f"{h['pro']}, estimert verdi {h['value']} og samlet dokumentasjon")
    agent_alt = (f"ERA Bolig, boligagenten for {h['address']}: fotoet av huset er merket av med fasade og tak til oppfølging "
                 f"og takrenner og grunnmur i god stand, etterfulgt av «Hva jeg ser», «Hva det betyr» for et hjem fra {h['year']} "
                 f"og forslaget «{h['measure']}» med estimert kostnad {h['cost']}")
    # Two questions, asked one after the other. The agent screen answers the first (it gets a ring once),
    # then the second arrives: the chips show the product working instead of decorating the hero.
    prompts = ["Hva bør jeg følge opp nå?", "Finn noen som kan fikse dette"]
    prompts_html = '<ul class="ny-prompts" aria-label="Eksempler på spørsmål til ERA">' + "".join(f"<li>{esc(t)}</li>" for t in prompts) + "</ul>"
    hero_visual = ('<div class="hero-visual">' + prompts_html + '<div class="hero-phones">'
                   + phone("/assets/story/app-minbolig.png", 853, 1844, minbolig_alt, "sm", eager=True)
                   + phone("/assets/story/app-agent.png", 853, 1844, agent_alt, "md", eager=True)
                   + '</div></div>')
    # The -m file of this photograph is a portrait crop (900x1519), so it is chosen with a media query. A
    # width descriptor would label it 1400w and desktop widths around 1400 px would pick the portrait.
    hero_img = "/assets/story/couple-sofa-window-v4.jpg"

    # 02: the journey as one flow. Anbefaler and Ordner explain the most, so they are the large screens.
    flow = app_flow(
        None, "Ditt hjem. Én agent.",
        [("Finn hjemmet", "Adresse inn. Hjemmeprofil ut.", "/assets/story/app-minbolig.png",
          "ERA Bolig: Min bolig med nøkkeltall, neste prosjekt, estimert verdi og dokumentasjon", 853, 1844, "md"),
         ("Vis eller spør", "Ta et bilde eller spør ERA.", "/assets/story/app-kamera.png",
          "ERA Bolig: kameraet rettet mot avflassende maling ved et vindu", 853, 1844, "sm"),
         ("Få et forslag", "Hva, hvorfor og når. Gjør det selv, eller få tilbud.", "/assets/story/app-agent.png",
          "ERA Bolig: boligagentens analyse av huset med funn, betydning og forslag", 853, 1844, "lg"),
         ("Få det gjort", "Behov, produkter, tilbud og oppfølging i én flyt.", "/assets/story/app-prosjekt.png",
          f"ERA Bolig: prosjektet «{h['measure']}» med kostnad, håndverker og oppgaver", 935, 1683, "lg"),
         ("Alt tilbake til hjemmet", "Neste gang starter ERA med historikken, ikke fra null.", "/assets/story/app-boligminne.png",
          "ERA Bolig, boligminnet: tidslinjen 2020 nytt bad, 2022 varmepumpe, 2024 nytt tak og 2026 fasadevask og maling", 783, 645, "sm")],
        "Eksempeldata. Samme hjem hele veien. Visualisering av farger og løsninger kommer.", "produkt",
        lede="Fra adresse og bilde til forslag, produkter, tilbud, gjennomføring og dokumentasjon – samlet i én enkel flyt.")

    # 03: what ERA knows. Documents lie scattered and gather; the list below is an example room.
    knows = (
        '<section class="section ny-knows" id="kjenner" data-nav="light">'
        '<div class="ny-knows-bg" aria-hidden="true"><img src="/assets/story/whole-home-v3.jpg" srcset="/assets/story/whole-home-v3-m.jpg 1400w, /assets/story/whole-home-v3.jpg 2400w" sizes="100vw" alt="" loading="lazy" decoding="async"></div>'
        '<div class="wrap ny-knows-grid"><div class="ny-knows-text">'
        '<div class="label">ERA kjenner hjemmet</div><h2>ERA vet hva den vet. Og sier fra når den ikke vet.</h2>'
        '<p class="ny-lede">ERA bygger én samlet hukommelse for hjemmet. Den bruker det som allerede finnes, lærer av det du legger til og sier tydelig fra når informasjon mangler.</p>'
        '<ul class="appsec-points">'
        '<li><b>Dokumentert</b>Vi vet hvor informasjonen kommer fra.</li>'
        '<li><b>ERA-forslag</b>ERA vurderer og forklarer hvorfor.</li>'
        '<li><b>Mangler</b>ERA sier fra når den ikke vet.</li></ul></div>'
        '<div class="ny-knows-stage" data-reveal>' + docs_scatter()
        + knows_view("Badet", "Eksempel · ett rom i et hjem",
                     [("doc", "Byggeår", "Fra tilstandsrapport 2021", "Dokumentert", "byggeaar"),
                      ("miss", "Dokumentasjon", "Mangler", "Mangler"),
                      ("miss", "Sist arbeid", "Bare nevnt i en e-post", "Mangler", "sistarbeid"),
                      ("ai", "ERA anbefaler", "Følg opp", "ERA-forslag")],
                     "Eksempeldata. ERA sier ifra når den ikke vet.", photo="/assets/story/bathroom-v3-m.jpg")
        + '</div></div></section>')

    # 04: one need, followed all the way to the result. The homeowner sees five steps; ERA does the rest.
    # The steps wake in order as the list scrolls into view. At "Du velger" the choices are buttons; the one
    # people reach for, "Finn noen som kan gjøre det", answers with what is already done for them.
    choices = [("Gjør det selv", "ERA hjelper med produkter, materialer og plan."),
               ("Finn produkter", "ERA foreslår produkter ut fra det hjemmet faktisk trenger."),
               ("Få tilbud fra proff", "Behovet er allerede beskrevet. Du slipper å starte fra null."),
               ("Minn meg på dette senere", "ERA tar det opp igjen når tiden er inne.")]
    chips = "".join(f'<button type="button" class="cine-chip" aria-pressed="false" data-note="{esc(n)}">{esc(c)}</button>' for c, n in choices)
    li = (
        '<li><b>ERA oppdager</b><span>Badet bør vurderes.</span></li>'
        '<li><b>ERA forklarer</b><span>Hvorfor, hvor viktig det er og hva som kan vente.</span></li>'
        f'<li><b>Du velger</b><span class="cine-chips">{chips}</span><span class="cine-note" aria-live="polite"></span></li>'
        '<li><b>ERA ordner</b><span class="mini-state" aria-label="Kartlagt, tilbud, utføres"><i class="is-done">Kartlagt</i><i class="is-now">Tilbud</i><i>Utføres</i></span></li>'
        '<li><b>Dokumenteres</b><span>Alt går tilbake til hjemmet.</span></li>')
    flow_steps = f'<ol class="cine-flow">{li}</ol>'
    need = cine("/assets/story/bathroom-old-v4.jpg",
                '<div class="cine-grid"><div class="cine-text">'
                '<h2>ERA oppdager behovet før du begynner å lete.</h2>'
                '<p class="cine-lede">Når ERA allerede vet hva som bør gjøres, slipper du å starte på nytt med Google, anbudssider og telefoner.</p>'
                '<p class="cine-fine">Eksempel. Produktforslag og påminnelser er under utvikling.</p></div>' + flow_steps + '</div>',
                sid="behov", pos="62% 50%")

    # 05: the home remembers. The house through the seasons, and a timeline of what has been done.
    timeline_steps = [("Kjøpt", False), ("Malt", False), ("Bad dokumentert", False), ("Elektrisk arbeid", False), ("Dokumentert", False), ("Neste behov", True)]
    timeline = '<ol class="cine-timeline cine-timeline--left">' + "".join(
        f'<li class="{"is-next" if nxt else ("is-link" if t == "Bad dokumentert" else "")}" style="--k:{k}"><span>{esc(t)}</span></li>' for k, (t, nxt) in enumerate(timeline_steps)) + "</ol>"
    seasons = '<div class="seasons" aria-hidden="true">' + "".join(
        f'<img{" class=" + chr(34) + "is-on" + chr(34) if i == 0 else ""} src="/assets/story/block-season-{i}-v3.jpg" srcset="/assets/story/block-season-{i}-v3-m.jpg 1400w, /assets/story/block-season-{i}-v3.jpg 1600w" '
        f'sizes="(max-width: 900px) 80vw, 420px" alt="" loading="lazy" decoding="async">' for i in range(4)) + "</div>"
    learns = cine("/assets/story/whole-home-v3.jpg",
                  '<div class="cine-grid cine-grid--seasons"><div class="cine-text" data-reveal>'
                  '<h2>Hjemmet husker. Du slipper.</h2>'
                  '<p class="cine-lede">Hvert prosjekt, bilde og dokument blir en del av hjemmet. Derfor starter ERA smartere neste gang.</p>'
                  + timeline + '<p class="cine-fine">Eksempel på et hjems tidslinje.</p></div>' + seasons + '</div>'
                  + '<ul class="husker-feats">'
                  '<li><b>Bilder og dokumentasjon</b><span>Alt samlet på ett sted.</span></li>'
                  '<li><b>Påminnelser</b><span>Beskjed når det er tid for vedlikehold, ut fra alder, materialer og forhold.</span><i class="nstep-tag">Planlagt</i></li>'
                  '<li><b>Del med andre</b><span>Del det som er relevant med håndverkere, styret eller kjøpere, når du selv velger det.</span><i class="nstep-tag">Planlagt</i></li></ul>',
                  sid="husker", pos="50% 60%")

    faq_items = [
        ('Hva er ERA?', 'ERA er hjemmets AI-agent. Den bygger kunnskap om hjemmet, oppdager relevante behov og hjelper deg fra spørsmål til ferdig jobb.'),
        ('Er ERA et nytt FDV-system?', 'Nei. Et FDV-system organiserer og dokumenterer informasjon. ERA bruker informasjonen aktivt for å forstå hjemmet, oppdage behov og hjelpe deg videre til handling.'),
        ('Hva er forskjellen på ERA og Boligmappa?', 'Boligmappa er først og fremst dokumentasjon og historikk. ERA bruker kunnskapen om hjemmet til å svare på: Hva betyr dette? Hva bør jeg gjøre nå? Og vil du at jeg skal hjelpe deg få det gjort?'),
        ('Hva er forskjellen på ERA og Mittanbud?', 'Mittanbud blir relevant når du allerede vet at du trenger en håndverker. ERA kan starte tidligere: forstå behovet, forklare det og hjelpe deg velge mellom å gjøre det selv eller få hjelp av proff.'),
        ('Hva er forskjellen på ERA og ChatGPT?', 'ChatGPT er generell AI. ERA bygger en vedvarende hukommelse rundt ditt konkrete hjem og bruker eiendomsdata, bilder, dokumentasjon og historikk som kontekst.'),
        ('Hva vet ERA om hjemmet mitt?', 'ERA starter med tilgjengelige eiendomsdata og informasjon du legger til, som bilder, dokumenter og historikk. Den viser hva som er dokumentert, hva den foreslår og hva den ikke vet.'),
        ('Kan ERA hjelpe meg gjøre det selv eller finne en proff?', 'Begge deler. Vil du gjøre jobben selv, skal ERA hjelpe med produkter, materialer og plan. Vil du ha hjelp, kan det samme behovet gå videre til en proff, uten at du må beskrive det på nytt. Produktforslag og tilbud er under utvikling.'),
        ('Fungerer ERA også for leilighet og borettslag?', 'Ja. ERA kan brukes for enebolig, rekkehus og leilighet. I borettslag og sameier kan noe informasjon og ansvar ligge hos styret, mens annet gjelder det enkelte hjemmet.'),
        ('Hva skjer med dataene mine?', 'Du bestemmer hvem som får tilgang. Data skal ikke deles med håndverkere, partnere eller andre uten at du velger det.'),
        ('Hva koster ERA?', 'ERA er gratis de første tolv månedene. Ingen betalingskort og ingen binding.'),
    ]
    faq = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in faq_items)
    done = ("Takk. Vi har adressen din.", "")
    hero_form = lead_form_html("hero", a, done, label="Skriv adressen din", placeholder="Myrerveien 46A, Oslo")
    end_form = lead_form_html("end", a, done, placeholder="Myrerveien 46A, Oslo")

    # 06: the close. One address field, almost no text.
    close = cine("/assets/story/door-evening-v4.jpg",
                 '<div class="cine-center">'
                 '<h2>Finn hjemmet ditt.</h2>'
                 '<p class="cine-lede">Se hva ERA allerede kan vite – og begynn å bygge hjemmets hukommelse.</p>'
                 + end_form +
                 '<p class="ny-micro">Gratis i tolv måneder · Ingen betalingskort</p>'
                 '<p class="ny-trust"><b>Dine data. Ditt hjem.</b> Du bestemmer hvem som får tilgang.</p></div>',
                 sid="skjema", cls="cine--center cine--close", pos="60% 50%")

    how, sofa, bilde, valget_html, ferdig, see = how_it_works(), reise_sofa(), reise_bilde(), valget(), reise_ferdig(), scene_see()

    # Om ERA is a teaser here and a page of its own next to this one.
    teaser = ('<section class="ny-teaser" data-nav="dark"><div class="wrap"><div><h2>Hvert hjem får en agent.</h2>'
              '<p>En agent som kjenner hjemmet, følger med på hva den trenger og hjelper deg få ting gjort.</p></div>'
              '<a class="link" href="/ny/om-era">Les historien om ERA →</a></div></section>')

    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Hjemmets AI-agent — ERA</title>
<meta name="description" content="{esc(NY_DESC)}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/", "Hjemmets AI-agent — ERA", NY_DESC)}
<link rel="preload" href="/fonts/d09f6137-d0ab-46d2-a3bf-0d7be812fb75.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body class="ny-page" data-audience="{a["key"]}" data-page="ny">
{ny_nav()}

<header class="hero hero--product ny-hero" data-nav="dark">
  <div class="hero-media"><picture><source media="(max-width: 899px)" srcset="{hero_img[:-4]}-m.jpg"><img src="{hero_img}" alt="" fetchpriority="high" style="object-position: 45% 50%"></picture></div>
  <div class="hero-grid">
  <div class="hero-text">
    <div class="label">ERA · for boligeiere</div>
    <h1 data-hero-h1 data-a="ERA kjenner hjemmet ditt. Og hjelper deg når noe skal gjøres.">Hjemmets AI-agent.<span class="h1-sub">ERA kjenner hjemmet ditt, oppdager hva som bør gjøres og hjelper deg få det gjort.</span></h1>
    <p class="lede" data-hero-sub data-a="Hjemmets AI-agent. Spør om historikk, dokumentasjon og neste steg, og få hjelp til å gjøre det.">Spør om hjemmet, ta et bilde eller se hva som bør følges opp. ERA hjelper deg videre med plan, produkter eller tilbud fra proff.</p>
    <div id="adresse">
      {hero_form}
    </div>
    <p class="ny-micro">Gratis i tolv måneder · Ingen betalingskort</p>
  </div>
  {hero_visual}
  </div>
</header>

<main>
  {how}

  {sofa}

  {bilde}

  {valget_html}

  {ferdig}

  {flow}

  {knows}

  {see}

  {need}

  {learns}

  <section class="section" data-nav="light" id="kategori">
    <div class="wrap narrow">
      <div class="label">Kategorien</div>
      <h2>Hva slags produkt er ERA?</h2>
      <div class="kat" role="list">
        <div class="kat-row" role="listitem"><b>Boligmappa</b><span>Dokumentasjon og historikk.</span></div>
        <div class="kat-row" role="listitem"><b>Mittanbud</b><span>Markedsplass for håndverkere, når du allerede vet hva som skal gjøres.</span></div>
        <div class="kat-row" role="listitem"><b>ChatGPT</b><span>Generell AI, uten vedvarende kontekst om hjemmet ditt.</span></div>
        <div class="kat-row kat-era" role="listitem"><b>ERA</b><span><i>Hjemmets AI-agent.</i> Kjenner hjemmet, oppdager behov og hjelper deg videre til handling.</span></div>
      </div>
    </div>
  </section>

  <section class="section alt" data-nav="light">
    <div class="wrap narrow">
      <div class="label">Spørsmål</div>
      <h2>Det folk lurer på.</h2>
      <div class="faq ny-faq">{faq}</div>
    </div>
  </section>

  {close}

  {teaser}
</main>

{ny_footer()}
<script src="/pages.js" defer></script>
</body>
</html>
'''


def partner_page():
    """/partnere: for meglere and partners. Short, no figures and no named counterparties; the contact form
    posts to /api/lead as audience "samarbeid". noindex until the text has been approved."""
    hero = ('<section class="cine cine--hero om-hero" data-nav="dark"><div class="cine-media"><img src="/assets/story/neighbourhood-dusk-v4.jpg" srcset="/assets/story/neighbourhood-dusk-v4-m.jpg 1400w, /assets/story/neighbourhood-dusk-v4.jpg 3000w" sizes="100vw" alt="" fetchpriority="high" decoding="async"></div><div class="cine-body">'
            '<div class="label">For meglere og partnere</div><h1>Hjemmet følger kjøperen videre.</h1>'
            '<p class="cine-lede">ERA samler hjemmets historikk, dokumentasjon og utført arbeid på ett sted. Sammen med meglere og partnere kan hjemmet bli levert med historikken på plass, og eieren får hjelp også etter overtakelsen.</p></div></section>')
    blocks = [("For meglere", "Hjemmet kan overleveres med dokumentasjon og historikk samlet. Kjøperen starter med et hjem ERA allerede kjenner, i stedet for en mappe med papirer."),
              ("For leverandører og faghandel", "Når ERA har beskrevet et behov, kan det gå videre til produkter og fagfolk. Behovet er allerede forklart, og resultatet dokumenteres tilbake på hjemmet."),
              ("For andre partnere", "Boligbyggerlag, forsikring, bank og andre som møter huseiere. Vi utforsker samarbeid der hjemmets historikk gjør tjenesten enklere for eieren.")]
    items = "".join(f'<li><h3>{esc(t)}</h3><p>{esc(d)}</p></li>' for t, d in blocks)
    body = ('<section class="section partner-blocks" data-nav="light"><div class="wrap wide">'
            '<h2 class="sr">Slik kan vi samarbeide</h2>'
            f'<ol class="partner-grid">{items}</ol>'
            '<p class="partner-status">ERA er i betaperiode, og enkelte deler er i pilot. Samarbeid avtales per partner, og ingenting her er et løfte om funksjoner som ikke er lansert.</p></div></section>')
    contact = ('<section class="section partner-contact" id="kontakt" data-nav="light"><div class="wrap narrow">'
               '<h2>Snakk med oss</h2>'
               '<form class="partner-form" novalidate>'
               '<label for="pf-name">Navn og firma</label><input id="pf-name" name="value" type="text" autocomplete="name" maxlength="200" required>'
               '<label for="pf-email">E-post</label><input id="pf-email" name="email" type="email" autocomplete="email" inputmode="email" maxlength="200" required>'
               '<label for="pf-msg">Hva vil du samarbeide om?</label><textarea id="pf-msg" name="message" rows="4" maxlength="1000"></textarea>'
               '<input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">'
               '<button type="submit" class="btn">Send</button></form>'
               '<div class="partner-err" role="alert" hidden></div>'
               '<div class="partner-done" role="status" tabindex="-1" hidden><b>Takk. Vi har meldingen din.</b><span>Vi svarer personlig.</span></div>'
               '<p class="partner-small">Vi svarer personlig. Ingen nyhetsbrev.</p></div></section>')
    desc = "For meglere og partnere: ERA samler hjemmets historikk, dokumentasjon og utført arbeid, slik at hjemmet kan følge kjøperen videre."
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>For meglere og partnere — ERA</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/partnere", "For meglere og partnere — ERA", desc)}
<link rel="preload" href="/fonts/d09f6137-d0ab-46d2-a3bf-0d7be812fb75.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body class="ny-page" data-audience="boligeier" data-page="partner">
{ny_nav("/", current=False)}
<main>
  {hero}
  {body}
  {contact}
</main>
{ny_footer("/")}
<script src="/pages.js" defer></script>
</body>
</html>
'''


def om_era_page():
    """/ny/om-era: the simple Om ERA page. A cinematic opening, why ERA exists, what is being built as one
    loop, and the people behind it. Sits next to /ny and leaves the existing /om-era alone."""
    a = AUDIENCES["boligeier"]
    about_src = "/assets/story/about-hero-v5.jpg"
    hero = ('<section class="cine cine--hero om-hero" data-nav="dark"><div class="cine-media"><img src="' + about_src + '" srcset="' + about_src[:-4]
            + '-m.jpg 900w, ' + about_src + ' 1600w" sizes="100vw" alt="" fetchpriority="high" decoding="async"></div><div class="cine-body">'
            '<div class="label">Om ERA</div><h1>Hvert hjem får en agent.</h1>'
            '<p class="cine-lede">ERA bygger hjemmets AI-agent: den kjenner hjemmet, oppdager hva som bør gjøres og hjelper deg fra behov til ferdig jobb. Bak den ligger hjemmedata, kunstig intelligens, handel, tjenester og dokumentasjon i én kontinuerlig flyt rundt hjemmet.</p>'
            '<p class="cine-gold">Fra hjemmedata til handling.<br>Fra handling tilbake til hjemmet.</p></div></section>')
    why = ('<section class="section om-why" data-nav="light"><div class="wrap narrow"><div class="label">Hvorfor ERA</div>'
           '<h2>Hjemmet er spredt over mange steder.</h2>'
           '<p class="om-text">Hjemmet er i dag fragmentert mellom dokumenter, håndverkere, bank, forsikring, produkter og Google. ERA samler konteksten og hjelper eieren fra spørsmål til handling.</p></div></section>')
    steps = ["Hjem", "Kunnskap", "Behov", "Handling", "Dokumentasjon", "Smartere hjem"]
    loop = ('<ol class="cine-timeline">' + "".join(
        f'<li class="{"is-next" if i == len(steps) - 1 else ""}"><span>{esc(t)}</span></li>' for i, t in enumerate(steps)) + "</ol>")
    build = cine("/assets/story/loop-home-v3.jpg",
                 '<div class="cine-center"><div class="label">Hva vi bygger</div><h2>Én enkel loop.</h2>' + loop + '</div>',
                 sid="bygger", cls="cine--center", pos="50% 55%")
    tech = ('<section class="section om-tech" id="teknologien" data-nav="light"><div class="wrap narrow"><div class="label">Proprietær analyseteknologi</div>'
            '<h2>ERA gjør fragmenterte hjemmedata om til kontinuerlig, handlingsbar kunnskap om hjemmet.</h2>'
            '<p>ERAs proprietære analyseteknologi er utviklet for å bygge og kontinuerlig oppdatere en strukturert digital kunnskapsmodell av det enkelte hjemmet.</p>'
            '<p>Teknologien kombinerer eiendomsdata, bilder, dokumenter, rom- og materialinformasjon, historikk, utførte arbeider og bruker-/fagpersoninput. AI brukes til å analysere og strukturere informasjonen, mens ERAs egen kunnskapsarkitektur vurderer blant annet kilde, kontekst, sikkerhet, motstridende informasjon og hvordan kunnskapen endrer seg over tid.</p>'
            '<p>Det unike ligger derfor ikke i én enkelt AI-modell, men i systemet rundt analysen: ERA bygger et vedvarende digitalt hjemmeminne hvor ny informasjon kobles til eksisterende kunnskap om hjemmet, fremfor at hver analyse behandles isolert.</p>'
            '<p>Dette gjør at ERA over tid kan gå fra å beskrive hjemmet til å forstå hva som er kjent og ukjent, identifisere relevante vedlikeholds- og oppussingsbehov, foreslå neste handling og dokumentere resultatet tilbake på hjemmet.</p></div></section>')
    team = ('<section class="section ny-team" id="teamet" data-nav="light"><div class="wrap wide">'
            '<div class="label">Menneskene bak ERA</div>'
            '<h2>Vi kjenner hjem. Og bygger teknologien rundt dem.</h2>'
            '<p class="ny-team-lede">ERA bygges av mennesker med lang erfaring fra eiendom, teknologi, finans, bygg, handel og AI. Sammen bygger vi en enklere måte å eie, forstå og ta vare på hjemmet på.</p>'
            + team_html() + '</div></section>')
    cta = ('<section class="ny-teaser ny-teaser--cta" data-nav="dark"><div class="wrap"><div><h2>Finn hjemmet ditt.</h2>'
           '<p>Skriv adressen din, så åpner vi ERA for hjemmet ditt. Gratis de første tolv månedene.</p></div>'
           '<a class="btn" href="/#adresse">Finn hjemmet mitt</a></div></section>')
    desc = "ERA bygger hjemmets AI-agent. Hvert hjem får en agent. Hvorfor ERA finnes, hva vi bygger og menneskene bak."
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Om ERA — Hvert hjem får en agent</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/ny/om-era", "Om ERA — Hvert hjem får en agent", desc)}
<link rel="preload" href="/fonts/d09f6137-d0ab-46d2-a3bf-0d7be812fb75.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body class="ny-page" data-audience="{a["key"]}" data-page="om-era-ny">
{ny_nav("/")}
<main>
  {hero}

  {why}

  {build}

  {tech}

  {team}

  {cta}
</main>

{ny_footer("/")}
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
with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(home_page())
print("wrote index.html (front page)")
os.makedirs(os.path.join(ROOT, "ny", "om-era"), exist_ok=True)
with open(os.path.join(ROOT, "ny", "om-era", "index.html"), "w", encoding="utf-8") as f:
    f.write(om_era_page())
print("wrote ny/om-era")
os.makedirs(os.path.join(ROOT, "partnere"), exist_ok=True)
with open(os.path.join(ROOT, "partnere", "index.html"), "w", encoding="utf-8") as f:
    f.write(partner_page())
print("wrote partnere")
