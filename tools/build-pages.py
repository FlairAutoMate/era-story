# -*- coding: utf-8 -*-
"""Generates the audience subpages (/boligeier, /styret, /handverker, /faghandel) from one
template and one content dict. Run from the project root: python tools/build-pages.py"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def esc(t):
    return html.escape(t, quote=True)


TAG_LABELS = {"customer": "Fra kunden", "doc": "Dokumentert", "ai": "ERA-forslag", "check": "Avklares på befaring", "board": "Styret", "pro": "Håndverker", "resident": "Beboer", "order": "Bestilling og levering", "pilot": "I pilot", "planned": "Planlagt", "illustration": "Illustrasjon av arbeidsflyt"}


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
        out.append(f'<div class="dash-group"><span class="tag tag-{g_tag}">{esc(TAG_LABELS[g_tag])}</span>' + "".join(
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
        label="For styret", hook="Fra vedlikeholdsbehov til ferdig jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler styret, boligeierne og håndverkerne rundt samme eiendom. Få hjelp til å forstå behovene, prioritere tiltak og følge arbeidet helt frem til dokumentert resultat.",
        hero_support="Styret skifter. Planen består.",
        image="/assets/story/block-bikes-v3.jpg", image_pos="50% 50%",
        hero_secondary=("Se hvordan det henger sammen", "/#styret"),
        scenes=dict(
            eyebrow="Fra behov til ferdig jobb", title="Én eiendom. Én sammenhengende vedlikeholdsflyt.",
            lede="Følg det samme fasadebehovet fra første funn til gjennomført og dokumentert arbeid. Beboerne er med hele veien: hver boligeier får egen boligoversikt, vedlikeholdsplan og påminnelser gjennom ERA for boligeiere.",
            items=[
                dict(nav="Oversikt", heading="Hva trenger bygget deres nå?",
                     text="Rapporter, tidligere arbeid og innmeldte behov gir styret ett samlet utgangspunkt.",
                     value="ERA skiller dokumenterte funn fra forslag som styret må vurdere.",
                     view=dash("Eiendomsoversikt", "Borgveien 14 · 24 seksjoner · Fasade",
                               kpis=[("Eiendom", "Borgveien 14"), ("Seksjoner", "24"), ("Område", "Fasade"), ("Sist utført", "Malt 2012")],
                               groups=[("doc", [("Tilstandsrapport 2021", "Maling flasser på sør- og vestvegg"), ("Innmeldt behov", "Avskalling ved inngang B")]),
                                       ("ai", [("Forslag", "Befaring innen 12 måneder")])],
                               footer="Eksempeldata. ERA-forslag vurderes og besluttes av styret.")),
                dict(nav="Prioritering", heading="Fra rapport til neste steg.",
                     text="Det dokumenterte behovet omformes til et konkret tiltak i vedlikeholdsplanen.",
                     value="Styret ser hvorfor tiltaket foreslås, når det bør vurderes og hvilket grunnlag det bygger på.",
                     view=dash("Vedlikeholdsplan", "Fasade · til vurdering",
                               kpis=[("Foreslått tiltak", "Male sør- og vestvegg"), ("Anbefalt år", "2027"), ("Kostnadsintervall", "1,0–1,3 mill"), ("Status", "Til vurdering")],
                               groups=[("doc", [("Funn", "Maling flasser, sør- og vestvegg · rapport 2021"), ("Egen oppgave i totalplanen", "Tak · 2031")]),
                                       ("ai", [("Grunnlag", "Rapport 2021 og innmeldt avskalling"), ("Per seksjon", "ca. 42–54 000 kr")])],
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
                     view=dash("Fasade 2027", "Uke 2 av 6 · i rute",
                               cols=[("board", [("Fremdrift", "Uke 2 av 6, i rute"), ("Avklaring", "Farge på beslag, svar innen fredag")]),
                                     ("pro", [("Arbeidsgrunnlag", "Omfang, bilder og avtalt tid"), ("Dokumentasjon", "Bilder legges inn underveis")]),
                                     ("resident", [("Når", "Stillas ved inngang B, uke 20–25"), ("Praktisk", "Balkonger ryddes før 12. mai")])],
                               footer="Eksempeldata. Varsling til beboere vises som illustrasjon av arbeidsflyten.")),
                dict(nav="Dokumentasjon", heading="Jobben er ferdig. Historikken lever videre.",
                     text="Utført arbeid, bilder og produkter samles på eiendommen, og vedlikeholdsplanen oppdateres.",
                     value="Neste styre starter med historikken, ikke fra null.",
                     view=dash("Dokumentasjon", "Fasade 2027 · ferdigstilt",
                               kpis=[("Utført", "Sør- og vestvegg, 2 strøk"), ("Bilder", "18 før og etter"), ("Produkter", "Maling og grunning"), ("Utført av", "Malermester Berg AS")],
                               groups=[("ai", [("Foreslått neste fasadekontroll", "2032")]),
                                       ("illustration", [("Påminnelse", "Fasadekontroll 2032")])],
                               footer="Eksempeldata. En ryddig logg, ikke en garanti. Taket står som egen oppgave i totalplanen.")),
            ],
        ),
        aside=dict(
            label="Beboerverdi", heading="Verdi for styret. Hjelp til hver bolig.",
            text="Styret får oversikt over felles vedlikehold. Boligeieren får relevant informasjon om fellesarbeidet, og hjelp til å følge opp egen bolig med dokumentasjon, vedlikeholdsplan og påminnelser. Fellesareal og privat bolig holdes adskilt: privat boligdokumentasjon deles ikke automatisk med styret.",
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
            ("Hvem eier dataene?", "Eiendommen. Styret bestemmer hvem som ser dem. Ved styreskifte følger alt med."),
        ],
        closing=dict(
            heading="Hva er neste tiltak for deres eiendom?",
            lede="Se hvordan ERA kan hjelpe dere fra første vurdering til ferdig dokumentert arbeid, med styret, boligeierne og håndverkeren i samme flyt.",
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
        label="For håndverkere", hook="Fra kundens boligbehov til din neste jobb.",
        lede="ERA er en AI-drevet boligplattform som kobler boligeiere, styrer og håndverkere. Ta kundens behov videre til befaring, tilbud og gjennomføring, og la dokumentasjonen følge boligen når jobben er ferdig.",
        hero_support="Du kan faget. ERA hjelper deg med flyten rundt jobben.",
        image="/assets/story/painter-v3.jpg", image_pos="30% 50%",
        hero_secondary=("Følg et oppdrag", "#slik"),
        steps_label="Følg samme jobb hele veien", steps_title="Ett prosjekt. Fem hendelser.",
        steps=[
            ("Se hva kunden trenger. Før du drar.",
             "Kundens beskrivelse, bilder og tilgjengelige boliginformasjon følger henvendelsen. Du får et bedre grunnlag for å vurdere jobben og forberede befaringen.",
             ("Se oppdragsgrunnlaget", detail_card(
                 "Oppdragsgrunnlag · Male stue", "Borgveien 14",
                 [("customer", [("Ønsket arbeid", "Stue, 2 vegger"), ("Bilder", "4 vedlagt"), ("Ønsket tid", "Uke 38–40")]),
                  ("ai", [("Anslått flate", "ca. 42 m²")]),
                  ("check", [("Forbehandling", "Sjekkes på befaring")])],
                 note="Bare det kunden faktisk har delt vises her. ERA-forslaget er et utgangspunkt, ikke en fasit."))),
            ("Ta befaringen videre til et tydelig tilbud.",
             "Samle mål, bilder og notater på oppdraget. ERA hjelper deg å strukturere arbeidsbeskrivelsen og kalkylen. Du vurderer mengder, pris og tilbud før det sendes.",
             ("Se veien til tilbud", detail_card(
                 "Tilbudsutkast · Male stue", "Borgveien 14 · 4 bilder vedlagt",
                 [("customer", [("Omfang", "Vegger, 2 strøk"), ("Forbehandling", "Lett sparkling"), ("Ønsket tid", "Uke 38–40"), ("Materialer", "Ligger klart"), ("Kundens estimat", "ca. 6 800 kr")])],
                 note="Befaringsnotatene brukes videre i tilbudsutkastet. Du vurderer mengder og pris før du sender."))),
            ("Avklart med kunden. Klart for oppstart.",
             "Hold avtalt omfang, materialbehov og prosjektinformasjon samlet, så du og kunden vet hva som skal gjøres.",
             ("Se arbeidsgrunnlaget", detail_card(
                 "Arbeidsgrunnlag · Male stue", "Godkjent av kunde",
                 [("customer", [("Omfang", "Vegger, 2 strøk"), ("Avtalt oppstart", "Uke 38")]),
                  ("ai", [("Produkter fra planen", "2 × maling 10 L, 1 × sparkel 5 kg, 2 ruller"), ("Materialpris", "ca. 1 900 kr")]),
                  ("order", [("Bestilling", "Én bestilling fra planen, uavhengig av kjede"), ("Levering", "Kjøres hjem, hentes i butikk, eller du henter")]),
                  ("pilot", [("Betaling i ERA", "Avtalt beløp og betalingsstatus")])],
                 note="Mengder og pris kommer fra planen og kan justeres etter befaringen. Kunden velger levering. Betaling i ERA er i pilot."))),
            ("Kunden vil også male taket.",
             "Gjør endringen tydelig med beskrivelse, pris og konsekvens for fremdriften. Send den til kunden for godkjenning før ekstraarbeidet starter.",
             ("Se en endringsordre", detail_card(
                 "Endringsordre · Male stue", "Tillegg til opprinnelig omfang",
                 [("customer", [("Opprinnelig omfang", "Vegger, 2 strøk"), ("Foreslått tillegg", "Tak, 1 strøk"), ("Prisendring", "+ ca. 1 800 kr")]),
                  ("check", [("Status", "Venter godkjenning")])],
                 note="Godkjent endring oppdaterer arbeidsgrunnlaget. Kunden ser alltid forskjellen på foreslått og godkjent."))),
            ("Din jobb blir en del av boligens historie.",
             "Samle bilder, produktinformasjon og utført arbeid i en ryddig overlevering. Kunden beholder dokumentasjonen i boligen, og arbeidet ditt blir synlig for fremtidig oppfølging.",
             ("Se overleveringen", detail_card(
                 "Overlevering · Male stue", "Ferdigstilt",
                 [("customer", [("Utført arbeid", "Vegger og tak, 2 strøk"), ("Bilder", "6 lagt til"), ("Produkter brukt", "Maling, sparkel, ruller"), ("Status", "Ferdigstilt og overlevert")]),
                  ("pilot", [("Betaling i ERA", "Avtalt beløp og om det er gjort opp")])],
                 note="Kunden finner det samme arbeidet igjen i boligens historikk, med ditt navn på. Ikke en sertifisering eller garanti, bare en ryddig logg."))),
        ],
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


MENU = [("/", "Historien"), ("/boligeier", "Boligeier"), ("/styret", "Styret"), ("/handverker", "Håndverker"), ("/faghandel", "Faghandel"), ("/om-era", "Om ERA"), ("/personvern", "Personvern")]


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
    scenes_section = ""
    if a.get("scenes"):
        sc = a["scenes"]
        items = sc["items"]
        tabs = "".join(
            f'<button type="button" role="tab" id="tab-{i+1}" aria-selected="{"true" if i == 0 else "false"}" aria-controls="scene-{i+1}" tabindex="{0 if i == 0 else -1}"><span class="n">0{i+1}</span><span class="t">{esc(it["nav"])}</span></button>'
            for i, it in enumerate(items))
        panels = "".join(
            f'<div class="scene" role="tabpanel" id="scene-{i+1}" aria-labelledby="tab-{i+1}"{"" if i == 0 else " hidden"}>'
            f'<div class="scene-text"><div class="label">Steg {i+1} · {esc(it["nav"])}</div><h3>{esc(it["heading"])}</h3><p>{esc(it["text"])}</p>'
            f'<p class="scene-value">{esc(it["value"])}</p>'
            f'<div class="scene-nav"><button type="button" class="scene-prev" data-dir="-1"{" disabled" if i == 0 else ""}>← Forrige</button><button type="button" class="scene-next" data-dir="1"{" disabled" if i == len(items) - 1 else ""}>Neste →</button></div></div>'
            f'<div class="scene-view">{it["view"]}</div></div>'
            for i, it in enumerate(items))
        scenes_section = (
            '<section class="section scenes" id="slik"><div class="wrap wide">'
            f'<div class="label">{esc(sc["eyebrow"])}</div><h2>{esc(sc["title"])}</h2><p class="steps-intro">{esc(sc["lede"])}</p>'
            f'<div class="stepnav" role="tablist" aria-label="Fem steg">{tabs}</div>'
            f'<div class="scene-panel">{panels}</div>'
            '</div></section>'
        )
    steps_section = scenes_section or (
        '<section class="section" id="slik">'
        f'<div class="label">{esc(steps_label)}</div><h2>{esc(steps_title)}</h2>{steps_intro}'
        f'<ol class="steps">{steps}</ol></section>'
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
  <div class="hero-media">{'<img src="' + a["image"] + '" srcset="' + a["image"][:-4] + '-m.jpg 1400w, ' + a["image"] + ' 3000w" sizes="100vw" alt="" style="object-position: ' + a["image_pos"] + '">'}</div>
  <div class="hero-text">
    <div class="label">{esc(a["label"])}</div>
    <h1>{esc(a["hook"])}</h1>{f'<div class="beta-badge">{esc(beta["badge"])}</div><p class="beta-note">{esc(beta["note"])}</p>' if beta else ''}
    <p class="lede">{esc(a["lede"])}</p>{f'<p class="hero-support">{esc(a["hero_support"])}</p>' if a.get("hero_support") else ''}
    <div class="hero-actions"><a class="btn" href="#skjema">{esc(beta["cta_primary"] if beta else a["form_cta"])}</a><a class="link" href="{hero_secondary[1]}">{esc(hero_secondary[0])}</a></div>
  </div>
</header>

<main>
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
      <p class="fine">Ingen binding. Dataene lagres kryptert i Norge og brukes bare til å ta kontakt.</p>
      {closing_note}
    </div>
  </section>
</main>

<footer class="foot">
  <div class="wrap">
    <div><div class="brand">era<span>.</span></div><div class="tag">Boligeierskap uten gjetting</div></div>
    <div class="cols">
      <div><b>Målgrupper</b>{"".join(f'<a href="/{s}">{esc(AUDIENCES[s]["nav"])}</a>' for s in ORDER)}</div>
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
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
            "Når du sender inn skjemaet på historien eller en av undersidene, lagrer vi det du skrev i feltet (adresse, adressen til bygget, firmanavn eller organisasjonsnummer, kjede eller butikk), hvilken målgruppe du leste som (boligeier, styret, håndverker eller faghandel), om du ba om en demo, tidspunkt, hvilken side du sendte fra, og nettlesertypen din.",
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
      <div><b>ERA</b><a href="/#hva">Hva ERA gjør</a><a href="/om-era">Om ERA</a><a href="/personvern">Personvern</a><a href="/">Historien</a></div>
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
