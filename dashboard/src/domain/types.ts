/**
 * Domenemodell for ERA Property – styredashboard.
 *
 * Backend-status (2026-09): dette repoet har ingen backend for disse objektene. Typene her er
 * frontendens kontrakt, og `data/adapters.ts` er det eneste stedet som må byttes ut når en
 * backend finnes. Se README-avsnittet «Backend-gap».
 */

export type TenantId = string;
export type Id = string;
export type IsoDate = string; // YYYY-MM-DD
export type IsoDateTime = string;

export type Role =
  | "styreleder"
  | "styremedlem"
  | "forretningsforer"
  | "vaktmester"
  | "beboer"
  | "leverandor"
  | "era_admin";

export interface Tenant {
  id: TenantId;
  name: string;
  kind: "borettslag" | "sameie";
  address: string;
  postal: string;
  buildingCount: number;
  unitCount: number;
  lastUpdated: IsoDateTime;
  /** Sant for demo-tenants. Vises alltid i UI når sant. */
  isDemo: boolean;
}

export interface Session {
  userId: Id;
  name: string;
  role: Role;
  tenantId: TenantId;
  unitId?: Id;
  supplierId?: Id;
}

/** Datakvalitet: hvordan en opplysning er fremkommet. */
export type Confidence = "bekreftet" | "era_forslag" | "antakelse" | "mangler";

export interface Building {
  id: Id;
  tenantId: TenantId;
  name: string;
  address: string;
  yearBuilt?: number;
  floors?: number;
  entrances: Entrance[];
}
export interface Entrance {
  id: Id;
  buildingId: Id;
  name: string;
  unitCount: number;
}
export interface Unit {
  id: Id;
  tenantId: TenantId;
  buildingId: Id;
  entranceId: Id;
  label: string;
  floor: number;
  sizeM2?: number;
}

export type BuildingPartCategory =
  | "tak"
  | "fasade"
  | "vinduer"
  | "balkonger"
  | "vvs"
  | "elektro"
  | "heis"
  | "brannsikkerhet"
  | "utearealer"
  | "drenering";

export interface BuildingPart {
  id: Id;
  tenantId: TenantId;
  buildingId?: Id;
  category: BuildingPartCategory;
  name: string;
  installedYear?: number;
  expectedLifetimeYears?: number;
  conditionGrade?: 0 | 1 | 2 | 3;
  conditionSource?: string;
  mapped: boolean;
}

export type Severity = "kritisk" | "hoy" | "middels" | "lav";

export type MaintenanceStatus =
  | "forslag"
  | "krever_beslutning"
  | "planlagt"
  | "pagar"
  | "ferdig"
  | "utsatt"
  | "mangler_data";

export interface CostRange {
  low: number;
  high: number;
  basis: Confidence;
  note?: string;
}

export interface MaintenanceAction {
  id: Id;
  tenantId: TenantId;
  title: string;
  buildingPartId: Id;
  buildingId?: Id;
  status: MaintenanceStatus;
  priority: Severity;
  riskIfDelayed: string;
  recommendedYear: number;
  recommendedQuarter?: 1 | 2 | 3 | 4;
  cost?: CostRange;
  basis: { confidence: Confidence; sources: Id[]; text: string };
  ownerId?: Id;
  relatedIssueIds: Id[];
  relatedDocumentIds: Id[];
  projectId?: Id;
  nextAction: string;
}

export type IssueStatus = "ny" | "under_vurdering" | "pagar" | "venter" | "lost" | "avvist";
export type Responsibility = "felles" | "privat" | "uavklart";
export type IssueSource = "beboer" | "vaktmester" | "styret" | "leverandor" | "kontroll" | "era";

export interface Issue {
  id: Id;
  tenantId: TenantId;
  ref: string;
  title: string;
  description: string;
  severity: Severity;
  status: IssueStatus;
  buildingId?: Id;
  entranceId?: Id;
  unitId?: Id;
  buildingPartId?: Id;
  responsibility: Responsibility;
  responsibilityNote?: string;
  ownerId?: Id;
  dueDate?: IsoDate;
  source: IssueSource;
  supplierId?: Id;
  reportedAt: IsoDateTime;
  reportedBy: string;
  photos: number;
  suggestedCategory?: { value: string; confidence: Confidence };
  facts: { text: string; confidence: Confidence }[];
  history: { at: IsoDateTime; text: string; by: string }[];
  comments: { at: IsoDateTime; by: string; text: string; internal?: boolean }[];
  tasks: { id: Id; text: string; done: boolean; ownerId?: Id }[];
  documentIds: Id[];
  projectId?: Id;
  maintenanceActionId?: Id;
  nextAction: string;
}

export type ProjectStage =
  | "planlagt"
  | "kartlegging"
  | "til_tilbud"
  | "til_beslutning"
  | "vedtatt"
  | "gjennomforing"
  | "kontroll"
  | "dokumentert";

export const PROJECT_STAGES: ProjectStage[] = [
  "planlagt",
  "kartlegging",
  "til_tilbud",
  "til_beslutning",
  "vedtatt",
  "gjennomforing",
  "kontroll",
  "dokumentert",
];

export interface Milestone {
  id: Id;
  title: string;
  date: IsoDate;
  done: boolean;
  kind: "milepael" | "beslutning" | "kontroll" | "frist";
}

export interface ChangeOrder {
  id: Id;
  ref: string;
  title: string;
  amount: number;
  status: "foreslatt" | "godkjent" | "avvist";
  scope: "felles" | "privat";
  at: IsoDate;
  unitId?: Id;
}

export interface Decision {
  id: Id;
  tenantId: TenantId;
  title: string;
  status: "krever_beslutning" | "vedtatt" | "avvist" | "utsatt";
  meetingDate?: IsoDate;
  decidedAt?: IsoDate;
  projectId?: Id;
  maintenanceActionId?: Id;
  quoteId?: Id;
  summary: string;
  basisDocumentIds: Id[];
}

export type UpgradeTier = "kun_felles" | "grunnpakke" | "oppgradering" | "komplett";

export type UnitResponseStatus =
  | "ikke_kontaktet"
  | "ikke_svart"
  | "kartlegging_pagar"
  | "vurderer"
  | "valgt"
  | "akseptert"
  | "avslatt";

export type ProductionReadiness = "klar" | "mangler_tilgang" | "mangler_avklaring" | "ikke_startet";

export interface PrivateQuote {
  tier: UpgradeTier;
  basePrice: number;
  options: { id: Id; name: string; price: number; selected: boolean }[];
  coordinationDiscount: number;
  vatIncluded: boolean;
  accepted?: IsoDate;
}

export interface UnitParticipation {
  unitId: Id;
  projectId: Id;
  responseStatus: UnitResponseStatus;
  tier?: UpgradeTier;
  accessConfirmed?: IsoDate;
  readiness: ProductionReadiness;
  readinessNote?: string;
  scheduledWeek?: number;
  productionStatus?: "ikke_startet" | "pagar" | "ferdig";
  surveyAnswers?: Record<string, string>;
  photos?: number;
  /** Kun synlig for beboeren selv, leverandøren og ERA-admin. Strippes av adapteret ellers. */
  privateQuote?: PrivateQuote;
}

export interface UpgradePackage {
  tier: UpgradeTier;
  name: string;
  description: string;
  includes: string[];
  excludes: string[];
  priceFrom?: number;
  priceTo?: number;
  coordinationDiscount?: number;
  coveredByTenant: boolean;
}

export interface Project {
  id: Id;
  tenantId: TenantId;
  title: string;
  purpose: string;
  scope: string;
  stage: ProjectStage;
  buildingIds: Id[];
  affectedUnitIds: Id[];
  ownerId: Id;
  supplierIds: Id[];
  progressPct?: number;
  budget?: number;
  forecast?: number;
  actual?: number;
  sharedCost?: number;
  privateAggregate?: { unitsOptingIn: number; total: number };
  milestones: Milestone[];
  openIssueIds: Id[];
  quoteRequestId?: Id;
  decisionIds: Id[];
  changeOrders: ChangeOrder[];
  documentIds: Id[];
  fdvStatus: "mangler" | "delvis" | "komplett" | "ikke_relevant";
  boardNextAction: string;
  hasPrivateUpgrades: boolean;
  packages?: UpgradePackage[];
  productOptions?: { id: Id; name: string; price: number; group: string }[];
  surveyQuestions?: { id: Id; text: string }[];
  startDate?: IsoDate;
  endDate?: IsoDate;
}

export interface Supplier {
  id: Id;
  name: string;
  trade: string;
  orgNumber: string;
  status: "godkjent" | "ny" | "avventer_dokumentasjon";
  contact: string;
}

export interface QuoteRequest {
  id: Id;
  tenantId: TenantId;
  title: string;
  projectId?: Id;
  maintenanceActionId?: Id;
  scopeItems: { id: Id; text: string; included: boolean }[];
  invitedSupplierIds: Id[];
  deadline: IsoDate;
  status: "utkast" | "sendt" | "tilbud_mottatt" | "besluttet";
  createdAt: IsoDate;
}

export interface QuoteLine {
  key: string;
  label: string;
  included: boolean | "forbehold";
  note?: string;
}

export interface Quote {
  id: Id;
  tenantId: TenantId;
  quoteRequestId: Id;
  supplierId: Id;
  totalExVat: number;
  totalIncVat: number;
  lines: QuoteLine[];
  reservations: string[];
  deliveryWeeks: number;
  startEarliest: IsoDate;
  warrantyYears: number;
  documentationCommitment: "full_fdv" | "delvis" | "ikke_spesifisert";
  changeRisk: "lav" | "middels" | "hoy";
  changeRiskNote: string;
  receivedAt: IsoDate;
  documentId?: Id;
  eraAssessment: { summary: string; strengths: string[]; concerns: string[]; missing: string[] };
}

export type ResidentRole = "eier" | "leietaker" | "styremedlem" | "styreleder";

export interface Resident {
  id: Id;
  tenantId: TenantId;
  name: string;
  unitId: Id;
  role: ResidentRole;
  /** Sensitive kontaktfelt; strippes av adapteret uten `residents:contact`. */
  email?: string;
  phone?: string;
  hasApp: boolean;
}

export type MessageSegment =
  | { kind: "alle" }
  | { kind: "bygg"; buildingId: Id }
  | { kind: "oppgang"; entranceId: Id }
  | { kind: "berorte"; projectId: Id }
  | { kind: "beboer"; residentId: Id };

export interface Message {
  id: Id;
  tenantId: TenantId;
  subject: string;
  body: string;
  segment: MessageSegment;
  recipients: number;
  linkedTo?: { type: "sak" | "avvik" | "prosjekt" | "tiltak" | "kontroll" | "tilbud"; id: Id };
  replyDeadline?: IsoDate;
  requiresConfirmation: boolean;
  signup?: { label: string; slots?: string[] };
  attachments: string[];
  status: "utkast" | "sendt" | "planlagt";
  sentAt?: IsoDateTime;
  stats?: { delivered: number; read: number; confirmed: number; replied: number };
}

export type DocumentType =
  | "tilstandsrapport"
  | "fdv"
  | "tilbud"
  | "kontrakt"
  | "garanti"
  | "protokoll"
  | "tegning"
  | "faktura"
  | "kontrollrapport"
  | "bilde"
  | "annet";

export interface DocumentFinding {
  id: Id;
  field: string;
  text: string;
  location: string;
  confidence: Confidence;
  confirmedBy?: string;
  correctedText?: string;
}

export interface Document {
  id: Id;
  tenantId: TenantId;
  title: string;
  type: DocumentType;
  date: IsoDate;
  source: string;
  status: "analysert" | "under_analyse" | "ikke_analysert" | "feil";
  analysisPct?: number;
  missingMetadata: string[];
  access: "styret" | "alle_beboere" | "privat" | "leverandor";
  links: {
    buildingId?: Id;
    entranceId?: Id;
    unitId?: Id;
    buildingPartId?: Id;
    issueId?: Id;
    maintenanceActionId?: Id;
    projectId?: Id;
    supplierId?: Id;
    warrantyUntil?: IsoDate;
  };
  findings: DocumentFinding[];
  pages?: number;
}

export type ActivityKind =
  | "dokument_analysert"
  | "avvik_registrert"
  | "tilbud_mottatt"
  | "beboer_svart"
  | "endringsordre_godkjent"
  | "milepael_fullfort"
  | "fdv_oppdatert"
  | "beslutning"
  | "melding_sendt"
  | "tiltak_oppdatert";

export interface Activity {
  id: Id;
  tenantId: TenantId;
  at: IsoDateTime;
  kind: ActivityKind;
  text: string;
  actor: string;
  link?: { type: "prosjekt" | "avvik" | "dokument" | "tilbud" | "tiltak" | "melding"; id: Id };
}

export interface CalendarEvent {
  id: Id;
  tenantId: TenantId;
  date: IsoDate;
  kind: "vedlikehold" | "kontroll" | "frist" | "beslutning" | "milepael" | "garanti";
  title: string;
  link?: { type: "prosjekt" | "tiltak" | "avvik" | "tilbud" | "dokument"; id: Id };
}

export interface Person {
  id: Id;
  name: string;
  role: Role;
  tenantId?: TenantId;
}

export interface BudgetLine {
  id: Id;
  tenantId: TenantId;
  year: number;
  label: string;
  buildingPartCategory?: BuildingPartCategory;
  projectId?: Id;
  budget: number;
  approved?: number;
  forecast?: number;
  actual?: number;
  scope: "felles" | "privat";
}

export interface PriorityItem {
  id: Id;
  title: string;
  type:
    | "kritisk_avvik"
    | "vedlikehold_naermer_seg"
    | "tilbud_ma_vurderes"
    | "beslutning_mangler"
    | "frist_utloper"
    | "prosjekt_avvik"
    | "mangler_dokumentasjon";
  severity: Severity;
  why: string;
  recommendedAction: string;
  dueDate?: IsoDate;
  ownerId?: Id;
  buildingPartLabel?: string;
  primary: { label: string; to: string };
  askEra: string;
}

export interface BoardSummary {
  actionsRequiringDecision: number;
  openIssues: number;
  criticalOpenIssues: number;
  activeProjects: number;
  quotesWaiting: number;
  upcomingDeadlines30d: number;
  buildingAreasMapped: { mapped: number; total: number };
  documentsMissingLink: number;
}

export interface AssistantAnswer {
  conclusion: string;
  reasoning: string[];
  sources: { label: string; documentId?: Id; link?: string }[];
  assumptions: string[];
  missing: string[];
  nextAction: string;
  actions: { label: string; kind: "oppgave" | "sak" | "melding" | "beslutningsgrunnlag"; to?: string }[];
}

export interface AssistantContext {
  tenantId: TenantId;
  role: Role;
  page: string;
  selected?: { type: string; id: Id; label: string };
}
