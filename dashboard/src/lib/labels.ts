import type {
  ActivityKind,
  BuildingPartCategory,
  Confidence,
  DocumentType,
  IssueSource,
  IssueStatus,
  MaintenanceStatus,
  ProductionReadiness,
  ProjectStage,
  Responsibility,
  Severity,
  UnitResponseStatus,
  UpgradeTier,
} from "@/domain/types";

export const SEVERITY_LABEL: Record<Severity, string> = { kritisk: "Kritisk", hoy: "Høy", middels: "Middels", lav: "Lav" };

export const MAINT_STATUS_LABEL: Record<MaintenanceStatus, string> = {
  forslag: "Forslag",
  krever_beslutning: "Krever beslutning",
  planlagt: "Planlagt",
  pagar: "Pågår",
  ferdig: "Ferdig",
  utsatt: "Utsatt",
  mangler_data: "Mangler data",
};

export const ISSUE_STATUS_LABEL: Record<IssueStatus, string> = {
  ny: "Ny",
  under_vurdering: "Under vurdering",
  pagar: "Pågår",
  venter: "Venter",
  lost: "Løst",
  avvist: "Avvist",
};

export const STAGE_LABEL: Record<ProjectStage, string> = {
  planlagt: "Planlagt",
  kartlegging: "Kartlegging",
  til_tilbud: "Til tilbud",
  til_beslutning: "Til beslutning",
  vedtatt: "Vedtatt",
  gjennomforing: "Gjennomføring",
  kontroll: "Kontroll",
  dokumentert: "Dokumentert",
};

export const CONFIDENCE_LABEL: Record<Confidence, string> = {
  bekreftet: "Bekreftet",
  era_forslag: "ERA-forslag",
  antakelse: "Antakelse",
  mangler: "Mangler grunnlag",
};

export const PART_LABEL: Record<BuildingPartCategory, string> = {
  tak: "Tak",
  fasade: "Fasade",
  vinduer: "Vinduer",
  balkonger: "Balkonger",
  vvs: "VVS",
  elektro: "Elektro",
  heis: "Heis",
  brannsikkerhet: "Brannsikkerhet",
  utearealer: "Utearealer",
  drenering: "Drenering",
};

export const DOC_TYPE_LABEL: Record<DocumentType, string> = {
  tilstandsrapport: "Tilstandsrapport",
  fdv: "FDV",
  tilbud: "Tilbud",
  kontrakt: "Kontrakt",
  garanti: "Garanti",
  protokoll: "Protokoll",
  tegning: "Tegning",
  faktura: "Faktura",
  kontrollrapport: "Kontrollrapport",
  bilde: "Bilde",
  annet: "Annet",
};

export const TIER_LABEL: Record<UpgradeTier, string> = {
  kun_felles: "Kun fellesarbeid",
  grunnpakke: "Privat grunnpakke",
  oppgradering: "Privat oppgradering",
  komplett: "Komplett baderom",
};

export const RESPONSE_LABEL: Record<UnitResponseStatus, string> = {
  ikke_kontaktet: "Ikke kontaktet",
  ikke_svart: "Ikke svart",
  kartlegging_pagar: "Kartlegging pågår",
  vurderer: "Vurderer",
  valgt: "Har valgt",
  akseptert: "Akseptert",
  avslatt: "Kun fellesarbeid",
};

export const READINESS_LABEL: Record<ProductionReadiness, string> = {
  klar: "Klar",
  mangler_tilgang: "Mangler tilgang",
  mangler_avklaring: "Mangler avklaring",
  ikke_startet: "Ikke startet",
};

export const RESPONSIBILITY_LABEL: Record<Responsibility, string> = { felles: "Felles", privat: "Privat", uavklart: "Uavklart" };

export const SOURCE_LABEL: Record<IssueSource, string> = {
  beboer: "Beboer",
  vaktmester: "Vaktmester",
  styret: "Styret",
  leverandor: "Leverandør",
  kontroll: "Kontroll",
  era: "ERA-analyse",
};

export const ACTIVITY_LABEL: Record<ActivityKind, string> = {
  dokument_analysert: "Dokument analysert",
  avvik_registrert: "Avvik registrert",
  tilbud_mottatt: "Tilbud mottatt",
  beboer_svart: "Beboer har svart",
  endringsordre_godkjent: "Endringsordre godkjent",
  milepael_fullfort: "Milepæl fullført",
  fdv_oppdatert: "FDV oppdatert",
  beslutning: "Vedtak",
  melding_sendt: "Melding sendt",
  tiltak_oppdatert: "Tiltak oppdatert",
};

/** Statusfarge-token per status. Farge er aldri eneste markør; tekstetikett følger alltid med. */
export type Tone = "critical" | "decision" | "planned" | "active" | "done" | "neutral";

export const MAINT_TONE: Record<MaintenanceStatus, Tone> = {
  forslag: "neutral",
  krever_beslutning: "decision",
  planlagt: "planned",
  pagar: "active",
  ferdig: "done",
  utsatt: "neutral",
  mangler_data: "neutral",
};

export const ISSUE_TONE: Record<IssueStatus, Tone> = {
  ny: "decision",
  under_vurdering: "planned",
  pagar: "active",
  venter: "neutral",
  lost: "done",
  avvist: "neutral",
};

export const SEVERITY_TONE: Record<Severity, Tone> = { kritisk: "critical", hoy: "decision", middels: "planned", lav: "neutral" };

export const STAGE_TONE: Record<ProjectStage, Tone> = {
  planlagt: "neutral",
  kartlegging: "planned",
  til_tilbud: "planned",
  til_beslutning: "decision",
  vedtatt: "planned",
  gjennomforing: "active",
  kontroll: "active",
  dokumentert: "done",
};

export const CONFIDENCE_TONE: Record<Confidence, Tone> = {
  bekreftet: "done",
  era_forslag: "planned",
  antakelse: "decision",
  mangler: "neutral",
};
