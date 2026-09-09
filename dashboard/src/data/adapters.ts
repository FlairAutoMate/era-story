/**
 * Adapterkontrakt mellom frontend og backend.
 *
 * Alle kall tar `Session` slik at tenant- og rolleskoping skjer i adapteret (som en backend
 * ville gjort), aldri i komponentene. Komponentene skal ikke vite om data kommer fra fixtures
 * eller et API. Når en backend finnes, implementeres dette grensesnittet mot API-et og
 * `fixtureAdapter.ts` beholdes til tester og demo.
 */
import type {
  Activity,
  AssistantAnswer,
  AssistantContext,
  BoardSummary,
  BudgetLine,
  Building,
  BuildingPart,
  CalendarEvent,
  Decision,
  Document,
  DocumentFinding,
  Id,
  Issue,
  MaintenanceAction,
  Message,
  MessageSegment,
  Person,
  PriorityItem,
  Project,
  Quote,
  QuoteRequest,
  Resident,
  Session,
  Supplier,
  Tenant,
  Unit,
  UnitParticipation,
  UpgradeTier,
} from "@/domain/types";

export class AccessDeniedError extends Error {
  constructor(message = "Du har ikke tilgang til dette innholdet.") {
    super(message);
    this.name = "AccessDeniedError";
  }
}

export interface DataAdapter {
  /* Sesjon og tenant */
  listTenantsFor(session: Session): Promise<Tenant[]>;
  getTenant(session: Session): Promise<Tenant>;
  listPeople(session: Session): Promise<Person[]>;

  /* Eiendom */
  listBuildings(session: Session): Promise<Building[]>;
  listUnits(session: Session): Promise<Unit[]>;
  listBuildingParts(session: Session): Promise<BuildingPart[]>;

  /* Styrets oversikt (beregnet) */
  getBoardSummary(session: Session): Promise<BoardSummary>;
  listPriorityItems(session: Session): Promise<PriorityItem[]>;
  listCalendar(session: Session): Promise<CalendarEvent[]>;
  listActivity(session: Session, limit?: number): Promise<Activity[]>;

  /* Vedlikehold */
  listMaintenance(session: Session): Promise<MaintenanceAction[]>;

  /* Saker og avvik */
  listIssues(session: Session): Promise<Issue[]>;
  createIssue(session: Session, input: Pick<Issue, "title" | "description" | "severity" | "buildingId" | "responsibility">): Promise<Issue>;
  addIssueComment(session: Session, issueId: Id, text: string, internal: boolean): Promise<Issue>;
  toggleIssueTask(session: Session, issueId: Id, taskId: Id): Promise<Issue>;

  /* Prosjekter */
  listProjects(session: Session): Promise<Project[]>;
  createProject(session: Session, input: Pick<Project, "title" | "purpose" | "scope" | "buildingIds">): Promise<Project>;
  listParticipation(session: Session, projectId: Id): Promise<UnitParticipation[]>;
  decideChangeOrder(session: Session, projectId: Id, changeOrderId: Id, approve: boolean): Promise<Project>;

  /* Tilbud */
  listQuoteRequests(session: Session): Promise<QuoteRequest[]>;
  listQuotes(session: Session): Promise<Quote[]>;
  listSuppliers(session: Session): Promise<Supplier[]>;
  createQuoteRequest(session: Session, input: Pick<QuoteRequest, "title" | "projectId" | "scopeItems" | "invitedSupplierIds" | "deadline">): Promise<QuoteRequest>;
  listDecisions(session: Session): Promise<Decision[]>;
  recordDecision(session: Session, decisionId: Id, outcome: "vedtatt" | "avvist" | "utsatt", quoteId?: Id): Promise<Decision>;

  /* Beboere og kommunikasjon */
  listResidents(session: Session): Promise<Resident[]>;
  listMessages(session: Session): Promise<Message[]>;
  sendMessage(session: Session, input: Pick<Message, "subject" | "body" | "segment" | "linkedTo" | "replyDeadline" | "requiresConfirmation" | "signup" | "attachments">, when: "na" | "utkast"): Promise<Message>;
  countRecipients(session: Session, segment: MessageSegment): Promise<number>;

  /* Dokumenter */
  listDocuments(session: Session): Promise<Document[]>;
  confirmFinding(session: Session, documentId: Id, findingId: Id, correctedText?: string): Promise<DocumentFinding>;

  /* Økonomi */
  listBudget(session: Session): Promise<BudgetLine[]>;

  /* Beboerflyt (egen bolig) */
  getMyParticipation(session: Session): Promise<{ project: Project; participation: UnitParticipation; unit: Unit } | null>;
  answerSurvey(session: Session, projectId: Id, answers: Record<string, string>, photos: number): Promise<UnitParticipation>;
  chooseTier(session: Session, projectId: Id, tier: UpgradeTier, optionIds: Id[]): Promise<UnitParticipation>;
  acceptPrivateQuote(session: Session, projectId: Id): Promise<UnitParticipation>;

  /* ERA-assistent */
  askEra(session: Session, question: string, context: AssistantContext): Promise<AssistantAnswer>;
}
