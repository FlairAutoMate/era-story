/**
 * DEMO: ERA-assistentens svar er regelstyrte fixtures. En ekte assistent må gi samme struktur
 * (konklusjon, begrunnelse, kilder, antakelser, mangler, neste handling), aldri fri tekst.
 */
import type { AssistantAnswer, AssistantContext } from "@/domain/types";

type Rule = { match: RegExp; answer: (ctx: AssistantContext) => AssistantAnswer };

const RULES: Rule[] = [
  {
    match: /prioriter|neste år|viktigst/i,
    answer: () => ({
      conclusion: "Styret bør prioritere tre ting neste år: takomlegging bygg C (vedtak nå), soilrørprosjektet (vedtak på generalforsamling 24. november) og betongbefaring av balkongene i bygg C.",
      reasoning: [
        "Tak C har tilstandsgrad 3 og har allerede lekket. Én vinter til gir sannsynlig ny skade.",
        "Soilrørene har gitt to lekkasjer på ett år. AV-31 er den siste. Hver lekkasje koster 80–150 000 kr.",
        "AV-30 viser rustutslag i balkongplate. Kostnaden øker jo lenger armeringskorrosjon får utvikle seg.",
      ],
      sources: [
        { label: "Tilstandsrapport 2024, s. 18 og 31", documentId: "doc-tilstand-2024" },
        { label: "Rørinspeksjon 2025, konklusjon", documentId: "doc-rorinspeksjon-2025" },
        { label: "AV-31 og AV-30", link: "/saker" },
      ],
      assumptions: ["Kostnadsanslag for balkonger (1,4–1,9 mill. kr) er ikke bekreftet av fagperson."],
      missing: ["El-anlegg og drenering er ikke kartlagt. Disse kan endre prioriteringen."],
      nextAction: "Lag beslutningsgrunnlag for styremøtet 23. september med de tre sakene.",
      actions: [
        { label: "Lag beslutningsgrunnlag", kind: "beslutningsgrunnlag", to: "/prosjekter/prj-tak?fane=tilbud" },
        { label: "Se vedlikeholdsplanen", kind: "oppgave", to: "/vedlikehold" },
      ],
    }),
  },
  {
    match: /sammenlign|tilbud/i,
    answer: () => ({
      conclusion: "Oslo Tak og Blikk og Takteam Øst kan sammenlignes på likt grunnlag. Byggmester Haugen mangler stillas, takrenner og FDV, og blir trolig dyrest når disse legges til.",
      reasoning: [
        "Takteam: 2,675 mill. kr inkl. mva, men råteforbehold uten øvre ramme.",
        "Oslo Tak og Blikk: 2,99 mill. kr inkl. mva, råte inntil 15 % inkludert, 10 års garanti, digital FDV.",
        "Haugen: 2,475 mill. kr, pluss anslått 180 000 kr stillas, takrenner og rigg etter medgått tid. Reelt 2,8–3,0 mill. kr.",
      ],
      sources: [
        { label: "Tilbud Takteam Øst, pkt. 7", documentId: "doc-tilbud-takteam" },
        { label: "Tilbud Oslo Tak og Blikk, s. 7", documentId: "doc-tilbud-oslotak" },
        { label: "Tilbud Byggmester Haugen", documentId: "doc-tilbud-haugen" },
      ],
      assumptions: ["Stillas for Haugen er anslått til 180 000 kr ut fra Takteams pris.", "Råteomfang i undertak er ukjent til taket åpnes."],
      missing: ["Timepris for tilleggsarbeid fra Takteam.", "Sentral godkjenning for Byggmester Haugen."],
      nextAction: "Be Takteam om en øvre ramme for råteforbeholdet før styremøtet. Da kan de to tilbudene sammenlignes direkte.",
      actions: [
        { label: "Åpne sammenligningen", kind: "oppgave", to: "/tilbud/qr-tak" },
        { label: "Lag beslutningsgrunnlag", kind: "beslutningsgrunnlag", to: "/tilbud/qr-tak" },
      ],
    }),
  },
  {
    match: /dokumentasjon|mangler vi|fdv/i,
    answer: () => ({
      conclusion: "Det mangler dokumentasjon på tre områder: el-anlegg, drenering og FDV for fasadeprosjektet. I tillegg har fire dokumenter ukjent kobling.",
      reasoning: [
        "El-anlegg og drenering har ingen registrerte dokumenter. Det gir «Mangler grunnlag» i vedlikeholdsplanen.",
        "Fasadeprosjektet har kontrakt og bilder, men ingen FDV ennå. Kontrakten krever FDV ved ferdigstillelse.",
        "Tre fakturaer og én skannet perm mangler kobling til prosjekt eller bygningsdel.",
      ],
      sources: [
        { label: "Kontrakt Nordfasade, pkt. 12", documentId: "doc-kontrakt-fasade" },
        { label: "Dokumentarkivet, filter «mangler metadata»", link: "/dokumenter?status=mangler" },
      ],
      assumptions: [],
      missing: ["Det er ukjent om tidligere styre hadde el-dokumentasjon i permen «Diverse 2015–2019»."],
      nextAction: "Koble de tre fakturaene til fasade- og brannprosjektet, og bestill el-kontroll for å få grunnlag.",
      actions: [
        { label: "Se dokumenter som mangler kobling", kind: "oppgave", to: "/dokumenter?status=mangler" },
        { label: "Opprett oppgave: bestill el-kontroll", kind: "oppgave", to: "/vedlikehold?tiltak=ma-elektro" },
      ],
    }),
  },
  {
    match: /beslutningsgrunnlag|styremøte/i,
    answer: () => ({
      conclusion: "Beslutningsgrunnlag for 23. september er klart for tre saker: valg av takleverandør, endringsordre EO-2 og el-kontroll.",
      reasoning: [
        "Sak 1: Tak C. To sammenlignbare tilbud, anbefalt å be Takteam om øvre ramme på råte.",
        "Sak 2: EO-2, 250 000 kr. Kontrakten krever skriftlig godkjenning før utførelse. Stillas flyttes 28. september.",
        "Sak 3: El-kontroll 60–90 000 kr. Gir grunnlag for et område uten data.",
      ],
      sources: [
        { label: "Tilbudssammenligning tak C", link: "/tilbud/qr-tak" },
        { label: "Kontrakt Nordfasade, pkt. 12", documentId: "doc-kontrakt-fasade" },
        { label: "Bilder råteskader", documentId: "doc-bilder-fasade" },
      ],
      assumptions: ["Budsjettramme for tak C er 2,4 mill. kr. Begge aktuelle tilbud ligger over."],
      missing: ["Forretningsfører har ikke bekreftet likviditet for EO-2."],
      nextAction: "Send beslutningsgrunnlaget til styret senest 16. september, en uke før møtet.",
      actions: [
        { label: "Lag beslutningsgrunnlag", kind: "beslutningsgrunnlag", to: "/prosjekter/prj-tak?fane=tilbud" },
        { label: "Skriv melding til styret", kind: "melding", to: "/beboere?ny=1" },
      ],
    }),
  },
  {
    match: /skriv|informasjon til|beboer/i,
    answer: () => ({
      conclusion: "Utkast til melding til beboere i bygg B om stillas fra 28. september er klart. Styret må godkjenne før utsendelse.",
      reasoning: ["Meldingen bruker datoene fra prosjektplanen og samme formulering som ved bygg A i juni.", "Mottakere: 16 boliger i oppgang 4 og 6."],
      sources: [{ label: "Prosjekt fasade, milepæl «Stillas bygg B montert»", link: "/prosjekter/prj-fasade?fane=fremdrift" }],
      assumptions: ["Datoen 28. september holder. Den avhenger av vedtak om EO-2 på styremøtet 23. september."],
      missing: [],
      nextAction: "Åpne utkastet, juster tekst og send med bekreftelse på mottak.",
      actions: [{ label: "Åpne meldingsutkast", kind: "melding", to: "/beboere?ny=1&prosjekt=prj-fasade" }],
    }),
  },
  {
    match: /risiko|utsette|vente/i,
    answer: (ctx) => ({
      conclusion: ctx.selected?.type === "tiltak" && ctx.selected.id === "ma-balkonger-c"
        ? "Å utsette balkongene ett år gir trolig 20–30 % høyere kostnad og risiko for bruksforbud hvis bæreevnen svekkes."
        : "Å utsette takomleggingen én vinter gir høy sannsynlighet for ny lekkasje. Kostnaden ved lekkasje er 80–150 000 kr per hendelse pluss forsikringsegenandel.",
      reasoning: [
        "Skaden er allerede registrert (AV-30 og lekkasje januar 2026).",
        "Erfaringstall for betong- og takskader viser at kostnaden øker med tiden når skaden først er synlig.",
      ],
      sources: [
        { label: "Tilstandsrapport 2024", documentId: "doc-tilstand-2024" },
        { label: "AV-30 Sprekk i balkongplate", link: "/saker?sak=iss-30" },
      ],
      assumptions: ["Prosentanslaget er et erfaringstall, ikke en beregning for denne eiendommen."],
      missing: ["Befaring av betongfagmann er ikke gjennomført."],
      nextAction: "Bestill befaring (ca. 25 000 kr) før beslutning om utsettelse.",
      actions: [{ label: "Opprett oppgave: bestill befaring", kind: "oppgave", to: "/vedlikehold?tiltak=ma-balkonger-c" }],
    }),
  },
  {
    match: /soilrør|soil|bad/i,
    answer: () => ({
      conclusion: "Soilrørprosjektet er i kartlegging. 40 av 48 boliger har svart. 15 vurderer eller har valgt privat oppgradering. 5 boliger mangler tilgangsavklaring. AV-31 (lekkasje) håndteres som strakstiltak.",
      reasoning: [
        "Svarfrist 15. september. 6 har ikke svart, 2 er ikke kontaktet (mangler app).",
        "Private tilvalg: 9 akseptert, 6 har valgt men ikke akseptert. Aggregert privat omsetning 1,845 mill. kr.",
        "Generalforsamling 24. november skal vedta fellesarbeidet og finansiering.",
      ],
      sources: [
        { label: "Berørte boliger, soilrør", link: "/prosjekter/prj-soil?fane=boliger" },
        { label: "Rørinspeksjon 2025", documentId: "doc-rorinspeksjon-2025" },
        { label: "AV-31", link: "/saker?sak=iss-31" },
      ],
      assumptions: ["Privat omsetning er aggregert. Styret ser ikke enkelttilbud."],
      missing: ["Tilbud på fellesarbeidet er ikke innhentet. Forespørselen ligger som utkast."],
      nextAction: "Send påminnelse til de 8 som ikke har svart, og ferdigstill tilbudsforespørselen for fellesarbeidet.",
      actions: [
        { label: "Send påminnelse", kind: "melding", to: "/beboere?ny=1&prosjekt=prj-soil" },
        { label: "Åpne tilbudsforespørsel", kind: "oppgave", to: "/tilbud/ny?prosjekt=prj-soil" },
      ],
    }),
  },
];

const FALLBACK = (ctx: AssistantContext): AssistantAnswer => ({
  conclusion: `Jeg har ikke nok grunnlag til å svare presist på det for ${ctx.page}. Her er hva jeg kan gjøre.`,
  reasoning: ["Jeg kan svare på prioritering, tilbud, dokumentasjon, beslutningsgrunnlag, beboerinformasjon, risiko ved å vente og status på prosjekter."],
  sources: [],
  assumptions: [],
  missing: ["Spørsmålet matcher ingen av områdene jeg har data for i denne demoen."],
  nextAction: "Velg ett av forslagene under, eller omformuler spørsmålet.",
  actions: [],
});

export function answerFor(question: string, ctx: AssistantContext): AssistantAnswer {
  const rule = RULES.find((r) => r.match.test(question));
  return rule ? rule.answer(ctx) : FALLBACK(ctx);
}

export function suggestionsFor(page: string, role: string): string[] {
  if (role === "beboer") return ["Hva skal borettslaget gjøre i badet mitt?", "Hva dekker borettslaget?", "Hva koster privat oppgradering?"];
  if (role === "leverandor") return ["Hvilke boliger mangler beslutning?", "Hvilke boliger er klare for produksjon?"];
  if (page.startsWith("/tilbud")) return ["Sammenlign disse tilbudene", "Hva mangler i tilbudet fra Haugen?", "Lag beslutningsgrunnlag til styremøtet"];
  if (page.startsWith("/prosjekter/prj-soil")) return ["Oppsummer status på soilrørprosjektet", "Skriv påminnelse til de som ikke har svart"];
  if (page.startsWith("/prosjekter")) return ["Hva må styret gjøre videre?", "Skriv informasjon til berørte beboere"];
  if (page.startsWith("/dokumenter")) return ["Hva mangler vi av dokumentasjon?"];
  if (page.startsWith("/vedlikehold")) return ["Hva er risikoen ved å utsette dette tiltaket?", "Hva bør styret prioritere neste år?"];
  return ["Hva bør styret prioritere neste år?", "Lag beslutningsgrunnlag til styremøtet", "Hva mangler vi av dokumentasjon?", "Oppsummer status på soilrørprosjektet"];
}
