# -*- coding: utf-8 -*-
"""Builds om-era/index.html — the "Om ERA" film as its own page — from index.html and
tools/om-era-template.html. The page reuses the story's head, nav, progress rail, finale,
footer and the whole <script data-dc-script> (one scroll engine for both pages); only the
scenes between the rail and the finale differ. Usage: python tools/build-om-era.py"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
tpl = open(os.path.join(ROOT, 'tools', 'om-era-template.html'), encoding='utf-8').read()

def between(s, a, b):
    i = s.index(a); j = s.index(b, i)
    return s[:i], s[i:j], s[j:]

# 1. head + everything up to and including the progress rail / fixed CTA
rail_end = '  <!-- 0 · DØREN'
head_and_nav, _, rest = src.partition(rail_end)
assert head_and_nav and rest, 'rail/door marker'

# 2. finale + footer + script
fin_start = '  <!-- 14 · ERA — WIDE finale'
_, finale_and_tail = src.split(fin_start, 1)
finale_and_tail = fin_start + finale_and_tail

# Om ERA's finale opens with the chapter's closing lines before the logo and form.
beats = re.search(r'<!-- OM ERA FINALE BEATS -->\n(.*?)<!-- /OM ERA FINALE BEATS -->\n', tpl, re.S)
assert beats, 'finale beats block in template'
scenes = tpl[:beats.start()] + tpl[beats.end():]
logo_line = '      <div style="position: absolute; left: clamp(24px, 7vw, 120px); right: 24px; top: 50%; transform: translateY(-50%); max-width: 560px">\n        <div style="font-size: clamp(56px, 8vw, 120px);'
assert finale_and_tail.count(logo_line) == 1, 'finale logo block'
finale_and_tail = finale_and_tail.replace(logo_line, beats.group(1) + logo_line, 1)

page = head_and_nav + scenes + finale_and_tail

# 3. page identity: title, description, canonical, body flag, in-page links become cross-page links
def rep(a, b, count=1):
    global page
    assert page.count(a) >= 1, a[:80]
    page = page.replace(a, b, count)
rep('<title>ERA — Velkommen til en ny ERA</title>', '<title>Om ERA — Et agentisk system for hele boligens livsløp</title>')
rep('<meta name="description" content="ERA forstår boligen din og hjelper deg å vite hva som bør gjøres — og hva som kan vente.">',
    '<meta name="description" content="Hvorfor ERA finnes, teknologien bak, visjonen og menneskene. ERA kobler boligdata, kunstig intelligens, handel, tjenester og dokumentasjon i én flyt rundt boligen.">')
rep('<link rel="canonical" href="https://era-story.vercel.app/">', '<link rel="canonical" href="https://era-story.vercel.app/om-era">')
rep('<meta property="og:url" content="https://era-story.vercel.app/">', '<meta property="og:url" content="https://era-story.vercel.app/om-era">')
rep('<meta property="og:title" content="ERA — Boligeierskap uten gjetting">', '<meta property="og:title" content="Om ERA — Et agentisk system for hele boligens livsløp">')
rep('<meta name="twitter:title" content="ERA — Boligeierskap uten gjetting">', '<meta name="twitter:title" content="Om ERA — Et agentisk system for hele boligens livsløp">')
rep('<body>', '<body data-page="om-era">')
# Om ERA's first paint is the about-hero photo, not the homepage's door — swap the LCP preload to match.
rep('<link rel="preload" href="/assets/story/door-evening-v4-m.jpg" as="image" media="(max-width: 899px)" fetchpriority="high">',
    '<link rel="preload" href="/assets/story/about-hero-v4-m.jpg" as="image" media="(max-width: 899px)" fetchpriority="high">')
rep('<link rel="preload" href="/assets/story/door-evening-v4.jpg" as="image" media="(min-width: 900px)" fetchpriority="high">',
    '<link rel="preload" href="/assets/story/about-hero-v4.jpg" as="image" media="(min-width: 900px)" fetchpriority="high">')
rep('<a href="#hjem" aria-label="ERA — til toppen"', '<a href="/" aria-label="ERA — til forsiden"')
page = page.replace("['hva', 'Hva ERA gjør', '#hva']", "['hva', 'Hva ERA gjør', '/#hva']")
page = page.replace("[['#hva', 'Hva ERA gjør'], ['/boligeier', 'Boligeier']", "[['/#hva', 'Hva ERA gjør'], ['/boligeier', 'Boligeier']")
page = page.replace('<a href="#hva">Hva ERA gjør</a>', '<a href="/#hva">Hva ERA gjør</a>')
page = page.replace("if (href === '#boligeier' || href === '#hva' || href === '#hjem') return 'owner';", "if (href === '#boligeier' || href === '#hva' || href === '/#hva' || href === '#hjem' || href === '/') return 'owner';")

out = os.path.join(ROOT, 'om-era', 'index.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write(page)
print('wrote om-era/index.html', len(page))
