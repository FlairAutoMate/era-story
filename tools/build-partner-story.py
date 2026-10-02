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
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://era-story.vercel.app"
# The investor page is its own Vercel project, deployed from sites/investor. Everything it links back to on
# the main site is written as an absolute SITE url, since "/" on this host is the investor page itself.
INVESTOR_SITE = "https://era-investor.vercel.app"


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
    """items: (number, title, text) eller (number, title, text, tag_kind).

    Det valgfrie fjerde feltet setter et statusmerke på kortet — Planlagt, I pilot,
    Fremtidsbilde. Statusen hører hjemme på kortet, ikke i en fotnote under: et tall
    uten status leses som noe som allerede skjer."""
    cards = []
    for it in items:
        n, t, x = it[0], it[1], it[2]
        kind = it[3] if len(it) > 3 else None
        badge = tag(kind) if kind else ""
        cards.append(
            f'<div class="p-step-card">{badge}<span class="p-reveal-n">{esc(n)}</span>'
            f'<b>{esc(t)}</b><p>{esc(x)}</p></div>')
    return '<div class="p-steps-grid reveal-stagger">' + "".join(cards) + '</div>'


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


def nav_html(brand, nav=None, label=None, back_href="/", back_label="Tilbake til ERA"):
    """`brand` er teksten etter «era.» i pillen — «Investor» for investorfortellingen, «× <navn>»
    for en partnerfortelling. `nav` er seksjonslista, og må matche id-ene bygget faktisk legger ut."""
    items = nav or []
    links = "".join(f'<a class="p-link" href="#{k}" data-act="{k}">{esc(l)}</a>' for k, l in items)
    return (
        '<nav class="p-nav" aria-label="' + esc(label or ("ERA " + brand)) + '">'
        '<div class="p-pill">'
        f'<span class="p-brand">era<span>.</span> {esc(brand)}</span>'
        f'{links}<a class="p-back" href="{esc(back_href)}">{esc(back_label)}</a>'
        '</div></nav>'
    )


def head_meta(path, title, description, site=SITE):
    return f'''<link rel="canonical" href="{site}{path}">
<meta name="robots" content="noindex,nofollow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ERA">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{site}{path}">
<meta property="og:locale" content="nb_NO">'''


def page(slug, p):
    body = p["build"](p)
    html = _page(slug, p, body)
    if p.get("standalone"):
        # On its own host, "/" and "/personvern" are not the main site's. Point them there.
        html = html.replace('href="/"', f'href="{SITE}/"').replace('href="/personvern"', f'href="{SITE}/personvern"')
    return html


def _page(slug, p, body):
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["description"])}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{head_meta(p.get("path", "/partner/" + slug), p["title"], p["description"], p.get("site", SITE))}
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
<link rel="stylesheet" href="/partner.css">
</head>
<body>
{nav_html(p.get("brand", "× " + p.get("partner_name", "")), p.get("nav"), p.get("nav_label"))}
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


# ── ERA Investor ──────────────────────────────────────────────────────────────
# Investorfortellingen fra investordekket, satt i samme scenespråk som partnersiden.
# Egen rute, noindex, og ikke lenket fra hovedmenyen — den deles som lenke, den skal
# ikke kunne finnes av seg selv.

TEAM = [
    ("Lars-Henrik Sand", "Founder", "17+ år innen eiendom, teknologi, markedsføring og digital distribusjon.", "team-lars.jpg"),
    ("Thomas Floden", "Partner", "20 år full-stack og AI-/LLM-produktarkitektur.", "team-thomas.jpg"),
    ("Ragnvald Løhren", "Co-founder", "Finans, investering, strategi og selskapsutvikling.", "team-ragnvald.jpg"),
    ("Eskild Løken Ugland", "Partner", "Tidligere salgs- og markedsdirektør i Block Watne. Kjedesjef i Mal Proff og Mesterfarge.", "team-eskild-v2.jpg"),
    ("Magnus Stensrud", "Daglig leder", "Administrasjon, salg, salgsledelse og kundereiser.", "team-magnus-v4.jpg"),
    ("William Lente", "Kommersiell · kundeopplevelse", "Digital markedsføring, leadgenerering, web og design.", "team-william.jpg"),
]


def team_grid(people):
    """Teamet som et rutenett. Mangler portrettet, vises en ERA-stilt plassholder med initialene,
    slik at raden ikke kollapser mens vi venter på foto."""
    cards = []
    for name, role, bio, asset in people:
        path = os.path.join(ROOT, "assets", "story", asset)
        if os.path.exists(path):
            media = f'<img src="/assets/story/{asset}" alt="{esc(name)}" loading="lazy" decoding="async">'
        else:
            initials = "".join(w[0] for w in name.split()[:2]).upper()
            media = f'<span class="p-team-ph" aria-hidden="true">{esc(initials)}</span>'
        cards.append(
            f'<figure class="p-team-card"><div class="p-team-shot">{media}</div>'
            f'<figcaption><b>{esc(name)}</b><span class="p-team-role">{esc(role)}</span>'
            f'<span class="p-team-bio">{esc(bio)}</span></figcaption></figure>')
    return '<div class="p-team">' + "".join(cards) + '</div>'


# Navngitte motparter star i fremdriftsseksjonen, der de er merket som dialog eller LOI.
# De star bevisst IKKE ved siden av en prosentsats: dette er en apen URL som blir
# videresendt, og en sats knyttet til et navn er publisert for motparten har sagt ja.
def build_investor(p):
    s = []

    s.append(hero(
        "ERA · INVESTOR", "Boliger har ingen hukommelse.<br>ERA gir dem en.",
        "Vedlikehold, dokumentasjon og utført arbeid ligger spredt. ERA samler boligens historie og gjør den handlingsbar.",
        "door-evening-v4.jpg", ("Se caset", "#problemet"), ("Tilbake til ERA", "/"),
    ))

    s.append(scene("problemet",
        '<div class="p-eyebrow">Problemet</div>'
        '<h2 class="p-h1">Boligens historie finnes ikke samlet noe sted.</h2>'
        + converge(
            "Slik er det i dag",
            ["Fragmentert data — dokumenter og historikk spredt",
             "Reaktivt vedlikehold — behov oppdages for sent",
             "Risiko ved salg — mangelfull dokumentasjon"],
            "Med ERA",
            ["Boligen husker — tilstand, tiltak og dokumentasjon følger boligen",
             "ERA vet hva som bør skje videre",
             "Dokumentasjonen følger boligen, også til neste eier"],
            "Boligen husker")
        + '<p class="p-payoff">ERA vet hva som bør skje videre.</p>',
        image="fragmented-home-v3.jpg", wide=True,
    ))

    s.append(scene("team",
        '<div class="p-eyebrow">Team</div>'
        '<h2 class="p-h1">Bygget for eiendom, teknologi og gjennomføring.</h2>'
        + team_grid(TEAM),
        dark=False, wide=True,
    ))

    s.append(scene("fremdrift",
        '<div class="p-eyebrow">Dokumentert fremdrift</div>'
        '<h2 class="p-h1">Fra produkt til kommersiell validering.</h2>'
        + dash("Status september 2026", "Signert, i prosess og i dialog",
               kpis=[("Håndverkerbedrifter på venteliste", "90"), ("Byer besøkt", "11"),
                     ("Boliger i pilot", "2 500"), ("Pilot", "Boligbyggelag og borettslag")],
               groups=[
                   ("doc", [("Perrongen BRL, Eidsvoll", "69 leiligheter · signert pilot")]),
                   ("pilot", [("Boligbyggelag og borettslag", "Prosess på gang — 2 500 boliger i pilot"),
                              ("ABBL + NBBL", "Dialog om distribusjon"),
                              ("Mesterfarge / Mal Proff", "LOI og nettverk — kommersiell inngang"),
                              ("Jotun", "Kommersiell dialog om distribusjon og produktsalg"),
                              ("2 eiendomsmeglerkjeder", "Interesse for distribusjon")]),
               ],
               footer="Kun Perrongen er en signert avtale. Øvrige, inkludert de 2 500 boligene i pilotprosess, er i prosess og ikke inngåtte avtaler."),
        image="block-facade-v3.jpg",
    ))

    s.append(scene("skalering",
        '<div class="p-eyebrow">Fra pilot til skalering</div>'
        '<h2 class="p-h1">Bevis modellen før vi skalerer den.</h2>'
        + flow([("NÅ · 2 500 boliger i pilotprosess", "solid"), ("BEVISE · 100+ aktive boliger", None),
                ("FØRSTE SKALA · 1 000 betalende", None), ("KONVERTERE · 2–3 boligbyggelag", None),
                ("ÅR 2 · 5–10k betalende", None)])
        + '<p class="p-payoff">1 000 betalende boliger er første tydelige kommersielle milepæl, før videre skalering mot 5 000–10 000.</p>',
        image="neighbourhood-dusk-v4.jpg", wide=True,
    ))

    # Tidslinjen ligger i denne seksjonen, ikke i en egen. Spørsmålet en investor stiller rett
    # etter å ha sett inntektsstrømmene er «når begynner de å tjene penger» — svaret hører til
    # ved siden av spørsmålet. Skaleringsseksjonen er en volumakse (antall boliger); å slå dem
    # sammen ville blandet to historier.
    s.append(scene("inntekt",
        '<div class="p-eyebrow">Inntektsmotor</div>'
        '<h2 class="p-h1">Én bolig. Flere inntektsstrømmer.</h2>'
        # Ingen statusmerker på kortene. Seksjonen skal vise forretningsmodellen, og et «Planlagt»
        # på hvert kort trekker blikket til hva som mangler i stedet for til modellen. Tidslinjen
        # rett under sier når hver strøm starter — samme informasjon, uten å undergrave.
        + steps_grid([
            ("49 kr", "per bolig / måned", "Abonnement via borettslag og sameier."),
            ("ca. 5 %", "provisjon på maling", "Produktsalg gjennom ERA. Forutsatt endelig avtale med leverandør."),
            ("3,5 %", "påslag på håndverkerjobber", "På faktura når oppdraget gjennomføres via ERA."),
            ("3 000 kr", "per boligsalg", "ERA inn i oppdragsavtalen for boligselgere, som revenue share med megler."),
            ("Provisjon", "forsikring og finansiering", "Når boligeieren går videre fra et dokumentert behov."),
        ])
        + '<p class="p-body-text">Øvrige byggfag kommer som partneravtaler på samme modell: elektro, VVS og snekker.</p>'
        + '<div class="p-eyebrow" style="margin-top: 38px">Når inntektene starter</div>'
        + reveal_list([
            ("Q4 2026", "Abonnement", "Første inntekter. Boliger og borettslag/sameier."),
            ("Q1 2027", "Malingsalg", "Provisjon på produkt solgt gjennom ERA."),
            ("Q1 2027", "Eiendomsmegler", "ERA inn i oppdragsavtalen for boligselgere."),
            ("Q1 2027", "Håndverkere", "Påslag på faktura for oppdrag gjennomført via ERA."),
            ("Q1 2027", "Øvrige byggfag", "Partneravtaler med elektro, VVS og snekker."),
        ])
        + '<p class="p-fine">Abonnementet er i signert pilot. De øvrige strømmene følger tidslinjen over.</p>'
        + '<p class="p-payoff">Abonnementet først. Produkt- og transaksjonsinntektene kobles på i Q1 2027.</p>',
        dark=False, wide=True,
    ))

    s.append(scene("distribusjon",
        '<div class="p-eyebrow">Marked og distribusjon</div>'
        '<h2 class="p-h1">Distribusjonen er bygget inn i ERA.</h2>'
        '<p class="p-lede">Vi går gjennom aktørene som allerede har tilgang til boligen – og lar selve bruken skape videre distribusjon.</p>'
        + flow([("Boligbyggelag · én avtale", None), ("Borettslag og sameier · mange boliger", None),
                ("Boligeiere · behov og prosjekter", "solid"), ("Produsenter og forhandlere · kjøp", None),
                ("Håndverkere · dokumentert jobb", None)])
        + '<p class="p-payoff">Vekst gjennom økosystemet rundt boligen – ikke bare betalt markedsføring.</p>',
        image="ecosystem-v3.jpg", wide=True,
    ))

    s.append(scene("kapital",
        '<div class="p-eyebrow">Kapital og milepæler</div>'
        '<h2 class="p-h1">Kapitalen skal bevise og skalere modellen.</h2>'
        + converge(
            "Bruk av kapital",
            ["Produkt og produksjonsdata", "Pilot og kundeaktivering",
             "Distribusjon og kommersialisering", "Kjernekapasitet i teamet"],
            "Milepæler",
            ["Perrongen: dokumentert aktivering og bruk", "2–3 boligbyggelag på kommersielle avtaler",
             "5 000–10 000 betalende boliger", "Dokumentert inntekt per aktiv bolig"],
            "Bevise, så skalere")
        + '<p class="p-body-text">Beløp og emisjonsvilkår presenteres separat.</p>',
        image="property-intelligence-v3.jpg", wide=True,
    ))

    s.append(scene(None,
        '<h2 class="p-h1">Boligen husker. ERA vet hva som bør skje videre.</h2>'
        '<p class="p-lede">Fra vedlikeholdsbehov til produkt, håndverker og dokumentert resultat.</p>'
        '<p class="p-body-text">Lars-Henrik Sand · ERA Technologies AS · Investor deck, september 2026</p>'
        '<div class="p-actions"><a class="link" href="/">Tilbake til ERA</a></div>',
        image="loop-home-v3.jpg", center=True,
    ))

    return "".join(s)



INVESTOR_NAV = [
    ("problemet", "Problemet"), ("team", "Team"), ("fremdrift", "Fremdrift"),
    ("skalering", "Skalering"), ("inntekt", "Inntekt"), ("distribusjon", "Distribusjon"),
    ("kapital", "Kapital"),
]

PARTNERS = {
    "investor": dict(
        partner_name="Investor",
        brand="Investor",
        nav=INVESTOR_NAV,
        nav_label="ERA Investor",
        path="/",
        out="sites/investor",
        site=INVESTOR_SITE,
        standalone=True,
        title="ERA — Investor",
        description="Boliger har ingen hukommelse. ERA gir dem en. Problem, team, dokumentert fremdrift, inntektsmodell, distribusjon og kapitalbruk.",
        build=build_investor,
    ),
}

def copy_site_files(out_dir, html):
    """A standalone site carries its own copy of every file it references, so the folder deploys alone.
    Collects the root-relative urls from the page and from its stylesheets, copies those files, and
    writes the site's vercel.json. Stale copies from earlier runs are removed first."""
    import re, shutil
    for d in ("assets", "fonts", "js"):
        shutil.rmtree(os.path.join(out_dir, d), ignore_errors=True)
    for f in ("fonts.css", "pages.css", "partner.css", "favicon.svg"):
        try:
            os.remove(os.path.join(out_dir, f))
        except FileNotFoundError:
            pass
    url_re = re.compile(r'(?<![A-Za-z0-9:])/(?:assets|fonts|js)/[A-Za-z0-9_./-]+[.][A-Za-z0-9]+')
    wanted = {"fonts.css", "pages.css", "partner.css", "favicon.svg"}
    wanted |= {m.group(0).lstrip("/") for m in url_re.finditer(html)}
    # stylesheets can pull in more files (the web fonts)
    for css in [w for w in sorted(wanted) if w.endswith(".css")]:
        text = open(os.path.join(ROOT, css), encoding="utf-8").read()
        wanted |= {m.group(0).lstrip("/") for m in url_re.finditer(text)}
    missing = []
    total = 0
    for rel in sorted(wanted):
        src = os.path.join(ROOT, *rel.split("/"))
        if not os.path.isfile(src):
            missing.append(rel)
            continue
        dst = os.path.join(out_dir, *rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        total += os.path.getsize(src)
    config = {
        "cleanUrls": True,
        "trailingSlash": False,
        "headers": [
            {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
            {"source": "/(assets|fonts|js)/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        ],
    }
    with open(os.path.join(out_dir, "vercel.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(config, indent=2) + "\n")
    print("  copied", len(wanted) - len(missing), "files,", round(total / 1e6, 1), "MB")
    if missing:
        raise SystemExit("missing files for " + os.path.relpath(out_dir, ROOT) + ": " + ", ".join(missing))


if __name__ == "__main__":
    for slug, p in PARTNERS.items():
        # `out` lar en fortelling bo utenfor /partner — investorsiden har sin egen rute.
        rel = p.get("out")
        out_dir = os.path.join(ROOT, rel) if rel else os.path.join(ROOT, "partner", slug)
        os.makedirs(out_dir, exist_ok=True)
        out = os.path.join(out_dir, "index.html")
        content = page(slug, p)
        open(out, "w", encoding="utf-8").write(content)
        print("wrote", os.path.relpath(out, ROOT), len(content))
        if p.get("standalone"):
            copy_site_files(out_dir, content)
