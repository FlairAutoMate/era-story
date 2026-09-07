# -*- coding: utf-8 -*-
"""ERA Partner Story system: builds /partner/<slug>/index.html for each entry in PARTNERS.

Deliberately independent of the homepage's scroll-motor (index.html's <script data-dc-script>,
a bespoke custom-element compiler tightly coupled to the public story's own chapters) and of
tools/build-pages.py's audience-page template. A partner story is a different kind of page —
long-form, cinematic, one per commercial conversation — so it gets its own small set of
reusable scene-kind builders below (hero, scene, split, transition, flow, dash, reveal_list,
converge, steps_grid) plus a lightweight IntersectionObserver reveal engine (js/partner-story.js)
instead of scroll-scrubbed state. Adding the next partner (Optimera, Tarkett, ...) means writing
a new content dict, not new template code — as long as these scene kinds cover the story.

Visually it shares the public design system: pages.css (tokens, type, the dash/kpi/tag/card
vocabulary already built for the audience pages) plus partner.css for the handful of components
pages.css has no use for (hero/scene rhythm, flow diagrams, crossfade transition, reveal list,
convergence). Photography is reused entirely from assets/story/ — no new images.

Usage: python tools/build-partner-story.py
"""
import html, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://era-story.vercel.app"


def esc(t):
    return html.escape(t, quote=True)


TAG_LABELS = {
    "customer": "Fra boligeier", "doc": "Dokumentert", "ai": "ERA-forslag", "check": "Avklares",
    "board": "Styret", "pro": "Fagperson", "resident": "Boligeier", "order": "Bestilling og levering",
    "pilot": "I pilot", "planned": "Planlagt", "vision": "Fremtidsbilde", "partner": "Partner",
}


def tag(kind):
    return f'<span class="tag tag-{kind}">{esc(TAG_LABELS[kind])}</span>'


def img(asset, alt=""):
    """A plain, non-editable <img> for a partner story (image-slot's drag-and-drop editing isn't
    needed here — every image already exists in assets/story/)."""
    base = f"/assets/story/{asset}"
    return f'<img src="{base}" srcset="{base[:-4]}-m.jpg 1400w, {base} 3000w" sizes="100vw" alt="{esc(alt)}">'


def dash(title, meta, kpis=(), groups=(), cols=(), footer=None, tag_kind=None):
    head_tag = tag(tag_kind) if tag_kind else ""
    out = ['<div class="dash">',
           f'<div class="dash-head"><div><div class="dash-title">{esc(title)}</div><div class="dash-meta">{esc(meta)}</div></div>{head_tag}</div>']
    if kpis:
        out.append('<div class="kpis">' + "".join(f'<div class="kpi"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in kpis) + '</div>')
    for g_tag, rows in groups:
        out.append(f'<div class="dash-group dash-group-{g_tag}">{tag(g_tag)}' + "".join(f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows) + '</div>')
    if cols:
        out.append('<div class="dash-cols">' + "".join(f'<div class="dcol">{tag(c_tag)}' + "".join(f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows) + '</div>' for c_tag, rows in cols) + '</div>')
    if footer:
        out.append(f'<div class="dash-foot">{esc(footer)}</div>')
    out.append('</div>')
    return "".join(out)


def flow(steps, vertical=False, note=None):
    """steps: list of (label, kind) where kind in {None, 'solid', 'muted', 'old'}."""
    cls = "p-flow vertical" if vertical else "p-flow"
    parts = [f'<div class="{cls}">']
    for i, (label, kind) in enumerate(steps):
        if i:
            parts.append('<span class="p-flow-arrow" aria-hidden="true">→</span>')
        step_cls = "p-flow-step" + (f" {kind}" if kind and kind != "old" else "")
        text = f'<span class="p-flow-old">{esc(label)}</span>' if kind == "old" else esc(label)
        parts.append(f'<span class="{step_cls}">{text}</span>')
    parts.append('</div>')
    if note:
        parts.append(f'<p class="p-fine">{esc(note)}</p>')
    return "".join(parts)


def reveal_list(items):
    """items: list of (number, title, text)."""
    rows = "".join(
        f'<div class="p-reveal-item"><div class="p-reveal-n">{esc(n)}</div><div><h3>{esc(t)}</h3><p>{esc(x)}</p></div></div>'
        for n, t, x in items
    )
    return f'<div class="p-reveal-list reveal-stagger">{rows}</div>'


def steps_grid(items):
    """items: list of (number, title, text)."""
    cards = "".join(
        f'<div class="p-step-card"><span class="p-reveal-n">{esc(n)}</span><b>{esc(t)}</b><p>{esc(x)}</p></div>'
        for n, t, x in items
    )
    return f'<div class="p-steps-grid reveal-stagger">{cards}</div>'


def converge(left_title, left_items, right_title, right_items, mid):
    l = "".join(f'<li>{esc(x)}</li>' for x in left_items)
    r = "".join(f'<li>{esc(x)}</li>' for x in right_items)
    return (
        '<div class="p-converge">'
        f'<div class="p-converge-col"><h4>{esc(left_title)}</h4><ul>{l}</ul></div>'
        f'<div class="p-converge-mid">{esc(mid)}</div>'
        f'<div class="p-converge-col"><h4>{esc(right_title)}</h4><ul>{r}</ul></div>'
        '</div>'
    )


def scene(id_, body, image=None, dark=True, short=False, wide=False, center=False, body_class=""):
    cls = "p-scene" + ("" if dark else " light") + (" short" if short else "")
    bcls = "p-scene-body" + (" wide" if wide else "") + (" center" if center else "") + ((" " + body_class) if body_class else "")
    media = ""
    if image:
        media = f'<div class="p-scene-media reveal-img">{img(image)}</div>'
    idattr = f' id="{esc(id_)}"' if id_ else ""
    return f'<section{idattr} class="{cls}">{media}<div class="{bcls} reveal">{body}</div></section>'


def hero(eyebrow, title, sub, image, primary, secondary):
    body = (
        f'<div class="p-eyebrow">{esc(eyebrow)}</div>'
        f'<h1 class="p-h1">{title}</h1>'
        f'<p class="p-lede">{esc(sub)}</p>'
        f'<div class="p-actions"><a class="btn" href="{primary[1]}">{esc(primary[0])}</a><a class="link" href="{secondary[1]}">{esc(secondary[0])}</a></div>'
    )
    return f'<section class="p-scene p-hero"><div class="p-scene-media reveal-img in-view">{img(image)}</div><div class="p-scene-body reveal in-view">{body}</div></section>'


def split(id_, eyebrow, heading, text, value, image, image_alt="", reverse=False, dark=True):
    body = (
        f'<div class="p-eyebrow{"" if dark else " dark2"}">{esc(eyebrow)}</div>'
        f'<h2 class="p-h2" style="margin-top:14px">{esc(heading)}</h2>'
        f'<p class="{"p-lede" if dark else "p-lede"}">{esc(text)}</p>'
        + (f'<p class="p-payoff">{esc(value)}</p>' if value else "")
    )
    cls = "p-split reverse" if reverse else "p-split"
    bg = "background:var(--navy);color:var(--warm)" if dark else "background:var(--paper);color:var(--ink)"
    idattr = f' id="{esc(id_)}"' if id_ else ""
    return (
        f'<section{idattr} class="{cls}" style="{bg}">'
        f'<div class="p-split-media reveal-img">{img(image, image_alt)}</div>'
        f'<div class="p-scene-body reveal">{body}</div>'
        '</section>'
    )


def transition(id_, image_from, image_to, eyebrow, line1, line2):
    idattr = f' id="{esc(id_)}"' if id_ else ""
    return (
        f'<section{idattr} class="p-transition reveal">'
        f'<div class="p-transition-layer from">{img(image_from)}</div>'
        f'<div class="p-transition-layer to">{img(image_to)}</div>'
        '<div class="p-transition-text">'
        f'<div><div class="p-eyebrow">{esc(eyebrow)}</div>'
        f'<h2 class="p-h1" style="color:#fff">{esc(line1)}</h2>'
        f'<p class="p-payoff">{esc(line2)}</p></div>'
        '</div></section>'
    )


NAV = [
    ("oversikt", "Oversikt"), ("b2c", "B2C"), ("distribusjon", "Distribusjon"),
    ("innsikt", "Innsikt"), ("pilot", "Pilot"),
]


def nav_html(partner_name, back_href="/", back_label="Tilbake til ERA"):
    links = "".join(f'<a class="p-link" href="#{k}" data-act="{k}">{esc(l)}</a>' for k, l in NAV)
    return (
        '<nav class="p-nav" aria-label="ERA × ' + esc(partner_name) + '">'
        '<div class="p-pill">'
        f'<span class="p-brand">era<span>.</span> × {esc(partner_name)}</span>'
        f'{links}<a class="p-back" href="{esc(back_href)}">{esc(back_label)}</a>'
        '</div></nav>'
    )


def head_meta(path, title, description):
    return f'''<link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="noindex,nofollow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ERA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:locale" content="nb_NO">'''


def page(slug, p):
    body = p["build"](p)
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["description"])}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta("/partner/" + slug, p["title"], p["description"])}
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
<link rel="stylesheet" href="/partner.css">
</head>
<body>
{nav_html(p["partner_name"])}
<main>
{body}
</main>
<footer class="p-foot">
  <span>© 2026 ERA technologies AS · Konseptdemonstrasjon, ikke en offentlig lansert løsning.</span>
  <span><a href="/">era.</a> · <a href="/personvern">Personvern</a></span>
</footer>
<script src="/js/image-slot.js"></script>
<script src="/js/partner-story.js" defer></script>
</body>
</html>
'''


# ── ERA × Jotun ────────────────────────────────────────────────────────────────────────────
def build_jotun(p):
    s = []

    s.append(hero(
        "ERA × JOTUN", "Fra boligbehov til handling.",
        "En ny måte å koble boligeier, produkt, forhandler og fagperson rundt det boligen faktisk trenger. Riktig produkt. Riktig bolig. Riktig tidspunkt.",
        "whole-home-v3.jpg", ("Se hvordan", "#oversikt"), ("Tilbake til ERA", "/"),
    ))

    # ACT 1 — ÉN BOLIG
    s.append(scene("oversikt",
        '<div class="p-eyebrow">Akt 1 · Én bolig</div>'
        '<h2 class="p-h1">Alt starter med boligen.</h2>'
        '<p class="p-lede">Vedlikeholdsbehov oppstår lenge før boligeieren begynner å lete etter produkter eller håndverkere.</p>'
        '<p class="p-payoff">ERA bygger en løpende forståelse av boligen.</p>'
        + flow([("Byggeår", None), ("Overflater", None), ("Tidligere tiltak", None), ("Vedlikehold", None), ("Bilder", None), ("Dokumentasjon", None)]),
        image="whole-home-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Den sentrale innsikten</div>'
        '<h2 class="p-h1">Behovet finnes før søket.</h2>'
        + flow([("Behov", "old"), ("Google / søk", "old"), ("Produkt", "old"), ("Butikk", "old")])
        + flow([("Bolig", None), ("ERA", None), ("Behov", None), ("Anbefaling", None), ("Jotun", "solid"), ("Forhandler", None), ("Handling", None)])
        + '<p class="p-payoff">ERA kan gjøre det mulig å møte boligeieren tidligere i beslutningsprosessen, før produktjakten starter.</p>',
        image="fragmented-home-v3.jpg", dark=True, wide=True,
    ))

    s.append(split(None, "Konkret eksempel", "Bør fasaden males i år?",
        "ERA veileder boligeieren: «Ta bilder av disse områdene.» Bildene brukes som beslutningsstøtte, ikke som en automatisk teknisk diagnose.",
        None, "roof-detail-v3.jpg", reverse=False))
    s.append(scene(None, dash(
        "ERA vurderer", "Fasade · basert på bilder og historikk",
        groups=[
            ("customer", [("Bilder delt", "6 av fasaden")]),
            ("doc", [("Tidligere vedlikehold", "Malt 2012")]),
            ("ai", [("Vurdering", "Overflate og tilstand tyder på behov"), ("Anbefaling", "Vedlikehold denne sesongen")]),
        ],
        footer="Eksempeldata og konseptvisning. En vurdering er beslutningsstøtte, ikke en garantert diagnose.",
    ), dark=False, short=True))

    s.append(scene(None,
        '<div class="p-eyebrow">Fra behov til prosjekt</div>'
        '<h2 class="p-h1">ERA gjør behovet konkret.</h2>'
        + dash("Prosjekt · Fasade", "Fra spørsmål til gjennomførbart prosjekt",
               kpis=[("Arbeid", "Forberedelse, grunning, overflatebehandling"), ("Areal", "Beregnes fra bildene"), ("Mengde", "Beregnes"), ("Tidspunkt", "Denne sesongen")]),
        image="photo-observation-v3.jpg",
    ))

    # ACT 2 — FRA BEHOV TIL KJØP
    s.append(scene("b2c",
        '<div class="p-eyebrow">Akt 2 · Fra behov til kjøp</div>'
        '<h2 class="p-h1">Koble prosjektet til riktig produktsystem.</h2>'
        '<p class="p-lede">ERA kan koble prosjektkonteksten til Jotuns produktdata, anbefalinger og produktsystemer.</p>'
        + flow([("ERA · prosjektkontekst", None), ("Jotun · produktdata", "solid"), ("Anbefalt system", None), ("Mengde", None), ("Handleliste", None)], vertical=True)
        + '<p class="p-fine">DEMO_PRODUCT_DATA — produktkortene under er illustrasjon, ikke reell Jotun-katalog.</p>',
        image="diy-commerce-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Til Jotun</div>'
        '<h2 class="p-h1">Produktdata inn. Relevant anbefaling ut.</h2>'
        + converge(
            "Jotun", ["Produktkatalog", "Bruksområder", "Overflater", "Produktsystemer", "Farger", "Dekning / mengde"],
            "ERA", ["Boligkontekst", "Prosjekt", "Behov", "Anbefaling", "Handleliste"],
            "→",
        )
        + '<p class="p-payoff">Neste steg: avklare hvilke produktkataloger, feeds eller API-er Jotun kan gjøre tilgjengelig.</p>',
        dark=False, short=True, wide=True,
    ))

    s.append(split(None, "I mellomtiden", "Fagkompetansen kan kobles på fra første pilot.",
        "Der produktdata ennå ikke er integrert, kan prosjektet struktureres av ERA og endelig produktvalg kvalitetssikres gjennom relevant malermesterkompetanse.",
        None, "painter-v3.jpg", reverse=True))
    s.append(scene(None, flow([("ERA", None), ("Behov", None), ("Arbeidsgrunnlag", None), ("Malermester", "solid"), ("Produktvalg", None), ("Prosjekt", None)]), dark=False, short=True))

    s.append(scene(None,
        '<div class="p-eyebrow">Målbildet</div>'
        '<h2 class="p-h1">Handlelisten er klar.</h2>'
        '<p class="p-lede">Alt prosjektet trenger, samlet før kunden går til butikk.</p>'
        + dash("Handleliste · Fasadeprosjekt", "Demo-produktdata",
               kpis=[("Grunning", "Produkt · demo"), ("Maling", "Produkt · demo"), ("Tilbehør", "Ruller, pensler, maskering"), ("Farge", "Valgt av kunde")],
               footer="DEMO_PRODUCT_DATA. Ingen reell Jotun-produktkobling ennå."),
        image="materials-floor-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Lokal handel</div>'
        '<h2 class="p-h1">Fra digitalt behov til lokal handel.</h2>'
        + dash("Nærmeste forhandler", "Basert på boligens adresse",
               kpis=[("Forhandler", "Lokal Jotun-forhandler"), ("Avstand", "3,2 km"), ("Produkter", "Tilgjengelig"), ("Handleliste", "Klar")])
        + '<div class="p-actions" style="margin-top:24px"><span class="btn" style="pointer-events:none">Hent i butikk</span><span class="link" style="pointer-events:none">Send til butikk</span></div>',
        image="materials-floor-v3.jpg", short=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Forhandlerens perspektiv</div>'
        '<h2 class="p-h1">Mer enn trafikk.</h2>'
        '<p class="p-lede">Et strukturert prosjekt kan følge kunden helt frem til forhandleren, i stedet for «jeg trenger litt maling».</p>'
        + dash("Prosjekt mottatt", "Fra ERA, klar for forhandler",
               kpis=[("Overflate", "Kjent"), ("Areal", "Kjent"), ("Produktsystem", "Valgt"), ("Handleliste", "Klar")],
               footer="Ingen dokumentert konverteringsgevinst ennå — dette er konseptet, ikke målte resultater.")
        + '<p class="p-payoff">Mer relevant kunde. Mer komplett prosjekt.</p>',
        dark=True,
    ))

    s.append(scene(None,
        '<h2 class="p-h1">To veier. Samme bolig.</h2>'
        + dash("Fasadeprosjekt", "Samme underlag, ulik vei",
               cols=[("order", [("Gjør det selv", "ERA → Jotun-system → handleliste → forhandler → kjøp")]),
                     ("pro", [("Få hjelp", "ERA → arbeidsgrunnlag → malermester → Jotun-system → utførelse")])],
               footer="Begge veier ender samme sted: dokumentasjon på boligen."),
        dark=False, short=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Jobben er gjort</div>'
        '<h2 class="p-h1">Og boligen husker hva som ble gjort.</h2>'
        + dash("Dokumentasjon", "Fasadeprosjekt · ferdigstilt",
               kpis=[("Produkt", "Registrert"), ("Farge", "Registrert"), ("Dato", "Registrert"), ("Utført av", "Registrert")])
        + flow([("Bolig", None), ("Behov", None), ("ERA", None), ("Jotun", "solid"), ("Forhandler / fagperson", None), ("Utført", None), ("Dokumentert", None), ("Bolig", None)])
        + '<p class="p-payoff">Fra boligdata til handling. Fra handling tilbake til boligen.</p>',
        image="loop-home-v3.jpg",
    ))

    # ACT 3 — ÉN BOLIG BLIR TUSEN
    s.append(transition("distribusjon", "block-bikes-v3.jpg", "neighbourhood-dusk-v4.jpg", "Akt 3 · Én bolig blir tusen", "Så skalerer vi perspektivet.", "Én bolig blir tusen."))

    s.append(scene(None,
        '<div class="p-eyebrow">Bygge etterspørsel</div>'
        '<h2 class="p-h1">Bygge etterspørsel, ikke bare vente på den.</h2>'
        '<p class="p-lede">ERA har som ambisjon å identifisere relevante vedlikeholdsbehov før boligeieren selv begynner å lete etter produkt eller fagperson.</p>'
        + flow([("Potensielt behov", None), ("Aktivert prosjekt", None), ("Anbefaling", None), ("Forhandler", None), ("Handling", None)]),
        image="neighbourhood-dusk-v4.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Fra historikk til fremtid</div>'
        '<h2 class="p-h1">Fra det som ble solgt til det som kan komme.</h2>'
        '<p class="p-lede">Historiske salgstall viser hva markedet allerede har kjøpt. Boligdata kan gi et nytt signal om hva markedet kan komme til å trenge.</p>'
        + flow([("Historisk salg 2025", "old"), ("Historisk salg 2026", "old")])
        + flow([("Kommende behov · fasade", None), ("Terrasse", None), ("Innvendig", None), ("Vedlikehold", None)], vertical=True)
        + '<p class="p-fine">Fremtidsbilde — ikke et validert prognoseprodukt i dag.</p>',
        dark=False, short=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Etterspørselslandskapet</div>'
        '<h2 class="p-h1">Riktig behov. Riktig sesong.</h2>'
        + dash("Eksempelklynger", TAG_LABELS["vision"] + " — ikke reelle tall",
               kpis=[("Oslo", "Fasade ↑"), ("Romerike", "Innvendig ↑"), ("Drammen", "Terrasse ↑")],
               tag_kind="vision")
        + flow([("Vår · fasade / terrasse", None), ("Sommer · utvendig", None), ("Høst · kontroll", None), ("Vinter · innvendig", None)])
        + '<p class="p-body-text">ERA kan kombinere boligkontekst, prosjektbehov og tidspunkt for å gjøre kommunikasjonen mer relevant.</p>',
        image="property-intelligence-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Sentralt til lokalt</div>'
        '<h2 class="p-h1">Fra sentral aktivitet til lokal handling.</h2>'
        + flow([("Jotun · kampanje / faginnhold / produkt", None), ("ERA · relevant bolig, behov, tidspunkt", "solid"), ("Lokal forhandler", None), ("Kunde", None)], vertical=True)
        + '<p class="p-payoff">Én digital motor kan koble sentrale initiativer til lokal etterspørsel.</p>',
        dark=False, short=True,
    ))

    # ACT 4 — DISTRIBUSJONSMULIGHETEN
    s.append(scene("innsikt",
        '<div class="p-eyebrow">Akt 4 · Distribusjonsmuligheten</div>'
        '<h2 class="p-h1">Fra aktivitet til dokumentert handling.</h2>'
        + flow([("Behov identifisert", None), ("Prosjekt opprettet", None), ("Produkt anbefalt", None), ("Handleliste", None), ("Forhandler valgt", None)], vertical=True)
        + flow([("Kjøp", "muted"), ("Utført", None), ("Dokumentert", None)], vertical=True)
        + '<p class="p-body-text">En sammenhengende digital reise kan gjøre det mulig å forstå hvilke aktiviteter som faktisk fører kunden videre. Der kjøpsdata ikke er tilgjengelig, skiller vi klikk og intensjon fra dokumentert gjennomføring — ikke bekreftet salg.</p>',
        image="ecosystem-v3.jpg",
    ))

    s.append(split(None, "Over tid", "Relasjonen slutter ikke ved kassen.",
        "ERA er bygget rundt boligens livsløp, ikke én enkelt transaksjon. Det gir muligheten til å møte kunden igjen når et nytt relevant behov oppstår.",
        None, "block-season-2-v3.jpg"))
    s.append(scene(None,
        dash("Boligens tidslinje", "Eksempel, Borgveien 14",
             kpis=[("2027", "Fasade"), ("2028", "Terrasse"), ("2029", "Innvendig"), ("2031", "Ny vurdering")])
        + '<p class="p-payoff">Én bolig. Mange prosjekter. Mange år.</p>'
        + '<p class="p-body-text">Gjennom ERA kan Jotun potensielt være relevant gjennom flere faser av boligens livsløp, ikke bare når kunden allerede har bestemt seg for å kjøpe maling. Dette handler om en digital kunderelasjon og løpende kontaktpunkter, ikke om eierskap til kunden.</p>',
        dark=False, short=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Forhandlernettverket</div>'
        '<h2 class="p-h1">Mer verdi i forhandlernettet.</h2>'
        '<p class="p-lede">ERA kan utvikles til et digitalt verktøy som skaper og strukturerer etterspørsel, og leder relevante prosjekter videre til Jotuns forhandlere.</p>'
        + flow([("Jotun sentralt", None), ("ERA", "solid"), ("Forhandler A / B / C", None), ("Lokale kundeprosjekter", None)])
        + '<p class="p-payoff">Et sterkere digitalt lag rundt eksisterende distribusjon.</p>',
        image="ecosystem-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Datalaget</div>'
        '<h2 class="p-h1">Boligbehov skaper et nytt datalag.</h2>'
        + flow([("Individuell boligkontekst", None), ("Aggregert, samtykkebasert innsikt", "solid")])
        + dash("Mulige innsiktskategorier", "Aggregert nivå, ikke individdata",
               kpis=[("Behov", ""), ("Geografi", ""), ("Kategori", ""), ("Tidspunkt", "")], tag_kind="vision")
        + '<p class="p-body-text">På aggregert og riktig samtykke- og personvernsgrunnlag kan slike signaler gi ny innsikt i hvordan etterspørselen utvikler seg. Boligeierens data eksponeres ikke i partnerinnsikt.</p>',
        dark=False, short=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Fremtidsbilde</div>'
        '<h2 class="p-h1">Fra signaler til forecast.</h2>'
        + flow([("Boliger", None), ("Behovssignaler", None), ("Geografi", None), ("Sesong", None), ("Kategori", None), ("Forventet etterspørsel", "solid")], vertical=True)
        + '<p class="p-body-text">På sikt kan dette gi et nytt beslutningsgrunnlag for marked, distribusjon og planlegging hos Jotun. Dette er en ambisjon for hvor samarbeidet kan gå, ikke et ferdig prognoseprodukt i dag.</p>',
        image="property-intelligence-v3.jpg",
    ))

    s.append(scene(None,
        '<h2 class="p-h1">Fra én bolig til et smartere marked.</h2>'
        + flow([("Bolig", None), ("Behov", None), ("ERA", None), ("Anbefaling", None), ("Jotun", "solid"), ("Produkt", None), ("Forhandler / malermester", None), ("Kjøp / utførelse", None), ("Dokumentasjon", None), ("Bolig", None)], vertical=True)
        + flow([("Mange boliger", None), ("Etterspørsel", None), ("Innsikt", None), ("Distribusjon", None), ("Forecast", None)]),
        dark=False, short=True, wide=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Fem forslag</div>'
        '<h2 class="p-h1">Hva dette kan gi Jotun.</h2>'
        + reveal_list([
            ("01", "Bygge etterspørsel", "Identifisere relevante behov tidligere i kundereisen."),
            ("02", "Smartere distribusjon", "Koble digital etterspørsel til lokale forhandlere og fagpersoner."),
            ("03", "Mer prediktiv innsikt", "Bevege seg fra historiske salgstall mot forståelse av kommende behov."),
            ("04", "Langsiktig B2C-kanal", "Bygge relevans rundt boligen over flere år og prosjekter."),
            ("05", "Sterkere forhandlernettverk", "Gi lokale partnere et nytt digitalt lag for etterspørsel, prosjekter og kundeaktivitet."),
        ]),
        image="ecosystem-v3.jpg",
    ))

    s.append(scene(None,
        '<h2 class="p-h1">Riktig løsning for riktig bolig, til riktig tid.</h2>'
        + converge(
            "ERA", ["Boligkontekst", "Kunstig intelligens", "Behov", "Prosjekt", "Kundereise", "Dokumentasjon"],
            "Jotun", ["Produkter", "Fagkunnskap", "Produktsystemer", "Merkevare", "Forhandlernettverk"],
            "Boligeieren",
        ),
        dark=False, short=True, wide=True,
    ))

    # PILOT
    s.append(scene("pilot",
        '<div class="p-eyebrow">Foreslått pilot</div>'
        '<h2 class="p-h1">Start med én komplett kundereise.</h2>'
        + steps_grid([
            ("01", "Koble produktdata", "Én kategori, avgrenset omfang."),
            ("02", "Velg én kategori", "Foreslått: maling / overflate."),
            ("03", "Bygg anbefalingsflyt", "Fra prosjekt til produktsystem."),
            ("04", "Koble forhandler", "Én til få pilotforhandlere."),
            ("05", "Test med reelle boligeiere", "Begrenset utvalg, tett oppfølging."),
            ("06", "Mål hele reisen", "Prosjekter, handlelister, ruting, henvendelser, dokumentert gjennomføring."),
        ]),
        image="whole-home-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Spørsmålet til Jotun</div>'
        '<h2 class="p-h1">Det vi trenger for å koble på Jotun.</h2>'
        + flow([("Produktkatalog", None), ("Produktdata", None), ("Bruksområder", None), ("Produktsystemer", None), ("Farger", None), ("Forhandlerdata", None), ("Eventuelle API-er / feeds", None)], vertical=True)
        + '<p class="p-payoff">ERA har den tekniske produktflyten. Neste steg er å koble på Jotuns produkt- og distribusjonsdata.</p>'
        + '<p class="p-body-text">Hvilke produktkataloger, feeds, API-er og forhandlerdata kan Jotun gjøre tilgjengelig for en pilot? Der produktdata ikke er tilgjengelig fra start, kan malermesterkompetanse brukes som faglig mellomledd i pilotfasen.</p>',
        dark=False, short=True,
    ))

    # FINALE
    s.append(scene(None,
        '<h2 class="p-h1">Det starter med boligen.</h2>'
        '<p class="p-lede">Og kan ende i et smartere distribusjonssystem.</p>'
        + flow([("Bolig", None), ("Behov", None), ("ERA", None), ("Jotun", "solid"), ("Forhandler / fagperson", None), ("Handling", None), ("Dokumentasjon", None), ("Bolig", None)], vertical=True)
        + '<div class="p-eyebrow" style="margin-top:30px">ERA × JOTUN</div>'
        '<p class="p-payoff">Fra boligbehov til handling.</p>'
        '<p class="p-body-text">Riktig produkt. Riktig bolig. Riktig tidspunkt. Riktig kanal.</p>'
        '<div class="p-actions"><a class="btn" href="#pilot">Utforsk piloten</a><a class="link" href="/">Tilbake til ERA</a></div>',
        image="whole-home-v3.jpg",
    ))

    return "".join(s)


PARTNERS = {
    "jotun": dict(
        partner_name="Jotun",
        title="ERA × Jotun — Fra boligbehov til handling",
        description="En cinematisk demonstrasjon av hva som skjer når ERAs forståelse av boligen kobles til Jotuns produkter, fagkunnskap og distribusjonsnettverk.",
        build=build_jotun,
    ),
}

if __name__ == "__main__":
    for slug, p in PARTNERS.items():
        out_dir = os.path.join(ROOT, "partner", slug)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "index.html")
        content = page(slug, p)
        open(out, "w", encoding="utf-8").write(content)
        print("wrote", os.path.relpath(out, ROOT), len(content))
