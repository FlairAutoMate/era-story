# -*- coding: utf-8 -*-
"""Generates the audience subpages (/boligeier, /styret, /handverker, /faghandel) from one
template and one content dict. Run from the project root: python tools/build-pages.py"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUDIENCES = {
    "boligeier": dict(
        key="owner", nav="Boligeier", title="ERA for boligeiere",
        label="For boligeier", hook="Boligeierskap uten gjetting.",
        lede="ERA forstår hva boligen din trenger, og hva som bør gjøres først. Tilstand, historikk, dokumentasjon og prioriteringer, samlet i én plan for hjemmet.",
        image="/assets/story/house-day-sun.jpg", image_pos="62% 48%",
        steps=[
            ("Boligen kartlegges", "Tilstandsrapport, FDV, kvitteringer og bilder samles på ett sted. Det du har liggende i skuffen, på e-post og på telefonen."),
            ("ERA forstår", "Hver del av boligen får tilstand, alder og neste forventede behov. Ikke bare det du ser, men det bak veggen også."),
            ("Du får en plan", "Hva som haster, hva som kan vente, og hva det koster. «Vi vil male stua» blir veggflate, forarbeid, strøk, tid og pris."),
            ("Gjør det selv, eller få hjelp", "Materialene er beregnet og kan bestilles. Eller jobben går til håndverker, ferdig beskrevet. Alt blir historikk i boligen."),
        ],
        gains=[
            ("Vit hva som haster", "Og hva som kan vente. Noen ganger er riktig råd å gjøre ingenting ennå."),
            ("Slutt på gjetting", "Kostnad, tid og forarbeid er regnet ut før du bestemmer deg."),
            ("Alt på ett sted", "Dokumentasjonen følger boligen, også til neste eier."),
            ("Dine data", "Lagret kryptert i Norge. Du bestemmer hvem som ser dem."),
        ],
        example=dict(title="Plan · Male stua", meta="Borgveien 14", rows=[("Vegg", "42 m²"), ("Forbehandling", "Lett sparkling"), ("Strøk", "2"), ("Tid", "1–2 dager"), ("Estimert kostnad", "ca. 6 800 kr")], note="Fra «vi vil male stua» til en plan du kan bestille etter. På minutter."),
        faq=[
            ("Må jeg ha tilstandsrapport?", "Nei. ERA starter med det du har. Jo mer du legger inn, jo mer presis blir planen."),
            ("Er ERA en markedsplass?", "Nei. ERA hjelper deg å ta riktig avgjørelse, også når den er å vente. Vi tjener ikke på at du pusser opp."),
            ("Hva skjer med dataene mine?", "De lagres kryptert i Norge og deles bare når du velger det: med håndverker, styret eller kjøper."),
        ],
        form_field="Adressen til boligen", form_cta="Finn min bolig",
        done=("Takk. Vi finner boligen din.", "Du hører fra oss når ERA er klar for adressen."),
        story="#boligeier",
    ),
    "styret": dict(
        key="board", nav="Styret", title="ERA for borettslag og sameier",
        label="For styret", hook="Styret skifter. Planen består.",
        lede="Tilstand, dokumentasjon og vedlikeholdsplan for hele eiendommen, klar til hvert styremøte og hver generalforsamling. Planen følger bygget, ikke menneskene.",
        image="/assets/story/block-exterior.jpg", image_pos="50% 50%",
        steps=[
            ("Bygget kartlegges", "Tilstand, FDV-dokumentasjon og historikk for fasade, tak, fellesareal og tekniske anlegg. Det forrige styre visste, og det ingen skrev ned."),
            ("ERA prioriterer", "Hva som haster, hva som kan vente, og hva det koster. Fordelt på seksjonene, år for år."),
            ("Styret vedtar", "Beslutningsgrunnlaget er ett ark, ikke en perm. Generalforsamlingen får svar på hvorfor, når og hvor mye."),
            ("Jobben bestilles ferdig beskrevet", "Håndverkeren får omfang, bilder og ønsket tid. Tilbudene blir sammenlignbare, og jobben blir dokumentert i eiendommens historikk."),
        ],
        gains=[
            ("Færre overraskelser", "Felleskostnadene følger en plan, ikke et lekket tak."),
            ("Ett ark til generalforsamlingen", "Tilstand, prioritet og kostnad på samme side. Vedtaket tar minutter."),
            ("Kontinuitet", "Nytt styre arver planen, dokumentasjonen og historikken. Ikke en e-postkonto."),
            ("Spart tid for frivillige", "Mindre leting, færre befaringer, ferdig beskrevne bestillinger."),
        ],
        example=dict(title="Vedlikeholdsplan · Fasade", meta="24 seksjoner", rows=[("Tilstand", "Slitt, ikke kritisk"), ("Anbefalt år", "2027"), ("Estimert kostnad", "1,2 mill"), ("Per seksjon", "ca. 50 000 kr"), ("Neste", "Tak · 2031")], note="Vedtaket tar ti minutter, ikke to møter. Håndverkeren har allerede fått jobben beskrevet."),
        faq=[
            ("Passer ERA for små sameier?", "Ja. Et sameie med fire seksjoner har de samme spørsmålene som ett med førti. Planen skalerer."),
            ("Erstatter ERA forretningsfører?", "Nei. ERA holder orden på bygget, ikke regnskapet. Forretningsføreren kan få tilgang til planen."),
            ("Hvem eier dataene?", "Eiendommen. Styret bestemmer hvem som ser dem. Ved styreskifte følger alt med."),
        ],
        form_field="Adressen til bygget", form_cta="Få planen for eiendommen",
        done=("Takk. Vi ser på eiendommen.", "Styret får et forslag til plan, klart til neste møte."),
        story="#styret",
    ),
    "handverker": dict(
        key="pro", nav="Håndverker", title="ERA for håndverkere",
        label="For håndverkere", hook="Jobben kommer ferdig forstått.",
        lede="Omfang, bilder, mål og ønsket tid ligger klart. Materialene også. Du gir tilbud, ikke befaring.",
        image="/assets/story/contractor.jpg", image_pos="50% 30%",
        steps=[
            ("Boligeieren melder et behov", "«Vi vil male stua.» Eller styret vedtar en fasade. Behovet oppstår i en plan, ikke i en telefon på kvelden."),
            ("ERA beskriver jobben", "Flate, tilstand, forarbeid, ønsket tid og bilder. Materialene er beregnet, og kunden har allerede et estimat."),
            ("Du gir tilbud", "På et oppdrag som er forstått. Ingen bomtur, ingen gjetting på omfang."),
            ("Jobben blir historikk", "Det du gjorde står i boligens dokumentasjon, med ditt navn på. Neste behov i samme bolig finner deg."),
        ],
        gains=[
            ("Kvalifiserte kunder", "De har plan og estimat før de spør. Tilbudet ditt treffer."),
            ("Færre bomturer", "Befaringen er gjort digitalt. Du reiser når jobben er din."),
            ("Mindre papir", "Omfang, materialer og dokumentasjon er ferdig når du kommer."),
            ("Gjenkjøp", "Boligen husker hvem som gjorde jobben. Det gjør styret også."),
        ],
        example=dict(title="Male stue · 42 m²", meta="Borgveien 14 · 4 bilder vedlagt", rows=[("Omfang", "Vegger, 2 strøk"), ("Forbehandling", "Lett sparkling"), ("Ønsket tid", "Uke 38–40"), ("Materialer", "Ligger klart"), ("Kundens estimat", "ca. 6 800 kr")], note="Slik ser et oppdrag ut når det kommer til deg. Du svarer med tilbud, ikke med spørsmål."),
        faq=[
            ("Koster det noe å motta oppdrag?", "ERA rulles ut trinnvis. Registrer firmaet, så tar vi kontakt med vilkårene som gjelder i ditt område."),
            ("Konkurrerer jeg med mange?", "Kunden ber om tilbud på et beskrevet oppdrag. Du ser omfanget før du bruker tid."),
            ("Hva med dokumentasjon etter jobben?", "Bilder og beskrivelse legges i boligens historikk. Det er din referanse neste gang."),
        ],
        form_field="Firmanavn eller organisasjonsnummer", form_cta="Motta oppdrag",
        done=("Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
        story="#handverker",
    ),
    "faghandel": dict(
        key="partner", nav="Faghandel", title="ERA for faghandel",
        label="For faghandel", hook="Behovet er beregnet før kunden går i butikken.",
        lede="Riktig produkt, riktig mengde, riktig tid, i én bestilling. Fra boliger og fra hele borettslag. Uavhengig av kjede.",
        image="/assets/story/illus-materials.svg", image_pos="50% 50%",
        steps=[
            ("ERA beregner behovet", "Flate, tilstand og forarbeid gir mengder: 2 × 10 liter maling, 1 × 5 kg sparkel, ruller, pensler, maskering."),
            ("Kunden velger levering", "Kjøres hjem, hentes i butikk, eller håndverkeren henter. Kunden bestemmer, dere leverer."),
            ("Bestillingen kommer til dere", "Riktige varelinjer, riktig mengde, riktig tidspunkt. Hele prosjektet, ikke én boks."),
            ("Neste prosjekt er kjent", "Planlagte fasader, tak og vinduer gir prognose. Også når det er 24 seksjoner i et borettslag."),
        ],
        gains=[
            ("Kvalifisert etterspørsel", "Bestillingen oppstår fra et faktisk behov i boligen, ikke fra inspirasjon."),
            ("Færre feilkjøp og returer", "Mengdene er regnet ut. Kunden kjøper riktig første gang."),
            ("Større kurv", "Hele prosjektet i én bestilling, med forarbeid og verktøy."),
            ("Prognose", "Vedlikeholdsplaner forteller hva som skal kjøpes neste år."),
        ],
        example=dict(title="Bestilling · Male stua", meta="Levering: kjøres hjem", rows=[("Maling", "2 × 10 L"), ("Sparkel", "1 × 5 kg"), ("Ruller", "2 stk"), ("Pensler", "3 stk"), ("Maskering", "2 ruller")], note="Mengder beregnet for 42 m², to strøk. Bestillingen er nesten skrevet før kunden har valgt farge."),
        faq=[
            ("Er ERA knyttet til én kjede?", "Nei. ERA kobler behov til partnere uavhengig av kjede. Kunden velger hvor bestillingen går."),
            ("Hvordan får vi bestillingene?", "Vi tilpasser oss deres bestillingsflyt, fra e-post til integrasjon. Ta kontakt, så viser vi hvordan."),
            ("Hva med borettslag?", "Styrets vedlikeholdsplan gir store, planlagte bestillinger. Fasade, tak og vinduer, år for år."),
        ],
        form_field="Kjede eller butikk", form_cta="Bli partner",
        done=("Takk. Vi tar kontakt.", "Vi viser hvordan beregnede behov i boliger og borettslag blir bestillinger hos dere."),
        story="#partnere",
    ),
}

ORDER = ["boligeier", "styret", "handverker", "faghandel"]


def esc(t):
    return html.escape(t, quote=True)


def page(slug, a):
    cur = ' aria-current="page"'
    nav_links = "".join(
        f'<a href="/{s}"{cur if s == slug else ""}>{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER
    )
    steps = "".join(
        f'<li><span class="n">0{i+1}</span><div><h3>{esc(h)}</h3><p>{esc(t)}</p></div></li>' for i, (h, t) in enumerate(a["steps"])
    )
    gains = "".join(f'<div class="gain"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in a["gains"])
    ex = a["example"]
    rows = "".join(f'<div class="row"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in ex["rows"])
    faq = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for q, ans in a["faq"])
    others = [s for s in ORDER if s != slug]
    other_links = " · ".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in others)
    done_head, done_sub = a["done"]
    is_svg = a["image"].endswith(".svg")
    return f'''<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(a["title"])} — ERA</title>
<meta name="description" content="{esc(a["lede"])}">
<meta name="theme-color" content="#0F1830">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
</head>
<body data-audience="{a["key"]}">
<nav class="nav" aria-label="Hovedmeny">
  <div class="pill">
    <a class="brand" href="/">era<span>.</span></a>
    <div class="links"><a href="/">Historien</a>{nav_links}</div>
    <a class="cta" href="#skjema">{esc(a["form_cta"])}</a>
  </div>
</nav>

<header class="hero">
  <div class="hero-media">{'<img src="' + a["image"] + '" alt="" style="object-position: ' + a["image_pos"] + '">'}</div>
  <div class="hero-text">
    <div class="label">{esc(a["label"])}</div>
    <h1>{esc(a["hook"])}</h1>
    <p class="lede">{esc(a["lede"])}</p>
    <div class="hero-actions"><a class="btn" href="#skjema">{esc(a["form_cta"])}</a><a class="link" href="/{a["story"]}">Se det i historien →</a></div>
  </div>
</header>

<main>
  <section class="section">
    <div class="label">Slik fungerer det</div>
    <h2>Fire steg. Ingen gjetting.</h2>
    <ol class="steps">{steps}</ol>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="label">Det får {"dere" if a["key"] in ("board", "partner") else "du"}</div>
      <h2>Gevinsten</h2>
      <div class="gains">{gains}</div>
    </div>
  </section>

  <section class="section">
    <div class="example">
      <div class="card">
        <div class="card-head"><span class="label">{esc(ex["title"])}</span><span class="meta">{esc(ex["meta"])}</span></div>
        {rows}
      </div>
      <div class="example-text"><h2>Slik ser det ut.</h2><p>{esc(ex["note"])}</p></div>
    </div>
  </section>

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
      <h2>{esc(a["hook"])}</h2>
      <p class="lede light">{esc(a["lede"])}</p>
      <form id="era-lead" class="lead" data-audience="{a["key"]}">
        <label class="sr" for="lead-value">{esc(a["form_field"])}</label>
        <input id="lead-value" name="value" type="text" autocomplete="off" required minlength="3" maxlength="200" placeholder="{esc(a["form_field"])}">
        <input name="website" type="text" tabindex="-1" autocomplete="off" aria-hidden="true" class="hp">
        <button type="submit">{esc(a["form_cta"])}</button>
      </form>
      <div class="done" role="status" aria-live="polite" hidden><b>{esc(done_head)}</b><span>{esc(done_sub)}</span></div>
      <div class="err" hidden></div>
      <p class="fine">Ingen binding. Dataene lagres kryptert i Norge og brukes bare til å ta kontakt.</p>
    </div>
  </section>
</main>

<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/#data">Personvern</a><a href="/">Historien</a></div>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 ERA AS</span><span>Oslo</span></div>
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
