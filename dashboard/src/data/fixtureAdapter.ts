/**
 * Fixture-adapter: implementerer `DataAdapter` mot demo-data i minnet.
 *
 * Adapteret håndhever tenant- og rolleskoping på samme måte som en backend må gjøre:
 *  - alt filtreres på `session.tenantId`
 *  - beboer ser bare egen bolig og eget private tilbud
 *  - leverandør ser bare tildelte prosjekter og boliger
 *  - styret ser aldri private tilbud (kun aggregert), og kontaktinfo krever `residents:contact`
 */
import { can } from "@/access/roles";
import type {
  Activity,
  AssistantAnswer,
  BoardSummary,
  BudgetLine,
  Building,
  BuildingPart,
  CalendarEvent,
  Decision,
  Document,
  Id,
  Issue,
  MaintenanceAction,
  Message,
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
} from "@/domain/types";
import { daysUntil, formatNOK, TODAY } from "@/lib/format";
import { PART_LABEL } from "@/lib/labels";
import { AccessDeniedError, type DataAdapter } from "./adapters";
import { answerFor } from "./fixtures/assistant";
import * as P from "./fixtures/perrongen";
import * as S from "./fixtures/solvang";

type Store = {
  tenants: Tenant[];
  people: Person[];
  buildings: Building[];
  units: Unit[];
  parts: BuildingPart[];
  maintenance: MaintenanceAction[];
  issues: Issue[];
  projects: Project[];
  participation: UnitParticipation[];
  quoteRequests: QuoteRequest[];
  quotes: Quote[];
  suppliers: Supplier[];
  decisions: Decision[];
  residents: Resident[];
  messages: Message[];
  documents: Document[];
  activities: Activity[];
  events: CalendarEvent[];
  budget: BudgetLine[];
};

const clone = <T,>(v: T): T => structuredClone(v);

function buildStore(): Store {
  return clone({
    tenants: [P.tenant, S.tenant2],
    people: [...P.people, ...S.people2],
    buildings: [...P.buildings, ...S.buildings2],
    units: [...P.units, ...S.units2],
    parts: P.buildingParts,
    maintenance: P.maintenanceActions,
    issues: [...P.issues, ...S.issues2],
    projects: [...P.projects, ...S.projects2],
    participation: P.participation,
    quoteRequests: P.quoteRequests,
    quotes: P.quotes,
    suppliers: P.suppliers,
    decisions: P.decisions,
    residents: P.residents,
    messages: P.messages,
    documents: [...P.documents, ...S.documents2],
    activities: P.activities,
    events: P.extraEvents,
    budget: P.budgetLines,
  });
}

const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

export interface FixtureOptions {
  /** Kunstig forsinkelse i ms for å vise loading-tilstander. */
  latency?: number;
  /** Demo-tilstander for QA: tom tenant, feil fra «backend», treg behandling. */
  mode?: "normal" | "tom" | "feil" | "treg";
}

export function createFixtureAdapter(opts: FixtureOptions = {}): DataAdapter {
  const store = buildStore();
  const latency = opts.mode === "treg" ? 2500 : (opts.latency ?? 250);
  const mode = opts.mode ?? "normal";
  let seq = 100;
  const nextId = (prefix: string) => `${prefix}-${++seq}`;

  async function guard(session: Session, ...perms: Parameters<typeof can>[1][]) {
    await wait(latency);
    if (mode === "feil") throw new Error("Tjenesten svarte ikke (demo: feiltilstand).");
    if (perms.length && !perms.some((p) => can(session.role, p))) throw new AccessDeniedError();
  }
  const scoped = <T extends { tenantId: string }>(session: Session, rows: T[]): T[] =>
    mode === "tom" ? [] : rows.filter((r) => r.tenantId === session.tenantId);

  const supplierProjects = (session: Session) =>
    scoped(session, store.projects).filter((p) => session.supplierId && p.supplierIds.includes(session.supplierId));

  const stripPrivate = (session: Session, rows: UnitParticipation[]): UnitParticipation[] =>
    rows.map((r) => {
      const own = session.role === "beboer" && session.unitId === r.unitId;
      const supplier = session.role === "leverandor";
      if (own || supplier || can(session.role, "private_quotes:read_all")) return r;
      const rest = { ...r };
      delete rest.privateQuote;
      return rest;
    });

  const log = (session: Session, kind: Activity["kind"], text: string, link?: Activity["link"]) => {
    store.activities.unshift({ id: nextId("act"), tenantId: session.tenantId, at: new Date().toISOString(), kind, text, actor: session.name, link });
  };

  const partLabel = (id: Id | undefined) => {
    const part = store.parts.find((p) => p.id === id);
    return part ? `${PART_LABEL[part.category]} · ${part.name}` : undefined;
  };

  const computeCalendar = (session: Session): CalendarEvent[] => {
    const t = session.tenantId;
    const out: CalendarEvent[] = [...scoped(session, store.events)];
    for (const m of scoped(session, store.maintenance)) {
      if (m.status === "ferdig") continue;
      const month = m.recommendedQuarter ? (m.recommendedQuarter - 1) * 3 + 1 : 5;
      out.push({ id: `ev-${m.id}`, tenantId: t, date: `${m.recommendedYear}-${String(month).padStart(2, "0")}-01`, kind: "vedlikehold", title: m.title, link: { type: "tiltak", id: m.id } });
    }
    for (const p of scoped(session, store.projects)) {
      for (const ms of p.milestones) {
        if (ms.done) continue;
        out.push({ id: `ev-${ms.id}`, tenantId: t, date: ms.date, kind: ms.kind === "beslutning" ? "beslutning" : ms.kind === "kontroll" ? "kontroll" : ms.kind === "frist" ? "frist" : "milepael", title: `${p.title}: ${ms.title}`, link: { type: "prosjekt", id: p.id } });
      }
    }
    for (const d of scoped(session, store.documents)) {
      if (d.links.warrantyUntil && !out.some((e) => e.kind === "garanti" && e.date === d.links.warrantyUntil)) {
        out.push({ id: `ev-${d.id}`, tenantId: t, date: d.links.warrantyUntil, kind: "garanti", title: `Garanti utløper: ${d.title}`, link: { type: "dokument", id: d.id } });
      }
    }
    return out.sort((a, b) => a.date.localeCompare(b.date));
  };

  const computePriorities = (session: Session): PriorityItem[] => {
    const items: PriorityItem[] = [];
    const issues = scoped(session, store.issues);
    const crit = issues.find((i) => i.severity === "kritisk" && i.status !== "lost" && i.status !== "avvist");
    if (crit) {
      items.push({
        id: `pri-${crit.id}`,
        title: crit.title,
        type: "kritisk_avvik",
        severity: "kritisk",
        why: `Kritisk avvik meldt ${daysUntil(crit.reportedAt) === 0 ? "i dag" : `for ${Math.abs(daysUntil(crit.reportedAt))} dager siden`}. ${crit.facts.find((f) => f.confidence === "bekreftet")?.text ?? ""}`,
        recommendedAction: crit.nextAction,
        dueDate: crit.dueDate,
        ownerId: crit.ownerId,
        buildingPartLabel: partLabel(crit.buildingPartId),
        primary: { label: "Åpne avviket", to: `/saker?sak=${crit.id}` },
        askEra: `Hva er status på ${crit.ref}?`,
      });
    }
    const qr = scoped(session, store.quoteRequests).find((q) => q.status === "tilbud_mottatt");
    if (qr) {
      const dec = scoped(session, store.decisions).find((d) => d.projectId === qr.projectId && d.status === "krever_beslutning");
      const n = store.quotes.filter((q) => q.quoteRequestId === qr.id).length;
      items.push({
        id: `pri-${qr.id}`,
        title: `Velg leverandør: ${qr.title}`,
        type: "tilbud_ma_vurderes",
        severity: "hoy",
        why: `${n} tilbud er mottatt og analysert. Ett tilbud mangler tre poster fra forespørselen. Oppstart før vinteren krever vedtak ${dec?.meetingDate ? "på styremøtet" : "snart"}.`,
        recommendedAction: "Sammenlign de to komplette tilbudene og be om øvre ramme på råteforbeholdet før vedtak.",
        dueDate: dec?.meetingDate,
        ownerId: store.projects.find((p) => p.id === qr.projectId)?.ownerId,
        buildingPartLabel: partLabel(store.maintenance.find((m) => m.id === qr.maintenanceActionId)?.buildingPartId),
        primary: { label: "Sammenlign tilbud", to: `/tilbud/${qr.id}` },
        askEra: "Sammenlign disse tilbudene",
      });
    }
    const over = scoped(session, store.projects).find((p) => p.budget && p.forecast && p.forecast > p.budget && p.changeOrders.some((c) => c.status === "foreslatt"));
    if (over) {
      const co = over.changeOrders.find((c) => c.status === "foreslatt")!;
      items.push({
        id: `pri-${over.id}`,
        title: `Endringsordre ${co.ref}: ${co.title}`,
        type: "prosjekt_avvik",
        severity: "hoy",
        why: `Prognosen er ${formatNOK((over.forecast ?? 0) - (over.budget ?? 0), { compact: true })} over vedtatt ramme. Kontrakten krever skriftlig godkjenning før utførelse.`,
        recommendedAction: over.boardNextAction,
        dueDate: over.milestones.find((m) => !m.done && m.kind === "beslutning")?.date,
        ownerId: over.ownerId,
        buildingPartLabel: partLabel(store.maintenance.find((m) => m.projectId === over.id)?.buildingPartId),
        primary: { label: "Behandle endringsordre", to: `/prosjekter/${over.id}?fane=tilbud` },
        askEra: `Hva betyr ${co.ref} for budsjettet?`,
      });
    }
    return items.slice(0, 3);
  };

  const summary = (session: Session): BoardSummary => {
    const issues = scoped(session, store.issues).filter((i) => i.status !== "lost" && i.status !== "avvist");
    const parts = scoped(session, store.parts);
    const projects = scoped(session, store.projects).filter((p) => p.stage !== "dokumentert" && p.stage !== "planlagt");
    const cal = computeCalendar(session).filter((e) => daysUntil(e.date) >= 0 && daysUntil(e.date) <= 30);
    const docs = scoped(session, store.documents).filter((d) => Object.keys(d.links).length === 0 || d.missingMetadata.length > 0);
    return {
      actionsRequiringDecision: scoped(session, store.maintenance).filter((m) => m.status === "krever_beslutning").length,
      openIssues: issues.length,
      criticalOpenIssues: issues.filter((i) => i.severity === "kritisk").length,
      activeProjects: projects.length,
      quotesWaiting: scoped(session, store.quoteRequests).filter((q) => q.status === "tilbud_mottatt").reduce((n, q) => n + store.quotes.filter((x) => x.quoteRequestId === q.id).length, 0),
      upcomingDeadlines30d: cal.length,
      buildingAreasMapped: { mapped: parts.filter((p) => p.mapped).length, total: parts.length },
      documentsMissingLink: docs.length,
    };
  };

  const boardOrAdmin = (session: Session) => guard(session, "board:read");

  return {
    async listTenantsFor(session) {
      await guard(session);
      return can(session.role, "tenant:switch") ? store.tenants : store.tenants.filter((t) => t.id === session.tenantId);
    },
    async getTenant(session) {
      await guard(session);
      const t = store.tenants.find((x) => x.id === session.tenantId);
      if (!t) throw new AccessDeniedError("Ukjent borettslag.");
      return t;
    },
    async listPeople(session) {
      await guard(session);
      return store.people.filter((p) => !p.tenantId || p.tenantId === session.tenantId);
    },
    async listBuildings(session) {
      await guard(session);
      return scoped(session, store.buildings);
    },
    async listUnits(session) {
      await guard(session);
      const all = scoped(session, store.units);
      if (session.role === "beboer") return all.filter((u) => u.id === session.unitId);
      if (session.role === "leverandor") {
        const ids = new Set(supplierProjects(session).flatMap((p) => p.affectedUnitIds));
        return all.filter((u) => ids.has(u.id));
      }
      return all;
    },
    async listBuildingParts(session) {
      await boardOrAdmin(session);
      return scoped(session, store.parts);
    },
    async getBoardSummary(session) {
      await boardOrAdmin(session);
      return summary(session);
    },
    async listPriorityItems(session) {
      await boardOrAdmin(session);
      return computePriorities(session);
    },
    async listCalendar(session) {
      await boardOrAdmin(session);
      return computeCalendar(session);
    },
    async listActivity(session, limit) {
      await boardOrAdmin(session);
      const rows = scoped(session, store.activities).sort((a, b) => b.at.localeCompare(a.at));
      return limit ? rows.slice(0, limit) : rows;
    },
    async listMaintenance(session) {
      await boardOrAdmin(session);
      return scoped(session, store.maintenance);
    },
    async listIssues(session) {
      await guard(session, "issues:read");
      return scoped(session, store.issues);
    },
    async createIssue(session, input) {
      await guard(session, "issues:write");
      const n = scoped(session, store.issues).length + 28;
      const issue: Issue = {
        id: nextId("iss"),
        tenantId: session.tenantId,
        ref: `AV-${n}`,
        ...input,
        status: "ny",
        source: "styret",
        reportedAt: new Date().toISOString(),
        reportedBy: session.name,
        photos: 0,
        facts: [],
        history: [{ at: new Date().toISOString(), text: "Opprettet", by: session.name }],
        comments: [],
        tasks: [],
        documentIds: [],
        nextAction: "Vurdere alvorlighetsgrad og ansvar.",
      };
      store.issues.unshift(issue);
      log(session, "avvik_registrert", `${issue.ref} ${issue.title}`, { type: "avvik", id: issue.id });
      return issue;
    },
    async addIssueComment(session, issueId, text, internal) {
      await guard(session, "issues:write");
      const issue = scoped(session, store.issues).find((i) => i.id === issueId);
      if (!issue) throw new AccessDeniedError("Fant ikke saken.");
      issue.comments.push({ at: new Date().toISOString(), by: session.name, text, internal });
      return issue;
    },
    async toggleIssueTask(session, issueId, taskId) {
      await guard(session, "issues:write");
      const issue = scoped(session, store.issues).find((i) => i.id === issueId);
      if (!issue) throw new AccessDeniedError("Fant ikke saken.");
      const task = issue.tasks.find((t) => t.id === taskId);
      if (task) task.done = !task.done;
      return issue;
    },
    async listProjects(session) {
      await guard(session, "projects:read", "supplier:read_assigned", "resident:read_own");
      const all = scoped(session, store.projects);
      if (session.role === "leverandor") return supplierProjects(session);
      if (session.role === "beboer") return all.filter((p) => session.unitId && p.affectedUnitIds.includes(session.unitId));
      return all;
    },
    async createProject(session, input) {
      await guard(session, "projects:write");
      const project: Project = {
        id: nextId("prj"),
        tenantId: session.tenantId,
        ...input,
        stage: "planlagt",
        affectedUnitIds: [],
        ownerId: session.userId,
        supplierIds: [],
        milestones: [],
        openIssueIds: [],
        decisionIds: [],
        changeOrders: [],
        documentIds: [],
        fdvStatus: "ikke_relevant",
        boardNextAction: "Definere omfang og starte kartlegging.",
        hasPrivateUpgrades: false,
      };
      store.projects.unshift(project);
      log(session, "tiltak_oppdatert", `Prosjekt opprettet: ${project.title}`, { type: "prosjekt", id: project.id });
      return project;
    },
    async listParticipation(session, projectId) {
      await guard(session, "projects:read", "supplier:read_assigned", "resident:read_own");
      const project = scoped(session, store.projects).find((p) => p.id === projectId);
      if (!project) throw new AccessDeniedError("Fant ikke prosjektet.");
      if (session.role === "leverandor" && !(session.supplierId && project.supplierIds.includes(session.supplierId))) throw new AccessDeniedError();
      let rows = store.participation.filter((p) => p.projectId === projectId);
      if (session.role === "beboer") rows = rows.filter((r) => r.unitId === session.unitId);
      return stripPrivate(session, rows);
    },
    async decideChangeOrder(session, projectId, changeOrderId, approve) {
      await guard(session, "board:decide");
      const project = scoped(session, store.projects).find((p) => p.id === projectId);
      if (!project) throw new AccessDeniedError("Fant ikke prosjektet.");
      const co = project.changeOrders.find((c) => c.id === changeOrderId);
      if (!co) throw new Error("Fant ikke endringsordren.");
      co.status = approve ? "godkjent" : "avvist";
      if (!approve && project.forecast && project.forecast > (project.budget ?? 0)) project.forecast -= co.amount;
      const dec = store.decisions.find((d) => d.projectId === projectId && d.status === "krever_beslutning" && d.title.includes(co.ref));
      if (dec) {
        dec.status = approve ? "vedtatt" : "avvist";
        dec.decidedAt = TODAY.toISOString().slice(0, 10);
      }
      log(session, approve ? "endringsordre_godkjent" : "beslutning", `${co.ref} ${co.title} ${approve ? "godkjent" : "avvist"}`, { type: "prosjekt", id: projectId });
      return project;
    },
    async listQuoteRequests(session) {
      await guard(session, "quotes:read");
      return scoped(session, store.quoteRequests);
    },
    async listQuotes(session) {
      await guard(session, "quotes:read");
      return scoped(session, store.quotes);
    },
    async listSuppliers(session) {
      await guard(session, "quotes:read", "projects:read", "supplier:read_assigned");
      return store.suppliers;
    },
    async createQuoteRequest(session, input) {
      await guard(session, "quotes:request");
      const qr: QuoteRequest = { id: nextId("qr"), tenantId: session.tenantId, ...input, status: "sendt", createdAt: TODAY.toISOString().slice(0, 10) };
      store.quoteRequests.unshift(qr);
      const project = store.projects.find((p) => p.id === input.projectId);
      if (project) {
        project.quoteRequestId = qr.id;
        if (project.stage === "planlagt" || project.stage === "kartlegging") project.stage = "til_tilbud";
      }
      log(session, "tiltak_oppdatert", `Tilbudsforespørsel sendt: ${qr.title}`, { type: "tilbud", id: qr.id });
      return qr;
    },
    async listDecisions(session) {
      await boardOrAdmin(session);
      return scoped(session, store.decisions);
    },
    async recordDecision(session, decisionId, outcome, quoteId) {
      await guard(session, "board:decide");
      const dec = scoped(session, store.decisions).find((d) => d.id === decisionId);
      if (!dec) throw new AccessDeniedError("Fant ikke beslutningen.");
      dec.status = outcome;
      dec.decidedAt = TODAY.toISOString().slice(0, 10);
      if (quoteId) dec.quoteId = quoteId;
      if (outcome === "vedtatt" && dec.projectId) {
        const project = store.projects.find((p) => p.id === dec.projectId);
        const quote = store.quotes.find((q) => q.id === quoteId);
        if (project && quote) {
          project.stage = "vedtatt";
          project.supplierIds = [quote.supplierId];
          project.forecast = quote.totalIncVat;
          project.sharedCost = quote.totalIncVat;
          const qr = store.quoteRequests.find((q) => q.id === quote.quoteRequestId);
          if (qr) qr.status = "besluttet";
        }
        const ma = store.maintenance.find((m) => m.id === dec.maintenanceActionId);
        if (ma) ma.status = "planlagt";
      }
      log(session, "beslutning", `${dec.title}: ${outcome}`, dec.projectId ? { type: "prosjekt", id: dec.projectId } : undefined);
      return dec;
    },
    async listResidents(session) {
      await guard(session, "residents:read");
      const rows = scoped(session, store.residents);
      if (can(session.role, "residents:contact")) return rows;
      return rows.map(({ email: _e, phone: _p, ...rest }) => rest);
    },
    async listMessages(session) {
      await guard(session, "residents:read", "messages:send");
      return scoped(session, store.messages).sort((a, b) => (b.sentAt ?? "").localeCompare(a.sentAt ?? ""));
    },
    async sendMessage(session, input, when) {
      await guard(session, "messages:send");
      const recipients = await this.countRecipients(session, input.segment);
      const msg: Message = {
        id: nextId("msg"),
        tenantId: session.tenantId,
        ...input,
        recipients,
        status: when === "na" ? "sendt" : "utkast",
        sentAt: when === "na" ? new Date().toISOString() : undefined,
        stats: when === "na" ? { delivered: recipients, read: 0, confirmed: 0, replied: 0 } : undefined,
      };
      store.messages.unshift(msg);
      if (when === "na") log(session, "melding_sendt", `Melding sendt til ${recipients} mottakere: ${msg.subject}`, { type: "melding", id: msg.id });
      return msg;
    },
    async countRecipients(session, segment) {
      const units = scoped(session, store.units);
      switch (segment.kind) {
        case "alle":
          return units.length;
        case "bygg":
          return units.filter((u) => u.buildingId === segment.buildingId).length;
        case "oppgang":
          return units.filter((u) => u.entranceId === segment.entranceId).length;
        case "berorte":
          return store.projects.find((p) => p.id === segment.projectId)?.affectedUnitIds.length ?? 0;
        case "beboer":
          return 1;
      }
    },
    async listDocuments(session) {
      await guard(session, "documents:read", "resident:read_own", "supplier:read_assigned");
      const rows = scoped(session, store.documents);
      if (session.role === "beboer") return rows.filter((d) => d.access === "alle_beboere" || (d.access === "privat" && d.links.unitId === session.unitId));
      if (session.role === "leverandor") {
        const ids = new Set(supplierProjects(session).map((p) => p.id));
        return rows.filter((d) => d.access === "leverandor" || (d.links.projectId && ids.has(d.links.projectId) && d.links.supplierId === session.supplierId));
      }
      return rows;
    },
    async confirmFinding(session, documentId, findingId, correctedText) {
      await guard(session, "documents:correct");
      const doc = scoped(session, store.documents).find((d) => d.id === documentId);
      const f = doc?.findings.find((x) => x.id === findingId);
      if (!doc || !f) throw new Error("Fant ikke funnet.");
      f.confirmedBy = session.name;
      f.confidence = "bekreftet";
      if (correctedText && correctedText !== f.text) f.correctedText = correctedText;
      log(session, "dokument_analysert", `Funn ${correctedText ? "korrigert" : "bekreftet"} i ${doc.title}`, { type: "dokument", id: doc.id });
      return f;
    },
    async listBudget(session) {
      await guard(session, "economy:read");
      return scoped(session, store.budget);
    },
    async getMyParticipation(session) {
      await guard(session, "resident:read_own");
      if (!session.unitId) return null;
      const unit = scoped(session, store.units).find((u) => u.id === session.unitId);
      const participation = store.participation.find((p) => p.unitId === session.unitId);
      const project = participation && scoped(session, store.projects).find((p) => p.id === participation.projectId);
      if (!unit || !participation || !project) return null;
      return { project, participation, unit };
    },
    async answerSurvey(session, projectId, answers, photos) {
      await guard(session, "resident:read_own");
      const row = store.participation.find((p) => p.projectId === projectId && p.unitId === session.unitId);
      if (!row) throw new AccessDeniedError();
      row.surveyAnswers = answers;
      row.photos = photos;
      if (row.responseStatus === "ikke_svart" || row.responseStatus === "ikke_kontaktet" || row.responseStatus === "kartlegging_pagar") row.responseStatus = "vurderer";
      log(session, "beboer_svart", `${session.name} har svart på kartleggingen`, { type: "prosjekt", id: projectId });
      return row;
    },
    async chooseTier(session, projectId, tier, optionIds) {
      await guard(session, "resident:read_own");
      const row = store.participation.find((p) => p.projectId === projectId && p.unitId === session.unitId);
      const project = store.projects.find((p) => p.id === projectId);
      if (!row || !project) throw new AccessDeniedError();
      row.tier = tier;
      if (tier === "kun_felles") {
        row.responseStatus = "avslatt";
        row.privateQuote = undefined;
        row.readiness = row.accessConfirmed ? "klar" : "mangler_tilgang";
        row.readinessNote = row.accessConfirmed ? undefined : "Bekreft tilgang på dagtid";
      } else {
        const pkg = project.packages?.find((p) => p.tier === tier);
        const base = pkg ? Math.round(((pkg.priceFrom ?? 0) + (pkg.priceTo ?? 0)) / 2) : 0;
        row.responseStatus = "valgt";
        row.readiness = "mangler_avklaring";
        row.readinessNote = "Tilbud ikke akseptert ennå";
        row.privateQuote = {
          tier,
          basePrice: base,
          options: (project.productOptions ?? []).filter((o) => o.price > 0).map((o) => ({ id: o.id, name: o.name, price: o.price, selected: optionIds.includes(o.id) })),
          coordinationDiscount: pkg?.coordinationDiscount ?? 0,
          vatIncluded: true,
        };
      }
      return row;
    },
    async acceptPrivateQuote(session, projectId) {
      await guard(session, "resident:read_own");
      const row = store.participation.find((p) => p.projectId === projectId && p.unitId === session.unitId);
      if (!row?.privateQuote) throw new Error("Ingen tilbud å akseptere.");
      row.privateQuote.accepted = TODAY.toISOString().slice(0, 10);
      row.responseStatus = "akseptert";
      row.readiness = row.accessConfirmed ? "klar" : "mangler_tilgang";
      row.readinessNote = row.accessConfirmed ? undefined : "Bekreft tilgang på dagtid";
      const project = store.projects.find((p) => p.id === projectId);
      if (project?.privateAggregate) {
        project.privateAggregate.unitsOptingIn += 0;
        project.privateAggregate.total += row.privateQuote.basePrice + row.privateQuote.options.filter((o) => o.selected).reduce((s, o) => s + o.price, 0) - row.privateQuote.coordinationDiscount;
      }
      log(session, "beboer_svart", `${session.name} har akseptert privat tilbud`, { type: "prosjekt", id: projectId });
      return row;
    },
    async askEra(session, question, context): Promise<AssistantAnswer> {
      await guard(session, "assistant:use");
      await wait(600);
      return answerFor(question, { ...context, tenantId: session.tenantId, role: session.role });
    },
  };
}

export type { DataAdapter };
