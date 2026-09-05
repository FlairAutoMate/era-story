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
        image="/assets/story/couple-sofa-window-v4.jpg", image_pos="45% 50%",
        steps=[
            ("Boligen kartlegges", "Tilstandsrapport, FDV, kvitteringer og bilder samles på ett sted. Det du har liggende i skuffen, på e-post og på telefonen."),
            ("ERA forstår", "Hver del av boligen får tilstand, alder og neste forventede behov. Ikke bare det du ser, men det bak veggen også."),
            ("Du får en plan", "Hva som haster, hva som kan vente, og hva det koster. «Vi vil male stua» blir veggflate, forarbeid, strøk, tid og pris. Det samme gjelder bad, gulv, elektro, rør og tak — og ERA sier fra når jobben krever fagperson."),
            ("Gjør det selv, eller få hjelp", "Materialene er beregnet og kan bestilles. Eller jobben går til håndverker, ferdig beskrevet. Alt blir historikk i boligen."),
        ],
        gains=[
            ("Vit hva som haster", "Og hva som kan vente. Noen ganger er riktig råd å gjøre ingenting ennå."),
            ("Slutt på gjetting", "Kostnad, tid og forarbeid er regnet ut før du bestemmer deg."),
            ("Alt på ett sted", "Dokumentasjonen følger boligen, også til neste eier."),
            ("Dine data", "Lagret kryptert innenfor EU/EØS. Du bestemmer hvem som ser dem."),
        ],
        example=dict(title="Plan · Male stua", meta="Borgveien 14", rows=[("Vegg", "42 m²"), ("Forbehandling", "Lett sparkling"), ("Strøk", "2"), ("Tid", "1–2 dager"), ("Estimert kostnad", "ca. 6 800 kr")], note="Fra «vi vil male stua» til en plan du kan bestille etter. På minutter."),
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
        label="For styret", hook="Styret skifter. Planen består.",
        lede="Tilstand, dokumentasjon og vedlikeholdsplan for hele eiendommen, klar til hvert styremøte og hver generalforsamling. Planen følger bygget, ikke menneskene.",
        image="/assets/story/block-bikes-v3.jpg", image_pos="50% 50%",
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
        form_field="Adressen til bygget", form_label="Adresse", form_cta="Få planen for eiendommen",
        done=("Takk. Vi ser på eiendommen.", "Vi tar kontakt med et forslag til plan, klart til neste møte."),
        story="#styret",
    ),
    "handverker": dict(
        key="pro", nav="Håndverker", title="ERA for håndverkere",
        label="For håndverkere", hook="Jobben kommer ferdig forstått.",
        lede="Omfang, bilder, mål og ønsket tid ligger klart. Materialene også. Du gir tilbud, ikke befaring.",
        image="/assets/story/painter-v3.jpg", image_pos="30% 50%",
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
        form_field="Firmanavn eller organisasjonsnummer", form_label="Firma", form_cta="Motta oppdrag",
        done=("Takk. Du er registrert.", "Vi tar kontakt når det er ferdig beskrevne oppdrag i ditt område."),
        story="#handverker",
    ),
    "faghandel": dict(
        key="partner", nav="Faghandel", title="ERA for faghandel",
        label="For faghandel", hook="Behovet er beregnet før kunden går i butikken.",
        lede="Riktig produkt, riktig mengde, riktig tid, i én bestilling. Fra boliger og fra hele borettslag. Uavhengig av kjede.",
        image="/assets/story/materials-floor-v3.jpg", image_pos="50% 50%",
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
            ("Hvordan får vi bestillingene?", "Vi finner en bestillingsflyt som passer dere. Ta kontakt, så viser vi hvordan."),
            ("Hva med borettslag?", "Styrets vedlikeholdsplan gir store, planlagte bestillinger. Fasade, tak og vinduer, år for år."),
        ],
        form_field="Kjede eller butikk", form_label="Butikk", form_cta="Bli partner",
        done=("Takk. Vi tar kontakt.", "Vi tar kontakt og viser hvordan beregnede behov blir bestillinger hos dere."),
        story="#partnere",
    ),
}

ORDER = ["boligeier", "styret", "handverker", "faghandel"]


def esc(t):
    return html.escape(t, quote=True)


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


MENU = [("/", "Historien"), ("/boligeier", "Boligeier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/personvern", "Personvern")]


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
    steps = "".join(
        f'<li><span class="n">0{i+1}</span><div><h3>{esc(h)}</h3><p>{esc(t)}</p></div></li>' for i, (h, t) in enumerate(a["steps"])
    )
    gains = "".join(f'<div class="gain"><h3>{esc(h)}</h3><p>{esc(t)}</p></div>' for h, t in a["gains"])
    ex = a["example"]
    rows = "".join(f'<div class="row"><span>{esc(k)}</span><b>{esc(v)}</b></div>' for k, v in ex["rows"])
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

<header class="hero">
  <div class="hero-media">{'<img src="' + a["image"] + '" alt="" style="object-position: ' + a["image_pos"] + '">'}</div>
  <div class="hero-text">
    <div class="label">{esc(a["label"])}</div>
    <h1>{esc(a["hook"])}</h1>{f'<div class="beta-badge">{esc(beta["badge"])}</div><p class="beta-note">{esc(beta["note"])}</p>' if beta else ''}
    <p class="lede">{esc(a["lede"])}</p>
    <div class="hero-actions">{f'<a class="btn" href="#skjema">{esc(beta["cta_primary"])}</a><a class="link" href="#slik">{esc(beta["cta_secondary"])}</a>' if beta else f'<a class="btn" href="#skjema">{esc(a["form_cta"])}</a><a class="link" href="/{a["story"]}">Se det i historien →</a>'}</div>
  </div>
</header>

<main>
  <section class="section" id="slik">
    <div class="label">Slik fungerer det</div>
    <h2>Fire steg. Ingen gjetting.</h2>
    <ol class="steps">{steps}</ol>
  </section>

  {beta_section}

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
    </div>
  </section>
</main>

<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/#om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
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
            "Når du sender inn skjemaet på historien eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede eller butikk), hvilken målgruppe du leste som (boligeier, styret, håndverker eller faghandel), tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
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
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/#om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
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
