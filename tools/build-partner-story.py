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


def browser_card(url, brand_note, nav_links, eyebrow, heading, text, cta_label, quote, quote_by):
    """A nested 'site preview' card — a concept of a partner's own website with ERA built in.
    Deliberately schematic, not a pixel clone of the partner's real UI."""
    return (
        '<div class="p-browser">'
        '<div class="p-browser-bar"><span class="p-browser-dot"></span><span class="p-browser-dot"></span><span class="p-browser-dot"></span>'
        f'<span class="p-browser-url">{esc(url)}</span></div>'
        '<div class="p-browser-body">'
        f'<div class="p-browser-nav"><span class="p-browser-brand"><b>JOTUN</b><i>{esc(brand_note)}</i></span><span class="p-browser-navlinks">{esc(nav_links)}</span></div>'
        '<div class="p-browser-hero"><div>'
        f'<div class="p-eyebrow" style="color:var(--gold-2)">{esc(eyebrow)}</div>'
        f'<h3>{esc(heading)}</h3><p>{esc(text)}</p>'
        f'<span class="p-browser-cta">{esc(cta_label)}</span>'
        '</div>'
        f'<div class="p-browser-quote">«{esc(quote)}»<b>— {esc(quote_by)}</b></div>'
        '</div></div></div>'
    )


def product_card(eyebrow, title, text, checks, cta_primary, cta_secondary):
    """Illustrative product highlight — a color swatch stands in for packaging, not a real
    product render (pair with a DEMO_PRODUCT_DATA-style disclaimer, as used elsewhere)."""
    li = "".join(f'<li>{esc(x)}</li>' for x in checks)
    return (
        '<div class="p-product">'
        '<div class="p-product-swatch" aria-hidden="true"></div>'
        '<div class="p-product-body">'
        f'<div class="p-eyebrow" style="color:var(--gold-2)">{esc(eyebrow)}</div>'
        f'<h3>{esc(title)}</h3><p>{esc(text)}</p>'
        f'<ul class="p-product-checks">{li}</ul>'
        f'<div class="p-actions" style="margin-top:16px"><span class="btn" style="pointer-events:none">{esc(cta_primary)}</span><span class="link" style="pointer-events:none">{esc(cta_secondary)}</span></div>'
        '</div></div>'
    )


def phone_card(image, title, meta, rows, cta):
    """A schematic phone-frame mockup of a concept ERA app screen; pass as split()'s
    media_html to replace the usual full-bleed photo in the media slot."""
    rows_html = "".join(f'<div class="drow"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in rows)
    return (
        '<div class="p-phone-stage"><div class="p-phone"><div class="p-phone-notch"></div>'
        '<div class="p-phone-screen">'
        f'<div class="p-phone-top"><b>{esc(title)}</b><span>{esc(meta)}</span></div>'
        f'<div class="p-phone-media" style="background-image:url(/assets/story/{esc(image)})"></div>'
        f'<div class="p-phone-body">{rows_html}<span class="p-phone-cta">{esc(cta)}</span></div>'
        '</div></div></div>'
    )


def mocknav():
    """A visual-only replica of the partner's real site nav, used once at the top of the closing
    'vision' act to set context — not part of the story's own <nav>, not interactive."""
    links = "".join(f'<a>{esc(l)}</a>' for l in ["Farger", "Produkter", "Inspirasjon", "Guider", "Våre tjenester"])
    return (
        '<div class="p-mocknav"><span class="p-mocknav-logo">JOTUN</span>'
        f'<nav class="p-mocknav-links">{links}</nav>'
        '<div class="p-mocknav-icons"><span>Finn forhandler</span><span aria-hidden="true">⚲</span><span aria-hidden="true">♡</span><span aria-hidden="true">◎</span></div>'
        '</div>'
    )


def timeline(stops):
    """stops: list of (number, text) — a horizontal numbered journey."""
    items = "".join(
        f'<div class="p-timeline-stop"><span class="p-timeline-n">{esc(n)}</span><p>{esc(t)}</p></div>'
        for n, t in stops
    )
    return f'<div class="p-timeline">{items}</div>'


def quote_float(quote, by):
    """A testimonial floating over a photo — pass alongside img() as split()'s media_html."""
    return f'<div class="p-quote-float">«{esc(quote)}»<b>— {esc(by)}</b></div>'


def check_icons(items):
    return '<ul class="p-check-icons">' + "".join(f'<li>{esc(x)}</li>' for x in items) + '</ul>'


def product_duo(product_html, use_title, use_text, use_cta, use_cta2):
    """A product_card() paired with a companion 'use this on your home' panel, side by side."""
    return (
        '<div class="p-product-duo">'
        f'{product_html}'
        f'<div class="p-usehome"><h4>{esc(use_title)}</h4><p>{esc(use_text)}</p>'
        f'<div class="p-actions" style="margin-top:14px"><span class="btn" style="pointer-events:none">{esc(use_cta)}</span><span class="link" style="pointer-events:none">{esc(use_cta2)}</span></div></div>'
        '</div>'
    )


def path_card(tag_label, image, title, text, cta):
    return (
        '<div class="p-path-card">'
        f'<div class="p-path-media">{img(image)}<span class="p-path-tag">{esc(tag_label)}</span></div>'
        f'<div class="p-path-body"><h4>{esc(title)}</h4><p>{esc(text)}</p>'
        f'<span class="btn" style="pointer-events:none">{esc(cta)}</span></div>'
        '</div>'
    )


def twopath(cards):
    return '<div class="p-twopath">' + "".join(cards) + '</div>'


def phone_checklist(title, items):
    """A phone-frame mockup whose screen holds a checklist instead of the usual project rows —
    used for the closing 'saved in ERA' moment."""
    li = "".join(f'<li>{esc(x)}</li>' for x in items)
    return (
        '<div class="p-phone-stage"><div class="p-phone"><div class="p-phone-notch"></div>'
        '<div class="p-phone-screen">'
        f'<div class="p-phone-top"><b>{esc(title)}</b></div>'
        f'<div class="p-phone-body"><ul class="p-check-icons" style="max-width:none;margin-top:4px">{li}</ul></div>'
        '</div></div></div>'
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


def split(id_, eyebrow, heading, text, value, image, image_alt="", reverse=False, dark=True, extra="", media_html=None):
    body = (
        f'<div class="p-eyebrow{"" if dark else " dark2"}">{esc(eyebrow)}</div>'
        f'<h2 class="p-h2" style="margin-top:14px">{esc(heading)}</h2>'
        f'<p class="{"p-lede" if dark else "p-lede"}">{esc(text)}</p>'
        + (f'<p class="p-payoff">{esc(value)}</p>' if value else "")
        + extra
    )
    cls = "p-split reverse" if reverse else "p-split"
    if not dark:
        cls += " light"
    bg = "background:var(--navy);color:var(--warm)" if dark else "background:var(--paper);color:var(--ink)"
    idattr = f' id="{esc(id_)}"' if id_ else ""
    media = media_html if media_html is not None else img(image, image_alt)
    media_reveal = "p-split-media" if media_html is not None else "p-split-media reveal-img"
    return (
        f'<section{idattr} class="{cls}" style="{bg}">'
        f'<div class="{media_reveal}">{media}</div>'
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
        '<p class="p-lede">Vedlikeholdsbehov oppstår lenge før boligeieren begynner å lete etter produkter eller malermestere.</p>'
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
        None, "roof-detail-v3.jpg", reverse=False,
        extra=dash(
            "ERA vurderer", "Fasade · basert på bilder og historikk",
            groups=[
                ("customer", [("Bilder delt", "6 av fasaden")]),
                ("doc", [("Tidligere vedlikehold", "Malt 2012")]),
                ("ai", [("Vurdering", "Overflate og tilstand tyder på behov"), ("Anbefaling", "Vedlikehold denne sesongen")]),
            ],
            footer="Eksempeldata og konseptvisning. En vurdering er beslutningsstøtte, ikke en garantert diagnose.",
        )))

    s.append(scene(None,
        '<div class="p-eyebrow">Fra behov til prosjekt</div>'
        '<h2 class="p-h1">ERA gjør behovet konkret.</h2>'
        + dash("Prosjekt · Fasade", "Fra spørsmål til gjennomførbart prosjekt",
               kpis=[("Arbeid", "Forberedelse, grunning, overflatebehandling"), ("Areal", "Beregnes fra bildene"), ("Mengde", "Beregnes"), ("Tidspunkt", "Denne sesongen")]),
        image="photo-observation-v3.jpg",
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Hvorfor nå</div>'
        '<h2 class="p-h1">Et AI-lag mellom boligen og handelen.</h2>'
        + flow([("Boligdata", None), ("Bilder", None), ("Historikk", None), ("Sesong", None), ("Produktdata", None)])
        + flow([("ERA Intelligence", "solid")])
        + flow([("Behov", None), ("Prosjekt", None), ("Produkt", None), ("Mengde", None), ("Tidspunkt", None), ("Forhandler", None)])
        + '<p class="p-payoff">Ikke bare en smart kundereise — en AI-drevet infrastruktur mellom boligen og handelen.</p>',
        image="property-intelligence-v3.jpg",
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

    s.append(split(None, "I mellomtiden", "Fagkompetansen kan kobles på fra første pilot.",
        "Der produktdata ennå ikke er integrert, kan prosjektet struktureres av ERA og endelig produktvalg kvalitetssikres gjennom relevant malermesterkompetanse.",
        None, "painter-v3.jpg", reverse=True,
        extra=flow([("ERA", None), ("Behov", None), ("Arbeidsgrunnlag", None), ("Malermester", "solid"), ("Produktvalg", None), ("Prosjekt", None)])))

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
        '<p class="p-lede">Et strukturert prosjekt kan følge kunden helt frem til forhandleren, i stedet for «jeg trenger litt maling».</p>'
        + dash("Nærmeste forhandler", "Basert på boligens adresse",
               kpis=[("Forhandler", "Lokal Jotun-forhandler"), ("Avstand", "3,2 km"), ("Produkter", "Tilgjengelig"), ("Handleliste", "Klar")],
               footer="Ingen dokumentert konverteringsgevinst ennå — dette er konseptet, ikke målte resultater.")
        + '<p class="p-payoff">Mer relevant kunde. Mer komplett prosjekt.</p>'
        + '<div class="p-actions" style="margin-top:24px"><span class="btn" style="pointer-events:none">Hent i butikk</span><span class="link" style="pointer-events:none">Send til butikk</span></div>',
        image="materials-floor-v3.jpg", short=True,
    ))

    # ACT 3 — ÉN BOLIG BLIR TUSEN
    s.append(transition("distribusjon", "block-bikes-v3.jpg", "neighbourhood-dusk-v4.jpg", "Akt 3 · Én bolig blir tusen", "Så skalerer vi perspektivet.", "Én bolig blir tusen."))

    s.append(scene(None,
        '<div class="p-eyebrow">Bygge etterspørsel</div>'
        '<h2 class="p-h1">Bygge etterspørsel, ikke bare vente på den.</h2>'
        '<p class="p-lede">ERA har som ambisjon å identifisere relevante vedlikeholdsbehov før boligeieren selv begynner å lete etter produkt eller fagperson. Historiske salgstall viser hva markedet allerede har kjøpt; boligdata kan gi et nytt signal om hva markedet kan komme til å trenge.</p>'
        + flow([("Historisk salg", "old"), ("Potensielt behov", None), ("Aktivert prosjekt", None), ("Anbefaling", None), ("Forhandler", None), ("Handling", None)])
        + '<p class="p-fine">Fremtidsbilde — ikke et validert prognoseprodukt i dag.</p>',
        image="neighbourhood-dusk-v4.jpg",
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

    # ACT 4 — DISTRIBUSJONSMULIGHETEN
    s.append(scene("innsikt",
        '<div class="p-eyebrow">Akt 4 · Distribusjonsmuligheten</div>'
        '<h2 class="p-h1">Fra aktivitet til dokumentert handling.</h2>'
        + flow([("Behov identifisert", None), ("Prosjekt opprettet", None), ("Produkt anbefalt", None), ("Handleliste", None), ("Forhandler valgt", None)], vertical=True)
        + flow([("Kjøp", "muted"), ("Utført", None), ("Dokumentert", None)], vertical=True)
        + '<p class="p-body-text">En sammenhengende digital reise kan gjøre det mulig å forstå hvilke aktiviteter som faktisk fører kunden videre. Der kjøpsdata ikke er tilgjengelig, skiller vi klikk og intensjon fra dokumentert gjennomføring — ikke bekreftet salg.</p>'
        + flow([("Bolig", None), ("Behov", None), ("Jotun-anbefaling", "solid"), ("Butikk", None), ("Kjøp", None), ("Utført", None), ("Dokumentert", None), ("Bolighistorikk", None), ("Neste behov", None)], vertical=True)
        + '<p class="p-payoff">Ikke bare leads til Jotun — et feedback- og demand intelligence-lag tilbake til ERA.</p>'
        + '<p class="p-fine">På aggregert og riktig samtykke- og personvernsgrunnlag kan slike signaler også gi ny innsikt i hvordan etterspørselen utvikler seg. Boligeierens data eksponeres ikke i partnerinnsikt.</p>',
        image="ecosystem-v3.jpg",
    ))

    s.append(split(None, "Over tid", "Relasjonen slutter ikke ved kassen.",
        "ERA er bygget rundt boligens livsløp, ikke én enkelt transaksjon. Det gir muligheten til å møte kunden igjen når et nytt relevant behov oppstår. Dette handler om en digital kunderelasjon og løpende kontaktpunkter, ikke om eierskap til kunden.",
        "Én bolig. Mange prosjekter. Mange år.",
        "block-season-2-v3.jpg",
        extra=dash("Boligens tidslinje", "Eksempel, Myrerveien 14",
                   kpis=[("2027", "Fasade"), ("2028", "Terrasse"), ("2029", "Innvendig"), ("2031", "Ny vurdering")])))

    s.append(scene(None,
        '<div class="p-eyebrow">Utover boligeieren</div>'
        '<h2 class="p-h1">Fire innganger. Samme motor.</h2>'
        '<p class="p-lede">Historien over er B2C-drevet, men prosjekt- og produktmotoren bak er ikke avgrenset til boligeieren.</p>'
        + flow([("Boligeier", None), ("Malermester", None), ("Borettslag / sameie", None), ("Forhandler", None)])
        + '<p class="p-payoff">Samme prosjekt- og produktmotor. Fire innganger til Jotuns produkter.</p>',
        image="ecosystem-v3.jpg",
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

    # PILOT — the closing scene: the concrete plan, the ask, and the exit.
    s.append(scene("pilot",
        '<div class="p-eyebrow">Forslag til neste steg</div>'
        '<h2 class="p-h1">ERA × Jotun Pilot Norge.</h2>'
        + dash("Pilotens omfang", "Foreslått ramme",
               kpis=[("Kategori", "Én · maling / overflate"), ("Forhandlere", "1–3 pilotforhandlere"), ("Boliger", "Reelt, begrenset utvalg"), ("Varighet", "8–12 uker")],
               footer="Mål: dokumentere om boligdata og AI kan skape tidligere etterspørsel, høyere prosjektverdi og målbar trafikk til Jotuns distribusjon.")
        + steps_grid([
            ("01", "Koble produktdata", "Én kategori, avgrenset omfang."),
            ("02", "Velg én kategori", "Foreslått: maling / overflate."),
            ("03", "Bygg anbefalingsflyt", "Fra prosjekt til produktsystem."),
            ("04", "Koble forhandler", "Én til få pilotforhandlere."),
            ("05", "Test med reelle boligeiere", "Begrenset utvalg, tett oppfølging."),
            ("06", "Mål hele reisen", "Prosjekter, handlelister, ruting, henvendelser, dokumentert gjennomføring."),
        ])
        + '<p class="p-payoff" style="margin-top:30px">I møtet ønsker vi å avklare:</p>'
        + flow([("Produktdata / API", None), ("Pilotforhandlere", None), ("Teknisk kontakt", None), ("KPI-er", None), ("Tidspunkt for oppstart", None)])
        + '<p class="p-body-text">ERA har den tekniske produktflyten. Der produktdata ikke er tilgjengelig fra start, kan malermesterkompetanse brukes som faglig mellomledd i pilotfasen.</p>'
        + '<div class="p-actions"><a class="link" href="/">Tilbake til ERA</a></div>',
        image="whole-home-v3.jpg",
    ))

    # KONKRET VISJON — a full mock-up of jotun.no with ERA built in, mirrored section-by-section
    # from a reference sketch: real-looking nav, a hero with a floating testimonial, the 5-step
    # journey, a product card paired with a "use on your home" panel, the ERA-app phone moment,
    # the DIY-vs-help fork, and a dark closing screen. Deliberately schematic (see the disclaimers
    # on each scene) — not a pixel clone of Jotun's real site.
    s.append(mocknav())

    s.append(split(None, "JOTUN × ERA", "Fra boligbehov til handling.",
        "Jotuns farger og produkter. ERAs kunnskap om boligen din. Sammen gjør vi det enklere å planlegge, handle og gjennomføre malingsprosjekter — enten du gjør det selv eller får hjelp av en fagperson.",
        None, "livingroom-wall-v3.jpg", dark=False,
        media_html=img("livingroom-wall-v3.jpg") + quote_float("Endelig en løsning som kjenner boligen min.", "Marte, Oslo"),
        extra=(
            '<div class="p-actions"><span class="btn" style="pointer-events:none">Kom i gang med ditt prosjekt →</span></div>'
            '<p class="p-fine">Vakkert hjem. Enklere prosjekter. — Konseptvisning, illustrasjon av hvordan integrasjonen kunne se ut på jotun.no, ikke en reell side.</p>'
        )))

    s.append(scene(None,
        '<div class="p-eyebrow">Slik fungerer det</div>'
        '<h2 class="p-h1">Fra inspirasjon til ferdig prosjekt.</h2>'
        '<p class="p-lede">Jotun og ERA guider deg hele veien — med riktig produkt, riktig mengde og riktig neste steg.</p>'
        + timeline([
            ("1", "Finn inspirasjon og produkt"),
            ("2", "Bruk på din bolig med ERA"),
            ("3", "Få mengde, farge og handleliste"),
            ("4", "Handle i butikk eller få hjelp av fagperson"),
            ("5", "Dokumenter og husk det i ERA"),
        ])
        + '<p class="p-fine">Konseptvisning av kundereisen — ikke en publisert funksjon på jotun.no i dag.</p>',
        dark=False, wide=True,
    ))

    s.append(scene(None,
        '<div class="p-eyebrow">Populært valg</div>'
        '<h2 class="p-h1">LADY New Era møter din bolig.</h2>'
        '<p class="p-lede">Når ERA har beregnet mengde og overflate, kan riktig produkt foreslås direkte — med begrunnelse, ikke bare en lenke til nettbutikken.</p>'
        + product_duo(
            product_card(
                "Populært valg", "LADY New Era",
                "Robust kvalitet som gir en varig, vakker matt finish.",
                ["Vakker, matt utseende", "Ekstremt slitesterk, flekkavvisende og vaskbar", "Resirkulert materiale — dokumentert lavere karbonavtrykk"],
                "Bruk på min bolig", "Finn farge",
            ),
            "Bruk LADY New Era på din bolig",
            "ERA kobler produktet til boligen din og hjelper deg videre med mengde, farge og neste steg.",
            "Finn boligen din", "Se hvordan det fungerer",
        )
        + '<p class="p-fine">DEMO_PRODUCT_DATA — illustrasjon, ikke reell Jotun-katalog eller -produktdata.</p>',
        dark=False, wide=True,
    ))

    s.append(split(None, "Din bolig. Ditt prosjekt.", "ERA kjenner boligen din.",
        "Ta et bilde av rommet, så hjelper ERA deg med å beregne hva du trenger. Du får en ferdig handleliste med Jotun-produkter, tilpasset din bolig og ditt prosjekt.",
        None, None, dark=False,
        media_html=phone_card(
            "materials-floor-v3.jpg", "Male stue", "Myrerveien 14",
            [("Rom", "Stue · 42 m²"), ("Strøk", "2")],
            "Fortsett",
        ),
        extra=(
            check_icons(["Enkel registrering med bilde", "Riktig mengde og tilbehør", "Anbefalt fremgangsmåte", "Lagre prosjektet i boligen din"])
            + '<div class="p-actions" style="margin-top:18px"><span class="btn" style="pointer-events:none">Prøv ERA med din bolig</span></div>'
            + '<p class="p-fine">Konseptvisning av en fremtidig ERA-app-skjerm — ikke et eksisterende produkt.</p>'
        )))

    s.append(scene(None,
        '<div class="p-eyebrow">To måter å gjøre jobben på</div>'
        '<h2 class="p-h1">Du velger. Vi legger til rette.</h2>'
        + twopath([
            path_card("Gjør det selv", "materials-floor-v3.jpg", "Handleliste klar",
                      "Få alt du trenger av Jotun-produkter og tilbehør, basert på ditt rom og prosjekt.",
                      "Finn nærmeste forhandler"),
            path_card("Få hjelp", "painter-v3.jpg", "Finn fagperson",
                      "Send prosjektet til en kvalifisert maler. De får all informasjon og kan gi tilbud.",
                      "Finn maler"),
        ])
        + '<p class="p-fine">Konseptvisning — ruting til forhandler og fagperson er ikke koblet i dag.</p>',
        dark=False, wide=True,
    ))

    s.append(split(None, "JOTUN × ERA", "Ferdig i dag. Husket i morgen.",
        "Når prosjektet er ferdig, kan du lagre bilder, produkt, fargekode og kvittering i ERA. Slik har du alltid oversikt over hva som er gjort i boligen din.",
        None, None, dark=True,
        media_html=phone_checklist("Prosjekt", ["Prosjekt fullført", "Bilder lagret", "Produkt og fargekode", "Kvittering", "En del av boligen din"]),
        extra=(
            '<div class="p-actions"><span class="btn" style="pointer-events:none">Start ditt første prosjekt →</span></div>'
            '<p class="p-fine">Hjem varer lenger. — Konseptvisning, ikke en publisert funksjon.</p>'
        )))

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
