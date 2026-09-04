# -*- coding: utf-8 -*-
"""Applies ERA's own deltas on top of a fresh Claude Design export (base.html → index.html):
audience pages in the menu/footer, faghandel/håndverker/styret copy, audience-aware finale with
the lead form, deep-link jump, mobile framing for the wall mask, company name.
Usage: python tools/rebase-deltas.py <base.html> <out index.html>"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
missing = []

def rep(a, b, count=1):
    global s
    if a not in s:
        missing.append(a[:100]); return
    s = s.replace(a, b, count)

# ── shared score-gauge helper: an SVG stroke-dasharray for a 0-100 score on a 24px ring,
#    used by the two new "ERA insight" cards below (chapters 3 and 9) ──
rep("  ty(op, d = 20) { return `translateY(${(1 - op) * d}px)`; }\n  mix(a, b, t) { return a + (b - a) * t; }",
    "  ty(op, d = 20) { return `translateY(${(1 - op) * d}px)`; }\n  mix(a, b, t) { return a + (b - a) * t; }\n  ring(score, r = 24) { const c = 2 * Math.PI * r; return { full: c, target: (score / 100) * c }; }")

# ── menu + footer ──
rep("const navItems = [['hva', 'Hva ERA gjør'], ['boligeier', 'Boligeier'], ['styret', 'Styret'], ['handverker', 'Håndverker'], ['partnere', 'Partnere']]\n      .map(([id, label]) => ({ href: '#' + id, label,",
    "// The menu goes straight to the audience pages; only \"Hva ERA gjør\" stays inside the story.\n    const navItems = [['hva', 'Hva ERA gjør', '#hva'], ['boligeier', 'Boligeier', '/boligeier'], ['styret', 'Styret', '/styret'], ['handverker', 'Håndverker', '/handverker'], ['partnere', 'Faghandel', '/faghandel']]\n      .map(([id, label, href]) => ({ href, label,")
rep('<a href="#hva">Hva ERA gjør</a><a href="#boligeier">Boligeier</a><a href="#styret">Styret</a>', '<a href="#hva">Hva ERA gjør</a><a href="/boligeier">Boligeier</a><a href="/styret">Styret</a>')
rep('<a href="#handverker">Håndverker</a><a href="#partnere">Partnere</a><a href="#data">Personvern</a>', '<a href="/handverker">Håndverker</a><a href="/faghandel">Faghandel</a><a href="#data">Personvern</a>')
rep('<span>© 2026 ERA AS</span>', '<span>© 2026 ERA technologies AS</span>')

# ── head: sharing metadata + cookieless analytics ──
rep('<link rel="icon" href="/favicon.svg" type="image/svg+xml">',
    '''<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://era-story.vercel.app/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ERA">
<meta property="og:title" content="ERA — Boligeierskap uten gjetting">
<meta property="og:description" content="Forstå boligen. Prioriter riktig. Gjør det som faktisk trengs. For boligeiere, styrer, håndverkere og faghandel.">
<meta property="og:image" content="https://era-story.vercel.app/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="https://era-story.vercel.app/">
<meta property="og:locale" content="nb_NO">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ERA — Boligeierskap uten gjetting">
<meta name="twitter:description" content="Forstå boligen. Prioriter riktig. Gjør det som faktisk trengs.">
<meta name="twitter:image" content="https://era-story.vercel.app/og.jpg">
<script defer src="/_vercel/insights/script.js"></script>''')

# ── mobile menu: a button in the pill, a panel under it (designer hides the links < 820 px) ──
rep('''      <a href="#start" style="display: inline-flex; align-items: center; height: 44px; padding: 0 18px; border-radius: 999px; background: {{ navCtaBg }}; color: {{ navCtaFg }}; font-weight: 600; font-size: 14.5px; transition: background 0.5s, color 0.5s; white-space: nowrap">{{ navCtaLabel }}</a>
    </div>
  </nav>''',
    '''      <div style="display: flex; align-items: center; gap: 6px">
        <a href="#start" style="display: inline-flex; align-items: center; height: 44px; padding: 0 18px; border-radius: 999px; background: {{ navCtaBg }}; color: {{ navCtaFg }}; font-weight: 600; font-size: 14.5px; transition: background 0.5s, color 0.5s; white-space: nowrap">{{ navCtaLabel }}</a>
        <button type="button" data-menu-toggle="1" aria-label="{{ navMenuAria }}" aria-expanded="{{ navMenuExpanded }}" style="display: {{ navMenuBtnDisplay }}; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 999px; border: 1px solid {{ navBorder }}; background: transparent; color: inherit; font: inherit; font-size: 20px; line-height: 1; cursor: pointer">{{ navMenuIcon }}</button>
      </div>
    </div>
    <div style="pointer-events: auto; position: absolute; top: 72px; left: 16px; right: 16px; display: {{ navMenuDisplay }}; flex-direction: column; padding: 10px; border-radius: 22px; background: {{ navMenuBg }}; color: {{ navMenuFg }}; border: 1px solid {{ navBorder }}; box-shadow: 0 20px 60px rgba(15,24,48,0.35); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px)">
      <sc-for list="{{ navMenuItems }}" as="mi" hint-placeholder-count="6">
        <a href="{{ mi.href }}" data-menu-close="1" style="display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-radius: 14px; color: inherit; font-size: 17px; font-weight: 600">{{ mi.label }}<span style="color: #D4B17A">→</span></a>
      </sc-for>
    </div>
  </nav>''')

# ── privacy: the story's claim must match where leads actually live, and link to the page ──
rep('>Lagret kryptert i Norge, i tråd med GDPR.</p>', '>Lagret kryptert innenfor EU/EØS, i tråd med GDPR.</p>')
rep('<a href="#data" style="display: inline-flex; align-items: center; gap: 6px; margin-top: 22px; font-size: 15px; font-weight: 600">Les om personvern →</a>', '<a href="/personvern" style="display: inline-flex; align-items: center; gap: 6px; margin-top: 22px; font-size: 15px; font-weight: 600">Les om personvern →</a>')
rep('<a href="#data">Personvern</a>', '<a href="/personvern">Personvern</a>')

# ── chapter 1: we walk through the home — the living room with the couple first, then the
#    older bathroom fades in exactly when «Men hva med badet?» is asked. The answer waits until chapter 9. ──
rep('''        <image-slot id="shot-couple-wide" shape="rect" src="/assets/story/bathroom-v2.jpg" placeholder="Shot 2 · Paret i leiligheten"></image-slot>
      </div>''',
    '''        <image-slot id="shot-couple-wide" shape="rect" src="/assets/story/couple-sofa-window-v2.jpg" placeholder="Shot 2 · Paret i stua"></image-slot>
      </div>
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ homeBathOp }}">
        <image-slot id="shot-bathroom-old" shape="rect" src="/assets/story/bathroom-old-v2.jpg" placeholder="Shot 2b · Det eldre badet"></image-slot>
      </div>''')
rep("      homeImgScale: 1 + h * 0.035, homeDim: ramp(h, 0.7, 0.95) * 0.5,",
    "      homeImgScale: 1 + h * 0.035, homeDim: ramp(h, 0.7, 0.95) * 0.5, homeBathOp: ease(ramp(h, 0.22, 0.32)),")

# ── chapter 3: building health-score card, next to the existing spot markers ──
rep("const s = g('see');",
    "const s = g('see');\n    const healthScore = 67, healthRing = this.ring(healthScore);\n    const healthCardOp = seg(s, 0.86, 1, 0.07), healthCardTy = ty(healthCardOp, 20), healthCardDisplay = mobile ? 'none' : 'block';\n    const healthLegendOp = ramp(s, 0.88, 0.93), healthLegendTy = ty(healthLegendOp, 10);\n    const healthCtaOp = ramp(s, 0.93, 0.97);\n    const healthRingDash = `${this.mix(0, healthRing.target, healthCardOp)} ${healthRing.full}`;\n    const healthScoreShown = Math.round(healthScore * healthCardOp);")
rep('''Bad, kjøkken og overflater er dine. Fasade, tak og rør er felles. ERA holder oversikt over begge.</p>
        </div>
      </div>
    </div>
  </section>''',
    '''Bad, kjøkken og overflater er dine. Fasade, tak og rør er felles. ERA holder oversikt over begge.</p>
        </div>
      </div>
      <div style="position: absolute; right: clamp(24px, 6vw, 90px); bottom: 6vh; width: min(260px, 82vw); padding: 22px 24px; border-radius: 24px; background: rgba(255,253,248,0.97); box-shadow: 0 40px 100px rgba(15,24,48,0.4); opacity: {{ healthCardOp }}; transform: {{ healthCardTy }}; display: {{ healthCardDisplay }}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px">
          <div style="font-size: 14.5px; font-weight: 700; letter-spacing: -0.01em; color: #131E3A; max-width: 150px">Eiendommens helsetilstand</div>
          <div style="position: relative; width: 56px; height: 56px; flex: none">
            <svg width="56" height="56" viewBox="0 0 56 56">
              <circle cx="28" cy="28" r="24" fill="none" stroke="#EFEAE0" stroke-width="6"></circle>
              <circle cx="28" cy="28" r="24" fill="none" stroke="#B0935F" stroke-width="6" stroke-linecap="round" stroke-dasharray="{{ healthRingDash }}" transform="rotate(-90 28 28)"></circle>
            </svg>
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 800; color: #131E3A; font-family: \'JetBrains Mono\', monospace">{{ healthScoreShown }}</div>
          </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 14px; font-size: 12.5px; opacity: {{ healthLegendOp }}; transform: {{ healthLegendTy }}">
          <div style="display: flex; align-items: center; gap: 8px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #C0483A"></span><span style="color: #131E3A">2 høy risiko</span></div>
          <div style="display: flex; align-items: center; gap: 8px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #B0935F"></span><span style="color: #131E3A">4 middels risiko</span></div>
          <div style="display: flex; align-items: center; gap: 8px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #4C8A63"></span><span style="color: #131E3A">8 ok</span></div>
          <div style="display: flex; align-items: center; gap: 8px"><span style="width: 7px; height: 7px; border-radius: 50%; background: #C7C2B6"></span><span style="color: #8A8579">1 ikke vurdert</span></div>
        </div>
        <a href="#prioriter" style="display: block; margin-top: 16px; font-size: 13px; font-weight: 600; color: #B0935F; opacity: {{ healthCtaOp }}">Se alle tiltak →</a>
      </div>
    </div>
  </section>''')

# ── chapter 4: ERA starts prioritising from the outside of the building ──
rep('<img src="/assets/story/couple-sofa-window-v2.jpg" alt="Badet — ett av mange valg i boligen" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 45% 50%;',
    '<img src="/assets/story/block-facade-v2.jpg" alt="Byggets fasade og balkonger — der prioriteringen begynner" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 45%;')

# ── chapter 4: early cue for the board ──
rep("prioCloud: ['Bad', 'Kjøkken', 'Stue', 'Vinduer', 'Balkong', 'Gulv', 'Elektrisk', 'Ventilasjon'],", "prioCloud: ['Bad', 'Kjøkken', 'Stue', 'Vinduer', 'Balkong', 'Fellesareal', 'Gulv', 'Elektrisk', 'Ventilasjon'],")

# ── chapter 5: the export carries its own mobile wall mask (mob ? 18/64/6/44); nothing to add ──
rep('''<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
          <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B0935F">Plan · Male stua</div>''',
    '''<div style="height: 88px; margin-bottom: 14px; border-radius: 12px; overflow: hidden"><img src="/assets/story/livingroom-wall-v2.jpg" alt="" style="width: 100%; height: 100%; object-fit: cover; object-position: 60% 40%"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px">
          <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B0935F">Plan · Male stua</div>''')
rep('''<div style="display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 20px; flex-wrap: wrap; opacity: {{ magicDoneOp }}">
          <div style="font-size: clamp(22px, 2.6vw, 30px); font-weight: 800; letter-spacing: -0.03em">Klar plan.</div>
          <a href="#start" style="display: inline-flex; align-items: center; height: 42px; padding: 0 18px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 14px; font-weight: 600" style-hover="background: #26344F">Finn min bolig</a>
        </div>''',
    '''<div style="display: flex; align-items: center; justify-content: space-between; gap: 14px; margin-top: 20px; flex-wrap: wrap; opacity: {{ magicDoneOp }}">
          <div style="font-size: clamp(22px, 2.6vw, 30px); font-weight: 800; letter-spacing: -0.03em">Klar plan.</div>
          <div style="display: flex; gap: 8px; flex-wrap: wrap">
            <a href="#partnere" style="display: inline-flex; align-items: center; height: 42px; padding: 0 16px; border-radius: 999px; border: 1px solid #E3DDD0; color: #131E3A; font-size: 13.5px; font-weight: 600">Se handleliste</a>
            <a href="#handverker" style="display: inline-flex; align-items: center; height: 42px; padding: 0 18px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 14px; font-weight: 600" style-hover="background: #26344F">Finn håndverker</a>
          </div>
        </div>''')


# ── chapter 7: faghandel block ──
rep('''<p style="margin: 20px 0 0; max-width: 400px; font-size: 14px; line-height: 1.5; color: #8A8579; display: {{ partnerNoteDisplay }}">For faghandel: riktige produkter kobles til et faktisk behov i boligen. <a href="#start" style="font-weight: 600">Snakk med ERA →</a></p>''',
    '''<div style="margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(19,30,58,0.1); max-width: 420px; display: {{ partnerNoteDisplay }}">
            <div style="font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B0935F">For faghandel</div>
            <p style="margin: 8px 0 0; font-size: 16px; line-height: 1.45; color: #131E3A">ERA beregner behovet før kunden går i butikken. Riktig produkt, riktig mengde, riktig tid, i én bestilling. Også for et helt borettslag. Uavhengig av kjede.</p>
            <a href="#start" data-partner="1" style="display: inline-flex; align-items: center; margin-top: 14px; height: 40px; padding: 0 18px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 14px; font-weight: 600" style-hover="background: #26344F">Bli partner →</a>
            <a href="/faghandel" style="display: inline-block; margin: 14px 0 0 16px; font-size: 14px; font-weight: 600" style-hover="color: #131E3A">Mer for faghandel →</a>
          </div>''')

rep('''<span style="font-size: 16px; font-weight: 600">{{ p.name }}</span>
              <span style="font-family: \'JetBrains Mono\', monospace; font-size: 13.5px; color: #5E6472">{{ p.qty }}</span>''',
    '''<span style="display: flex; align-items: center; gap: 10px; font-size: 16px; font-weight: 600"><span style="width: 6px; height: 6px; border-radius: 50%; background: #D4B17A; flex: none"></span>{{ p.name }}</span>
              <span style="font-family: \'JetBrains Mono\', monospace; font-size: 13.5px; color: #5E6472">{{ p.qty }}</span>''')

# ── chapter 8: håndverker ──
rep('Mindre tid på befaring og tilbud. Mer tid på jobben.</p>', 'Omfang, bilder, mål og ønsket tid ligger klart. Materialene også. Du gir tilbud, ikke befaring.</p>')
rep('''<a href="#start" style="pointer-events: auto; display: inline-flex; align-items: center; padding: 0 14px; border-radius: 10px; border: 1px solid #E3DDD0; color: #131E3A; font-size: 13.5px; font-weight: 600">For håndverkere →</a>
          </div>
        </div>''',
    '''<a href="/handverker" data-pro="1" style="pointer-events: auto; display: inline-flex; align-items: center; padding: 0 14px; border-radius: 10px; border: 1px solid #E3DDD0; color: #131E3A; font-size: 13.5px; font-weight: 600">For håndverkere →</a>
          </div>
        </div>
        <p style="margin: 0; max-width: 440px; text-align: {{ proTextAlign }}; font-size: 15px; line-height: 1.5; color: rgba(247,244,238,0.8); opacity: {{ proBtnOp }}; display: {{ partnerNoteDisplay }}">Kunden har plan, estimat og materialer klare. Færre bomturer, mindre papir. Og jobben blir stående i boligens historikk, med ditt navn på.</p>''')

# ── chapter 9: ERA insight card for the bathroom, evidence for "Ikke nå." ──
rep("const t = g('trust');",
    "const t = g('trust');\n    const bathScore = 58, bathRing = this.ring(bathScore);\n    const bathCardOp = seg(t, 0.62, 1, 0.08), bathCardTy = ty(bathCardOp, 24);\n    const bathTextOp = ramp(t, 0.66, 0.74), bathTextTy = ty(bathTextOp, 10);\n    const bathRecOp = ramp(t, 0.74, 0.84), bathRecTy = ty(bathRecOp, 10);\n    const bathRingDash = `${this.mix(0, bathRing.target, bathCardOp)} ${bathRing.full}`;\n    const bathScoreShown = Math.round(bathScore * bathCardOp);")
rep('''<h2 style="margin: 0; font-size: clamp(28px, 3.8vw, 50px); font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; text-wrap: balance; line-height: 1.1">Riktig beslutning er ikke alltid å gjøre mer.</h2>
        </div>
        <div style="height: 40vh"></div>
      </div></div>''',
    '''<h2 style="margin: 0; font-size: clamp(28px, 3.8vw, 50px); font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; text-wrap: balance; line-height: 1.1">Riktig beslutning er ikke alltid å gjøre mer.</h2>
        </div>
        <div style="height: 40vh"></div>
      </div></div>
      <div style="position: absolute; left: clamp(24px, 7vw, 120px); top: 100px; width: min(280px, 84vw); padding: 22px 24px; border-radius: 24px; background: rgba(255,253,248,0.97); box-shadow: 0 40px 100px rgba(0,0,0,0.4); opacity: {{ bathCardOp }}; transform: {{ bathCardTy }}">
        <div style="height: 84px; margin-bottom: 14px; border-radius: 12px; overflow: hidden"><img src="/assets/story/bathroom-old-v2.jpg" alt="" style="width: 100%; height: 100%; object-fit: cover; object-position: 30% 55%"></div>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <div>
            <div style="font-size: 16px; font-weight: 800; letter-spacing: -0.02em; color: #131E3A">Bad</div>
            <div style="font-size: 12px; color: #9A968C">Ca. 5 m²</div>
          </div>
          <div style="position: relative; width: 56px; height: 56px; flex: none">
            <svg width="56" height="56" viewBox="0 0 56 56">
              <circle cx="28" cy="28" r="24" fill="none" stroke="#EFEAE0" stroke-width="6"></circle>
              <circle cx="28" cy="28" r="24" fill="none" stroke="#B0935F" stroke-width="6" stroke-linecap="round" stroke-dasharray="{{ bathRingDash }}" transform="rotate(-90 28 28)"></circle>
            </svg>
            <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 800; color: #131E3A; font-family: \'JetBrains Mono\', monospace">{{ bathScoreShown }}</div>
          </div>
        </div>
        <div style="opacity: {{ bathTextOp }}; transform: {{ bathTextTy }}">
          <div style="margin-top: 14px; font-size: 13px; font-weight: 700; color: #B0935F">Middels risiko</div>
          <div style="margin-top: 4px; font-size: 12.5px; line-height: 1.4; color: #8A8579">Funnet: alder, slitasje og utette fuger</div>
        </div>
        <div style="display: flex; align-items: flex-start; gap: 10px; margin-top: 16px; padding: 14px; border-radius: 14px; background: #E9F3E6; opacity: {{ bathRecOp }}; transform: {{ bathRecTy }}">
          <span style="flex: none; width: 18px; height: 18px; border-radius: 50%; background: #3E7B4F; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800">✓</span>
          <div>
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #3E7B4F">Anbefaling fra ERA</div>
            <div style="margin-top: 2px; font-size: 13.5px; line-height: 1.4; color: #2E5C3C">Inspeksjon innen 12 måneder. Oppgradering kan vente 5–10 år.</div>
          </div>
        </div>
      </div>''')

# ── chapter 11: styret ──
rep('>For styret gjelder det samme — bare for hele eiendommen.</p>', '>Bad, kjøkken og overflater er dine. Fasade, tak og rør er felles. ERA holder oversikt over begge.</p>')
rep("const tagMap = { 4: 'Fasade', 9: 'FDV', 14: 'Kostnad', 1: 'Tak', 16: 'Prioritet' };", "const tagMap = { 4: 'Fasade 2027', 9: 'FDV', 14: 'Kostnad', 1: 'Tak 2031', 16: 'Prioritet 1' };")
rep('''<a href="#start" style="display: inline-flex; align-items: center; margin-top: 26px; height: 44px; padding: 0 20px; border-radius: 999px; background: #D4B17A; color: #131E3A; font-size: 14.5px; font-weight: 700; opacity: {{ boardCtaOp }}" style-hover="background: #E2C48F; color: #131E3A">Se ERA for borettslag og sameier →</a>''',
    '''<p style="margin: 22px 0 0; max-width: 420px; font-size: 16px; line-height: 1.45; color: rgba(247,244,238,0.85); opacity: {{ boardCtaOp }}; display: {{ partnerNoteDisplay }}"><b style="color: #FFFFFF">Styret skifter. Planen består.</b> Fasaden males i 2027, 1,2 millioner fordelt på 24 seksjoner, med tilbud fra håndverker som allerede har fått jobben beskrevet. Vedtaket tar ti minutter, ikke to møter.</p>
        <a href="#start" data-board="1" style="display: inline-flex; align-items: center; margin-top: 22px; height: 44px; padding: 0 20px; border-radius: 999px; background: #D4B17A; color: #131E3A; font-size: 14.5px; font-weight: 700; opacity: {{ boardCtaOp }}" style-hover="background: #E2C48F; color: #131E3A">Se planen for eiendommen →</a>
        <a href="/styret" style="display: inline-block; margin: 22px 0 0 18px; font-size: 14.5px; font-weight: 600; color: rgba(247,244,238,0.8); opacity: {{ boardCtaOp }}" style-hover="color: #FFFFFF">Mer for styret →</a>''')

# ── finale: audience-aware wording + real form ──
rep('''<h2 style="margin: 22px 0 0; font-size: clamp(24px, 3vw, 40px); font-weight: 700; letter-spacing: -0.02em; color: #FFFFFF; text-wrap: balance; opacity: {{ finTagOp }}; transform: {{ finTagTy }}">Boligeierskap uten gjetting.</h2>
        <p style="margin: 12px 0 0; font-size: clamp(15px, 1.6vw, 19px); color: rgba(247,244,238,0.7); opacity: {{ finTagOp }}">Forstå boligen. Prioriter riktig. Gjør det som faktisk trengs.</p>''',
    '''<h2 style="margin: 22px 0 0; font-size: clamp(24px, 3vw, 40px); font-weight: 700; letter-spacing: -0.02em; color: #FFFFFF; text-wrap: balance; opacity: {{ finTagOp }}; transform: {{ finTagTy }}">{{ finHead }}</h2>
        <p style="margin: 12px 0 0; font-size: clamp(15px, 1.6vw, 19px); color: rgba(247,244,238,0.7); opacity: {{ finTagOp }}">{{ finSub }}</p>
        <p style="margin: 14px 0 0; font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: rgba(212,177,122,0.85); opacity: {{ finTagOp }}">Bygget for norske boligeiere, styrer og håndverkere</p>''')
rep('''<div style="display: flex; align-items: center; gap: 8px; padding: 8px 8px 8px 22px; border-radius: 999px; background: #FFFFFF; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 460px; max-width: 100%">
            <span style="flex: 1; min-width: 0; text-align: left; font-size: 16px; color: #9A968C; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">{{ finInputLabel }}</span>
            <span style="display: inline-flex; align-items: center; height: 46px; padding: 0 22px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 15px; font-weight: 600; white-space: nowrap">Finn min bolig</span>
          </div>
          <a href="#styret" style="font-size: 15px; font-weight: 600; color: #D4B17A" style-hover="color: #FFFFFF">Se ERA for borettslag og sameier →</a>''',
    '''<form id="era-lead" data-audience="{{ leadAudience }}" style="display: {{ leadFormDisplay }}; flex-direction: column; align-items: flex-start; gap: 10px; width: 460px; max-width: 100%; margin: 0">
            <div style="display: flex; align-items: center; gap: 8px; padding: 8px 8px 8px 22px; border-radius: 999px; background: #FFFFFF; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 100%">
              <label for="era-lead-value" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0)">{{ finField }}</label>
              <div style="position: relative; flex: 1; min-width: 0; display: flex; align-items: center">
                <input id="era-lead-value" name="value" type="text" autocomplete="off" required minlength="3" maxlength="200" placeholder="{{ finField }}" style="width: 100%; border: 0; outline: 0; background: transparent; font: inherit; font-size: 16px; color: #131E3A">
                <span id="era-lead-typewriter" aria-hidden="true" style="position: absolute; inset: 0; display: flex; align-items: center; pointer-events: none; background: #FFFFFF; font-size: 16px; color: #9A968C; white-space: nowrap; overflow: hidden"></span>
                <span class="field-label" aria-hidden="true">{{ finLabel }}</span>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px; padding: 8px 8px 8px 22px; border-radius: 999px; background: #FFFFFF; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 100%">
              <label for="era-lead-email" style="position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0)">E-postadressen din</label>
              <div style="position: relative; flex: 1; min-width: 0; display: flex; align-items: center">
                <input id="era-lead-email" name="email" type="email" autocomplete="email" required maxlength="200" placeholder="Din e-post" style="width: 100%; border: 0; outline: 0; background: transparent; font: inherit; font-size: 16px; color: #131E3A">
                <span class="field-label" aria-hidden="true">E-post</span>
              </div>
              <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" style="position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0">
              <button type="submit" style="display: inline-flex; align-items: center; height: 46px; padding: 0 22px; border-radius: 999px; border: 0; background: #131E3A; color: #F7F4EE; font: inherit; font-size: 15px; font-weight: 600; white-space: nowrap; cursor: pointer; opacity: {{ leadBtnOp }}">{{ leadBtnLabel }}</button>
            </div>
          </form>
          <div role="status" aria-live="polite" style="display: {{ leadDoneDisplay }}; align-items: center; gap: 14px; padding: 18px 24px; border-radius: 22px; background: rgba(255,253,248,0.97); color: #131E3A; box-shadow: 0 20px 60px rgba(0,0,0,0.3); width: 460px; max-width: 100%">
            <div style="flex: none; width: 40px; height: 40px; border-radius: 50%; background: #3E7B4F; display: flex; align-items: center; justify-content: center">
              <svg width="20" height="16" viewBox="0 0 20 16" fill="none"><path d="M2 8L7.5 13.5L18 2" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="stroke-dasharray: 24; stroke-dashoffset: {{ leadCheckOffset }}; transition: stroke-dashoffset 0.6s cubic-bezier(0.4,0,0.2,1) 0.1s"></path></svg>
            </div>
            <div style="display: flex; flex-direction: column; gap: 6px">
              <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.02em">{{ leadDoneHead }}</div>
              <div style="font-size: 14.5px; color: #5E6472">{{ leadDoneSub }}</div>
            </div>
          </div>
          <div style="font-size: 13.5px; color: rgba(247,244,238,0.7); display: {{ leadErrorDisplay }}">{{ leadError }}</div>
          <a href="{{ finLinkHref }}" style="font-size: 15px; font-weight: 600; color: #D4B17A" style-hover="color: #FFFFFF">{{ finLinkLabel }}</a>''')

# ── state, handlers ──
rep("state = { prog: {}, theme: 'dark', activeNav: '', chapter: 0, navShown: false, mobile: false, reduced: false };",
    "state = { prog: {}, theme: 'dark', activeNav: '', chapter: 0, navShown: false, mobile: false, reduced: false, audience: 'owner', lead: 'idle', leadError: '', leadCheckDrawn: false, menuOpen: false };")
rep('''    this._onVis = () => { this._raf = null; this.update(); };
    document.addEventListener('visibilitychange', this._onVis);
    this.update();''',
    '''    this._onVis = () => { this._raf = null; this.update(); };
    document.addEventListener('visibilitychange', this._onVis);
    // Who is reading? The last story link decides the finale's wording and next step.
    this._onClick = (e) => {
      const t = e.target && e.target.closest && e.target.closest('[data-menu-toggle], [data-menu-close]');
      if (t) { this.setState({ menuOpen: t.hasAttribute('data-menu-toggle') ? !this.state.menuOpen : false }); if (t.hasAttribute('data-menu-toggle')) return; }
      const a = e.target && e.target.closest && e.target.closest('a[href^="#"], a[data-board], a[data-pro], a[data-partner]');
      if (!a) return;
      const aud = this.audienceFor(a.getAttribute('href'), a);
      if (aud) this.setState({ audience: aud });
    };
    document.addEventListener('click', this._onClick);
    const initial = this.audienceFor(location.hash, null);
    if (initial && initial !== 'owner') this.setState({ audience: initial });
    // Deep links (/#styret from the audience pages): re-apply the jump once the chapters exist.
    const hash = location.hash.slice(1);
    if (hash) {
      const jump = () => { const el = document.getElementById(hash); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY, behavior: 'instant' }); };
      window.setTimeout(jump, 60);
      window.setTimeout(jump, 500);
    }
    // The finale form posts to /api/lead — one JSON document per lead, stored privately.
    this._onSubmit = async (e) => {
      const form = e.target;
      if (!form || form.id !== 'era-lead') return;
      e.preventDefault();
      if (this.state.lead === 'sending') return;
      const value = (form.elements.value && form.elements.value.value || '').trim();
      const email = (form.elements.email && form.elements.email.value || '').trim();
      const website = (form.elements.website && form.elements.website.value || '').trim();
      if (value.length < 3) { this.setState({ lead: 'error', leadError: 'Skriv inn litt mer, så finner vi riktig sted.' }); return; }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { this.setState({ lead: 'error', leadError: 'Skriv inn en gyldig e-postadresse.' }); return; }
      this.setState({ lead: 'sending', leadError: '' });
      try {
        const r = await fetch('/api/lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ audience: this.state.audience, value, email, website, page: location.href }) });
        const j = await r.json().catch(() => ({}));
        if (r.ok && j.ok) {
          this.setState({ lead: 'done', leadError: '', leadCheckDrawn: false });
          if (!this._mq.matches) requestAnimationFrame(() => requestAnimationFrame(() => this.setState({ leadCheckDrawn: true })));
        }
        else this.setState({ lead: 'error', leadError: 'Noe gikk galt hos oss. Prøv igjen om et øyeblikk.' });
      } catch (err) {
        this.setState({ lead: 'error', leadError: 'Ingen kontakt med serveren. Sjekk nettet og prøv igjen.' });
      }
    };
    document.addEventListener('submit', this._onSubmit);
    this.update();''')
rep('''    document.removeEventListener('visibilitychange', this._onVis);
  }''',
    '''    document.removeEventListener('visibilitychange', this._onVis);
    document.removeEventListener('click', this._onClick);
    document.removeEventListener('submit', this._onSubmit);
  }
  audienceFor(href, a) {
    if (a && a.hasAttribute('data-board')) return 'board';
    if (a && a.hasAttribute('data-pro')) return 'pro';
    if (a && a.hasAttribute('data-partner')) return 'partner';
    if (href === '#styret') return 'board';
    if (href === '#handverker') return 'pro';
    if (href === '#partnere') return 'partner';
    if (href === '#boligeier' || href === '#hva' || href === '#hjem') return 'owner';
    return null;
  }''')

# ── address autocomplete (Kartverket/Geonorge) on the finale field, owner/board only ──
rep("    document.addEventListener('submit', this._onSubmit);\n    this.update();",
    "    document.addEventListener('submit', this._onSubmit);\n    this.initAddressAutocomplete();\n    this.initPlaceholderTypewriter();\n    this.update();")
rep('''    if (href === '#boligeier' || href === '#hva' || href === '#hjem') return 'owner';
    return null;
  }''',
    '''    if (href === '#boligeier' || href === '#hva' || href === '#hjem') return 'owner';
    return null;
  }
  initAddressAutocomplete() {
    const input = document.getElementById('era-lead-value');
    if (!input) return;
    const box = document.createElement('div');
    box.setAttribute('role', 'listbox');
    box.style.cssText = 'position:fixed;z-index:9999;display:none;background:#FFFFFF;border-radius:16px;box-shadow:0 20px 50px rgba(15,24,48,0.28);overflow:hidden auto;max-height:280px;font-family:\\'Schibsted Grotesk\\',system-ui,sans-serif';
    document.body.appendChild(box);
    let items = [], active = -1, timer = null, ctrl = null;
    const eligible = () => this.state.audience === 'owner' || this.state.audience === 'board';
    const close = () => { box.style.display = 'none'; box.innerHTML = ''; items = []; active = -1; input.removeAttribute('aria-expanded'); input.removeAttribute('aria-activedescendant'); };
    const place = () => { const r = input.getBoundingClientRect(); box.style.left = r.left + 'px'; box.style.top = (r.bottom + 8) + 'px'; box.style.width = r.width + 'px'; };
    const render = () => {
      if (!items.length) { close(); return; }
      place();
      box.innerHTML = items.map((it, i) => `<div role="option" id="era-addr-${i}" data-i="${i}" style="padding:11px 16px;cursor:pointer;font-size:14.5px;color:#131E3A;background:${i === active ? '#F7F4EE' : '#FFFFFF'};border-top:${i ? '1px solid #EFEAE0' : '0'}"><div>${it.text}</div><div style="margin-top:2px;font-size:12.5px;color:#8A8579">${it.sub}</div></div>`).join('');
      box.style.display = 'block';
      input.setAttribute('aria-expanded', 'true');
      if (active >= 0) input.setAttribute('aria-activedescendant', 'era-addr-' + active); else input.removeAttribute('aria-activedescendant');
    };
    const select = (i) => {
      const it = items[i]; if (!it) return;
      input.value = it.full; close();
      const btn = input.closest('form') && input.closest('form').querySelector('button[type="submit"]');
      if (btn && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        btn.animate([{ boxShadow: '0 0 0 0 rgba(212,177,122,0.6)' }, { boxShadow: '0 0 0 4px rgba(212,177,122,0.35)' }, { boxShadow: '0 0 0 14px rgba(212,177,122,0)' }], { duration: 900, easing: 'ease-out', iterations: 2 });
      }
    };
    const search = (q) => {
      if (ctrl) ctrl.abort();
      ctrl = new AbortController();
      fetch(`https://ws.geonorge.no/adresser/v1/sok?sok=${encodeURIComponent(q)}&treffPerSide=6&fuzzy=true`, { signal: ctrl.signal })
        .then((r) => r.ok ? r.json() : null)
        .then((data) => {
          if (!data || input.value.trim() !== q) return;
          const list = Array.isArray(data.adresser) ? data.adresser : [];
          items = list.map((a) => { const sub = [a.postnummer, a.poststed].filter(Boolean).join(' '); return { text: a.adressetekst || '', sub, full: [a.adressetekst, sub].filter(Boolean).join(', ') }; });
          active = -1;
          render();
        })
        .catch(() => {});
    };
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    input.addEventListener('input', () => {
      if (!eligible()) { close(); return; }
      const q = input.value.trim();
      clearTimeout(timer);
      if (q.length < 3) { close(); return; }
      timer = setTimeout(() => search(q), 250);
    });
    input.addEventListener('keydown', (e) => {
      if (!items.length) return;
      if (e.key === 'ArrowDown') { e.preventDefault(); active = Math.min(active + 1, items.length - 1); render(); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); active = Math.max(active - 1, 0); render(); }
      else if (e.key === 'Enter') { if (active >= 0) { e.preventDefault(); select(active); } }
      else if (e.key === 'Escape') { close(); }
    });
    input.addEventListener('blur', () => { setTimeout(close, 150); });
    box.addEventListener('mousedown', (e) => {
      e.preventDefault();
      const row = e.target.closest('[data-i]');
      if (row) select(Number(row.dataset.i));
    });
    window.addEventListener('scroll', () => { if (box.style.display === 'block') place(); }, { passive: true });
    window.addEventListener('resize', () => { if (box.style.display === 'block') place(); });
  }
  initPlaceholderTypewriter() {
    const input = document.getElementById('era-lead-value');
    const span = document.getElementById('era-lead-typewriter');
    if (!input || !span) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const EXAMPLES = {
      owner: ['Storgata 1, Oslo', 'Kirkeveien 44, Bergen', 'Skogveien 12, Trondheim'],
      board: ['Sameiet Solsiden, Oslo', 'Borettslaget Utsikten, Bergen', 'Sameiet Fjordblikk, Stavanger'],
      pro: ['Byggmester Hansen AS', 'Mester Rørlegger AS', '987 654 321'],
      partner: ['Byggmakker Lillestrøm', 'Montér Sandvika', 'XL-BYGG Ringerike'],
    };
    let stopped = false;
    const stop = () => { stopped = true; span.style.display = 'none'; };
    input.addEventListener('focus', stop, { once: true });
    input.addEventListener('pointerdown', stop, { once: true });
    input.addEventListener('input', stop, { once: true });
    let exIdx = 0;
    const after = (ms, fn) => { if (!stopped) setTimeout(fn, ms); };
    const eraseFrom = (text, j) => {
      if (j < 0) { exIdx++; after(300, nextWord); return; }
      span.textContent = text.slice(0, j);
      after(25, () => eraseFrom(text, j - 1));
    };
    const typeFrom = (text, i) => {
      if (i > text.length) { after(1300, () => eraseFrom(text, text.length)); return; }
      span.textContent = text.slice(0, i);
      after(45, () => typeFrom(text, i + 1));
    };
    const nextWord = () => {
      const list = EXAMPLES[this.state.audience] || EXAMPLES.owner;
      typeFrom(list[exIdx % list.length], 0);
    };
    nextWord();
  }''')

# ── finale values ──
rep("    const f = g('finale');\n",
    """    const f = g('finale');
    const finaleByAudience = {
      owner: { finHead: 'Boligeierskap uten gjetting.', finSub: 'Forstå boligen. Prioriter riktig. Gjør det som faktisk trengs.',
        finField: 'Skriv adressen din', finLabel: 'Adresse', finCta: 'Finn min bolig', finLinkHref: '#styret', finLinkLabel: 'Se ERA for borettslag og sameier →' },
      board: { finHead: 'Eiendomsforvaltning uten gjetting.', finSub: 'Tilstand, plan og kostnader for hele eiendommen, klar til neste generalforsamling. Planen følger bygget, ikke styret.',
        finField: 'Adressen til bygget', finLabel: 'Adresse', finCta: 'Få planen for eiendommen', finLinkHref: '#boligeier', finLinkLabel: 'Se ERA for boligeiere →' },
      pro: { finHead: 'Få oppdrag som er ferdig forstått.', finSub: 'Kvalifiserte kunder med plan og estimat, ferdig beskrevet omfang og materialer som ligger klart. Mindre befaring, mer jobb.',
        finField: 'Firmanavn eller organisasjonsnummer', finLabel: 'Firma', finCta: 'Motta oppdrag', finLinkHref: '#boligeier', finLinkLabel: 'Se ERA for boligeiere →' },
      partner: { finHead: 'Riktige produkter til et faktisk behov.', finSub: 'Ferdig beregnede bestillinger fra boliger og borettslag, levert slik kunden vil ha det. Færre feilkjøp, større prosjekter, uavhengig av kjede.',
        finField: 'Kjede eller butikk', finLabel: 'Butikk', finCta: 'Bli partner', finLinkHref: '#boligeier', finLinkLabel: 'Se ERA for boligeiere →' }
    };
    const finaleVals = finaleByAudience[this.state.audience] || finaleByAudience.owner;
    if (mobile && this.state.audience === 'owner') finaleVals.finField = 'Adresse';
    const doneByAudience = {
      owner: ['Takk. Vi finner boligen din.', 'Vi svarer på e-posten du oppga, når ERA er klar for adressen.'],
      board: ['Takk. Vi ser på eiendommen.', 'Vi sender et forslag til plan på e-post, klart til neste møte.'],
      pro: ['Takk. Du er registrert.', 'Vi sender e-post når det er ferdig beskrevne oppdrag i ditt område.'],
      partner: ['Takk. Vi tar kontakt.', 'Vi sender en e-post og viser hvordan beregnede behov blir bestillinger hos dere.']
    };
    const menuOpen = this.state.menuOpen;
    const menuVals = {
      navMenuBtnDisplay: mobile ? 'inline-flex' : 'none', navMenuDisplay: mobile && menuOpen ? 'flex' : 'none',
      navMenuIcon: menuOpen ? '×' : '☰', navMenuAria: menuOpen ? 'Lukk menyen' : 'Åpne menyen', navMenuExpanded: menuOpen ? 'true' : 'false',
      navMenuBg: dark ? 'rgba(15,24,48,0.92)' : 'rgba(255,253,248,0.96)', navMenuFg: dark ? '#F7F4EE' : '#131E3A',
      navMenuItems: [['#hva', 'Hva ERA gjør'], ['/boligeier', 'Boligeier'], ['/styret', 'Styret'], ['/handverker', 'Håndverker'], ['/faghandel', 'Faghandel'], ['/personvern', 'Personvern']].map(([href, label]) => ({ href, label }))
    };
    const lead = this.state.lead, ld = doneByAudience[this.state.audience] || doneByAudience.owner;
    const leadVals = {
      leadAudience: this.state.audience,
      leadFormDisplay: lead === 'done' ? 'none' : 'flex', leadDoneDisplay: lead === 'done' ? 'flex' : 'none',
      leadBtnLabel: lead === 'sending' ? 'Sender…' : finaleVals.finCta, leadBtnOp: lead === 'sending' ? 0.7 : 1,
      leadDoneHead: ld[0], leadDoneSub: ld[1],
      leadCheckOffset: (lead === 'done' && (this.state.leadCheckDrawn || this._mq.matches)) ? 0 : 24,
      leadErrorDisplay: lead === 'error' ? 'block' : 'none', leadError: this.state.leadError
    };
""")
# spread the new values into the returned bindings
rep("...heights, ...resp, ...themeVals,", "...finaleVals, ...leadVals, ...menuVals, ...heights, ...resp, ...themeVals,")
rep("...finaleVals, ...leadVals, ...menuVals, ...heights, ...resp, ...themeVals,",
    "healthScore, healthScoreShown, healthRingDash, healthCardOp, healthCardTy, healthCardDisplay, healthLegendOp, healthLegendTy, healthCtaOp, bathScore, bathScoreShown, bathRingDash, bathCardOp, bathCardTy, bathTextOp, bathTextTy, bathRecOp, bathRecTy, ...finaleVals, ...leadVals, ...menuVals, ...heights, ...resp, ...themeVals,")

# chaos card: bathroom, not the couple
rep('"chaosBath": "/assets/story/couple-sofa-window-v2.jpg"', '"chaosBath": "/assets/story/bathroom-v2.jpg"')

# ── floating field labels for the finale's two lead-form pills ──
rep('''  a:focus-visible { outline: 2px solid #D4B17A; outline-offset: 3px; border-radius: 6px; }
</style>''',
    '''  a:focus-visible { outline: 2px solid #D4B17A; outline-offset: 3px; border-radius: 6px; }
  .field-label { position: absolute; left: 0; top: -20px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(247,244,238,0.65); opacity: 0; transform: translateY(4px); transition: opacity 0.18s ease, transform 0.18s ease; pointer-events: none; white-space: nowrap; }
  #era-lead-value:focus ~ .field-label, #era-lead-value:not(:placeholder-shown) ~ .field-label,
  #era-lead-email:focus ~ .field-label, #era-lead-email:not(:placeholder-shown) ~ .field-label { opacity: 1; transform: translateY(0); }
</style>''')

# ── a persistent, discreet CTA below the chapter rail (second conversion surface) ──
rep('''        <span style="width: 1px; height: 20px; margin-right: 3px; background: {{ railLine }}; opacity: {{ c.lineOp }}"></span>
      </div>
    </sc-for>
  </div>''',
    '''        <span style="width: 1px; height: 20px; margin-right: 3px; background: {{ railLine }}; opacity: {{ c.lineOp }}"></span>
      </div>
    </sc-for>
    <a href="#start" style="pointer-events: auto; margin-top: 14px; display: inline-flex; align-items: center; height: 38px; padding: 0 18px; border-radius: 999px; background: {{ navCtaBg }}; color: {{ navCtaFg }}; font-weight: 700; font-size: 13px; white-space: nowrap; box-shadow: 0 10px 24px rgba(15,24,48,0.25); transition: background 0.5s, color 0.5s">{{ finCta }}</a>
  </div>''')

# ── door glow tied to scroll speed, not just progress ──
rep('''  update() {
    const vh = window.innerHeight;
    const reduced = this._mq.matches;''',
    '''  update() {
    const vh = window.innerHeight;
    const reduced = this._mq.matches;
    const nowT = performance.now(), scrollNow = window.scrollY;
    if (this._lastScrollT == null) { this._lastScrollT = nowT; this._lastScrollY = scrollNow; this._scrollSpeed = 0; }
    else {
      const dt = Math.max(1, nowT - this._lastScrollT), dy = Math.abs(scrollNow - this._lastScrollY);
      const inst = Math.min(1, (dy / dt) / 2.5);
      this._scrollSpeed = this._scrollSpeed * 0.7 + inst * 0.3;
      this._lastScrollT = nowT; this._lastScrollY = scrollNow;
    }''')
rep("      doorLeftTx: `${-open * 100}%`, doorRightTx: `${open * 100}%`, doorSeamOp: 1 - ramp(d, 0.08, 0.28), doorSeamGlow: seg(d, 0.06, 0.16, 0.05) * 0.8, doorGlowA: 0.55 * seg(d, 0.14, 0.5, 0.15), doorGlowR: `${30 + open * 50}%`, doorGlowScale: 1 + open * 0.08, doorPos: `50% ${58 - open * 4}%`, doorDim: 0.35 - open * 0.2,",
    "      doorLeftTx: `${-open * 100}%`, doorRightTx: `${open * 100}%`, doorSeamOp: 1 - ramp(d, 0.08, 0.28), doorSeamGlow: seg(d, 0.06, 0.16, 0.05) * 0.8, doorGlowA: 0.55 * seg(d, 0.14, 0.5, 0.15) * (1 + (this._scrollSpeed || 0) * 0.7), doorGlowR: `${30 + open * 50 + (this._scrollSpeed || 0) * 10}%`, doorGlowScale: 1 + open * 0.08 + (this._scrollSpeed || 0) * 0.05, doorPos: `50% ${58 - open * 4}%`, doorDim: 0.35 - open * 0.2,")

# ── chapter 2: more photorealistic paper — grain texture, dual-layer contact shadows,
#    and a faint desk-surface background, all CSS-only (no new image assets) ──
rep("    const white = '#FFFFFF', shadowLg = '0 30px 70px rgba(19,30,58,0.16)', shadowMd = '0 18px 50px rgba(19,30,58,0.1)', shadowSm = '0 10px 26px rgba(19,30,58,0.08)';",
    "    const white = '#FFFFFF', shadowLg = '0 2px 4px rgba(19,30,58,0.14), 0 30px 70px rgba(19,30,58,0.18)', shadowMd = '0 2px 3px rgba(19,30,58,0.12), 0 18px 50px rgba(19,30,58,0.12)', shadowSm = '0 1px 2px rgba(19,30,58,0.1), 0 10px 26px rgba(19,30,58,0.09)';")
rep('''  <section id="forsta" ref="{{ refChaos }}" data-theme="light" style="position: relative; height: {{ h_chaos }}; background: #F7F4EE" data-screen-label="02 Informasjonskaos" aria-label="Informasjonen finnes overalt">''',
    '''  <section id="forsta" ref="{{ refChaos }}" data-theme="light" style="position: relative; height: {{ h_chaos }}; background: radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.7) 0%, transparent 62%), repeating-linear-gradient(118deg, rgba(19,30,58,0.02) 0px, rgba(19,30,58,0.02) 1px, transparent 1px, transparent 3px), #F7F4EE" data-screen-label="02 Informasjonskaos" aria-label="Informasjonen finnes overalt">''')
rep('''          <div style="position: absolute; left: 50%; top: 50%; width: {{ it.w }}; transform: translate(-50%, -50%) translate({{ it.tx }}, {{ it.ty }}) rotate({{ it.rot }}) scale({{ it.scale }}); opacity: {{ it.op }}; padding: {{ it.pad }}; border-radius: {{ it.radius }}; background: {{ it.bg }}; box-shadow: {{ it.shadow }}; border: 1px solid rgba(19,30,58,0.06); overflow: hidden; font-family: {{ it.font }}; z-index: {{ it.z }}">''',
    '''          <div style="position: absolute; left: 50%; top: 50%; width: {{ it.w }}; transform: translate(-50%, -50%) translate({{ it.tx }}, {{ it.ty }}) rotate({{ it.rot }}) scale({{ it.scale }}); opacity: {{ it.op }}; padding: {{ it.pad }}; border-radius: {{ it.radius }}; background: {{ it.bg }}; box-shadow: {{ it.shadow }}; border: 1px solid rgba(19,30,58,0.06); overflow: hidden; font-family: {{ it.font }}; z-index: {{ it.z }}">
            <div aria-hidden="true" style="position: absolute; inset: 0; pointer-events: none; mix-blend-mode: multiply; opacity: 0.07; background-image: url(&quot;data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E&quot;)"></div>''')

# ══════════════════════════════════════════════════════════════════════════════════════════
# ── HELE BOLIGEN (2026-09): maling er ett eksempel; ERA følger behovene rundt hele boligen,
#    flere fag, handel + tjenester i samme reise, dokumentasjon tilbake, livsløps-payoff.
#    Nye bilder (tomme til foto foreligger) hentes fra window.__resources: wholeHome, plumber, electrician.
# ══════════════════════════════════════════════════════════════════════════════════════════

# central image map: three new motifs, empty until photography is supplied
rep('"t1": "/assets/story/block-season-1-v2.jpg",',
    '"t1": "/assets/story/block-season-1-v2.jpg",\n  "wholeHome": "",\n  "plumber": "",\n  "electrician": "",')

# premium ERA placeholder treatment (navy + warm vignette + faint grid), dev label, hide the slot's own empty chrome
rep('''#era-lead-email:focus ~ .field-label, #era-lead-email:not(:placeholder-shown) ~ .field-label { opacity: 1; transform: translateY(0); }
</style>''',
    '''#era-lead-email:focus ~ .field-label, #era-lead-email:not(:placeholder-shown) ~ .field-label { opacity: 1; transform: translateY(0); }
  /* Placeholder for photography not yet delivered: intentional ERA treatment, never a grey box. Remove .era-ph-label when the photo lands. */
  .era-ph { position: absolute; inset: 0; background: radial-gradient(ellipse 70% 60% at 55% 45%, rgba(212,177,122,0.18), transparent 70%), linear-gradient(160deg, #1B2848 0%, #131E3A 45%, #0F1830 100%); }
  .era-ph::after { content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(247,244,238,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(247,244,238,0.06) 1px, transparent 1px); background-size: 72px 72px; -webkit-mask-image: radial-gradient(ellipse 60% 55% at 55% 45%, #000 20%, transparent 80%); mask-image: radial-gradient(ellipse 60% 55% at 55% 45%, #000 20%, transparent 80%); }
  .era-ph-label { position: absolute; left: 20px; top: 84px; z-index: 2; padding: 6px 10px; border-radius: 999px; border: 1px dashed rgba(212,177,122,0.6); background: rgba(15,24,48,0.5); font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.1em; color: #D4B17A; pointer-events: none; }
  image-slot[placeholder^="Bilde"]::part(empty) { visibility: hidden !important; }
</style>''')

# ── 05: maling er ett eksempel ──
rep('color: #D4B17A; margin-bottom: 18px">For boligeier</div>', 'color: #D4B17A; margin-bottom: 18px">For boligeier · Ett eksempel</div>')
rep('font-size: 14px; font-weight: 600" style-hover="background: #26344F">Finn håndverker</a>', 'font-size: 14px; font-weight: 600" style-hover="background: #26344F">Få hjelp</a>')

# ── 05b + 05c: new sticky scenes between «Male stua» and «Valget» ──
rep('''  <!-- 6 · VALGET -->''',
    '''  <!-- 5b · HELE BOLIGEN — samme intelligens, hele boligen: markører på ett bilde, så ut til fasade og tak -->
  <section id="hele-boligen" ref="{{ refWhole }}" data-theme="dark" style="position: relative; height: {{ h_whole }}; background: #0F1830" data-screen-label="05b Hele boligen" aria-label="ERA følger behovene rundt hele boligen">
    <div style="position: sticky; top: 0; height: 100vh; overflow: hidden; isolation: isolate">
      <div style="position: absolute; inset: 0; transform: translateZ(0) scale({{ wholeImgScale }}); backface-visibility: hidden">
        <div class="era-ph"></div>
        <image-slot class="era-ph-slot" id="whole-home-overview" shape="rect" src="{{ wholeHomeSrc }}" placeholder="Bilde · Hele boligen"></image-slot>
        <div class="era-ph-label" style="opacity: {{ wholeHomeDevOp }}">BILDE · HELE BOLIGEN</div>
      </div>
      <div style="position: absolute; inset: 0; opacity: {{ wholeOutOp }}; transform: translateZ(0); backface-visibility: hidden">
        <img src="/assets/story/roof-detail-v2.jpg" alt="Byggets fasade og tak" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 60% 50%">
      </div>
      <div style="position: absolute; inset: 0; pointer-events: none; background: linear-gradient(90deg, rgba(15,24,48,0.72) 0%, rgba(15,24,48,0.35) 32%, rgba(15,24,48,0.05) 55%, transparent 100%)"></div>
      <div style="position: absolute; inset: 0; pointer-events: none; background: rgba(15,24,48,{{ wholeDim }})"></div>
      <sc-for list="{{ wholeSpots }}" as="w" hint-placeholder-count="8">
        <div style="position: absolute; left: {{ w.x }}; top: {{ w.y }}; opacity: {{ w.op }}; transform: translate(-50%, -50%) scale({{ w.scale }}); display: {{ spotDisplay }}; pointer-events: none">
          <span style="position: absolute; left: -7px; top: -7px; width: 14px; height: 14px; border-radius: 50%; background: #D4B17A; box-shadow: 0 0 0 5px rgba(212,177,122,0.3), 0 0 0 12px rgba(212,177,122,0.12)"></span>
          <span style="position: absolute; left: 16px; top: -15px; padding: 7px 12px; border-radius: 999px; background: rgba(255,253,248,0.96); box-shadow: 0 10px 30px rgba(15,24,48,0.35); font-size: 12.5px; font-weight: 700; color: #131E3A; white-space: nowrap">{{ w.label }}</span>
        </div>
      </sc-for>
      <div style="position: absolute; left: 16px; right: 16px; bottom: 20px; display: {{ spotListDisplay }}; gap: 6px; flex-wrap: wrap; pointer-events: none">
        <sc-for list="{{ wholeSpots }}" as="wc" hint-placeholder-count="8">
          <span style="padding: 7px 12px; border-radius: 999px; background: rgba(255,253,248,0.94); font-size: 12px; font-weight: 700; color: #131E3A; opacity: {{ wc.op }}"><span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #D4B17A; margin-right: 7px; vertical-align: 1px"></span>{{ wc.label }}</span>
        </sc-for>
      </div>
      <div style="position: absolute; left: clamp(24px, 7vw, 120px); right: 24px; top: {{ magicTextTop }}; transform: {{ magicTextTy }}; max-width: 560px; pointer-events: none">
        <div style="position: absolute; left: 0; top: 50%; transform: translateY(-50%) {{ whole0Ty }}; opacity: {{ whole0Op }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #D4B17A; margin-bottom: 18px">Dette er én jobb</div>
          <h2 style="margin: 0; font-size: clamp(30px, 4.2vw, 56px); line-height: 1.06; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; text-wrap: balance; text-shadow: 0 4px 40px rgba(15,24,48,0.6)">Men boligen er mer enn én vegg.</h2>
        </div>
        <div style="position: absolute; left: 0; top: 50%; transform: translateY(-50%) {{ whole1Ty }}; opacity: {{ whole1Op }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #D4B17A; margin-bottom: 18px">ERA ser hele boligen</div>
          <h2 style="margin: 0; font-size: clamp(28px, 3.6vw, 48px); line-height: 1.08; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; text-wrap: balance; text-shadow: 0 4px 40px rgba(15,24,48,0.6)">ERA følger behovene rundt hele boligen.</h2>
        </div>
        <div style="position: absolute; left: 0; top: 50%; transform: translateY(-50%) {{ whole2Ty }}; opacity: {{ whole2Op }}">
          <h2 style="margin: 0; font-size: clamp(32px, 4.6vw, 60px); line-height: 1.04; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; text-shadow: 0 4px 40px rgba(15,24,48,0.6)">Én bolig.<br>Mange behov.<br><span style="color: #D4B17A">Samme ERA.</span></h2>
        </div>
        <div style="height: 30vh"></div>
      </div>
    </div>
  </section>

  <!-- 5c · FLERE TYPER BEHOV — tre crossfades: bad (eksisterende), elektro (placeholder), fasade/tak (eksisterende) -->
  <section id="behov" ref="{{ refNeeds }}" data-theme="dark" style="position: relative; height: {{ h_needs }}; background: #0F1830" data-screen-label="05c Flere behov" aria-label="Forskjellige behov, forskjellig kompetanse">
    <div style="position: sticky; top: 0; height: 100vh; overflow: hidden; isolation: isolate">
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ needsAOp }}">
        <img src="/assets/story/bathroom-old-v2.jpg" alt="Et eldre bad med slitte fuger" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 40% 50%">
      </div>
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ needsBOp }}">
        <div class="era-ph"></div>
        <image-slot class="era-ph-slot" id="professional-electrician-context" shape="rect" src="{{ electricianSrc }}" placeholder="Bilde · Elektriker"></image-slot>
        <div class="era-ph-label" style="opacity: {{ electricianDevOp }}">BILDE · ELEKTRIKER</div>
      </div>
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ needsCOp }}">
        <img src="/assets/story/block-facade-v2.jpg" alt="Byggets fasade" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 40%">
      </div>
      <div style="position: absolute; inset: 0; pointer-events: none; background: linear-gradient(180deg, rgba(15,24,48,0.25) 0%, transparent 35%, transparent 60%, rgba(15,24,48,0.6) 100%)"></div>
      <div style="position: absolute; inset: 0; pointer-events: none; background: rgba(15,24,48,{{ needsDim }})"></div>
      <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 24px; pointer-events: none">
        <div style="position: relative; width: min(760px, 100%)">
          <sc-for list="{{ needsWords }}" as="nw" hint-placeholder-count="3">
            <div style="position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%) {{ nw.ty }}; opacity: {{ nw.op }}">
              <h2 style="margin: 0; font-size: clamp(48px, 9vw, 120px); font-weight: 800; letter-spacing: -0.04em; line-height: 1; color: #FFFFFF; text-shadow: 0 4px 40px rgba(15,24,48,0.7)">{{ nw.word }}</h2>
              <div style="margin-top: 18px; display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; background: rgba(255,253,248,0.94); font-size: 13px; font-weight: 700; color: #131E3A"><span style="width: 7px; height: 7px; border-radius: 50%; background: {{ nw.dot }}"></span>{{ nw.note }}</div>
            </div>
          </sc-for>
          <div style="position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%) {{ needsEndTy }}; opacity: {{ needsEndOp }}">
            <h2 style="margin: 0 auto; max-width: 720px; font-size: clamp(26px, 3.6vw, 48px); font-weight: 800; letter-spacing: -0.03em; line-height: 1.12; color: #FFFFFF; text-wrap: balance">Forskjellige behov.<br>Forskjellig kompetanse.<br><span style="color: #D4B17A">Én sammenhengende vei videre.</span></h2>
          </div>
          <div style="height: 40vh"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- 6 · VALGET -->''')

# ── 06: tre veier ──
rep('color: #B0935F; margin-bottom: 16px">Ett behov. To veier.</div>', 'color: #B0935F; margin-bottom: 16px">Ett behov. Riktig vei.</div>')
rep('font-weight: 800; letter-spacing: -0.03em">Hvordan vil du gjøre det?</h2>', 'font-weight: 800; letter-spacing: -0.03em">Hvordan bør dette løses?</h2>')
rep('''      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 16px; width: 100%; max-width: 860px">
        <div style="padding: 36px; border-radius: 26px; background: #F2E9DC; opacity: {{ choiceLOp }}; transform: {{ choiceLTx }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #8A7758">A</div>
          <div style="margin-top: 12px; font-size: 28px; font-weight: 800; letter-spacing: -0.02em">Gjøre det selv</div>
          <p style="margin: 10px 0 0; font-size: 15.5px; line-height: 1.5; color: #6E5F44">Materialer og mengder — ferdig beregnet.</p>
        </div>
        <div style="padding: 36px; border-radius: 26px; background: #131E3A; color: #F7F4EE; opacity: {{ choiceROp }}; transform: {{ choiceRTx }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #D4B17A">B</div>
          <div style="margin-top: 12px; font-size: 28px; font-weight: 800; letter-spacing: -0.02em">Få hjelp</div>
          <p style="margin: 10px 0 0; font-size: 15.5px; line-height: 1.5; color: rgba(247,244,238,0.7)">Jobben går til fagfolk — ferdig beskrevet.</p>
        </div>
      </div>
      <div style="font-size: 14px; color: #9A968C; opacity: {{ choiceNoteOp }}">Scroll videre — vi viser begge.</div>''',
    '''      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 240px), 1fr)); gap: 14px; width: 100%; max-width: 980px">
        <div style="padding: {{ choicePad }}; border-radius: 26px; background: #F2E9DC; opacity: {{ choiceLOp }}; transform: {{ choiceLTx }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #8A7758">A</div>
          <div style="margin-top: 10px; font-size: clamp(22px, 2.2vw, 28px); font-weight: 800; letter-spacing: -0.02em">Gjør det selv</div>
          <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.5; color: #6E5F44">Veiledning, mengder og riktige produkter. Maling, olje på gulvet, det små.</p>
        </div>
        <div style="padding: {{ choicePad }}; border-radius: 26px; background: #131E3A; color: #F7F4EE; opacity: {{ choiceROp }}; transform: {{ choiceRTx }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #D4B17A">B</div>
          <div style="margin-top: 10px; font-size: clamp(22px, 2.2vw, 28px); font-weight: 800; letter-spacing: -0.02em">Få hjelp</div>
          <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.5; color: rgba(247,244,238,0.7)">Behovet er beskrevet, fagområdet funnet. Bad, kjøkken, fasade.</p>
        </div>
        <div style="padding: {{ choicePad }}; border-radius: 26px; background: #FFFDF9; border: 1.5px solid #D4B17A; opacity: {{ choiceCOp }}; transform: {{ choiceCTy }}">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B0935F">C</div>
          <div style="margin-top: 10px; font-size: clamp(22px, 2.2vw, 28px); font-weight: 800; letter-spacing: -0.02em">Krever fagperson</div>
          <p style="margin: 8px 0 0; font-size: 15px; line-height: 1.5; color: #6E5F44">ERA leder deg til riktig kompetanse. Elektro, rør, tak.</p>
        </div>
      </div>
      <div style="text-align: center; opacity: {{ choiceNoteOp }}">
        <p style="margin: 0; font-size: clamp(15px, 1.6vw, 18px); font-weight: 600; color: #131E3A">ERA hjelper deg til riktig kompetanse når jobben krever det.</p>
        <div style="margin-top: 8px; font-size: 14px; color: #9A968C">Scroll videre — vi viser begge veiene.</div>
      </div>''')

# ── 07: samme bilde, bredere handel ──
rep('''        <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B0935F">A · Gjøre det selv</div>
        <h2 style="margin: 18px 0 0; font-size: clamp(32px, 4.2vw, 56px); line-height: 1.04; font-weight: 800; letter-spacing: -0.03em; opacity: {{ comHeadOp }}; transform: {{ comHeadTy }}">Alt du trenger.<br><span style="font-weight: 500; color: #5E6472">Allerede beregnet.</span></h2>
        <div style="display: flex; flex-direction: column; margin-top: 26px; max-width: 420px">''',
    '''        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap">
          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #B0935F">A · Gjør det selv</div>
          <div style="display: {{ comCatDisplay }}; gap: 5px; flex-wrap: wrap">
            <sc-for list="{{ comCatChips }}" as="cc" hint-placeholder-count="6">
              <span style="padding: 4px 9px; border-radius: 999px; border: 1px solid rgba(19,30,58,0.14); font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #5E6472; opacity: {{ cc.op }}">{{ cc.label }}</span>
            </sc-for>
          </div>
        </div>
        <h2 style="margin: 14px 0 0; font-size: clamp(28px, 3.6vw, 46px); line-height: 1.04; font-weight: 800; letter-spacing: -0.03em; opacity: {{ comHeadOp }}; transform: {{ comHeadTy }}">Gjør det selv?<br><span style="font-weight: 500; color: #5E6472">Fra oppgaven til det du faktisk trenger.</span></h2>
        <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 16px; max-width: 520px">
          <sc-for list="{{ comSteps }}" as="cs" hint-placeholder-count="6">
            <span style="display: inline-flex; align-items: center; gap: 6px; opacity: {{ cs.op }}"><span style="padding: 5px 10px; border-radius: 999px; background: #FFFFFF; border: 1px solid #E3DDD0; font-size: 11.5px; font-weight: 700; color: #131E3A">{{ cs.label }}</span><span style="font-size: 11px; color: #B0935F; opacity: {{ cs.arrowOp }}">→</span></span>
          </sc-for>
        </div>
        <div style="display: flex; flex-direction: column; margin-top: 16px; max-width: 420px">''')
rep('font-size: 13.5px; font-weight: 600">Kjøres hjem</span>', 'font-size: 13.5px; font-weight: 600">Lever hjem</span>')
rep('font-size: 13.5px; font-weight: 600">Hentes i butikk</span>', 'font-size: 13.5px; font-weight: 600">Hent i butikk</span>')

# ── 08: maler først, så rørlegger og elektriker; oppdragskort per fag; bestilling for produkter og tjenester ──
rep('''        <image-slot id="shot-contractor" shape="rect" src="/assets/story/painter-v2.jpg" placeholder="Shot 11 · Maleren i stua"></image-slot>
      </div>''',
    '''        <image-slot id="shot-contractor" shape="rect" src="/assets/story/painter-v2.jpg" placeholder="Shot 11 · Maleren i stua"></image-slot>
      </div>
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ proShot1Op }}">
        <div class="era-ph"></div>
        <image-slot class="era-ph-slot" id="professional-plumber" shape="rect" src="{{ plumberSrc }}" placeholder="Bilde · Rørlegger"></image-slot>
        <div class="era-ph-label" style="opacity: {{ plumberDevOp }}">BILDE · RØRLEGGER</div>
      </div>
      <div style="position: absolute; inset: 0; transform: translateZ(0); backface-visibility: hidden; opacity: {{ proShot2Op }}">
        <div class="era-ph"></div>
        <image-slot class="era-ph-slot" id="professional-electrician" shape="rect" src="{{ electricianSrc }}" placeholder="Bilde · Elektriker"></image-slot>
        <div class="era-ph-label" style="opacity: {{ electricianDevOp }}">BILDE · ELEKTRIKER</div>
      </div>''')
rep('''          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #D4B17A">B · Få hjelp</div>
          <h2 style="margin: 16px 0 0; font-size: clamp(30px, 3.8vw, 50px); line-height: 1.04; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; opacity: {{ proHeadOp }}; transform: {{ proHeadTy }}; text-wrap: balance">Jobben kommer ferdig forstått.</h2>
          <p style="margin: 14px 0 0; font-size: clamp(16px, 1.8vw, 21px); line-height: 1.35; font-weight: 500; color: rgba(247,244,238,0.75); opacity: {{ proSubOp }}">Omfang, bilder, mål og ønsket tid ligger klart. Materialene også. Du gir tilbud, ikke befaring.</p>
        </div>''',
    '''          <div style="font-size: 12px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: #D4B17A">{{ proEyebrow }}</div>
          <div style="display: flex; gap: 5px; flex-wrap: wrap; justify-content: {{ proChipJustify }}; margin-top: 12px; opacity: {{ proTradesOp }}">
            <sc-for list="{{ proTrades }}" as="tr" hint-placeholder-count="7">
              <span style="padding: 5px 10px; border-radius: 999px; background: {{ tr.bg }}; border: 1px solid {{ tr.border }}; font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: {{ tr.fg }}">{{ tr.label }}</span>
            </sc-for>
          </div>
          <h2 style="margin: 12px 0 0; font-size: clamp(28px, 3.4vw, 44px); line-height: 1.04; font-weight: 800; letter-spacing: -0.03em; color: #FFFFFF; opacity: {{ proHeadOp }}; transform: {{ proHeadTy }}; text-wrap: balance">{{ proHead }}</h2>
          <p style="margin: 12px 0 0; font-size: clamp(15px, 1.6vw, 18px); line-height: 1.35; font-weight: 500; color: rgba(247,244,238,0.75); opacity: {{ proSubOp }}">{{ proSub }}</p>
        </div>''')
rep('''            <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.02em">Male stue · 42 m²</div>
            <span style="padding: 5px 10px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 11px; font-weight: 700">Nytt oppdrag</span>
          </div>
          <div style="margin-top: 3px; font-size: 13px; color: #8A8579">Borgveien 14 · 4 bilder vedlagt</div>''',
    '''            <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.02em">{{ jobTitle }}</div>
            <span style="padding: 5px 10px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 11px; font-weight: 700; white-space: nowrap">{{ jobTrade }}</span>
          </div>
          <div style="margin-top: 3px; font-size: 13px; color: #8A8579">{{ jobMeta }}</div>''')
rep('''        <p style="margin: 0; max-width: 440px; text-align: {{ proTextAlign }}; font-size: 15px; line-height: 1.5; color: rgba(247,244,238,0.8); opacity: {{ proBtnOp }}; display: {{ partnerNoteDisplay }}">Kunden har plan, estimat og materialer klare. Færre bomturer, mindre papir. Og jobben blir stående i boligens historikk, med ditt navn på.</p>''',
    '''        <div style="position: relative; width: min(440px, 100%); min-height: {{ proTailH }}; text-align: {{ proTextAlign }}">
          <p style="position: absolute; left: 0; right: 0; top: 0; margin: 0; font-size: 15px; line-height: 1.5; color: rgba(247,244,238,0.8); opacity: {{ proNote0Op }}; display: {{ partnerNoteDisplay }}">Kunden har plan, estimat og materialer klare. Færre bomturer, mindre papir. Og jobben blir stående i boligens historikk, med ditt navn på.</p>
          <div style="position: absolute; left: 0; right: 0; top: 0; opacity: {{ proNote1Op }}; transform: {{ proNote1Ty }}">
            <div style="display: flex; flex-direction: column; gap: 4px; font-size: clamp(14px, 1.5vw, 17px); font-weight: 600; color: rgba(247,244,238,0.85); align-items: {{ proAlign }}">
              <span>Behovet er allerede forstått.</span><span>Fagområdet er identifisert.</span><span>Arbeidsgrunnlaget følger prosjektet.</span>
            </div>
            <div style="margin-top: 10px; font-size: clamp(18px, 2vw, 24px); font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF">Du starter ikke med en tom forespørsel.</div>
          </div>
          <div style="position: absolute; left: 0; right: 0; top: 0; opacity: {{ proNote2Op }}; transform: {{ proNote2Ty }}; display: flex; flex-direction: column; gap: 10px; align-items: {{ proAlign }}">
            <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: {{ proChipJustify }}">
              <span style="padding: 5px 10px; border-radius: 999px; background: rgba(212,177,122,0.18); border: 1px solid rgba(212,177,122,0.5); font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #F7F4EE">Produkter</span>
              <span style="padding: 5px 10px; border-radius: 999px; background: rgba(212,177,122,0.18); border: 1px solid rgba(212,177,122,0.5); font-size: 10.5px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #F7F4EE">Tjenester</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap; justify-content: {{ proChipJustify }}">
              <sc-for list="{{ orderSteps }}" as="os" hint-placeholder-count="4">
                <span style="display: inline-flex; align-items: center; gap: 6px; opacity: {{ os.op }}"><span style="padding: 7px 12px; border-radius: 999px; background: rgba(255,253,248,0.96); font-size: 12.5px; font-weight: 700; color: #131E3A">{{ os.label }}</span><span style="font-size: 12px; color: #D4B17A; opacity: {{ os.arrowOp }}">→</span></span>
              </sc-for>
            </div>
            <p style="margin: 0; font-size: 14.5px; line-height: 1.5; color: rgba(247,244,238,0.8); display: {{ partnerNoteDisplay }}">Én reise for det du kjøper og det du får gjort. Bestilling, betaling og avtalt tid på samme sted.</p>
          </div>
        </div>''')

# ── 09: «Ferdig.» før badet ──
rep('''        <p style="position: absolute; left: 0; right: 0; top: 50%; margin: 0; transform: translateY(-50%) {{ trust0Ty }}; font-size: clamp(24px, 3.2vw, 40px); font-weight: 500; font-style: italic; color: #F7F4EE; opacity: {{ trust0Op }}; line-height: 1.25; text-shadow: 0 2px 24px rgba(15,24,48,0.6)">«Må vi egentlig pusse opp badet?»</p>''',
    '''        <div style="position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%) {{ trustDoneTy }}; opacity: {{ trustDoneOp }}">
          <h2 style="margin: 0; font-size: clamp(48px, 9vw, 120px); font-weight: 800; letter-spacing: -0.04em; color: #FFFFFF; line-height: 1">Ferdig.</h2>
          <p style="margin: 18px 0 0; font-size: clamp(18px, 2.2vw, 26px); font-weight: 600; color: rgba(247,244,238,0.85); opacity: {{ trustDone2Op }}; transform: {{ trustDone2Ty }}">Men ERA stopper ikke der.</p>
        </div>
        <p style="position: absolute; left: 0; right: 0; top: 50%; margin: 0; transform: translateY(-50%) {{ trust0Ty }}; font-size: clamp(24px, 3.2vw, 40px); font-weight: 500; font-style: italic; color: #F7F4EE; opacity: {{ trust0Op }}; line-height: 1.25; text-shadow: 0 2px 24px rgba(15,24,48,0.6)">«Må vi egentlig pusse opp badet?»</p>''')

# ── 10: dokumentasjonen kommer tilbake til boligen ──
rep('''        <div style="position: absolute; left: 20px; top: 20px; pointer-events: none; padding: 9px 14px; border-radius: 999px; background: rgba(255,253,248,0.92); font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; display: flex; gap: 10px; align-items: center">{{ memYear }}<span style="font-family: 'Schibsted Grotesk', sans-serif; font-size: 12px; color: #8A8579">{{ memSeason }}</span></div>''',
    '''        <div style="position: absolute; inset: 0; pointer-events: none; background: rgba(15,24,48,{{ memBackDim }})"></div>
        <div style="position: absolute; inset: 0; pointer-events: none; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; padding: 20px; text-align: center; opacity: {{ memBackOp }}">
          <div style="display: flex; gap: 6px; flex-wrap: wrap; justify-content: center; max-width: 440px">
            <sc-for list="{{ memBackChips }}" as="mb" hint-placeholder-count="8">
              <span style="padding: 6px 11px; border-radius: 999px; background: rgba(255,253,248,0.95); font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #131E3A; opacity: {{ mb.op }}; transform: {{ mb.ty }}">{{ mb.label }}</span>
            </sc-for>
          </div>
          <div style="font-size: clamp(18px, 2vw, 24px); font-weight: 800; letter-spacing: -0.02em; color: #FFFFFF; text-shadow: 0 2px 24px rgba(15,24,48,0.6)">Jobben er ferdig.<br>Boligen er oppdatert.</div>
        </div>
        <div style="position: absolute; left: 20px; top: 20px; pointer-events: none; padding: 9px 14px; border-radius: 999px; background: rgba(255,253,248,0.92); font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 500; display: flex; gap: 10px; align-items: center; opacity: {{ memYearOp }}">{{ memYear }}<span style="font-family: 'Schibsted Grotesk', sans-serif; font-size: 12px; color: #8A8579">{{ memSeason }}</span></div>''')
rep('<p style="margin: 16px 0 0; font-size: 16px; color: #5E6472; opacity: {{ memHead2Op }}">Det som blir gjort i dag gjør neste beslutning enklere.</p>',
    '<p style="margin: 16px 0 0; font-size: 16px; color: #5E6472; opacity: {{ memHead2Op }}">Neste gang ERA hjelper deg, finnes historikken allerede der.</p>')

# ── 12: the big reveal — kategorier → flyt-sløyfe → «Hele boligen. Én sammenhengende flyt.» → agentisk payoff ──
rep('''        <h2 style="margin: 0; font-size: clamp(32px, 4.6vw, 60px); font-weight: 800; letter-spacing: -0.03em; transform: {{ splitHeadTy }}">Din bolig. Vårt bygg.<br><span style="color: #B0935F">Én sammenheng.</span></h2>
        <p style="margin: 0; max-width: 520px; font-size: 17px; line-height: 1.5; color: #5E6472">Fra behov til ferdig jobb — og alt som kommer etterpå. For din bolig og for hele eiendommen.</p>''',
    '''        <h2 style="margin: 0; font-size: clamp(32px, 4.6vw, 60px); font-weight: 800; letter-spacing: -0.03em; transform: {{ splitHeadTy }}; opacity: {{ splitHeadOp }}">{{ splitHead1 }}<br><span style="color: #B0935F">{{ splitHead2 }}</span></h2>
        <p style="margin: 0; max-width: 520px; font-size: 17px; line-height: 1.5; color: #5E6472; opacity: {{ splitHeadOp }}">{{ splitSub }}</p>
        <div style="position: relative; width: min(880px, 100%); height: {{ splitStripH }}">
          <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 6px; flex-wrap: wrap; opacity: {{ splitCatOp }}">
            <sc-for list="{{ splitCats }}" as="sc" hint-placeholder-count="8">
              <span style="padding: 6px 12px; border-radius: 999px; background: #131E3A; color: #F7F4EE; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; opacity: {{ sc.op }}">{{ sc.label }}</span>
            </sc-for>
          </div>
          <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 4px; flex-wrap: wrap; opacity: {{ splitLoopOp }}">
            <sc-for list="{{ splitLoop }}" as="sl" hint-placeholder-count="9">
              <span style="display: inline-flex; align-items: center; gap: 4px; opacity: {{ sl.op }}"><span style="padding: 6px 11px; border-radius: 999px; background: {{ sl.bg }}; border: 1px solid {{ sl.border }}; color: {{ sl.fg }}; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap">{{ sl.label }}</span><span style="font-size: 12px; color: #B0935F; opacity: {{ sl.arrowOp }}">{{ sl.arrow }}</span></span>
            </sc-for>
          </div>
        </div>
        <div style="max-width: 640px; opacity: {{ splitAgentOp }}; transform: {{ splitAgentTy }}">
          <div style="font-size: clamp(18px, 2.2vw, 26px); font-weight: 800; letter-spacing: -0.02em; color: #131E3A">Et agentisk system for hele boligens livsløp.</div>
          <p style="margin: 8px 0 0; font-size: 15.5px; line-height: 1.5; color: #5E6472">ERA kobler boligdata, kunstig intelligens, handel, tjenester og dokumentasjon i én kontinuerlig flyt rundt boligen.</p>
        </div>''')

# ── engine: refs, chapter map, heights, responsive values, bindings ──
rep("const chapMap = { door: 0, home: 0, chaos: 1, see: 1, prio: 2, magic: 3, choice: 4,",
    "const chapMap = { door: 0, home: 0, chaos: 1, see: 1, prio: 2, magic: 3, whole: 3, needs: 3, choice: 4,")
rep("h_magic: H(360), h_choice: H(180), h_commerce: H(300), h_pro: H(260), h_trust: H(320), h_memory: H(340), h_board: H(340), h_split: H(280),",
    "h_magic: H(360), h_whole: H(360), h_needs: H(260), h_choice: H(200), h_commerce: H(300), h_pro: H(400), h_trust: H(380), h_memory: H(360), h_board: H(340), h_split: H(400),")
rep("refMagic: this.ref('magic'), refChoice: this.ref('choice'),", "refMagic: this.ref('magic'), refWhole: this.ref('whole'), refNeeds: this.ref('needs'), refChoice: this.ref('choice'),")
rep("stackAlign: 'start', stackGap: '18px', stackPad: '84px 20px 20px', memEvPad: '4px 0 10px', memEvSize: '16px', partnerNoteDisplay: 'none',",
    "stackAlign: 'start', stackGap: '18px', stackPad: '84px 20px 20px', memEvPad: '4px 0 10px', memEvSize: '16px', partnerNoteDisplay: 'none', comCatDisplay: 'none', choicePad: '20px 22px', proChipJustify: 'flex-start', proTailH: '150px', splitStripH: '150px',")
rep("stackAlign: 'center', stackGap: '48px', stackPad: '0 clamp(24px, 7vw, 120px)', memEvPad: '10px 0 18px', memEvSize: '20px', partnerNoteDisplay: 'block',",
    "stackAlign: 'center', stackGap: '48px', stackPad: '0 clamp(24px, 7vw, 120px)', memEvPad: '10px 0 18px', memEvSize: '20px', partnerNoteDisplay: 'block', comCatDisplay: 'flex', choicePad: '30px 32px', proChipJustify: 'flex-end', proTailH: '150px', splitStripH: '56px',")

# scroll values for the new and changed scenes
rep("    const ch = g('choice');\n    const choiceLOp = seg(ch, 0.22, 1, 0.1), choiceROp = seg(ch, 0.38, 1, 0.1);",
    """    // ── 05b hele boligen: markers on the whole-home image, then out to facade/roof. Positions are % of the frame;
    //    adjust the interior six once the whole-home photograph is delivered (a = scroll progress where each appears).
    const wh = g('whole');
    const wholeOut = ease(ramp(wh, 0.78, 0.9));
    const wholeSpotDefs = [
      ['Maling', '30%', '36%', 0.2, 0], ['Gulv', '44%', '80%', 0.27, 0], ['Kjøkken', '68%', '46%', 0.4, 0], ['Bad', '84%', '28%', 0.47, 0],
      ['Rør og sanitær', '76%', '72%', 0.6, 0], ['Elektro', '16%', '20%', 0.67, 0], ['Fasade', '58%', '56%', 0.86, 1], ['Tak', '64%', '18%', 0.91, 1]
    ];
    const wholeSpots = wholeSpotDefs.map(([label, x, y, a, outer]) => { const op = outer ? seg(wh, a, 1, 0.04) : seg(wh, a, 0.8, 0.04); return { label, x, y, op, scale: 0.94 + op * 0.06 }; });
    const whole0Op = seg(wh, 0.03, 0.16, 0.05), whole1Op = seg(wh, 0.2, 0.36, 0.05), whole2Op = seg(wh, 0.92, 1, 0.04);
    const hasImg = (k) => !!(RS[k] && String(RS[k]).trim());

    // ── 05c flere behov: bad → elektro → fasade/tak, then the line
    const ne = g('needs');
    const needsB = seg(ne, 0.36, 0.6, 0.06), needsC = seg(ne, 0.66, 1, 0.06);
    const needsWords = [['Bad.', 'Fuger, alder, dokumentasjon', '#B0935F', 0.05, 0.28], ['Elektro.', 'Krever fagperson', '#131E3A', 0.4, 0.58], ['Fasade. Tak.', 'Felles ansvar', '#B0935F', 0.68, 0.82]]
      .map(([word, note, dot, a, b]) => { const op = seg(ne, a, b, 0.05); return { word, note, dot, op, ty: ty(op, 14) }; });
    const needsEndOp = seg(ne, 0.9, 1, 0.05);

    const ch = g('choice');
    const choiceLOp = seg(ch, 0.22, 1, 0.1), choiceROp = seg(ch, 0.38, 1, 0.1), choiceCOp = seg(ch, 0.52, 1, 0.1);""")
rep("    const comShotBOp = 0;",
    """    const comShotBOp = 0;
    const comSteps = ['Arbeidsbeskrivelse', 'Materialer', 'Mengde', 'Produkter', 'Pris', 'Tilgjengelighet'].map((label, i, arr) => { const op = seg(co, 0.14 + i * 0.05, 1, 0.05); return { label, op, arrowOp: i < arr.length - 1 ? 1 : 0 }; });
    const comCatChips = ['Maling', 'Gulv', 'Bad', 'Kjøkken', 'Beslag', 'Verktøy'].map((label, i) => ({ label, op: seg(co, 0.55 + i * 0.045, 1, 0.05) }));""")
rep("""    const jobRows = [['Omfang', 'Vegger, 2 strøk'], ['Ønsket tid', 'Uke 38–40'], ['Materialer', 'Ligger klart']].map(([k, v], i) => ({ k, v, op: seg(pr, 0.3 + i * 0.12, 1, 0.05) }));
    const proCardOp = seg(pr, 0.12, 1, 0.1);""",
    """    // three professional states on one sticky scene: painter (existing photo) → plumber → electrician; then ordering for products + services
    const proState = pr >= 0.62 ? 2 : pr >= 0.42 ? 1 : 0;
    const proShot1Op = seg(pr, 0.42, 0.62, 0.05), proShot2Op = seg(pr, 0.64, 1, 0.05);
    const jobCards = [
      { title: 'Male stue · 42 m²', meta: 'Borgveien 14 · 4 bilder vedlagt', trade: 'Maler', rows: [['Omfang', 'Vegger, 2 strøk'], ['Ønsket tid', 'Uke 38–40'], ['Materialer', 'Ligger klart']], at: 0.12 },
      { title: 'Lekkasje under kjøkkenvask', meta: 'Borgveien 14 · 2 bilder og video', trade: 'Rørlegger', rows: [['Omfang', 'Avløp og vannlås'], ['Ønsket tid', 'Denne uken'], ['Grunnlag', 'Bilder, alder, tidligere arbeid']], at: 0.44 },
      { title: 'Ny kurs til kjøkken', meta: 'Borgveien 14 · sikringsskap dokumentert', trade: 'Elektriker', rows: [['Omfang', '1 kurs · 16 A'], ['Ønsket tid', 'Uke 40'], ['Grunnlag', 'Skap, tavle og plan ligger klart']], at: 0.66 }
    ];
    const job = jobCards[proState];
    const jobRows = job.rows.map(([k, v], i) => ({ k, v, op: seg(pr, job.at + 0.06 + i * 0.04, 1, 0.03) }));
    const proCardOp = Math.max(seg(pr, 0.12, 0.38, 0.05), seg(pr, 0.44, 0.58, 0.05), seg(pr, 0.66, 1, 0.05));
    const proHeads = [['B · Få hjelp', 'Jobben kommer ferdig forstått.', 'Omfang, bilder, mål og ønsket tid ligger klart. Materialene også. Du gir tilbud, ikke befaring.'],
      ['B · Riktig fagområde', 'Riktig fagperson for riktig jobb.', 'ERA kobler behovet til riktig fagområde og relevante fagpersoner. Rørlegger til røret, elektriker til kursen.'],
      ['Fra valg til gjennomføring', 'Fra valg til gjennomføring.', 'Produkter og tjenester går i samme reise: bestill, betal, avtal tid — og jobben blir gjort.']];
    const proTextState = pr >= 0.84 ? 2 : pr >= 0.4 ? 1 : 0;
    const proHeadOp = Math.max(seg(pr, 0.05, 0.36, 0.05), seg(pr, 0.42, 0.8, 0.05), seg(pr, 0.86, 1, 0.05));
    const proSubOp = Math.max(seg(pr, 0.2, 0.36, 0.05), seg(pr, 0.5, 0.8, 0.05), seg(pr, 0.9, 1, 0.05));
    const proTradeNames = ['Maler', 'Tømrer', 'Rørlegger', 'Elektriker', 'Flislegger', 'Gulvlegger', 'Taktekker'];
    const proActiveTrade = ['Maler', 'Rørlegger', 'Elektriker'][proState];
    const proTrades = proTradeNames.map((label) => { const on = label === proActiveTrade; return { label, bg: on ? '#D4B17A' : 'rgba(247,244,238,0.08)', border: on ? '#D4B17A' : 'rgba(247,244,238,0.25)', fg: on ? '#131E3A' : 'rgba(247,244,238,0.8)' }; });
    const proTradesOp = seg(pr, 0.42, 1, 0.05);
    const proNote0Op = seg(pr, 0.28, 0.38, 0.05), proNote1Op = seg(pr, 0.5, 0.8, 0.05), proNote2Op = seg(pr, 0.88, 1, 0.05);
    const orderSteps = ['Produkt / tjeneste', 'Bestill', 'Betal', 'Lever · hent · avtal tid'].map((label, i, arr) => ({ label, op: seg(pr, 0.9 + i * 0.02, 1, 0.02), arrowOp: i < arr.length - 1 ? 1 : 0 }));""")
rep("""    const bathCardOp = seg(t, 0.62, 1, 0.08), bathCardTy = ty(bathCardOp, 24);""",
    """    const bathCardOp = seg(t, 0.7, 1, 0.08), bathCardTy = ty(bathCardOp, 24);
    const trustDoneOp = seg(t, 0.03, 0.17, 0.05), trustDone2Op = seg(t, 0.09, 0.17, 0.04);""")
rep("""    const memData = [['2026', 'ERA kobles til', 0.08], ['2028', 'Fasade og balkonger utbedres', 0.3], ['2031', 'Tak og vinduer fornyes', 0.5], ['2036', 'Godt vedlikeholdt — verdien består', 0.68]];""",
    """    const memBackOp = 1 - ramp(me, 0.12, 0.2);
    const memBackChips = ['Utført arbeid', 'Fagperson', 'Produkter', 'Dato', 'Kostnad', 'Bilder', 'Kvittering', 'Garanti'].map((label, i) => { const op = seg(me, 0.005 + i * 0.012, 0.12, 0.02); return { label, op, ty: ty(op, 10) }; });
    const memData = [['2026', 'Stua malt — dokumentert', 0.22], ['2028', 'Fasade og balkonger utbedres', 0.4], ['2031', 'Tak og vinduer fornyes', 0.56], ['2036', 'Godt vedlikeholdt — verdien består', 0.7]];""")
rep("    const memLineH = `${Math.round(ramp(me, 0.08, 0.68) * 100)}%`;", "    const memLineH = `${Math.round(ramp(me, 0.22, 0.7) * 100)}%`;")
rep("    const memDocs = [['Tilstandsrapport', 0.1], ['Fasadeprosjekt · FDV', 0.32], ['Takgaranti', 0.52], ['Vedlikeholdsplan', 0.7]]",
    "    const memDocs = [['Tilstandsrapport', 0.24], ['Fasadeprosjekt · FDV', 0.42], ['Takgaranti', 0.58], ['Vedlikeholdsplan', 0.72]]")
rep("    const sp = g('split'), merge = ease(ramp(sp, 0.6, 0.8));",
    """    const sp = g('split'), merge = ease(ramp(sp, 0.6, 0.8));
    const splitReveal = sp >= 0.885;
    const splitHeadOp = splitReveal ? ramp(sp, 0.885, 0.91) : 1 - ramp(sp, 0.86, 0.885);
    const splitCats = ['Maling', 'Gulv', 'Bad', 'Kjøkken', 'Elektro', 'Rør og sanitær', 'Fasade', 'Tak'].map((label, i) => ({ label, op: seg(sp, 0.8 + i * 0.008, 0.87, 0.02) }));
    const splitLoop = ['Boligdata', 'Forstå', 'Vurdere', 'Handle', 'Produkt / fagperson', 'Bestille / betale', 'Utføre', 'Dokumentere', 'Boligen'].map((label, i, arr) => {
      const last = i === arr.length - 1;
      return { label, op: seg(sp, 0.9 + i * 0.008, 1, 0.02), arrow: last ? '↺' : '→', arrowOp: 1, bg: last ? '#131E3A' : '#FFFFFF', border: last ? '#131E3A' : '#E3DDD0', fg: last ? '#F7F4EE' : '#131E3A' };
    });
    const splitLoopOp = seg(sp, 0.9, 1, 0.03), splitAgentOp = seg(sp, 0.95, 1, 0.03);""")

# bindings
rep("      magicPlanOp: seg(m, 0.44, 1, 0.05), magicPlanTy: ty(seg(m, 0.44, 1, 0.05), 30), planRows, magicDoneOp: seg(m, 0.9, 1, 0.05),",
    """      magicPlanOp: seg(m, 0.44, 1, 0.05), magicPlanTy: ty(seg(m, 0.44, 1, 0.05), 30), planRows, magicDoneOp: seg(m, 0.9, 1, 0.05),
      wholeHomeSrc: RS.wholeHome || '', wholeHomeDevOp: hasImg('wholeHome') ? 0 : 1, plumberSrc: RS.plumber || '', plumberDevOp: hasImg('plumber') ? 0 : 1, electricianSrc: RS.electrician || '', electricianDevOp: hasImg('electrician') ? 0 : 1,
      wholeImgScale: 1 + wh * 0.03, wholeOutOp: wholeOut, wholeDim: 0.1 + seg(wh, 0, 0.18, 0.06) * 0.3 + seg(wh, 0.92, 1, 0.04) * 0.25, wholeSpots,
      whole0Op, whole0Ty: ty(whole0Op), whole1Op, whole1Ty: ty(whole1Op, 12), whole2Op, whole2Ty: ty(whole2Op, 16),
      needsAOp: 1 - needsB - needsC, needsBOp: needsB, needsCOp: needsC, needsDim: 0.22 + needsEndOp * 0.4, needsWords, needsEndOp, needsEndTy: ty(needsEndOp, 16),
      choiceCOp, choiceCTy: ty(choiceCOp, 30),
      comSteps, comCatChips,
      proShot1Op, proShot2Op, proEyebrow: proHeads[proTextState][0], proHead: proHeads[proTextState][1], proSub: proHeads[proTextState][2], proTrades, proTradesOp,
      jobTitle: job.title, jobMeta: job.meta, jobTrade: job.trade, proNote0Op, proNote1Op, proNote1Ty: ty(proNote1Op, 14), proNote2Op, proNote2Ty: ty(proNote2Op, 14), orderSteps,
      trustDoneOp, trustDoneTy: ty(trustDoneOp), trustDone2Op, trustDone2Ty: ty(trustDone2Op, 10),
      memBackOp, memBackDim: memBackOp * 0.5, memBackChips, memYearOp: 1 - memBackOp,
      splitHeadOp, splitHead1: splitReveal ? 'Hele boligen.' : 'Din bolig. Vårt bygg.', splitHead2: splitReveal ? 'Én sammenhengende flyt.' : 'Én sammenheng.',
      splitSub: splitReveal ? 'Fra boligdata til handling. Fra handling tilbake til boligen.' : 'Fra behov til ferdig jobb — og alt som kommer etterpå. For din bolig og for hele eiendommen.',
      splitCats, splitCatOp: seg(sp, 0.8, 0.87, 0.02), splitLoop, splitLoopOp, splitAgentOp, splitAgentTy: ty(splitAgentOp, 12),""")
rep("      proImgScale: 1 + pr * 0.035, proHeadOp: seg(pr, 0.05, 1, 0.08), proHeadTy: ty(seg(pr, 0.05, 1, 0.08)), proSubOp: seg(pr, 0.5, 1, 0.08), proCardOp, proCardTy: ty(proCardOp, 40), jobRows, proBtnOp: seg(pr, 0.72, 1, 0.06),",
    "      proImgScale: 1 + pr * 0.035, proHeadOp, proHeadTy: ty(proHeadOp), proSubOp, proCardOp, proCardTy: ty(proCardOp, 40), jobRows, proBtnOp: Math.max(seg(pr, 0.3, 0.38, 0.04), seg(pr, 0.54, 0.58, 0.04), seg(pr, 0.76, 1, 0.04)),")
rep("      trustImgOp: 0.6 + seg(t, 0.03, 1, 0.1) * 0.4, trustImgScale: 1 + t * 0.035, trustDim: ramp(t, 0.3, 0.5) * 0.35,\n      trust0Op: seg(t, 0.05, 0.28), trust0Ty: ty(seg(t, 0.05, 0.28)), trust1Op: seg(t, 0.38, 0.7, 0.06), trust2Op: seg(t, 0.5, 0.7, 0.05), trust2Ty: ty(seg(t, 0.5, 0.7, 0.05), 12),\n      trust3Op: seg(t, 0.8, 1, 0.06), trust3Ty: ty(seg(t, 0.8, 1, 0.06)),",
    "      trustImgOp: 0.6 + seg(t, 0.03, 1, 0.1) * 0.4, trustImgScale: 1 + t * 0.035, trustDim: ramp(t, 0.42, 0.58) * 0.35,\n      trust0Op: seg(t, 0.24, 0.42), trust0Ty: ty(seg(t, 0.24, 0.42)), trust1Op: seg(t, 0.5, 0.76, 0.06), trust2Op: seg(t, 0.6, 0.76, 0.05), trust2Ty: ty(seg(t, 0.6, 0.76, 0.05), 12),\n      trust3Op: seg(t, 0.84, 1, 0.06), trust3Ty: ty(seg(t, 0.84, 1, 0.06)),")
rep("      splitMergeOp: ramp(sp, 0.64, 0.78), splitLogoScale: 0.7 + ramp(sp, 0.64, 0.84) * 0.3, splitHeadTy: ty(ramp(sp, 0.7, 0.9), 24),",
    "      splitMergeOp: ramp(sp, 0.64, 0.78), splitLogoScale: (0.7 + ramp(sp, 0.64, 0.84) * 0.3) * (1 - splitLoopOp * 0.45), splitHeadTy: ty(ramp(sp, 0.7, 0.88), 24),")

if missing:
    print("MISSING:"); [print(" -", x) for x in missing]; sys.exit(1)
open(dst, 'w', encoding='utf-8').write(s)
print('written', dst, len(s))
