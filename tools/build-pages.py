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
    "address": "Eksempelveien 12",
    "city": "Oslo",
    "type": "enebolig",
    "area": "162 m²",
    "year": "1967",
    "condition": "God",
    "score": "78 av 100",
    "measure": "Fasadevask og maling",
    "cost": "85 000–140 000 kr",
    "start": "april 2026",
    "duration": "2–3 uker",
    "pro": "Fasadeeksperten (eksempel)",
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


import os

# Private Beta: the invitation flow on the front page is built but OFF. The markup and script for «Jeg har en
# invitasjon» exist behind this flag, and the ERA app/backend (ERA-ID, invite tokens, the maximum of five,
# referral status) is owned by the CTO, not by this repo. Turn it on only when the app API answers on api_base:
#   POST {api_base}/invite/validate   {token}                 -> {status}
#   POST {api_base}/invite/accept     {token, home, source}   -> {status, url?}
# status is one of: valid, expired, already_used, revoked, accepted, capacity_reached.
# For local testing: ERA_INVITE_FLOW=1 ERA_API_BASE=http://localhost:9000 python tools/build-pages.py
FEATURES = {
    "invite_flow": os.environ.get("ERA_INVITE_FLOW") == "1",
    "api_base": os.environ.get("ERA_API_BASE", ""),
}


def era_config_meta():
    import json
    cfg = {"invite": FEATURES["invite_flow"], "api": FEATURES["api_base"]}
    return '<meta name="era-config" content=\'' + json.dumps(cfg) + '\'>'


# Status for what ERA Prosjekt can do, one place so every page says the same thing. Beta = available to beta
# users. I pilot = tested with selected partners. Planlagt = not available yet. Copy never upgrades a status.
STATUS = {
    "kjenne": "Beta", "forstaa": "Beta", "rommet": "I pilot", "plan": "Beta", "beskrivelse": "Beta",
    "handleliste": "I pilot", "produkter": "I pilot", "kjop": "Planlagt", "proff": "Beta", "husker": "Beta",
}


def st(key):
    return f'<i class="nstep-tag">{esc(STATUS[key])}</i>'


def capabilities_section():
    """/boligeier: what ERA can help with, grouped by what the owner is trying to get done. An editorial list,
    not eight identical cards."""
    rows = [("Kjenne boligen", "Eiendomsdata, bilder, dokumenter, rom, materialer og historikk samlet i boligens hukommelse.", "kjenne"),
            ("Forstå behovet", "Se hva som bør følges opp, hvorfor, og hva som mangler. Et utgangspunkt, ikke en diagnose.", "forstaa"),
            ("Se rommet før du bestemmer deg", "Utforsk løsninger, materialer og uttrykk før prosjektet starter.", "rommet"),
            ("Lage prosjektplan", "En strukturert beskrivelse av hva som skal gjøres.", "plan"),
            ("Lage handlelisten", "Materialer, produkter og mengder samlet.", "handleliste"),
            ("Gjøre det selv", "Gå fra plan til produkter, og hent eller bestill.", "kjop"),
            ("Få hjelp av proff", "Send prosjektet videre og be om tilbud. Du beskriver behovet én gang.", "proff"),
            ("Huske resultatet", "Arbeid, bilder og dokumentasjon tilbake på boligen.", "husker")]
    lis = "".join(f'<li><b>{esc(t)}</b><span>{esc(d)}</span>{st(k)}</li>' for t, d, k in rows)
    return ('<section class="section cap" id="kan-hjelpe" data-nav="light"><div class="wrap wide">'
            '<div class="label">Boligens AI-agent</div><h2>Dette kan ERA hjelpe deg med.</h2>'
            '<p class="cap-lede">ERA kjenner boligen, forstår behovet og hjelper deg få det gjort. Fra bilde eller spørsmål til prosjektplan, handleliste, produkter eller tilbud fra håndverker, og tilbake på boligen når jobben er ferdig.</p>'
            f'<ol class="cap-list">{lis}</ol>'
            '<p class="cap-note">Beta betyr tilgjengelig for betabrukere. I pilot betyr testet med utvalgte partnere. Planlagt betyr ikke tilgjengelig ennå.</p></div></section>')


def prosjekt_flow_section():
    """/boligeier: ERA Prosjekt, from idea to finished project, in the seven steps."""
    steps = [("Vis eller beskriv", "Ta et bilde, velg et rom eller fortell ERA hva du vil gjøre.", "forstaa"),
             ("Se mulighetene", "ERA bruker det den vet om boligen til å hjelpe deg forstå løsninger og alternativer.", "forstaa"),
             ("Få prosjektplanen", "ERA strukturerer hva som skal gjøres.", "plan"),
             ("Få det du trenger", "Materialer, mengder, produkter og handleliste.", "handleliste"),
             ("Velg hvordan", "Gjør det selv, eller få hjelp av proff.", None),
             ("Få det gjort", "Kjøp produkter, hent i butikk, eller send prosjektet videre for tilbud.", "kjop"),
             ("Alt tilbake til boligen", "Resultat, bilder, kvitteringer og dokumentasjon kan føres tilbake til boligen.", "husker")]
    lis = "".join(f'<li><span class="pf-n">{i+1}</span><div><b>{esc(t)}</b><p>{esc(d)}</p>' + (st(k) if k else "") + '</div></li>' for i, (t, d, k) in enumerate(steps))
    return ('<section class="section pflow alt" id="era-prosjekt" data-nav="light"><div class="wrap wide">'
            '<div class="label">ERA Prosjekt</div><h2>Fra idé til ferdig prosjekt.</h2>'
            '<p class="cap-lede">ERA Prosjekt er en del av Boligens AI-agent, ikke en egen app. Det er veien din når du vil vedlikeholde, male, bytte gulv, pusse opp et rom eller gjøre større og mindre arbeid i boligen.</p>'
            f'<ol class="pf-steps">{lis}</ol>'
            '<p class="cap-note">Bytter du fra gjør-det-selv til proff, beholder ERA prosjektet. Du slipper å forklare det på nytt, og du velger hva som følger forespørselen.</p>'
            '<a class="link" href="#adresse">Start et prosjekt →</a></div></section>')



# FAQ about access. The invite questions are only added when the invite flow is switched on, so the page never
# describes a feature that does not exist yet.
ACCESS_FAQ = [("Hvordan får jeg tilgang til ERA?",
               "ERA er foreløpig i Private Beta. Du kan få tilgang gjennom en invitasjon fra ERA, en samarbeidspartner"
               + (" eller en eksisterende ERA-bruker" if FEATURES["invite_flow"] else "")
               + ". Hvis du ikke har en invitasjon, kan du be om tidlig tilgang.")]
if FEATURES["invite_flow"]:
    ACCESS_FAQ += [("Hvor mange kan jeg invitere?", "Hver aktiv ERA-ID kan invitere opptil fem andre til Private Beta."),
                   ("Kan jeg få flere enn fem invitasjoner?", "Ikke som standard. Private Beta er begrenset mens vi utvikler produktet og åpner kapasiteten gradvis.")]

def access_section():
    """/boligeier: how access works. The invitation steps only appear when the flow is on."""
    if FEATURES["invite_flow"]:
        steps = [("Finn boligen", "Start med adressen."), ("Bruk invitasjonen", "Aktiver ERA hvis du er invitert."),
                 ("Har du ingen invitasjon?", "Be om tidlig tilgang."), ("Når boligen åpnes", "Vi gir beskjed."),
                 ("Når du har brukt ERA", "Du kan invitere opptil fem andre.")]
    else:
        steps = [("Finn boligen", "Start med adressen."), ("Be om tidlig tilgang", "ERA er foreløpig på invitasjon."),
                 ("Når boligen åpnes", "Vi gir beskjed."), ("Bruk ERA", "Spør, vis og start et prosjekt.")]
    lis = "".join(f'<li><span class="pf-n">{i+1}</span><div><b>{esc(t)}</b><p>{esc(d)}</p></div></li>' for i, (t, d) in enumerate(steps))
    return ('<section class="section pflow" id="tilgang" data-nav="light"><div class="wrap wide">'
            '<div class="label">Private Beta</div><h2>Slik får du tilgang.</h2>'
            '<p class="cap-lede">ERA åpner nå for de første hjemmene. Tilgang gis foreløpig på invitasjon mens vi utvikler ERA sammen med de første boligeierne.</p>'
            f'<ol class="pf-steps">{lis}</ol></div></section>')


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
        key="owner", nav="Boligeier", title="ERA for boligeiere",
        meta="Boligens AI-agent for boligeiere. ERA kjenner boligen, forstår behovet og hjelper deg fra bilde eller spørsmål til prosjektplan, handleliste og tilbud fra håndverker, og lagrer resultatet i boligens hukommelse.",
        label="For boligeiere", hook="Å eie hjem uten gjetting.",
        lede="En personlig agent for boligen din. ERA kjenner boligen, ser hva den trenger og hjelper deg få det gjort.",
        image="/assets/story/couple-sofa-v3.jpg", image_pos="55% 55%",
        app_hero=dict(src="/assets/story/app-hjem.png", w=935, h=1683, size="lg",
                      alt=f"ERA Bolig på mobil: forsiden for {DEMO_HOME['address']} med boligtype {DEMO_HOME['type']}, "
                          f"{DEMO_HOME['area']}, byggeår {DEMO_HOME['year']}, tilstand {DEMO_HOME['condition']} "
                          f"{DEMO_HOME['score']}, neste tiltak «{DEMO_HOME['measure']}», estimert kostnad "
                          f"{DEMO_HOME['cost']}"),
        app_sections=[
            capabilities_section(),
            access_section(),
            app_section(
                "Min bolig", "Alt om boligen. Ett sted.",
                "Ikke bare data fra registre. ERA bygger en levende boligprofil som utvikler seg når du legger til rom, dokumentasjon, arbeid og nye opplysninger.",
                phone("/assets/story/app-minbolig.png", 853, 1844,
                      f"ERA Bolig: Min bolig for {DEMO_HOME['address']} – {DEMO_HOME['type']} fra {DEMO_HOME['year']} på "
                      f"{DEMO_HOME['area']} med tilstand {DEMO_HOME['condition']} {DEMO_HOME['score']}, neste prosjekt "
                      f"«{DEMO_HOME['measure']}» til {DEMO_HOME['cost']} med oppstart {DEMO_HOME['start']} og "
                      f"{DEMO_HOME['pro']} og samlet dokumentasjon",
                      "lg"),
                alt_bg=True, flip=True, sid="slik"),
            app_section(
                "Kamera", "Vis ERA hva du ser.",
                "Ta et bilde av noe du lurer på. ERA analyserer det sammen med informasjonen den allerede har om boligen.",
                phone("/assets/story/app-kamera.png", 853, 1844,
                      "ERA Bolig: kameraet rettet mot avflassende maling på kledningen ved et vindu, med teksten «Ta et bilde – fokuser på problemet, så analyserer ERA det for deg» og valget «Analyser med ERA»",
                      "lg", cap="Eksempeldata · Eksempelveien 12"),
                foot="Du starter med det du faktisk ser, ikke med et skjema."),
            app_section(
                "Boligagent", "Ikke bare et AI-svar. Et svar om boligen din.",
                "ERA kombinerer det du spør om eller viser med tilgjengelig informasjon om boligens alder, historikk, tilstand og tidligere arbeid.",
                phone("/assets/story/app-agent.png", 853, 1844,
                      f"ERA Bolig, boligagenten for {DEMO_HOME['address']}: fotoet av huset er merket av med fasade og tak "
                      "til oppfølging og takrenner og grunnmur i god stand, etterfulgt av «Hva jeg ser» med de fire "
                      f"punktene, «Hva det betyr» for en bolig fra {DEMO_HOME['year']}, og forslaget «{DEMO_HOME['measure']}» "
                      f"med estimert kostnad {DEMO_HOME['cost']}, oppstart {DEMO_HOME['start']} og {DEMO_HOME['pro']}",
                      "lg"),
                points=[("Hva jeg ser", "Fasade og tak bør følges opp. Takrenner og grunnmur er i god stand."),
                        ("Hva det betyr", f"Boligen er fra {DEMO_HOME['year']}. Det gjør fasade, tak og el-anlegg verdt å se nærmere på."),
                        ("Mitt forslag", f"«{DEMO_HOME['measure']}» med kostnad, oppstart og en håndverker som kan gjøre jobben.")],
                alt_bg=True, flip=True, sid="boligagent"),
            next_steps_section(
                "Se rommet før du bestemmer deg · I pilot", "Se rommet. Velg løsningen. Start prosjektet.",
                "ERA kan bygge en visuell modell av rommet og hjelpe deg utforske løsninger, materialer og uttrykk før prosjektet starter. Funksjonen er i pilot. Poenget er ikke inspirasjon alene, men at du kan gå videre til et faktisk prosjekt.",
                cards=[
                    ("Gjør det selv", "Plan, materialer, produkter og handleliste. Vil du gjøre jobben selv, hjelper ERA deg fra plan til handleliste. Kjøp og henting i butikk krever partnerintegrasjon.", None, None, "I pilot"),
                    ("Få hjelp av proff", "ERA bruker prosjektbeskrivelsen til å gjøre forespørselen bedre strukturert: hva som skal gjøres, rom eller område, bilder du velger og relevant informasjon om boligen. Be om tilbud fra håndverkere i ERA-nettverket.", None, None, "Beta"),
                ],
                sid="visualiser",
                foot="Visualisering, handleliste og produkter er i pilot. Kjøp og henting direkte i ERA er planlagt og ikke tilgjengelig ennå. Tilbud fra håndverker er tilgjengelig i beta."),
            prosjekt_flow_section(),
            app_section(
                "Prosjektet i appen", "Fra anbefaling til gjennomføring.",
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
                "Neste steg · Delvis planlagt", "Når boligen trenger mer enn en påminnelse.",
                "ERA kobler det dokumenterte behovet med riktige muligheter for gjennomføring – enten det gjelder forsikring, finansiering eller fagfolk i ERA-nettverket.",
                cards=[
                    ("Forsikring", "Sjekk om forholdet kan være relevant for forsikringen din, og finn frem nødvendig dokumentasjon.",
                     "Avklar dekning", "#boligagent", "Planlagt"),
                    ("Finansiering", "Få oversikt over forventet kostnad og mulige finansieringsalternativer før du starter prosjektet.",
                     "Se muligheter", "#boligagent", "Planlagt"),
                    ("Gjennomføring", "Gå videre til håndverker i ERA-nettverket med samme dokumentasjon, bilder og prosjektgrunnlag.",
                     "Innhent tilbud", "/handverker"),
                ],
                sid="neste-steg",
                foot="Forsikring og finansiering er planlagt og ikke tilgjengelig ennå. ERA gir grunnlag for å vurdere alternativer. ERA gir ikke forsikrings- eller lånetilsagn, og lover ikke dekning, godkjenning eller vilkår."),
            app_section(
                "Boligminne", "Alt som gjøres blir en del av boligen.",
                "Arbeid, dokumentasjon og historikk følger boligen videre – slik at du slipper å starte på nytt hver gang noe skal vedlikeholdes, vurderes eller forbedres.",
                ui("/assets/story/app-boligminne.png", 783, 645,
                   "ERA Bolig, boligminnet: tidslinjen 2020 nytt bad, 2022 varmepumpe, 2024 nytt tak og 2026 fasadevask og maling",
                   cap="Eksempeldata · Eksempelveien 12"),
                points=[("Det som er gjort", "Bad, varmepumpe og tak ligger med år og dokumentasjon."),
                        ("Det som kommer", "Fasadeprosjektet fra bildet står som planlagt.")],
                alt_bg=False, flip=True, sid="boligminne"),
            app_loop(
                "Hele løpet", "Fra spørsmål til ferdig dokumentert.",
                [("Boligen", "ERA kjenner den.", "/assets/story/app-hjem.png",
                  "ERA Bolig: forsiden for eksempelboligen med tilstand og neste tiltak", 935, 1683),
                 ("Kamera", "Vis ERA problemet.", "/assets/story/app-kamera.png",
                  "ERA Bolig: kameraet rettet mot avflassende maling ved et vindu", 853, 1844),
                 ("Boligagent", "Forstå hva det betyr.", "/assets/story/app-agent.png",
                  "ERA Bolig: boligagentens analyse av huset med funn, betydning og forslag", 853, 1844),
                 ("Prosjekt", "Planlegg og gjennomfør.", "/assets/story/app-prosjekt.png",
                  "ERA Bolig: prosjektet «Fasadevask og maling» med kostnad, håndverker og fremdrift", 935, 1683),
                 ("Min bolig", "Dokumenter og husk.", "/assets/story/app-minbolig.png",
                  "ERA Bolig: Min bolig med nøkkeltall, neste prosjekt og dokumentasjon", 853, 1844)],
                "Eksempeldata. Samme eksempelbolig, Eksempelveien 12, gjennom hele løpet."),
        ],
        gains=[
            ("Vit hva som haster", "Og hva som kan vente. Noen ganger er riktig råd å gjøre ingenting ennå."),
            ("Slutt på gjetting", "Kostnad, tid og forarbeid er regnet ut før du bestemmer deg."),
            ("Alt på ett sted", "Dokumentasjonen følger boligen, også til neste eier."),
            ("Dine data", "Lagret kryptert innenfor EU/EØS. Du bestemmer hvem som ser dem."),
        ],
        # FAQ-en er kategoriavklarende forst, kjopsnar etterpa. De seks forste staar apent;
        # resten ligger bak «Se alle sporsmal». Rekkefolgen er bevisst: tvilen om hva ERA *er*
        # ryddes for sporsmal om data, handling og pris.
        faq=[
            ("Hva er ERA?",
             "ERA er Boligens AI-agent, en personlig agent som kjenner boligen din, ser hva den trenger og hjelper deg få det gjort. Du kan spørre ERA, ta et bilde eller starte et prosjekt."),
            ("Er ERA bare en chatbot?",
             "Nei. ERA er bygget rundt den konkrete boligen. Bilder, dokumenter, rom, historikk og utført arbeid kan bli del av boligkonteksten, slik at ERA ikke trenger å starte fra null hver gang."),
            ("Hvordan henger ERA sammen med Boligmappa?",
             "Boligmappa samler dokumentasjon og historikk om boligen. ERA bruker slik kunnskap til å svare på hva det betyr og hva du bør gjøre nå – og ferdig arbeid kan dokumenteres tilbake."),
            ("Gjelder ERA for leilighet og borettslag, eller bare enebolig?",
             "Begge deler. Den signerte piloten er et borettslag med 69 leiligheter. Bor du i borettslag eller sameie, "
             "får du din egen oversikt over boligen, vedlikeholdsplan og påminnelser, samtidig som styret kan bruke ERA for "
             "fellesarealene."),
            ("Hva er forskjellen på ERA og Mittanbud?",
             "Mittanbud blir relevant når du allerede vet at du trenger en håndverker. ERA kan starte tidligere, og hjelpe "
             "deg forstå behovet og vurdere hva som bør gjøres. Deretter velger du:",
             [("Gjør det selv — ", "ERA hjelper med plan, produkter og veiledning."),
              ("Få hjelp av proff — ", "behovet er allerede beskrevet, så du slipper å starte prosessen på nytt.")]),
            ("Hva vet ERA om boligen min?",
             "ERA starter med det som allerede finnes eller kan hentes inn om boligen, og lærer mer etter hvert som du "
             "legger til bilder, dokumenter og informasjon. ERA skiller mellom tre ting:",
             [("Dokumentert — ", "vi vet hvor informasjonen kommer fra."),
              ("ERA-forslag — ", "ERA gjør en vurdering og forklarer hvorfor."),
              ("Mangler — ", "ERA sier fra når informasjonen ikke finnes.")]),
            ("Kan ERA hjelpe meg å gjøre det selv eller finne en proff?",
             "Ja. ERA utvikles for begge veier. Vil du gjøre jobben selv, kan ERA hjelpe med plan → produkter → mengder → "
             "handleliste → veiledning. Vil du heller ha hjelp, kan det samme behovet brukes videre mot en proff."),
            ("Hva koster ERA?",
             "ERA er gratis for boligeiere i betaperioden. Ingen betalingskort."),

            # ── bak «Se alle spørsmål» ──
            ("Kan ERA analysere et bilde?",
             "Ja, i beta. Du kan ta et bilde eller beskrive hva du lurer på, og ERA vurderer det sammen med det den vet om boligen. Svaret er et utgangspunkt for hva som bør følges opp. Det er ikke en diagnose eller en teknisk inspeksjon."),
            ("Kan ERA hjelpe meg planlegge oppussing?",
             "ERA Prosjekt skal hjelpe deg fra idé til ferdig prosjekt: vis eller beskriv hva du vil gjøre, få en prosjektplan og velg om du vil gjøre det selv eller få hjelp. Prosjektplan er tilgjengelig i beta. Handleliste og produkter er i pilot. Å se rommet før du bestemmer deg er også i pilot."),
            ("Kan jeg se hvordan rommet kan bli?",
             "Det er i pilot: ERA kan bygge en visuell modell av rommet og la deg utforske løsninger, materialer og uttrykk før prosjektet starter. Funksjonen testes med utvalgte partnere og er ikke tilgjengelig for alle ennå."),
            ("Kan ERA lage en prosjektbeskrivelse?",
             "Ja, i beta. Du beskriver behovet én gang, og ERA samler det som kan følge prosjektet videre: hva som skal gjøres, rom eller område, bilder du velger, ønsket resultat og relevant informasjon om boligen. Du velger hva som følger forespørselen."),
            ("Kan ERA lage en handleliste?",
             "Det er i pilot. ERA utvikles for å gå fra prosjektplan til materialer, produkter og en samlet handleliste. Funksjonen testes med utvalgte partnere og er ikke tilgjengelig for alle ennå."),
            ("Kan ERA hjelpe med mengder og materialer?",
             "Det er i pilot. Målet er at ERA hjelper deg å anslå hva du trenger, ut fra prosjektplanen. Kontroller alltid mengder og produkter før du kjøper."),
            ("Kan jeg hente produktene i butikk?",
             "Det er planlagt. Kjøp og henting i butikk krever integrasjon med partnere, og er ikke tilgjengelig ennå."),
            ("Hva er forskjellen på ERA og generell AI?",
             "Generell AI kjenner ikke boligen din. ERA bygger en vedvarende hukommelse rundt din konkrete bolig — med "
             "boligdata, bilder, dokumentasjon, historikk og det som blir gjort over tid. Derfor kan et spørsmål som «Hva "
             "bør jeg følge opp nå?» besvares i kontekst av akkurat din bolig."),
            ("Må jeg ha tilstandsrapport?",
             "Nei. ERA starter med det du har. Jo mer du legger inn, jo mer presis blir planen."),
            ("Må jeg legge inn alt selv?",
             "Nei. Målet er at du skal kunne starte med adressen, og at ERA bygger boligprofilen gradvis. Du skal ikke "
             "måtte fylle ut et langt skjema før ERA blir nyttig."),
            ("Kan jeg ta et bilde og spørre ERA?",
             "Ja. Bilder er en viktig del av ERA-opplevelsen. Du skal kunne vise ERA noe du lurer på, og få hjelp til å "
             "forstå hva du ser i sammenheng med resten av boligen. For eksempel:",
             ["«Hva bør jeg gjøre med denne veggen?»",
              "«Bør dette følges opp?»",
              "«Hva trenger jeg hvis jeg vil fikse dette selv?»"]),
            ("Kan ERA hente tilbud fra håndverkere?",
             "ERA har fundamentet for reisen fra behov i boligen til konkret arbeid, tilbud, valg av utførende, gjennomføring "
             "og dokumentasjon. Målet er at du skal kunne gå fra «dette bør gjøres» til «få hjelp av proff» uten å "
             "beskrive hele behovet på nytt."),
            ("Får ERA betalt når jeg kjøper noe?",
             "ERA kan få betalt fra partnere når du velger å kjøpe et produkt eller en tjeneste gjennom ERA. Det endrer "
             "ikke at du bestemmer hva du vil gjøre og hvem du vil bruke."),
            ("Hva skjer etter betaperioden?",
             "Prismodellen er ikke fastsatt ennå. Du binder deg ikke til noe, og endringer kommuniseres tydelig før de "
             "trer i kraft."),
            *ACCESS_FAQ,
            ("Hvorfor er ERA på invitasjon?",
             "ERA er i Private Beta. Vi åpner kapasiteten gradvis, slik at vi kan følge opp brukerne tett, forbedre ERA "
             "basert på reelle behov og sikre kvalitet før en bredere åpning."),
            ("Hva skjer når jeg ber om tilgang?",
             "Vi registrerer interessen for boligen og åpner nye hjem fortløpende. Du oppgir adressen, og vi sier fra når "
             "ERA er klar for den. Ingen binding, og dataene lagres kryptert i EU/EØS og brukes bare til å ta kontakt."),
            ("Hva skjer når jobben er ferdig?",
             "Resultatet skal tilbake til boligen. Bilder, dokumentasjon og relevant historikk gjør boligprofilen bedre, "
             "slik at neste prosjekt ikke starter fra null. ERA ser hva som kommer. Du slipper å følge med."),
            ("Følger informasjonen boligen over tid?",
             "Det er selve ideen. ERA bygger en digital hukommelse rundt boligen, slik at tidligere arbeid, dokumentasjon "
             "og historikk kan gi bedre beslutninger senere."),
            ("Hva skjer med dataene mine?",
             "Du bestemmer hvem som får tilgang. Data om boligen deles ikke med håndverkere, partnere eller andre bare "
             "fordi de finnes i ERA. Deling skjer når det er relevant og du velger det. Lagret kryptert innenfor EU/EØS."),
            ("Kan jeg slette alt?",
             "Ja. Du kan når som helst be om innsyn i, retting av eller sletting av det du har sendt inn, også e-posten. "
             "Send en melding via skjemaet med «personvern» først i teksten, så ordner vi det."),
            ("Hvem står bak ERA?",
             "ERA technologies AS, med base i Oslo. Teamet har bakgrunn fra eiendom, bygg, faghandel, teknologi og "
             "finans. Du finner menneskene og hvorfor ERA finnes under Om ERA."),
        ],
        beta=dict(
            badge="Private Beta · Tilgang på invitasjon",
            note="Gratis for boligeiere i betaperioden. Ingen betalingskort.",
            cta_primary="Be om tilgang", cta_secondary="Se hvordan ERA fungerer",
            heading="Test ERA sammen med de første boligeierne",
            lede="Som betabruker får du hjelp til å forstå, planlegge og gjennomføre vedlikehold og oppgraderinger i boligen.",
            items=[
                "Ta bilde av et behov i boligen.",
                "Få analyse, oppgaveliste og prisestimat.",
                "Finn relevante produkter.",
                "Velg mellom å gjøre jobben selv eller få hjelp.",
                "Samle utført arbeid og dokumentasjon på boligen.",
                "Påminnelser om kommende vedlikehold.",
            ],
            cta="Be om tilgang",
            fine="Ingen betalingskort. Ingen binding.",
        ),
        form_field="Adressen til boligen", form_label="Adresse", form_cta="Be om tilgang",
        done=("Boligen din venter på ERA.", "Vi sier fra når ERA er klar for adressen."),
        story="#boligeier",
    ),
    "styret": dict(
        key="board", nav="Styret", title="ERA for borettslag og sameier",
        label="For styret", hook="Fra vedlikeholdsbehov til ferdig jobb.",
        lede="ERA er en AI-agent som kobler styret, eierne og håndverkerne rundt samme eiendom. Få hjelp til å forstå behovene, prioritere tiltak og følge arbeidet helt frem til dokumentert resultat.",
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
                foot="Eksempeldata. Skjermbilde fra ERA for boligeiere.", sid="boligeier-visning"),
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
            lede="Følg det samme fasadebehovet fra første funn til gjennomført og dokumentert arbeid. Beboerne er med hele veien: hver eier får egen oversikt over hjemmet, vedlikeholdsplan og påminnelser gjennom ERA for boligeiere.",
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
        lede="ERA er en AI-agent som kobler boligeiere, styrer og håndverkere. Ta kundens behov videre til befaring, tilbud og gjennomføring, og la dokumentasjonen følge hjemmet når jobben er ferdig.",
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
                               kpis=[("Adresse", "Eksempelveien 12"), ("Rom", "Stue, 2 vegger"), ("Bilder", "4 vedlagt"), ("Ønsket tid", "Uke 38–40")],
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
            ("Boligeier", "Beskriver behovet, og tar stilling til tilbud og endringer underveis."),
            ("Håndverker", "Vurderer, utfører og dokumenterer jobben fra befaring til overlevering."),
            ("Styret", "Følger opp og godkjenner når oppdraget gjelder fellesareal, ikke eget hjem."),
        ],
        roles_note="Ved private oppdrag er boligeieren kunden. Ved fellesarbeid er det styret som bestiller og godkjenner på vegne av sameiet eller borettslaget.",
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


MENU = [("/historie", "Historien"), ("/boligeier", "Boligeier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/ny/om-era", "Om ERA"), ("/personvern", "Personvern")]


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
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligens AI-agent</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/historie#hva">Hva ERA gjør</a><a href="/ny/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/historie">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>'''


FAQ_VISIBLE = 7


def dm(desktop, mobile, tag="span"):
    """The same message, written twice: the full version for a desktop reader and a shorter one for a phone.
    Both are in the HTML; CSS (.d-only / .m-only, break at 900 px) shows one. Used only where the phone
    reader needs a different amount of text, not a different message."""
    return f'<{tag} class="d-only">{desktop}</{tag}><{tag} class="m-only">{mobile}</{tag}>'


def faq_html(items, visible=FAQ_VISIBLE, m_visible=None):
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

    mv = visible if m_visible is None else m_visible
    # Questions mv..visible are open on desktop only; on a phone they sit behind «Se alle spørsmål» (a copy of
    # them leads the hidden list, shown on phones only).
    def tag(html_, cls):
        return html_.replace("<details>", f'<details class="{cls}">', 1)
    head = "".join((tag(one(it), "d-only") if i >= mv else one(it)) for i, it in enumerate(items[:visible]))
    rest = items[visible:]
    if not rest:
        return head
    moved = "".join(tag(one(it), "m-only") for it in items[mv:visible])
    return (head + '<details class="faq-more"><summary>Se alle spørsmål</summary>'
            '<div class="faq">' + moved + "".join(one(it) for it in rest) + "</div></details>")


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
            '<section class="section aside-sec"><div class="wrap narrow aside">'
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
    faq = faq_html(a["faq"], m_visible=3)
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

  <section class="section alt gains-sec">
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
            "Når du sender inn skjemaet på historien eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede eller butikk), hvilken målgruppe du leste som (boligeier, styret, håndverker eller faghandel), om du ba om en demo, tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
            "På forsiden søker du først etter boligen, og ingenting lagres før du trykker «Be om tilgang». Da gjelder noe mer: velger du et forslag i adressesøket, lagrer vi også det Kartverket returnerer for den adressen: postnummer og sted, kommune, gårds-, bruks-, feste- og seksjonsnummer og et koordinatpunkt. Velger du ikke et forslag, lagrer vi bare teksten du skrev.",
            "Etter at du har bedt om tilgang, kan du også svare på hva du ønsker mest hjelp med (et valg fra en fast liste) og legge igjen e-postadressen din. Begge deler er valgfrie og lagres som egne poster knyttet til forespørselen med en intern id. Kommer du fra en lenke fra en samarbeidspartner (for eksempel ?source=navn), lagrer vi navnet på kilden sammen med forespørselen.",
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
            "På forsiden teller vi også hendelser som at du søkte etter en bolig, valgte et adresseforslag, ba om tilgang eller sendte inn e-post. Hendelsene inneholder bare hvilket skjema det gjelder og eventuell kilde, ikke adressen, e-posten eller invitasjonskoder.",
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
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligens AI-agent</div></div>
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


NY_DESC = "En personlig agent for boligen din. ERA kjenner boligen, ser hva den trenger og hjelper deg få det gjort. Private Beta – tilgang på invitasjon."


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
          <button type="submit">Finn boligen din</button>
        </div>
      </form>
      <div class="done done--follow" role="status" aria-live="polite" hidden>
        <div class="check"><svg width="20" height="16" viewBox="0 0 20 16" fill="none"><path d="M2 8L7.5 13.5L18 2" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div class="done-body" data-body></div>
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
    <div class="right"><a class="cta" href="{base}#adresse">Finn boligen din</a><button type="button" class="menu-btn" data-menu-toggle="1" aria-label="Åpne menyen" aria-expanded="false">☰</button></div>
  </div>
  <div class="menu-panel" hidden>{panel}</div>
</nav>'''


def ny_footer(base=""):
    return f'''<footer class="foot" data-nav="light">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligens AI-agent</div></div>
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
            '<div class="flow-return" aria-hidden="true"><span class="flow-return-line"></span><span class="flow-return-label">Tilbake til boligen</span></div>'
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
            '<p class="docs-cap">Spredt i dag. Samlet i boligen.</p>')


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
    v1 = shot("/assets/story/app-agent.png", "ERA Bolig: boligagentens svar om boligen, med funn, betydning og forslag")
    v2 = shot("/assets/story/app-kamera.png", "ERA Bolig: kameraet rettet mot avflassende maling, klart til å analysere bildet")
    v3 = shot("/assets/story/app-prosjekt.png", "ERA Bolig: prosjektet med plan, valget mellom å gjøre det selv eller be om tilbud, og fremdrift")
    steps = [(v1, "Spør", "«Hva bør jeg følge opp?» ERA svarer ut fra det den vet om boligen.", "«Hva bør jeg følge opp?»"),
             (v2, "Vis", "Ta et bilde av noe du lurer på. ERA bruker bildet sammen med det den allerede vet om boligen.", "Ta et bilde av noe du lurer på."),
             (v3, "Gjør", "«Jeg vil male stua.» ERA hjelper deg gjøre ideen om til en plan, og du velger om du vil gjøre det selv eller få tilbud fra proff.", "«Jeg vil male stua.»")]
    items = "".join(f'<li>{v}<div class="how-cap"><span class="how-n">{i+1}</span><div><h3>{esc(t)}</h3><p>{dm(esc(d), esc(m))}</p></div></div></li>' for i, (v, t, d, m) in enumerate(steps))
    return ('<section class="section how" id="slik" data-nav="light" data-reveal><div class="wrap wide">'
            '<div class="label">Slik fungerer ERA</div><h2>Bare spør ERA.</h2>'
            '<p class="how-lede">' + dm("Still et spørsmål, ta et bilde eller fortell hva du vil gjøre. ERA setter det i sammenheng med det den allerede vet om boligen.", "Spør, vis eller fortell. ERA setter det i sammenheng med det den vet om boligen.") + '</p>'
            f'<ol class="how-steps">{items}</ol><span class="how-line" aria-hidden="true"></span></div></section>').replace('__CHECK__', CHECK_SVG)


def reise_sofa():
    """Customer journey 1: it often starts on the sofa, with an idea. Not a reminder from ERA: ERA does not
    claim to watch the home on its own. The person asks, and ERA picks it up."""
    body = ('<div class="reise-text"><h2>Det starter ofte i sofaen.</h2>'
            '<p class="cine-lede">Du har en idé om boligen. Fortell ERA hva du vil gjøre.</p>'
            '<p class="reise-say">«Vi burde male stua.»</p></div>'
            '<div class="reise-note" aria-hidden="true"><b>Du til ERA</b><span>Jeg vil male stua.</span><em>ERA setter det sammen med det den vet om boligen, og lager en plan.</em></div>')
    return cine("/assets/story/couple-reminder-v5.jpg", body, sid="sofaen", cls="cine--reise cine--sofa d-only", pos="50% 55%").replace('<section class="cine', '<section data-reveal class="cine', 1)


def reise_bilde():
    """Customer journey 2: take a photo, ERA makes the plan. Four things, not six panels."""
    rows = [("Hva ERA ser", "Maling som flasser på veggen"), ("Forslag", "Maling og farge som passer boligen"),
            ("Prosjektplan", "Forarbeid, sparkling, grunning og strøk"), ("Handleliste", "Materialer og produkter")]
    lis = "".join(f'<li style="--i:{i}"><span>{esc(k)}</span><b>{esc(v)}</b></li>' for i, (k, v) in enumerate(rows))
    body = ('<div class="reise-text"><div class="label">ERA Prosjekt</div><h2>Fra idé til ferdig prosjekt.</h2>'
            '<p class="cine-lede">Fortell ERA hva du vil gjøre. ERA hjelper deg gjøre ideen om til en plan, og ERA tar prosjektet med videre.</p>'
            '<p class="cine-fine">Eksempel. Prosjektplan er i beta, handleliste og produkter er i pilot. Å se rommet før du bestemmer deg er i pilot.</p>'
            '<a class="link reise-cta" href="#adresse">Start et prosjekt →</a></div>'
            '<div class="reise-card" aria-hidden="false"><div class="reise-card-head"><b>era.</b><span>Eksempel · Eksempelveien 12</span></div>'
            f'<ul class="reise-rows">{lis}</ul>'
            '<div class="reise-paths"><span>Gjør det selv</span><span>Få tilbud fra proff</span></div>'
            '<p class="reise-ctx">Bytter du til proff, beholder ERA prosjektet. Du slipper å forklare det på nytt.</p></div>')
    return cine("/assets/story/couple-wall-v5.jpg", body, sid="bilde", cls="cine--reise cine--bilde", pos="40% 50%").replace('<section class="cine', '<section data-reveal class="cine', 1)


def valget():
    """ERA Prosjekt, one plan two ways. A dark navy surface; ERA in the middle. The plan splits in two."""
    left = [("Plan", "plan"), ("Materialer og handleliste", "handleliste"), ("Produkter", "produkter"), ("Hent eller bestill", "kjop")]
    right = [("Prosjektbeskrivelse", "beskrivelse"), ("Relevante bilder du velger", "beskrivelse"), ("Prosjektkontekst", "beskrivelse"), ("Få tilbud", "proff")]
    li = lambda xs: "".join(f'<li>{esc(x)}' + (" " + st(k) if k else "") + '</li>' for x, k in xs)
    return ('<section class="valget" id="valget" data-nav="dark" data-reveal><div class="wrap wide">'
            '<div class="label">ERA Prosjekt</div><h2>Gjør det selv, eller få hjelp.</h2>'
            '<p class="valget-lede">Én plan. To veier. Du skal slippe å starte på nytt: ERA tar prosjektet med videre.</p>'
            '<div class="valget-grid">'
            f'<div class="valget-col valget-col--l"><div class="valget-photo"><img src="/assets/story/materials-floor-v3-m.jpg" alt="" loading="lazy" decoding="async"></div><h3>Gjør det selv</h3><ul>{li(left)}</ul></div>'
            '<div class="valget-core" aria-hidden="true"><span>era<i>.</i></span></div>'
            f'<div class="valget-col valget-col--r"><div class="valget-photo"><img src="/assets/story/painter-v3-m.jpg" alt="" loading="lazy" decoding="async"></div><h3>Få hjelp av proff</h3><ul>{li(right)}</ul></div>'
            '</div><p class="valget-ctx">Bytter du fra gjør-det-selv til proff, beholder ERA prosjektet. Du slipper å forklare det på nytt, og du velger hva som følger forespørselen.</p>'
            '<p class="valget-cta"><a class="link" href="#adresse">Finn boligen din →</a></p>'
            '<p class="cine-fine">Beta: tilgjengelig for betabrukere. I pilot: testet med utvalgte partnere. Planlagt: ikke tilgjengelig ennå.</p></div></section>')


def reise_ferdig():
    """Customer journey 3: the same couple back on the sofa. Only the status arrives."""
    st = ["Ferdig", "Dokumentert", "Lagret på boligen"]
    lis = "".join(f'<li style="--i:{i}"><span>{CHECK_SVG}</span>{esc(t)}</li>' for i, t in enumerate(st))
    body = ('<div class="reise-text"><h2>Ferdig.<br>Og boligen husker det.</h2>'
            '<p class="cine-lede">Arbeidet, relevante bilder og dokumentasjon kan bli en del av boligens historie. Neste gang starter ERA med mer kunnskap, ikke fra null.</p></div>'
            f'<div class="reise-card reise-card--done"><ul class="reise-done">{lis}</ul></div>')
    return cine("/assets/story/couple-done-v5.jpg", body, sid="ferdig", cls="cine--reise cine--ferdig d-only", pos="50% 50%").replace('<section class="cine', '<section data-reveal class="cine', 1)


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
            '<div class="cine-text see-text"><div class="label">Fra bilde til forslag</div><h2>Vis ERA det du ser.</h2>'
            '<p class="cine-lede">Ta et bilde av et rom, en overflate eller noe du lurer på. ERA bruker bildet sammen med det den allerede vet om boligen for å hjelpe deg videre.</p>'
            '<p class="see-sub d-only">Fasadens tilstand, dokumentasjon, alder og tidligere arbeid kan vurderes i samme kontekst. Svaret er et utgangspunkt, ikke en diagnose eller en teknisk inspeksjon.</p>'
            f'<ul class="see-list">{rows}</ul>'
            '<p class="see-sources"><b>ERA bruker</b> bildene dine, byggeår og materialer, tidligere arbeid og kvitteringer, og fagkunnskap.</p>'
            '<ul class="see-areas d-only" aria-label="Områder ERA ser på">' + "".join(f'<li>{t}</li>' for t in ("Tak", "Takrenner", "Fasade", "Vinduer", "Bad", "Ventilasjon", "Kjøkken", "Uteområde")) + '</ul>'
            '<a class="link see-cta" href="#adresse">Vis ERA →</a>'
            '<p class="cine-fine">Eksempeldata.<span class="m-only"> Svaret er et utgangspunkt, ikke en diagnose.</span></p></div>')
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
                    f"{h['pro']} og samlet dokumentasjon")
    agent_alt = (f"ERA Bolig, boligagenten for {h['address']}: fotoet av huset er merket av med fasade og tak til oppfølging "
                 f"og takrenner og grunnmur i god stand, etterfulgt av «Hva jeg ser», «Hva det betyr» for en bolig fra {h['year']} "
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
        None, "Din bolig. Én agent.",
        [("Finn boligen", "Adresse inn. Boligprofil ut.", "/assets/story/app-minbolig.png",
          "ERA Bolig: Min bolig med nøkkeltall, neste prosjekt og dokumentasjon", 853, 1844, "md"),
         ("Vis eller spør", "Ta et bilde eller spør ERA.", "/assets/story/app-kamera.png",
          "ERA Bolig: kameraet rettet mot avflassende maling ved et vindu", 853, 1844, "sm"),
         ("Få et forslag", "Hva, hvorfor og når. Gjør det selv, eller få tilbud.", "/assets/story/app-agent.png",
          "ERA Bolig: boligagentens analyse av huset med funn, betydning og forslag", 853, 1844, "lg"),
         ("Få det gjort", "Behov, produkter, tilbud og oppfølging i én flyt.", "/assets/story/app-prosjekt.png",
          f"ERA Bolig: prosjektet «{h['measure']}» med kostnad, håndverker og oppgaver", 935, 1683, "lg"),
         ("Alt tilbake til boligen", "Neste gang starter ERA med historikken, ikke fra null.", "/assets/story/app-boligminne.png",
          "ERA Bolig, boligminnet: tidslinjen 2020 nytt bad, 2022 varmepumpe, 2024 nytt tak og 2026 fasadevask og maling", 783, 645, "sm")],
        "Eksempeldata. Samme bolig hele veien. Visualisering av farger og løsninger er i pilot.", "produkt",
        lede="ERA kan hjelpe deg fra behov til prosjektplan, handleliste, produkter eller håndverker, og husker resultatet når jobben er ferdig.")

    # 03: what ERA knows. Documents lie scattered and gather; the list below is an example room.
    knows = (
        '<section class="section ny-knows" id="kjenner" data-nav="light">'
        '<div class="ny-knows-bg" aria-hidden="true"><img src="/assets/story/whole-home-v3.jpg" srcset="/assets/story/whole-home-v3-m.jpg 1400w, /assets/story/whole-home-v3.jpg 2400w" sizes="100vw" alt="" loading="lazy" decoding="async"></div>'
        '<div class="wrap ny-knows-grid"><div class="ny-knows-text">'
        '<div class="label">ERA kjenner boligen</div><h2>ERA starter ikke fra null.</h2>'
        '<p class="ny-lede">' + dm("Bilder, dokumenter, rom, materialer, historikk og utført arbeid settes i sammenheng med det ERA allerede vet om boligen. Boligen får et minne: ny informasjon kobles til det som allerede er kjent, og ERA sier fra når noe mangler.", "ERA setter bilder, dokumenter og historikk sammen med det den allerede vet. Boligen får et minne.") + '</p>'
        '<ul class="appsec-points">'
        '<li><b>Dokumentert</b>Vi vet hvor informasjonen kommer fra.</li>'
        '<li><b>ERA-forslag</b>ERA vurderer og forklarer hvorfor.</li>'
        '<li><b>Mangler</b>ERA sier fra når den ikke vet.</li></ul>'
        '<a class="link ny-knows-cta" href="#adresse">Se hva ERA kan vite om boligen din →</a></div>'
        '<div class="ny-knows-stage" data-reveal>' + docs_scatter()
        + knows_view("Badet", "Eksempel · ett rom i en bolig",
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
               ("Finn produkter", "ERA foreslår produkter ut fra det boligen faktisk trenger."),
               ("Få tilbud fra proff", "Behovet er allerede beskrevet. Du slipper å starte fra null."),
               ("Minn meg på dette senere", "ERA tar det opp igjen når tiden er inne.")]
    chips = "".join(f'<button type="button" class="cine-chip" aria-pressed="false" data-note="{esc(n)}">{esc(c)}</button>' for c, n in choices)
    li = (
        '<li><b>ERA ser</b><span>Badet bør vurderes.</span></li>'
        '<li><b>ERA forklarer</b><span>Hvorfor, hvor viktig det er og hva som kan vente.</span></li>'
        f'<li><b>Du velger</b><span class="cine-chips">{chips}</span><span class="cine-note" aria-live="polite"></span></li>'
        '<li><b>ERA ordner</b><span class="mini-state" aria-label="Kartlagt, tilbud, utføres"><i class="is-done">Kartlagt</i><i class="is-now">Tilbud</i><i>Utføres</i></span></li>'
        '<li><b>Dokumenteres</b><span>Alt går tilbake til boligen.</span></li>')
    flow_steps = (f'<ol class="cine-flow">{li}</ol>'
                  '<button type="button" class="cine-more m-only" aria-expanded="false" data-more>Se hele løpet</button>')
    need = cine("/assets/story/bathroom-old-v4.jpg",
                '<div class="cine-grid"><div class="cine-text">'
                '<h2>ERA hjelper deg se behovet før du begynner å lete.</h2>'
                '<p class="cine-lede">Når ERA allerede vet hva som bør gjøres, slipper du å starte på nytt med Google, anbudssider og telefoner.</p>'
                '<p class="cine-fine">Eksempel. Beta: oppdage, forklare og tilbud fra proff. I pilot: produkter. Planlagt: påminnelser.</p></div>' + flow_steps + '</div>',
                sid="behov", pos="62% 50%")

    # 05: the home remembers. The house through the seasons, and a timeline of what has been done.
    timeline_steps = [("Kjøpt", False), ("Malt", False), ("Bad dokumentert", False), ("Elektrisk arbeid", False), ("Dokumentert", False), ("Neste behov", True)]
    timeline = '<ol class="cine-timeline cine-timeline--left">' + "".join(
        f'<li class="{"is-next" if nxt else ("is-link" if t == "Bad dokumentert" else "")}" style="--k:{k}"><span>{esc(t)}</span></li>' for k, (t, nxt) in enumerate(timeline_steps)) + "</ol>"
    seasons = '<div class="seasons d-only" aria-hidden="true">' + "".join(
        f'<img{" class=" + chr(34) + "is-on" + chr(34) if i == 0 else ""} src="/assets/story/block-season-{i}-v3.jpg" srcset="/assets/story/block-season-{i}-v3-m.jpg 1400w, /assets/story/block-season-{i}-v3.jpg 1600w" '
        f'sizes="(max-width: 900px) 80vw, 420px" alt="" loading="lazy" decoding="async">' for i in range(4)) + "</div>"
    learns = cine("/assets/story/whole-home-v3.jpg",
                  '<div class="cine-grid cine-grid--seasons"><div class="cine-text" data-reveal>'
                  '<h2>ERA ser hva som kommer. Du slipper å følge med.</h2>'
                  '<p class="cine-lede">Når jobben er ferdig, blir resultatet en del av det ERA vet om boligen. Jo mer boligen lever, desto mer lærer ERA om den.</p>'
                  + timeline + '<p class="cine-fine">Eksempel på en boligs tidslinje.</p></div>' + seasons + '</div>'
                  + '<ul class="husker-feats d-only">'
                  '<li><b>Bilder og dokumentasjon</b><span>Alt samlet på ett sted.</span></li>'
                  '<li><b>Påminnelser</b><span>Beskjed når det er tid for vedlikehold, ut fra alder, materialer og forhold.</span><i class="nstep-tag">Planlagt</i></li>'
                  '<li><b>Del med andre</b><span>Del det som er relevant med håndverkere, styret eller kjøpere, når du selv velger det.</span><i class="nstep-tag">Planlagt</i></li></ul>',
                  sid="husker", pos="50% 60%")

    faq_items = [
        ('Hva er ERA?', 'ERA er Boligens AI-agent, en personlig agent som kjenner boligen din, ser hva den trenger og hjelper deg få det gjort. Du kan spørre ERA, ta et bilde eller starte et prosjekt. ERA bruker informasjonen den har om boligen til å forstå sammenhengen og hjelpe deg videre.'),
        ('Er ERA bare en chatbot?', 'Nei. ERA er bygget rundt den konkrete boligen. Bilder, dokumenter, rom, historikk og utført arbeid kan bli del av boligkonteksten, slik at ERA ikke trenger å starte fra null hver gang.'),
        ('Er ERA et nytt FDV-system?', 'Nei. Et FDV-system organiserer og dokumenterer informasjon. ERA bruker informasjonen til å forstå boligen, hjelpe deg se hva som bør følges opp og ta deg videre til handling.'),
        ('Hvordan henger ERA sammen med Boligmappa?', 'Boligmappa samler dokumentasjon og historikk om boligen. ERA bruker slik kunnskap til å svare på hva det betyr og hva du bør gjøre nå – og ferdig arbeid kan dokumenteres tilbake.'),
        ('Hva er forskjellen på ERA og Mittanbud?', 'Mittanbud blir relevant når du allerede vet at du trenger en håndverker. ERA kan starte tidligere: forstå behovet, forklare det og hjelpe deg velge mellom å gjøre det selv eller få hjelp av proff.'),
        ('Hva er forskjellen på ERA og generell AI?', 'Generell AI kjenner ikke boligen din. ERA er bygget rundt din konkrete bolig og bruker eiendomsdata, bilder, dokumentasjon og historikk som kontekst, så den ikke starter fra null.'),
        ('Hva vet ERA om boligen min?', 'ERA starter med tilgjengelige eiendomsdata og informasjon du legger til, som bilder, dokumenter og historikk. Den viser hva som er dokumentert, hva den foreslår og hva den ikke vet.'),
        ('Kan ERA hjelpe meg gjøre det selv eller finne en proff?', 'Begge deler. Vil du gjøre jobben selv, skal ERA hjelpe med produkter, materialer og plan. Vil du ha hjelp, kan det samme behovet gå videre til en proff, uten at du må beskrive det på nytt. Handleliste og produkter er i pilot, og tilbud fra proff er i beta.'),
        ('Fungerer ERA også for leilighet og borettslag?', 'Ja. ERA kan brukes for enebolig, rekkehus og leilighet. I borettslag og sameier kan noe informasjon og ansvar ligge hos styret, mens annet gjelder den enkelte boligen.'),
        ('Hva skjer med dataene mine?', 'Du bestemmer hvem som får tilgang. Data skal ikke deles med håndverkere, partnere eller andre uten at du velger det.'),
        ('Hva koster ERA?', 'ERA er gratis for boligeiere i betaperioden. Ingen betalingskort.'),
    ]
    # Six questions open, the rest behind «Se alle spørsmål». The rest is these four plus every question on
    # /boligeier that the front page does not already answer, so the two lists cannot drift apart.
    covered = ("Hva er ERA?", "Hva er forskjellen på ERA og", "Hva vet ERA om", "Kan ERA hjelpe meg", "Gjelder ERA for leilighet", "Hva koster ERA", "Hva skjer med dataene")
    extra = [it for it in AUDIENCES["boligeier"]["faq"] if not it[0].startswith(covered)]
    faq = faq_html(faq_items + extra, m_visible=3)
    done = ("Takk. Vi har adressen din.", "")
    hero_form = lead_form_html("hero", a, done, label="Skriv adressen din", placeholder="Eksempelveien 12, Oslo")
    end_form = lead_form_html("end", a, done, placeholder="Eksempelveien 12, Oslo")

    # 06: the close. One address field, almost no text.
    close = cine("/assets/story/door-evening-v4.jpg",
                 '<div class="cine-center">'
                 '<h2>Din bolig kan få en agent.</h2>'
                 '<p class="cine-lede">ERA åpner nå for de første hjemmene.</p>'
                 + end_form +
                 '<p class="ny-micro">Private Beta · Tilgang på invitasjon</p>'
                 '<p class="ny-trust"><b>Dine data. Ditt hjem.</b> Du bestemmer hvem som får tilgang.</p></div>',
                 sid="skjema", cls="cine--center cine--close", pos="60% 50%")

    how, sofa, bilde, valget_html, ferdig, see = how_it_works(), reise_sofa(), reise_bilde(), valget(), reise_ferdig(), scene_see()

    # Om ERA is a teaser here and a page of its own next to this one.
    teaser = ('<section class="ny-teaser" data-nav="dark"><div class="wrap"><div><h2>Hvert hjem får en agent.</h2>'
              '<p>Vi bygger en personlig agent for boligen din: en agent som kjenner boligen, ser hva den trenger og hjelper deg få det gjort.</p></div>'
              '<a class="link" href="/ny/om-era">Les historien om ERA →</a></div></section>')

    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Boligens AI-agent — ERA</title>
<meta name="description" content="{esc(NY_DESC)}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/", "Boligens AI-agent — ERA", NY_DESC)}
{era_config_meta()}
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
    <div class="label">{dm('ERA · for boligeiere', 'Boligens AI-agent')}</div>
    <h1 data-hero-h1 data-a="Boligens AI-agent.">En personlig agent for boligen din.<span class="h1-sub">Kjenner boligen, ser hva den trenger og hjelper deg få det gjort.</span></h1>
    <p class="lede d-only" data-hero-sub data-a="Kjenner boligen, ser hva den trenger og hjelper deg få det gjort.">Boligens AI-agent. Spør ERA, ta et bilde eller start et prosjekt.</p>
    <div id="adresse">
      {hero_form}
    </div>
    <p class="ny-micro">Private Beta · Tilgang på invitasjon</p>
  </div>
  {hero_visual}
  </div>
</header>

<main>
  {how}

  {knows}

  {see}

  {need}

  {sofa}

  {bilde}

  {valget_html}

  {ferdig}

  {learns}

  {flow}

  <section class="section" data-nav="light" id="kategori">
    <div class="wrap narrow">
      <div class="label">Kategorien</div>
      <h2>Hva slags produkt er ERA?</h2>
      <div class="kat" role="list">
        <div class="kat-row" role="listitem"><b>Mittanbud</b><span>Markedsplass for håndverkere, når du allerede vet hva som skal gjøres.</span></div>
        <div class="kat-row" role="listitem"><b>Generell AI</b><span>Uten vedvarende kontekst om boligen din.</span></div>
        <div class="kat-row kat-era" role="listitem"><b>ERA</b><span><i>Boligens AI-agent.</i> Kjenner boligen, ser hva den trenger og tar deg fra behov til ferdig jobb.</span></div>
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
            '<div class="label">For meglere og partnere</div><h1>Boligen følger kjøperen videre.</h1>'
            '<p class="cine-lede">ERA samler boligens historikk, dokumentasjon og utført arbeid på ett sted. Sammen med meglere og partnere kan boligen bli levert med historikken på plass, og eieren får hjelp også etter overtakelsen.</p></div></section>')
    blocks = [("For meglere", "Boligen kan overleveres med dokumentasjon og historikk samlet. Kjøperen starter med en bolig ERA allerede kjenner, i stedet for en mappe med papirer."),
              ("For leverandører og faghandel", "Når ERA har beskrevet et behov, kan det gå videre til produkter og fagfolk. Behovet er allerede forklart, og resultatet dokumenteres tilbake på boligen."),
              ("For andre partnere", "Boligbyggerlag, forsikring, bank og andre som møter boligeiere. Vi utforsker samarbeid der boligens historikk gjør tjenesten enklere for eieren.")]
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
    desc = "For meglere og partnere: ERA samler boligens historikk, dokumentasjon og utført arbeid, slik at boligen kan følge kjøperen videre."
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
            '<div class="label">Om ERA</div><h1>Vi bygger en personlig agent for hvert hjem.</h1>'
            '<p class="cine-lede">Boliginformasjon er i dag spredt mellom dokumenter, bilder, mennesker og systemer. Samtidig må boligeieren selv forstå hva som bør gjøres, finne produkter, kontakte håndverkere og huske hva som ble gjort.</p>'
            '<p class="cine-gold">ERA samler denne konteksten rundt én agent for boligen.</p></div></section>')
    why = ('<section class="section om-why" data-nav="light"><div class="wrap narrow"><div class="label">Hva ERA gjør</div>'
           '<h2>Én agent som kjenner boligen og ser hva den trenger.</h2>'
           '<p class="om-text">Du snakker med ERA om boligen din: still et spørsmål, ta et bilde eller fortell hva du vil gjøre. ERA setter det i sammenheng med det den allerede vet, og hjelper deg videre til plan, handleliste, produkter eller håndverker.</p></div></section>')
    steps = ["Bolig", "Kunnskap", "Behov", "Prosjekt", "Handling", "Dokumentasjon", "Smartere bolig"]
    loop = ('<ol class="cine-timeline">' + "".join(
        f'<li class="{"is-next" if i == len(steps) - 1 else ""}"><span>{esc(t)}</span></li>' for i, t in enumerate(steps)) + "</ol>")
    build = cine("/assets/story/loop-home-v3.jpg",
                 '<div class="cine-center"><div class="label">Slik henger det sammen</div><h2>Én enkel loop.</h2>' + loop + '<p class="cine-lede">ERA Prosjekt tar deg fra idé til ferdig jobb: prosjektplan, handleliste, produkter eller tilbud fra håndverker. Resultatet blir en del av boligen.</p></div>',
                 sid="bygger", cls="cine--center", pos="50% 55%")
    tech = ('<section class="section om-tech" id="teknologien" data-nav="light"><div class="wrap narrow"><div class="label">Hvordan ERA kan gjøre det</div>'
            '<h2>ERA gjør fragmenterte boligdata om til kontinuerlig, handlingsbar kunnskap om boligen.</h2>'
            '<p class="om-tech-lead">En vedvarende, strukturert kunnskapsmodell kobler sammen data, bilder, dokumenter, rom, materialer, historikk og arbeid over tid. Det er det som gjør at ERA kjenner og husker boligen.</p>'
            '<p>ERAs proprietære analyseteknologi er utviklet for å bygge og kontinuerlig oppdatere en strukturert digital kunnskapsmodell av den enkelte boligen.</p>'
            '<p>Teknologien kombinerer eiendomsdata, bilder, dokumenter, rom- og materialinformasjon, historikk, utførte arbeider og bruker-/fagpersoninput. AI brukes til å analysere og strukturere informasjonen, mens ERAs egen kunnskapsarkitektur vurderer blant annet kilde, kontekst, sikkerhet, motstridende informasjon og hvordan kunnskapen endrer seg over tid.</p>'
            '<p>Det unike ligger derfor ikke i én enkelt AI-modell, men i systemet rundt analysen: ERA bygger et vedvarende digitalt boligminne hvor ny informasjon kobles til eksisterende kunnskap om boligen, fremfor at hver analyse behandles isolert.</p>'
            '<p>Dette gjør at ERA over tid kan gå fra å beskrive boligen til å forstå hva som er kjent og ukjent, identifisere relevante vedlikeholds- og oppussingsbehov, foreslå neste handling og dokumentere resultatet tilbake på boligen.</p></div></section>')
    team = ('<section class="section ny-team" id="teamet" data-nav="light"><div class="wrap wide">'
            '<div class="label">Menneskene bak ERA</div>'
            '<h2>Vi kjenner bolig. Og bygger teknologien rundt den.</h2>'
            '<p class="ny-team-lede">ERA bygges av mennesker med lang erfaring fra eiendom, teknologi, finans, bygg, handel og AI. Sammen bygger vi en enklere måte å eie, forstå og ta vare på boligen på.</p>'
            + team_html() + '</div></section>')
    cta = ('<section class="ny-teaser ny-teaser--cta" data-nav="dark"><div class="wrap"><div><h2>Din bolig kan få en agent.</h2>'
           '<p>ERA åpner nå for de første hjemmene.</p></div>'
           '<a class="btn" href="/#adresse">Finn boligen din</a></div></section>')
    desc = "Vi bygger en personlig agent for hvert hjem. Hvorfor ERA finnes, hvordan det henger sammen og menneskene bak."
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Om ERA — en personlig agent for hvert hjem</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/ny/om-era", "Om ERA — en personlig agent for hvert hjem", desc)}
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
