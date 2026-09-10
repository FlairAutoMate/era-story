# -*- coding: utf-8 -*-
"""Generates the audience subpages (/boligeier, /styret, /handverker, /faghandel) and /personvern
from one template and one content dict. Run from the project root: python tools/build-pages.py

Product content per audience lives in tools/content_<slug>.py (see AUDIENCES[slug]["product_module"]).
Each module exposes render(H, a) -> HTML string, where H is the helpers namespace defined below and
a is the audience dict. The output is inserted right after the hero, before the scenes section."""
import html, importlib, json, os, sys

# The content modules are imported at build time; no tools/__pycache__/ should appear in the repo.
sys.dont_write_bytecode = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.dirname(os.path.abspath(__file__))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)


def esc(t):
    return html.escape(str(t), quote=True)


def rel(href):
    """External links are plain same-tab links with rel=noopener (no target=_blank)."""
    return ' rel="noopener"' if str(href).startswith("http") else ""


PILOT = dict(
    owner="https://pilot.era-app.no/register?entry=homeowner",
    board="https://pilot.era-app.no/register?entry=sameie",
    pro="https://pilot.era-app.no/register?entry=contractor",
)

STATUS = {"beta": "Kontrollert beta", "pilot": "I pilot", "dev": "Under utvikling", "planned": "Planlagt", "now": "Tilgjengelig nå", "illustration": "Illustrasjon av arbeidsflyt"}

TAG_LABELS = {"customer": "Fra kunden", "doc": "Dokumentert", "ai": "ERA-forslag", "check": "Avklares på befaring", "board": "Styret", "pro": "Håndverker", "resident": "Beboer", "order": "Bestilling og levering", "pilot": "I pilot", "planned": "Planlagt", "illustration": "Illustrasjon av arbeidsflyt", "beta": "Kontrollert beta", "dev": "Under utvikling", "now": "Tilgjengelig nå"}

# Tag kinds that product.css knows (.pw-tag--<kind>). ok/warn/wait have no default label.
TAG_KINDS = set(TAG_LABELS) | {"ok", "warn", "wait"}
MUTED_GROUP_KINDS = {"illustration", "pilot", "planned", "dev", "check"}
# Product surfaces are named exactly «ERA Bolig», «ERA Styret», «ERA Håndverker»; faghandel is not a
# fourth app, its window is titled «ERA for faghandel».
APP_CLASS = {"ERA Bolig": "pw-app--bolig", "ERA Styret": "pw-app--styret", "ERA Håndverker": "pw-app--handverker", "ERA for faghandel": "pw-app--faghandel"}


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


class H:
    """Helpers namespace handed to tools/content_<slug>.py: render(H, a).

    Every builder returns an HTML string composed from the product.css vocabulary (.pw-*). All text
    arguments are escaped with H.esc(); only parameters whose name ends with _html accept pre-built
    HTML (nest builders by passing their output there). Headings inside modules: H.section() emits
    the h2, cards/widgets emit h3, never h1. Reuse the example data verbatim (Borgveien 14 etc.) and
    let H.window() carry the «Eksempeldata» chip.

    Constants
      H.esc(text), H.rel(href)            escape · ' rel="noopener"' for http(s) links, else ''
      H.dash(...), H.detail_card(...)     the legacy scene views (pages.css .dash / .card)
      H.TAG_LABELS                        kind -> label (doc, ai, customer, check, order, board, pro,
                                          resident, illustration, pilot, planned, beta, dev, now)
      H.STATUS                            beta «Kontrollert beta», pilot «I pilot», dev «Under utvikling»,
                                          planned «Planlagt», now «Tilgjengelig nå»,
                                          illustration «Illustrasjon av arbeidsflyt»
      H.PILOT                             owner / board / pro registration URLs (never for faghandel)
      H.TAG_KINDS                         every kind product.css styles (TAG_LABELS + ok, warn, wait)

    Window
      H.window(app, ctx, body_html=None, tabs=None, compact=False, dark_shadow=False, foot=None,
               uid=None, side=False, numbered=False, equalize=True, chips=("Eksempeldata",), dense=False)
        -> <div class="pw"> with .pw-bar (era. mark, .pw-app chip = app, .pw-ctx = ctx in mono,
           right-aligned .pw-chip per chips entry). tabs=[(id, label, panel_html), ...] renders a
           role=tablist .pw-tabs (ids are namespaced: «{uid}-{id}-tab» / «{uid}-{id}», uid defaults
           to pw1, pw2 … per page) and a <div class="pw-panels" data-equalize> holding the
           role=tabpanel .pw-panel elements (first selected, the rest hidden; pages.js wires
           keyboard, roving tabindex and equal height ≥900px). side=True puts the tablist in the
           180px sidebar (.pw-layout + .pw-tabs--side, ≥900px). numbered=True prefixes 01, 02 …
           dense=True (implies numbered) is for many tabs: ≤560px only the numbers stay visible and
           every panel opens with a .pw-panel-step line naming the step. Without tabs: a plain
           .pw-body with body_html. foot -> .pw-foot text.

    Tiles and rows (inside a panel)
      H.kpis([(label, value), (label, value, sub), (label, value, sub, variant), ...])
        -> .pw-kpis of .pw-kpi; variant in mono | accent | warn | good; sub may be None
      H.kpi(label, value, sub=None, variant=None) -> one bare full-width .pw-kpi (a single stat in a widget)
      H.rows([(k, v), (k, v, tag_kind), (k, v, tag_kind, tag_label), ...], group_tag=None, group_label=None)
        -> .pw-rows of .pw-row (tag appended to the value); with group_tag -> .pw-group led by that tag
           (ai -> .pw-group--ai; illustration/pilot/planned/dev/check -> .pw-group--muted)
      H.status_rows([(k, v), (k, v, variant), ...])   variant now | later | None -> .pw-status-list
      H.checklist(items, variant='')   items: str or (text, tag_kind) or (text, tag_kind, tag_label)
                                       variant '' | x | dot | muted -> .pw-list
      H.flow(steps, active=None, dark=False, arrows=True)   active: index, label or a list of either
                                       -> .pw-flow chips joined by → (arrows=False for plain choices)
      H.cols([(head, rows), ...])      head: a tag kind (-> .pw-tag) or a plain title (-> .pw-widget-title)
                                       -> .pw-cols of .pw-col with stacked rows; H.col(head, rows) for one
      H.table(headers, rows, num_cols=(), chosen=())   -> .pw-table.pw-table--stack (td carries data-l;
                                       stacks ≤560px viewport or inside a container ≤480px wide);
                                       num_cols / chosen are column / row indices
      H.timeline([(y, t), (y, t, d), (y, t, d, state), (y, t, d, state, tag_kind), ...] or dicts with
                 keys y t d state tag)   state done | next | later -> ol.pw-timeline
      H.msg(text, meta, out=False), H.msgs([(text, meta), (text, meta, out), ...]) -> .pw-msg(s)
      H.widget(title, inner_html, wide=False, tag=None, tag_label=None, cls=None) -> .pw-widget
                                       (tag -> .pw-widget-head with the tag beside the title; cls adds
                                       classes such as pw-desk / pw-mob); H.grid(widgets_html) -> .pw-grid;
      H.dashboard(widgets_html) -> .pw-dashboard (dense grid; wide widgets span two columns ≥520px)
      H.ring(score, label=None) -> .pw-ring (SVG arc = score/100); H.ring_row(score, inner_html)
      H.progress(pct, variant=None)   variant good | warn -> .pw-progress
      H.note(text) -> <p class="pw-note"> (small muted footnote inside a panel or widget)
      H.panel_lead(text) -> <p class="pw-panel-lead"> (the step's one sentence at the top of a panel)
      H.foot(text) -> .pw-foot; H.where(text, dark=False) -> .pw-where chip
      H.tag(kind, label=None) -> <span class="pw-tag pw-tag--kind">; label defaults to TAG_LABELS/STATUS

    Page-level blocks (outside the window)
      H.section(inner_html, id=None, alt=False, dark=False, wide=False, narrow=False, eyebrow=None,
                title=None, lede=None, cls=None)
        -> <section class="section [alt|dark] [cls]" id=…><div class="wrap [wide|narrow]">
           <div class="label">eyebrow</div><h2>title</h2><p class="steps-intro">lede</p>inner</div></section>
      H.groups([(title, lead, items), (title, lead, items, tag_kind), ...]) -> .pw-groups of .pw-group-card
                                       (items as in checklist; max 6 per group)
      H.compare(left_title, left_items, right_title, right_items) -> .pw-compare (right column navy)
      H.results([(title, mechanism), (title, mechanism, tag_kind), (title, mechanism, tag_kind, label), ...],
                cols=None)              -> .pw-results (first tile navy); cols=3 caps at three columns
      H.roles([(role, gets), ...], cols=None) -> .pw-roles; cols=3 caps at three columns
      H.saves(x_items, fromto_items, x_title='Det du slipper', fromto_title='Det du får') -> .pw-saves
      H.legend(kinds, note=None)      kinds: kind or (kind, note) or (kind, note, label) -> .pw-legend
      H.scenario(title, text, cols, tag=None)   cols as in H.cols -> .pw-scenario
      H.chain([(who, what), (who, what, tag_kind), (who, what, tag_kind, end_bool), ...]) -> .pw-chain
      H.cta(label, href, variant=None)   variant gold | ghost -> a.pw-cta; H.cta_row(ctas_html)
      H.card(title, tag_kind, promise, value, inner_html, cta_label=None, cta_href=None, tile=False)
        -> .pw-card; H.cards(cards_html) -> .pw-cards
      H.arch(surfaces, model, services, light=False)   surfaces [(name, role), (name, role, tag_kind)];
                                       model (title, text); services [str] -> .pw-arch
    """
    esc = staticmethod(esc)
    rel = staticmethod(rel)
    dash = staticmethod(dash)
    detail_card = staticmethod(detail_card)
    TAG_LABELS = TAG_LABELS
    STATUS = STATUS
    PILOT = PILOT
    TAG_KINDS = TAG_KINDS
    _n = 0

    @classmethod
    def reset(cls):
        cls._n = 0

    @staticmethod
    def tag(kind, label=None):
        text = label or TAG_LABELS.get(kind) or STATUS.get(kind) or kind
        return f'<span class="pw-tag pw-tag--{esc(kind)}">{esc(text)}</span>'

    # ---- window ----
    @classmethod
    def window(cls, app, ctx, body_html=None, tabs=None, compact=False, dark_shadow=False, foot=None,
               uid=None, side=False, numbered=False, equalize=True, chips=("Eksempeldata",), dense=False):
        cls._n += 1
        uid = uid or f"pw{cls._n}"
        numbered = numbered or dense
        app_cls = APP_CLASS.get(app, "")
        app_html = f'<span class="pw-app{(" " + app_cls) if app_cls else ""}">{esc(app)}</span>'
        ctx_html = f'<span class="pw-ctx">{esc(ctx)}</span>' if ctx else ""
        chips_html = "".join(f'<span class="pw-chip">{esc(c)}</span>' for c in (chips or ()))
        bar = (f'<div class="pw-bar"><span class="pw-brand">era<span>.</span></span>{app_html}{ctx_html}'
               f'<span class="pw-bar-right">{chips_html}</span></div>')
        classes = "pw" + (" pw--compact" if compact else "") + (" pw--dark-shadow" if dark_shadow else "")
        if tabs:
            btns, panels = [], []
            for i, (tid, label, panel_html) in enumerate(tabs):
                t_id, p_id = f"{uid}-{tid}-tab", f"{uid}-{tid}"
                n = f'<span class="n">{i + 1:02d}</span>' if numbered else ""
                sel = "true" if i == 0 else "false"
                btns.append(f'<button type="button" class="pw-tab" role="tab" id="{t_id}" aria-selected="{sel}" '
                            f'aria-controls="{p_id}" tabindex="{0 if i == 0 else -1}">{n}<span class="t">{esc(label)}</span></button>')
                hidden = "" if i == 0 else " hidden"
                step = f'<div class="pw-panel-step">{n}{esc(label)}</div>' if dense else ""
                panels.append(f'<div class="pw-panel" role="tabpanel" id="{p_id}" aria-labelledby="{t_id}"{hidden}>{step}{panel_html}</div>')
            tab_cls = "pw-tabs" + (" pw-tabs--side" if side else "") + (" pw-tabs--dense" if dense else "")
            tablist = f'<div class="{tab_cls}" role="tablist" aria-label="{esc(app)}">{"".join(btns)}</div>'
            panels_html = f'<div class="pw-panels"{" data-equalize" if equalize else ""}>{"".join(panels)}</div>'
            inner = f'<div class="pw-layout">{tablist}{panels_html}</div>' if side else tablist + panels_html
        else:
            inner = f'<div class="pw-body">{body_html or ""}</div>'
        foot_html = f'<div class="pw-foot">{esc(foot)}</div>' if foot else ""
        return f'<div class="{classes}">{bar}{inner}{foot_html}</div>'

    # ---- tiles and rows ----
    @staticmethod
    def kpi(label, value, sub=None, variant=None):
        """One bare .pw-kpi: full width inside a widget (H.kpis would put it in the 2-column grid ≤560px)."""
        klass = "pw-kpi" + (f" pw-kpi--{variant}" if variant else "")
        sub_html = f'<small>{esc(sub)}</small>' if sub else ""
        return f'<div class="{klass}"><span>{esc(label)}</span><b>{esc(value)}</b>{sub_html}</div>'

    @classmethod
    def kpis(cls, items):
        out = []
        for it in items:
            label, value = it[0], it[1]
            sub = it[2] if len(it) > 2 else None
            variant = it[3] if len(it) > 3 else None
            out.append(cls.kpi(label, value, sub, variant))
        return f'<div class="pw-kpis">{"".join(out)}</div>'

    @classmethod
    def _row(cls, it):
        k, v = it[0], it[1]
        t = ""
        if len(it) > 2 and it[2]:
            t = cls.tag(it[2], it[3] if len(it) > 3 else None)
        return f'<div class="pw-row"><span>{esc(k)}</span><b>{esc(v)}{t}</b></div>'

    @classmethod
    def rows(cls, items, group_tag=None, group_label=None):
        body = "".join(cls._row(it) for it in items)
        if group_tag:
            variant = " pw-group--ai" if group_tag == "ai" else (" pw-group--muted" if group_tag in MUTED_GROUP_KINDS else "")
            return f'<div class="pw-group{variant}">{cls.tag(group_tag, group_label)}{body}</div>'
        return f'<div class="pw-rows">{body}</div>'

    @staticmethod
    def status_rows(items):
        out = []
        for it in items:
            k, v = it[0], it[1]
            variant = it[2] if len(it) > 2 else None
            klass = "pw-status" + (f" pw-status--{variant}" if variant else "")
            out.append(f'<div class="{klass}"><span class="k">{esc(k)}</span><span class="v">{esc(v)}</span></div>')
        return f'<div class="pw-status-list">{"".join(out)}</div>'

    @classmethod
    def _li(cls, it):
        if isinstance(it, str):
            return f"<li>{esc(it)}</li>"
        text = it[0]
        kind = it[1] if len(it) > 1 else None
        label = it[2] if len(it) > 2 else None
        tag = (" " + cls.tag(kind, label)) if kind else ""
        return f"<li>{esc(text)}{tag}</li>"

    @classmethod
    def checklist(cls, items, variant=""):
        klass = "pw-list" + (f" pw-list--{variant}" if variant else "")
        return f'<ul class="{klass}">{"".join(cls._li(it) for it in items)}</ul>'

    @staticmethod
    def flow(steps, active=None, dark=False, arrows=True):
        act = active if isinstance(active, (list, tuple, set)) else ([active] if active is not None else [])
        parts = []
        for i, s in enumerate(steps):
            is_active = (i in act) or (s in act)
            if i and arrows:
                parts.append('<span class="pw-flow-arr">→</span>')
            parts.append(f'<span class="pw-flow-step{" is-active" if is_active else ""}">{esc(s)}</span>')
        return f'<div class="pw-flow{" pw-flow--dark" if dark else ""}">{"".join(parts)}</div>'

    @classmethod
    def col(cls, head, rows_items, head_label=None):
        head_html = cls.tag(head, head_label) if head in TAG_KINDS else f'<div class="pw-widget-title">{esc(head)}</div>'
        return f'<div class="pw-col">{head_html}<div class="pw-rows">{"".join(cls._row(it) for it in rows_items)}</div></div>'

    @classmethod
    def cols(cls, items):
        return '<div class="pw-cols">' + "".join(cls.col(*it) for it in items) + '</div>'

    @staticmethod
    def table(headers, rows, num_cols=(), chosen=()):
        ths = []
        for i, h in enumerate(headers):
            num = ' class="num"' if i in num_cols else ""
            ths.append(f'<th{num}>{esc(h)}</th>')
        trs = []
        for r_i, r in enumerate(rows):
            tds = []
            for i, c in enumerate(r):
                num = ' class="num"' if i in num_cols else ""
                tds.append(f'<td data-l="{esc(headers[i])}"{num}>{esc(c)}</td>')
            klass = ' class="is-chosen"' if r_i in chosen else ""
            trs.append(f'<tr{klass}>{"".join(tds)}</tr>')
        return f'<table class="pw-table pw-table--stack"><thead><tr>{"".join(ths)}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

    @classmethod
    def timeline(cls, items):
        lis = []
        for it in items:
            if isinstance(it, dict):
                y, t, d, state, kind = it.get("y", ""), it["t"], it.get("d"), it.get("state"), it.get("tag")
            else:
                y, t = it[0], it[1]
                d = it[2] if len(it) > 2 else None
                state = it[3] if len(it) > 3 else None
                kind = it[4] if len(it) > 4 else None
            klass = "pw-tl" + (f" is-{state}" if state else "")
            tag = (" " + cls.tag(kind)) if kind else ""
            d_html = f'<span class="d">{esc(d)}</span>' if d else ""
            lis.append(f'<li class="{klass}"><span class="y">{esc(y)}</span><span class="t">{esc(t)}{tag}</span>{d_html}</li>')
        return f'<ol class="pw-timeline">{"".join(lis)}</ol>'

    @staticmethod
    def msg(text, meta, out=False):
        return f'<div class="pw-msg{" pw-msg--out" if out else ""}"><div class="pw-msg-meta">{esc(meta)}</div>{esc(text)}</div>'

    @classmethod
    def msgs(cls, items):
        return '<div class="pw-msgs">' + "".join(cls.msg(*it) for it in items) + '</div>'

    @staticmethod
    def widget(title, inner_html, wide=False, tag=None, tag_label=None, cls=None):
        """A white tile. tag puts a status/source tag beside the title (.pw-widget-head); cls adds
        classes such as pw-desk / pw-mob for width-specific variants."""
        title_html = f'<div class="pw-widget-title">{esc(title)}</div>' if title else ""
        if tag:
            title_html = f'<div class="pw-widget-head">{title_html}{H.tag(tag, tag_label)}</div>'
        klass = "pw-widget" + (" pw-widget--wide" if wide else "") + (f" {cls}" if cls else "")
        return f'<div class="{klass}">{title_html}{inner_html}</div>'

    @staticmethod
    def grid(widgets_html):
        return f'<div class="pw-grid">{"".join(widgets_html)}</div>'

    @staticmethod
    def dashboard(widgets_html):
        return f'<div class="pw-dashboard">{"".join(widgets_html)}</div>'

    @staticmethod
    def ring(score, label=None):
        score = max(0, min(100, int(score)))
        arc = round(score / 100 * 150.8, 1)
        rest = round(150.8 - arc, 1)
        lbl = f' aria-label="{esc(label)}"' if label else ' aria-hidden="true"'
        return (f'<div class="pw-ring"><svg viewBox="0 0 56 56"{lbl}>'
                '<circle cx="28" cy="28" r="24" fill="none" stroke="#EFEAE0" stroke-width="6"/>'
                f'<circle cx="28" cy="28" r="24" fill="none" stroke="#B0935F" stroke-width="6" stroke-linecap="round" stroke-dasharray="{arc} {rest}" transform="rotate(-90 28 28)"/>'
                f'</svg><b>{score}</b></div>')

    @classmethod
    def ring_row(cls, score, inner_html, label=None):
        return f'<div class="pw-ring-row">{cls.ring(score, label)}<div>{inner_html}</div></div>'

    @staticmethod
    def progress(pct, variant=None):
        pct = max(0, min(100, int(pct)))
        return f'<div class="pw-progress{(" pw-progress--" + variant) if variant else ""}"><i style="width: {pct}%"></i></div>'

    @staticmethod
    def note(text):
        return f'<p class="pw-note">{esc(text)}</p>'

    @staticmethod
    def panel_lead(text):
        return f'<p class="pw-panel-lead">{esc(text)}</p>'

    @staticmethod
    def foot(text):
        return f'<div class="pw-foot">{esc(text)}</div>'

    @staticmethod
    def where(text, dark=False):
        return f'<span class="pw-where{" pw-where--dark" if dark else ""}">{esc(text)}</span>'

    # ---- page-level blocks ----
    @staticmethod
    def section(inner_html, id=None, alt=False, dark=False, wide=False, narrow=False, eyebrow=None, title=None, lede=None, cls=None):
        klass = "section" + (" alt" if alt else "") + (" dark" if dark else "") + (f" {cls}" if cls else "")
        wrap = "wrap" + (" wide" if wide else "") + (" narrow" if narrow else "")
        id_attr = f' id="{esc(id)}"' if id else ""
        head = ""
        if eyebrow:
            head += f'<div class="label">{esc(eyebrow)}</div>'
        if title:
            head += f'<h2>{esc(title)}</h2>'
        if lede:
            head += f'<p class="steps-intro">{esc(lede)}</p>'
        return f'<section class="{klass}"{id_attr}><div class="{wrap}">{head}{inner_html}</div></section>'

    @classmethod
    def groups(cls, items):
        cards = []
        for it in items:
            title, lead, lis = it[0], it[1], it[2]
            kind = it[3] if len(it) > 3 else None
            tag = cls.tag(kind) if kind else ""
            lead_html = f'<p class="pw-lead">{esc(lead)}</p>' if lead else ""
            cards.append(f'<div class="pw-group-card">{tag}<h3>{esc(title)}</h3>{lead_html}{cls.checklist(lis)}</div>')
        return f'<div class="pw-groups">{"".join(cards)}</div>'

    @classmethod
    def compare(cls, left_title, left_items, right_title, right_items):
        return ('<div class="pw-compare">'
                f'<div class="pw-compare-col"><div class="pw-compare-head">{esc(left_title)}</div>{cls.checklist(left_items, "x")}</div>'
                f'<div class="pw-compare-col pw-compare-col--era"><div class="pw-compare-head">{esc(right_title)}</div>{cls.checklist(right_items)}</div>'
                '</div>')

    @classmethod
    def results(cls, items, cols=None):
        out = []
        for it in items:
            title, mech = it[0], it[1]
            kind = it[2] if len(it) > 2 else None
            label = it[3] if len(it) > 3 else None
            tag = (" " + cls.tag(kind, label)) if kind else ""
            out.append(f'<div class="pw-result"><h3>{esc(title)}</h3><p>{esc(mech)}{tag}</p></div>')
        klass = "pw-results" + (f" pw-results--{int(cols)}" if cols else "")
        return f'<div class="{klass}">{"".join(out)}</div>'

    @staticmethod
    def roles(items, cols=None):
        klass = "pw-roles" + (f" pw-roles--{int(cols)}" if cols else "")
        return f'<div class="{klass}">' + "".join(f'<div class="pw-role"><b>{esc(r)}</b><span>{esc(g)}</span></div>' for r, g in items) + '</div>'

    @classmethod
    def saves(cls, x_items, fromto_items, x_title="Det du slipper", fromto_title="Det du får"):
        fromto = "".join(f"<li>{esc(t)}</li>" for t in fromto_items)
        return ('<div class="pw-saves">'
                f'<div class="pw-saves-col"><h3>{esc(x_title)}</h3>{cls.checklist(x_items, "x")}</div>'
                f'<div class="pw-saves-col"><h3>{esc(fromto_title)}</h3><ul class="pw-fromto">{fromto}</ul></div>'
                '</div>')

    @classmethod
    def legend(cls, kinds, note=None):
        parts = []
        for it in kinds:
            if isinstance(it, str):
                parts.append(f'<span class="pw-legend-item">{cls.tag(it)}</span>')
            else:
                kind = it[0]
                n = it[1] if len(it) > 1 else None
                label = it[2] if len(it) > 2 else None
                n_html = f'<span class="note">{esc(n)}</span>' if n else ""
                parts.append(f'<span class="pw-legend-item">{cls.tag(kind, label)}{n_html}</span>')
        if note:
            parts.append(f'<span class="note">{esc(note)}</span>')
        return f'<div class="pw-legend">{"".join(parts)}</div>'

    @classmethod
    def scenario(cls, title, text, cols, tag=None):
        tag_html = cls.tag(tag) if tag else ""
        grid = ('<div class="pw-scenario-grid">' + "".join(cls.col(*it) for it in cols) + '</div>') if cols else ""
        return f'<div class="pw-scenario">{tag_html}<h3>{esc(title)}</h3><p>{esc(text)}</p>{grid}</div>'

    @classmethod
    def chain(cls, steps):
        out = []
        for it in steps:
            who, what = it[0], it[1]
            kind = it[2] if len(it) > 2 else None
            end = it[3] if len(it) > 3 else False
            tag = cls.tag(kind) if kind else ""
            out.append(f'<div class="pw-chain-step{" pw-chain-step--end" if end else ""}"><div class="who">{esc(who)}</div><div class="what">{esc(what)}</div>{tag}</div>')
        return f'<div class="pw-chain">{"".join(out)}</div>'

    @staticmethod
    def cta(label, href, variant=None):
        klass = "pw-cta" + (f" pw-cta--{variant}" if variant else "")
        return f'<a class="{klass}" href="{esc(href)}"{rel(href)}>{esc(label)}</a>'

    @staticmethod
    def cta_row(ctas_html):
        return f'<div class="pw-cta-row">{"".join(ctas_html)}</div>'

    @classmethod
    def card(cls, title, tag_kind, promise, value, inner_html, cta_label=None, cta_href=None, tile=False):
        tag = cls.tag(tag_kind) if tag_kind else ""
        cta = cls.cta(cta_label, cta_href) if cta_label and cta_href else ""
        promise_html = f'<p class="pw-promise">{esc(promise)}</p>' if promise else ""
        value_html = f'<p class="pw-value">{esc(value)}</p>' if value else ""
        return (f'<div class="pw-card{" pw-card--tile" if tile else ""}"><div class="pw-card-head"><h3>{esc(title)}</h3>{tag}</div>'
                f'{promise_html}{value_html}{inner_html or ""}{cta}</div>')

    @staticmethod
    def cards(cards_html):
        return f'<div class="pw-cards">{"".join(cards_html)}</div>'

    @classmethod
    def arch(cls, surfaces, model, services, light=False):
        s_html = []
        for it in surfaces:
            name, role = it[0], it[1]
            kind = it[2] if len(it) > 2 else None
            tag = cls.tag(kind) if kind else ""
            s_html.append(f'<div class="pw-arch-surface"><div class="name">{esc(name)}</div><div class="role">{esc(role)}</div>{tag}</div>')
        m_t, m_d = model
        svc = "".join(f"<span>{esc(s)}</span>" for s in services)
        return (f'<div class="pw-arch{" pw-arch--light" if light else ""}"><div class="pw-arch-surfaces">{"".join(s_html)}</div>'
                f'<div class="pw-arch-model"><div class="t">{esc(m_t)}</div><div class="d">{esc(m_d)}</div></div>'
                f'<div class="pw-arch-services">{svc}</div></div>')


PRIVACY_LINE = "Ingen binding. Dataene lagres kryptert innenfor EU/EØS og brukes bare til å følge opp henvendelsen."


AUDIENCES = {
    "boligeier": dict(
        key="owner", nav="Boligeier", title="ERA for boligeiere",
        label="For boligeier", hook="Boligeierskap uten gjetting.",
        lede="ERA forstår hva boligen din trenger, og hva som bør gjøres først. Tilstand, historikk, dokumentasjon og prioriteringer, samlet i én plan for hjemmet.",
        image="/assets/story/couple-sofa-window-v4.jpg", image_alt="Et par i sofaen ved vinduet i sin egen stue", image_pos="45% 50%",
        cta_primary=("Start som boligeier", PILOT["owner"]),
        cta_secondary=("Se produktet i bruk", "#produktet"),
        nav_cta=("Start som boligeier", PILOT["owner"]),
        product_module="content_boligeier",
        scenes_id="slik",
        scenes=dict(
            eyebrow="Fra behov til plan", title="Fra «vi vil male stua» til en plan du kan bestille etter.",
            lede="Følg boligens vei fra det som ligger i skuffen til en klar plan, med samme eksempel gjennom alle stegene.",
            items=[
                dict(nav="Kartlegging", heading="Boligen kartlegges.",
                     text="Tilstandsrapport, FDV, kvitteringer og bilder samles på ett sted, det du har liggende i skuffen, på e-post og på telefonen.",
                     value="Utgangspunktet er det du allerede har, ikke en ny rapport du må bestille.",
                     view=dash("Boligminne", "Borgveien 14",
                               kpis=[("Tilstandsrapport", "2021"), ("FDV", "3 dokumenter"), ("Kvitteringer", "12 lagt inn"), ("Bilder", "24 lagt inn")],
                               footer="Eksempeldata. Jo mer du legger inn, jo mer presis blir planen.")),
                dict(nav="Forståelse", heading="ERA forstår.",
                     text="Hver del av boligen får tilstand, alder og neste forventede behov, ikke bare det du ser, men det bak veggen også.",
                     value="Vurderingen bygger på det som er dokumentert, ikke gjetning.",
                     view=dash("Boligens tilstand", "Basert på boligminnet",
                               groups=[("doc", [("Stue", "Vegg slitt, ingen skader")]),
                                       ("ai", [("Neste forventede behov", "Overflatebehandling innen 12 mnd")])],
                               footer="Eksempeldata. ERA-forslaget er et utgangspunkt du vurderer.")),
                dict(nav="Plan", heading="Du får en plan.",
                     text="Hva som haster, hva som kan vente, og hva det koster. «Vi vil male stua» blir veggflate, forarbeid, strøk, tid og pris.",
                     value="Det samme gjelder bad, gulv, elektro, rør og tak, og ERA sier fra når jobben krever fagperson.",
                     view=dash("Plan · Male stua", "Borgveien 14",
                               kpis=[("Vegg", "42 m²"), ("Forbehandling", "Lett sparkling"), ("Strøk", "2"), ("Estimert kostnad", "ca. 6 800 kr")],
                               footer="Eksempeldata. Fra «vi vil male stua» til en plan du kan bestille etter, på minutter.")),
                dict(nav="Veivalg", heading="Gjør det selv, eller få hjelp.",
                     text="Materialene er beregnet og kan bestilles. Eller jobben går til håndverker, ferdig beskrevet.",
                     value="Alt blir historikk i boligen, uansett hvilken vei du velger.",
                     view=dash("Veivalg", "Male stue · 42 m²",
                               cols=[("order", [("Gjør det selv", "Materialer beregnet, klar for bestilling")]),
                                     ("pro", [("Få hjelp", "Jobb ferdig beskrevet til håndverker")])],
                               footer="Eksempeldata. Uansett vei blir jobben historikk i boligen.")),
            ],
        ),
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
            ("Hva skjer når jeg trykker «Start som boligeier»?", "Du kommer til registreringen i ERA-piloten på pilot.era-app.no. Der oppretter du boligprofilen din. Registreringen er gratis i betaperioden."),
        ],
        beta=dict(
            badge="Nå i kontrollert beta — åpnes for 300 boligeiere",
            note="Gratis for boligeiere i betaperioden. Begrenset antall plasser.",
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
            fine="Ingen betalingskort. Ingen binding. Begrenset antall plasser i betaperioden.",
        ),
        closing=dict(
            id="start",
            heading="Start som boligeier.",
            lede="ERA Bolig er åpen i kontrollert beta for 300 boligeiere. Gratis i betaperioden, uten betalingskort og uten binding.",
            primary=("Start som boligeier", PILOT["owner"]),
            form=False,
            fine="Du registrerer deg i ERA-piloten på pilot.era-app.no.",
            links=[("Les om personvern", "/personvern")],
        ),
    ),
    "styret": dict(
        key="board", nav="Styret", title="ERA for borettslag og sameier",
        label="For styret", hook="Fra vedlikeholdsbehov til ferdig jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler styret, boligeierne og håndverkerne rundt samme eiendom. Få hjelp til å forstå behovene, prioritere tiltak og følge arbeidet helt frem til dokumentert resultat.",
        hero_support="Styret skifter. Planen består.",
        image="/assets/story/block-bikes-v3.jpg", image_alt="Sykler utenfor en boligblokk i et borettslag", image_pos="50% 50%",
        cta_primary=("Registrer borettslag eller sameie", PILOT["board"]),
        cta_secondary=("Book en gjennomgang", "#skjema"),
        nav_cta=("Registrer eiendom", PILOT["board"]),
        product_module="content_styret",
        scenes_id="slik",
        scenes=dict(
            eyebrow="Fra behov til ferdig jobb", title="Én eiendom. Én sammenhengende vedlikeholdsflyt.",
            lede="Følg det samme fasadebehovet fra første funn til gjennomført og dokumentert arbeid. Beboerne er med hele veien: hver boligeier får egen boligoversikt, vedlikeholdsplan og påminnelser gjennom ERA Bolig.",
            items=[
                dict(nav="Oversikt", heading="Hva trenger bygget deres nå?",
                     text="Rapporter, tidligere arbeid og innmeldte behov gir styret ett samlet utgangspunkt.",
                     value="ERA skiller dokumenterte funn fra forslag som styret må vurdere.",
                     view=dash("Eiendomsoversikt", "Samlet utgangspunkt for styret",
                               kpis=[("Eiendom", "Borgveien 14"), ("Seksjoner", "24"), ("Område", "Fasade"), ("Sist utført", "Malt 2012")],
                               groups=[("doc", [("Tilstandsrapport 2021", "Maling flasser på sør- og vestvegg"), ("Innmeldt behov", "Avskalling ved inngang B")]),
                                       ("ai", [("Forslag", "Befaring innen 12 måneder")])],
                               footer="Eksempeldata. ERA-forslag vurderes og besluttes av styret.")),
                dict(nav="Prioritering", heading="Fra rapport til neste steg.",
                     text="Det dokumenterte behovet omformes til et konkret tiltak i vedlikeholdsplanen.",
                     value="Styret ser hvorfor tiltaket foreslås, når det bør vurderes og hvilket grunnlag det bygger på.",
                     view=dash("Vedlikeholdsplan", "Forslag fra ERA, til styrets vurdering",
                               kpis=[("Foreslått tiltak", "Male sør- og vestvegg"), ("Anbefalt år", "2027"), ("Kostnadsintervall", "1,0–1,3 mill"), ("Status", "Til vurdering")],
                               groups=[("doc", [("Funn", "Maling flasser, sør- og vestvegg · rapport 2021"), ("Egen oppgave i totalplanen", "Tak · 2031")]),
                                       ("ai", [("Grunnlag", "Rapport 2021 og innmeldt avskalling"), ("Per seksjon", "ca. 42–54 000 kr")])],
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
            link="Se ERA Bolig →", href="/boligeier",
        ),
        gains=[
            ("Forstå hva bygget trenger", "Eiendommens dokumentasjon og innmeldte behov blir grunnlag for foreslåtte tiltak, prioritering og vedlikeholdsplan."),
            ("Ta tiltakene videre", "Styret vurderer underlaget, beslutter og følger opp arbeidet med håndverkeren."),
            ("Bevar resultatet", "Utført arbeid dokumenteres, beboerne informeres og historikken følger eiendommen videre."),
        ],
        faq=[
            ("Passer ERA for små sameier?", "Ja. Et sameie med fire seksjoner har de samme spørsmålene som ett med førti. Planen skalerer."),
            ("Erstatter ERA forretningsfører?", "Nei. ERA holder orden på bygget, ikke regnskapet. Forretningsføreren kan få tilgang til planen."),
            ("Vi har allerede et styresystem. Hvor passer ERA inn?", "ERA samler oppfølgingen av eiendommen fra vedlikeholdsbehov til gjennomført og dokumentert arbeid. I en gjennomgang ser vi på hvordan dere jobber i dag, og hvor ERA kan bidra i arbeidsflyten deres."),
            ("Hvem eier dataene?", "Eiendommen. Styret bestemmer hvem som ser dem. Ved styreskifte følger alt med."),
        ],
        closing=dict(
            id="skjema",
            heading="Hva er neste tiltak for deres eiendom?",
            lede="Se hvordan ERA kan hjelpe dere fra første vurdering til ferdig dokumentert arbeid, med styret, boligeierne og håndverkeren i samme flyt.",
            primary=("Registrer borettslag eller sameie", PILOT["board"]),
            lead_in="Vil dere heller se ERA Styret sammen med oss først?",
            form=True,
        ),
        intents=[
            ("demo", "Book en gjennomgang", "Takk. Vi tar kontakt for å avtale en gjennomgang.", "Du hører fra oss med forslag til tidspunkt."),
            ("interest", "Meld interesse", "Takk. Vi ser på eiendommen.", "Vi tar kontakt med et forslag til plan, klart til neste møte."),
        ],
        form_field="Adressen til bygget", form_label="Adresse", form_cta="Book en gjennomgang",
        done=("Takk. Vi tar kontakt for å avtale en gjennomgang.", "Du hører fra oss med forslag til tidspunkt."),
    ),
    "handverker": dict(
        key="pro", nav="Håndverker", title="ERA for håndverkere",
        label="For håndverkere", hook="Fra kundens boligbehov til din neste jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler boligeiere, styrer og håndverkere. Ta kundens behov videre til befaring, tilbud og gjennomføring, og la dokumentasjonen følge boligen når jobben er ferdig.",
        hero_support="Du kan faget. ERA hjelper deg med flyten rundt jobben.",
        image="/assets/story/painter-v3.jpg", image_alt="Maler i arbeid med rulle i en stue", image_pos="30% 50%",
        cta_primary=("Start som håndverker", PILOT["pro"]),
        cta_secondary=("Se hvordan en jobb flyter gjennom ERA", "#flyt"),
        nav_cta=("Start som håndverker", PILOT["pro"]),
        product_module="content_handverker",
        scenes_id="prosjekt",
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
                               kpis=[("Omfang", "Vegger, 2 strøk"), ("Forbehandling", "Lett sparkling"), ("Ønsket tid", "Uke 38–40"), ("Kundens estimat", "ca. 6 800 kr")],
                               groups=[("customer", [("Materialer", "Ligger klart i planen")]),
                                       ("ai", [("Kalkyle", "Strukturert fra mål og notater, du justerer")])],
                               footer="Eksempeldata. Tilbudet sendes først når du har godkjent det.")),
                dict(nav="Avtale", heading="Avklart med kunden. Klart for oppstart.",
                     text="Avtalt omfang, materialbehov og prosjektinformasjon holdes samlet, så du og kunden vet hva som skal gjøres.",
                     value="Produkter og mengder kommer fra planen. Kunden velger levering.",
                     view=dash("Arbeidsgrunnlag", "Male stue · godkjent av kunde",
                               kpis=[("Omfang", "Vegger, 2 strøk"), ("Avtalt oppstart", "Uke 38"), ("Materialpris", "ca. 1 900 kr"), ("Status", "Godkjent")],
                               groups=[("ai", [("Produkter fra planen", "2 × maling 10 L, 1 × sparkel 5 kg, 2 ruller")]),
                                       ("order", [("Bestilling", "Én bestilling fra planen, uavhengig av kjede"), ("Levering", "Kjøres hjem, hentes i butikk, eller du henter")]),
                                       ("pilot", [("Betaling i ERA", "Avtalt beløp og betalingsstatus")])],
                               footer="Eksempeldata. Betaling i ERA er i pilot.")),
                dict(nav="Endring", heading="Kunden vil også male taket.",
                     text="Endringen beskrives med pris og konsekvens for fremdriften, og sendes til kunden for godkjenning før ekstraarbeidet starter.",
                     value="Kunden ser alltid forskjellen på foreslått og godkjent.",
                     view=dash("Endringsordre", "Male stue · tillegg til opprinnelig omfang",
                               kpis=[("Opprinnelig omfang", "Vegger, 2 strøk"), ("Foreslått tillegg", "Tak, 1 strøk"), ("Prisendring", "+ ca. 1 800 kr"), ("Status", "Venter godkjenning")],
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
            id="skjema",
            heading="Mer tid til faget. Bedre kontroll på jobben.",
            lede="Se hvordan ERA knytter kundens behov til arbeidsflyten din, fra første henvendelse til ferdig dokumentert oppdrag.",
            primary=("Start som håndverker", PILOT["pro"]),
            lead_in="Vil du heller ta en prat først?",
            form=True,
        ),
        intents=[
            ("interest", "Meld interesse", "Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
            ("demo", "Be om demo", "Takk. Vi tar kontakt for å avtale en demo.", "Du hører fra oss med forslag til tidspunkt."),
        ],
        form_field="Firmanavn eller organisasjonsnummer", form_label="Firma", form_cta="Meld interesse",
        done=("Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
    ),
    "faghandel": dict(
        key="partner", nav="Faghandel", title="ERA for faghandel",
        label="For faghandel", hook="Behovet er beregnet før kunden går i butikken.",
        lede="Riktig produkt, riktig mengde, riktig tid, i én bestilling. Fra boliger og fra hele borettslag. Uavhengig av kjede.",
        image="/assets/story/materials-floor-v3.jpg", image_alt="Malingsspann, ruller og verktøy på gulvet", image_pos="50% 50%",
        cta_primary=("Utforsk partnerskap med ERA", "#skjema"),
        cta_secondary=("Se dashboardet for kjede og forhandler", "#dashboard"),
        nav_cta=("Utforsk partnerskap", "#skjema"),
        product_module="content_faghandel",
        scenes_id="slik",
        scenes=dict(
            # The h2 names the order journey (behov → levering → bestilling → prognose); the hero
            # keeps «Behovet er beregnet før kunden går i butikken.» to itself.
            eyebrow="Fra behov til bestilling", title="Mengden, leveringen og bestillingen. Og det som kommer neste år.",
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
        # No «Gevinsten» section: content_faghandel.py's #verdi carries the same four points.
        gains=[],
        faq=[
            ("Er ERA knyttet til én kjede?", "Nei. ERA kobler behov til partnere uavhengig av kjede. Kunden velger hvor bestillingen går."),
            ("Hvordan får vi bestillingene?", "Vi finner en bestillingsflyt som passer dere. Ta kontakt, så viser vi hvordan."),
            ("Hva med borettslag?", "Styrets vedlikeholdsplan gir store, planlagte bestillinger. Fasade, tak og vinduer, år for år."),
        ],
        closing=dict(
            id="skjema",
            heading="Utforsk partnerskap med ERA.",
            lede="Fortell oss hvilken kjede, produsent eller butikk dere representerer, så viser vi hvordan beregnede behov blir bestillinger hos dere.",
            form=True,
        ),
        intents=[
            ("interest", "Bli partner", "Takk. Vi tar kontakt.", "Vi viser hvordan beregnede behov blir bestillinger hos dere."),
            ("demo", "Be om demo", "Takk. Vi tar kontakt for å avtale en demo.", "Du hører fra oss med forslag til tidspunkt."),
        ],
        form_field="Kjede, produsent eller butikk", form_label="Virksomhet", form_cta="Bli partner",
        done=("Takk. Vi tar kontakt.", "Vi viser hvordan beregnede behov blir bestillinger hos dere."),
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


# Global nav, this order on every page. The first item links to the homepage product section.
MENU = [("/#hva", "Hva ERA gjør"), ("/boligeier", "Boligeier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/om-era", "Om ERA"), ("/personvern", "Personvern")]


def nav_html(current, cta):
    cta_label, cta_href = cta
    cur = ' aria-current="page"'
    links = "".join(f'<a href="{h}"{cur if h == "/" + current else ""}>{esc(l)}</a>' for h, l in MENU if h != "/personvern")
    panel = "".join(f'<a href="{h}" data-menu-close="1">{esc(l)}<span>→</span></a>' for h, l in MENU)
    return f'''<nav class="nav" aria-label="Hovedmeny">
  <div class="pill">
    <a class="brand" href="/">era<span>.</span></a>
    <div class="links">{links}</div>
    <div class="right"><a class="cta" href="{cta_href}"{rel(cta_href)}>{esc(cta_label)}</a><button type="button" class="menu-btn" data-menu-toggle="1" aria-label="Åpne menyen" aria-expanded="false" aria-controls="hovedmeny">☰</button></div>
  </div>
  <div class="menu-panel" id="hovedmeny" hidden>{panel}</div>
</nav>'''


def footer_html():
    return f'''<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/om-era">Om ERA</a><a href="/personvern">Personvern</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA technologies AS</span><span>Oslo</span></div>
</footer>'''


def render_product(a):
    """Imports tools/content_<slug>.py and returns its render(H, a) output ('' when absent)."""
    name = a.get("product_module")
    if not name:
        return ""
    H.reset()
    mod = importlib.import_module(name)
    return mod.render(H, a) or ""


def closing_section(a):
    """Per-page closing: heading, lede, optional primary button, optional lead form (with the page's
    intents), fine print and links. The form is the only place that posts to /api/lead."""
    c = a["closing"]
    cid = c.get("id", "skjema")
    parts = [f'<section class="section dark closing" id="{cid}"><div class="wrap narrow">',
             '<div class="brand big">era<span>.</span></div>',
             f'<h2>{esc(c["heading"])}</h2>',
             f'<p class="lede light">{esc(c["lede"])}</p>']
    if c.get("primary"):
        lbl, href = c["primary"]
        parts.append(f'<a class="btn" href="{href}"{rel(href)}>{esc(lbl)}</a>')
    if c.get("form"):
        intents = a.get("intents") or []
        if c.get("lead_in"):
            parts.append(f'<p class="lead-in">{esc(c["lead_in"])}</p>')
        if intents:
            parts.append('<div class="intent" role="group" aria-label="Hva ønsker du?">' + "".join(
                f'<button type="button" data-intent="{k}" data-label="{esc(lbl)}" aria-pressed="{"true" if i == 0 else "false"}">{esc(lbl)}</button>'
                for i, (k, lbl, _h, _s) in enumerate(intents)
            ) + '</div>')
        intents_attr = (' data-intents="' + esc(json.dumps({k: [h, sub] for k, _l, h, sub in intents}, ensure_ascii=False)) + '"') if intents else ""
        intent_field = f'<input type="hidden" name="intent" value="{intents[0][0]}">' if intents else ""
        done_head, done_sub = a["done"]
        parts.append(f'''<form id="era-lead" class="lead" data-audience="{a["key"]}"{intents_attr}>
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
      <div class="done" role="status" aria-live="polite" tabindex="-1" hidden>
        <div class="check"><svg width="20" height="16" viewBox="0 0 20 16" fill="none"><path d="M2 8L7.5 13.5L18 2" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
        <div><b>{esc(done_head)}</b><span>{esc(done_sub)}</span></div>
      </div>
      <div class="err" role="alert" tabindex="-1" hidden></div>
      <p class="fine">{esc(PRIVACY_LINE)}</p>''')
    if c.get("fine"):
        parts.append(f'<p class="fine">{esc(c["fine"])}</p>')
    if c.get("links"):
        parts.append('<div class="closing-links">' + "".join(f'<a class="link" href="{h}"{rel(h)}>{esc(l)}</a>' for l, h in c["links"]) + '</div>')
    if c.get("note"):
        parts.append(f'<p class="fine">{esc(c["note"])}</p>')
    parts.append('</div></section>')
    return "\n      ".join(parts)


def page(slug, a):
    beta = a.get("beta")
    primary_label, primary_href = a["cta_primary"]
    secondary_label, secondary_href = a["cta_secondary"]
    has_form = bool(a["closing"].get("form"))
    product_html = render_product(a)

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
    scenes_id = a.get("scenes_id", "slik")
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
            elif has_form:
                nxt = f'<a class="scene-next" href="#skjema">{esc(a["form_cta"])}</a>'
            else:
                nxt = f'<a class="scene-next" href="{primary_href}"{rel(primary_href)}>{esc(primary_label)}</a>'
            return f'<div class="scene-nav">{prev}{nxt}</div>'
        panels = "".join(
            f'<div class="scene" role="tabpanel" id="scene-{i+1}" aria-labelledby="tab-{i+1}"{"" if i == 0 else " hidden"}>'
            f'<div class="scene-text"><div class="label">Steg {i+1} · {esc(it["nav"])}</div><h3>{esc(it["heading"])}</h3><p>{esc(it["text"])}</p>'
            f'<p class="scene-value">{esc(it["value"])}</p></div>'
            f'<div class="scene-view">{it["view"]}</div>{scene_nav(i)}</div>'
            for i, it in enumerate(items))
        scenes_section = (
            f'<section class="section scenes" id="{scenes_id}"><div class="wrap wide">'
            f'<div class="label">{esc(sc["eyebrow"])}</div><h2>{esc(sc["title"])}</h2><p class="steps-intro">{esc(sc["lede"])}</p>'
            f'<div class="stepnav" role="tablist" aria-label="{len(items)} steg" style="grid-template-columns: repeat({len(items)}, minmax(0, 1fr))">{tabs}</div>'
            f'<div class="scene-panel">{panels}</div>'
            '</div></section>'
        )
    steps_section = scenes_section or (
        f'<section class="section" id="{scenes_id}">'
        f'<div class="label">{esc(steps_label)}</div><h2>{esc(steps_title)}</h2>{steps_intro}'
        f'<ol class="steps">{steps}</ol></section>'
    )
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
    # «Gevinsten» is skipped when a page's product module already carries its value section (faghandel).
    gains_section = ""
    if a.get("gains"):
        gains = "".join(f'<div class="gain"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in a["gains"])
        gains_section = (
            '<section class="section alt"><div class="wrap">'
            f'<div class="label">Det får {"dere" if a["key"] in ("board", "partner") else "du"}</div>'
            f'<h2>Gevinsten</h2><div class="gains">{gains}</div>'
            '</div></section>'
        )
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
            f'<a class="btn" href="{primary_href}"{rel(primary_href)}>{esc(primary_label)}</a>'
            f'<p class="fine">{esc(beta["fine"])}</p>'
            '</div></section>'
        )
    beta_hero = f'<div class="beta-badge">{esc(beta["badge"])}</div><p class="beta-note">{esc(beta["note"])}</p>' if beta else ''
    hero_support = f'<p class="hero-support">{esc(a["hero_support"])}</p>' if a.get("hero_support") else ''
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
<link rel="stylesheet" href="/product.css">
</head>
<body data-audience="{a["key"]}">
{nav_html(slug, a["nav_cta"])}

<header class="hero">
  <div class="hero-media">{'<img src="' + a["image"] + '" srcset="' + a["image"][:-4] + '-m.jpg 1400w, ' + a["image"] + ' 3000w" sizes="100vw" alt="' + esc(a["image_alt"]) + '" style="object-position: ' + a["image_pos"] + '">'}</div>
  <div class="hero-text">
    <div class="label">{esc(a["label"])}</div>
    <h1>{esc(a["hook"])}</h1>{beta_hero}
    <p class="lede">{esc(a["lede"])}</p>{hero_support}
    <div class="hero-actions"><a class="btn" href="{primary_href}"{rel(primary_href)}>{esc(primary_label)}</a><a class="link" href="{secondary_href}"{rel(secondary_href)}>{esc(secondary_label)}</a></div>
  </div>
</header>

<main>
  {product_html}

  {steps_section}

  {aside_section}

  {roles_section}

  {features_section}

  {beta_section}

  {gains_section}

  {example_section}

  <section class="section alt">
    <div class="wrap narrow">
      <div class="label">Spørsmål</div>
      <h2>Det folk lurer på.</h2>
      <div class="faq">{faq}</div>
    </div>
  </section>

  {closing_section(a)}
</main>

{footer_html()}
<script src="/pages.js" defer></script>
</body>
</html>
'''


PRIVACY_DESC = "Hva ERA lagrer når du bruker skjemaene på denne siden, hvor det lagres, hvor lenge, og hvordan du får det slettet."


def privacy_page():
    """Honest to what the site actually does today: the lead forms (api/lead.js stores value, audience,
    intent, time, page and user agent; no name, e-mail, phone or IP), one private store in the EU, no
    cookies. This is the only page that may name the storage region; every other page says just
    «kryptert innenfor EU/EØS». Sections are (heading, paragraphs[, raw_html_after])."""
    sections = [
        ("Hva vi samler inn", [
            "Når du sender inn skjemaet på forsiden eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede, produsent eller butikk), hvilken målgruppe du leste som (boligeier, styret, håndverker eller faghandel), om du ba om en gjennomgang eller demo, tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
            "Vi samler ikke inn navn, e-post eller telefonnummer gjennom skjemaet i dag, og vi lagrer ikke IP-adressen din.",
        ]),
        ("Hvorfor", [
            "Skjemaet registrerer interesse for en adresse, en eiendom eller en virksomhet. Vi bruker innsendingene til å se hvor interessen er, og til å prioritere hvor ERA åpner først.",
            "Fordi skjemaet ikke inneholder kontaktopplysninger, kan vi bare ta kontakt der det finnes en registrert kontaktvei, for eksempel en virksomhets eller et borettslags registrerte kontaktopplysninger, eller når du selv tar kontakt med oss. Opplysningene brukes ikke til noe annet. Vi selger eller deler ikke opplysningene.",
        ]),
        ("Hvor og hvor lenge", [
            "Opplysningene lagres kryptert hos vår driftsleverandør Vercel, i et privat lager innenfor EU/EØS (Frankfurt). Bare ERA technologies AS har tilgang.",
            "Vi sletter innsendingen senest tolv måneder etter at den kom inn, eller så snart du ber om det.",
        ]),
        ("Registrering i ERA-piloten", [
            "Knappene «Start som boligeier», «Registrer borettslag eller sameie» og «Start som håndverker» fører til pilot.era-app.no. Det er en egen tjeneste med egen registrering; registreringen skjer ikke på denne nettsiden.",
            "Det du legger inn der, omfattes av pilotens egne personvernvilkår, ikke av denne siden.",
        ], "<!-- AVKLAR: lenke til pilotens personvernerklæring -->"),
        ("Informasjonskapsler og analyse", [
            "Siden setter ingen informasjonskapsler. Vi bruker Vercel Web Analytics, som teller sidevisninger uten cookies og uten å identifisere deg. Derfor trenger vi ikke et samtykkebanner.",
        ]),
        ("Dine rettigheter", [
            "Du kan når som helst be om innsyn i, retting av eller sletting av det du har sendt inn. Bruk skjemaet på forsiden eller en av undersidene, skriv «personvern» først i teksten og oppgi hva du sendte inn, så finner vi innsendingen og retter eller sletter den. Fordi skjemaet ikke inneholder kontaktopplysninger, kan vi bare svare der det finnes en registrert kontaktvei. Behandlingsansvarlig er ERA technologies AS, Oslo.",
        ]),
    ]
    body = "".join(
        f'<section class="pv"><h2>{esc(s[0])}</h2>{"".join(f"<p>{esc(p)}</p>" for p in s[1])}{s[2] if len(s) > 2 else ""}</section>'
        for s in sections)
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
<link rel="stylesheet" href="/product.css">
</head>
<body class="light">
{nav_html("personvern", ("Til forsiden", "/"))}
<main class="doc">
  <div class="wrap narrow">
    <div class="label">Personvern</div>
    <h1>Din bolig. Dine data.</h1>
    <p class="lede dark">ERA lagrer boligens historie for deg, ikke om deg. Her står nøyaktig hva denne nettsiden gjør med det du sender inn.</p>
    <p class="fine dark">Sist oppdatert 10. september 2026.</p>
    {body}
  </div>
</main>
{footer_html()}
<script src="/pages.js" defer></script>
</body>
</html>
'''


if __name__ == "__main__":
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
