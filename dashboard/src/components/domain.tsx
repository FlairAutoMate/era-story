/**
 * Domenekomponenter som brukes på flere sider: statusmerker, oppslag, aktivitetsstrøm,
 * vedlikeholdstidslinje, stegvisning, beslutningspanel og kostnadsdeling.
 */
import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router";
import type { Activity, CalendarEvent, Decision, IssueStatus, MaintenanceStatus, Project, ProjectStage, Quote, Severity } from "@/domain/types";
import { PROJECT_STAGES } from "@/domain/types";
import { useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import { daysUntil, formatDate, formatDateTime, formatNOK, TODAY } from "@/lib/format";
import { ACTIVITY_LABEL, ISSUE_STATUS_LABEL, ISSUE_TONE, MAINT_STATUS_LABEL, MAINT_TONE, SEVERITY_LABEL, SEVERITY_TONE, STAGE_LABEL, STAGE_TONE } from "@/lib/labels";
import { Badge, Button, Callout, ConfirmModal, EmptyState } from "./ui";
import { useToast } from "./toast";

export const MaintStatusBadge = ({ s }: { s: MaintenanceStatus }) => <Badge tone={MAINT_TONE[s]}>{MAINT_STATUS_LABEL[s]}</Badge>;
export const IssueStatusBadge = ({ s }: { s: IssueStatus }) => <Badge tone={ISSUE_TONE[s]}>{ISSUE_STATUS_LABEL[s]}</Badge>;
export const SeverityBadge = ({ s }: { s: Severity }) => <Badge tone={SEVERITY_TONE[s]}>{SEVERITY_LABEL[s]}</Badge>;
export const StageBadge = ({ s }: { s: ProjectStage }) => <Badge tone={STAGE_TONE[s]}>{STAGE_LABEL[s]}</Badge>;

/** Oppslag for navn på personer, bygg, bygningsdeler og leverandører. */
export function useLookup() {
  const people = useQuery((a, s) => a.listPeople(s));
  const buildings = useQuery((a, s) => a.listBuildings(s));
  const parts = useQuery((a, s) => (can(s.role, "board:read") ? a.listBuildingParts(s) : Promise.resolve([])));
  const suppliers = useQuery((a, s) => a.listSuppliers(s).catch(() => []));
  return useMemo(() => {
    const person = (id?: string) => people.data?.find((p) => p.id === id)?.name ?? (id ? id : undefined);
    const building = (id?: string) => buildings.data?.find((b) => b.id === id)?.name;
    const entrance = (id?: string) => buildings.data?.flatMap((b) => b.entrances).find((e) => e.id === id)?.name;
    const part = (id?: string) => parts.data?.find((p) => p.id === id)?.name;
    const supplier = (id?: string) => suppliers.data?.find((s) => s.id === id)?.name;
    return { person, building, entrance, part, supplier, buildings: buildings.data ?? [], parts: parts.data ?? [], suppliers: suppliers.data ?? [], people: people.data ?? [] };
  }, [people.data, buildings.data, parts.data, suppliers.data]);
}

export function Deadline({ date }: { date?: string }) {
  if (!date) return <span className="muted">Ingen frist</span>;
  const n = daysUntil(date);
  const cls = n < 0 ? "critical" : n <= 7 ? "decision" : "neutral";
  return (
    <Badge tone={cls} plain>
      {n < 0 ? `Passert ${formatDate(date)}` : n === 0 ? "I dag" : n <= 14 ? `Om ${n} d. (${formatDate(date)})` : formatDate(date)}
    </Badge>
  );
}

/* ---------- ActivityTimeline ---------- */
const activityLink = (a: Activity) => {
  if (!a.link) return undefined;
  switch (a.link.type) {
    case "prosjekt":
      return `/prosjekter/${a.link.id}`;
    case "avvik":
      return `/saker?sak=${a.link.id}`;
    case "dokument":
      return `/dokumenter?dok=${a.link.id}`;
    case "tilbud":
      return `/tilbud`;
    case "tiltak":
      return `/vedlikehold?tiltak=${a.link.id}`;
    case "melding":
      return `/beboere?fane=meldinger`;
  }
};

export function ActivityTimeline({ items, compact }: { items: Activity[]; compact?: boolean }) {
  if (items.length === 0) return <EmptyState title="Ingen aktivitet ennå" what="Her vises hendelser som dokumenter som er analysert, avvik, tilbud og beboersvar." />;
  return (
    <ul className="activity">
      {items.map((a) => {
        const to = activityLink(a);
        return (
          <li key={a.id}>
            <time dateTime={a.at}>{formatDateTime(a.at)}</time>
            <div>
              <div className="k">{ACTIVITY_LABEL[a.kind]}</div>
              <div>{to ? <Link to={to}>{a.text}</Link> : a.text}</div>
              {!compact && <div className="muted small">{a.actor}</div>}
            </div>
          </li>
        );
      })}
    </ul>
  );
}

/* ---------- MaintenanceTimeline (12 mnd / 36 mnd / 10 år) ---------- */
export type Horizon = "12" | "36" | "120";

const eventLink = (e: CalendarEvent) => {
  if (!e.link) return undefined;
  switch (e.link.type) {
    case "prosjekt":
      return `/prosjekter/${e.link.id}`;
    case "tiltak":
      return `/vedlikehold?tiltak=${e.link.id}`;
    case "avvik":
      return `/saker?sak=${e.link.id}`;
    case "tilbud":
      return `/tilbud`;
    case "dokument":
      return `/dokumenter?dok=${e.link.id}`;
  }
};

const MONTHS = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"];

export function MaintenanceTimeline({ events, horizon, onHorizon, limitPerCol = 4 }: { events: CalendarEvent[]; horizon: Horizon; onHorizon: (h: Horizon) => void; limitPerCol?: number }) {
  const cols = useMemo(() => {
    const start = new Date(TODAY.getFullYear(), TODAY.getMonth(), 1);
    if (horizon === "12") {
      return Array.from({ length: 12 }, (_, i) => {
        const d = new Date(start.getFullYear(), start.getMonth() + i, 1);
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
        return { key, label: `${MONTHS[d.getMonth()]}${d.getMonth() === 0 || i === 0 ? ` ${String(d.getFullYear()).slice(2)}` : ""}`, now: i === 0, match: (e: CalendarEvent) => e.date.startsWith(key) };
      });
    }
    if (horizon === "36") {
      return Array.from({ length: 12 }, (_, i) => {
        const d = new Date(start.getFullYear(), start.getMonth() + i * 3, 1);
        const q = Math.floor(d.getMonth() / 3) + 1;
        const from = d.toISOString().slice(0, 10);
        const to = new Date(d.getFullYear(), d.getMonth() + 3, 1).toISOString().slice(0, 10);
        return { key: from, label: `Q${q} ${String(d.getFullYear()).slice(2)}`, now: i === 0, match: (e: CalendarEvent) => e.date >= from && e.date < to };
      });
    }
    return Array.from({ length: 10 }, (_, i) => {
      const y = TODAY.getFullYear() + i;
      return { key: String(y), label: String(y), now: i === 0, match: (e: CalendarEvent) => e.date.startsWith(String(y)) };
    });
  }, [horizon]);

  const upcoming = events.filter((e) => daysUntil(e.date) >= -30);
  return (
    <div>
      <div className="row" style={{ marginBottom: 10 }}>
        <div className="timeline-toggle" role="group" aria-label="Tidshorisont">
          {(["12", "36", "120"] as Horizon[]).map((h) => (
            <button key={h} aria-pressed={horizon === h} onClick={() => onHorizon(h)}>
              {h === "12" ? "12 måneder" : h === "36" ? "36 måneder" : "10-årsplan"}
            </button>
          ))}
        </div>
      </div>
      <div className={`tl ${horizon === "36" ? "y3" : horizon === "120" ? "y10" : ""}`}>
        {cols.map((c) => {
          const evs = upcoming.filter(c.match);
          return (
            <div key={c.key} className={`col${c.now ? " now" : ""}`}>
              <div className="m">{c.label}</div>
              {evs.slice(0, limitPerCol).map((e) => {
                const to = eventLink(e);
                const inner = (
                  <>
                    <span className="sr">{e.kind}: </span>
                    {e.title}
                  </>
                );
                return to ? (
                  <Link key={e.id} to={to} className={`ev ${e.kind}`} title={`${formatDate(e.date)} · ${e.title}`}>
                    {inner}
                  </Link>
                ) : (
                  <span key={e.id} className={`ev ${e.kind}`} title={`${formatDate(e.date)} · ${e.title}`}>
                    {inner}
                  </span>
                );
              })}
              {evs.length > limitPerCol && <span className="more">+{evs.length - limitPerCol} til</span>}
            </div>
          );
        })}
      </div>
      <div className="legend" aria-hidden="true">
        <span><i style={{ background: "var(--planned)" }} />Vedlikehold</span>
        <span><i style={{ background: "var(--active)" }} />Kontroll</span>
        <span><i style={{ background: "var(--danger)" }} />Frist</span>
        <span><i style={{ background: "var(--decision)" }} />Styrebeslutning</span>
        <span><i style={{ background: "var(--good)" }} />Milepæl</span>
        <span><i style={{ background: "var(--copper)" }} />Garanti</span>
      </div>
    </div>
  );
}

/* ---------- Prosjektstatusflyt ---------- */
export function StageBar({ stage }: { stage: ProjectStage }) {
  const idx = PROJECT_STAGES.indexOf(stage);
  return (
    <div className="stagebar" aria-label={`Status: ${STAGE_LABEL[stage]}`}>
      {PROJECT_STAGES.map((s, i) => (
        <span key={s} className={i < idx ? "done" : i === idx ? "now" : ""} aria-current={i === idx ? "step" : undefined}>
          {STAGE_LABEL[s]}
        </span>
      ))}
    </div>
  );
}

export function StageDots({ stage }: { stage: ProjectStage }) {
  const idx = PROJECT_STAGES.indexOf(stage);
  return (
    <div className="stages" aria-hidden="true">
      {PROJECT_STAGES.map((s, i) => (
        <i key={s} className={i < idx ? "done" : i === idx ? "now" : ""} />
      ))}
    </div>
  );
}

/* ---------- DecisionPanel ---------- */
export function DecisionPanel({ decision, quotes, onDone, compact }: { decision: Decision; quotes?: Quote[]; onDone?: () => void; compact?: boolean }) {
  const session = useSession();
  const lookup = useLookup();
  const toast = useToast();
  const [confirm, setConfirm] = useState<{ outcome: "vedtatt" | "avvist" | "utsatt"; quoteId?: string } | null>(null);
  const [quoteId, setQuoteId] = useState<string>(quotes?.[0]?.id ?? "");
  const mut = useMutation((a, s, id: string, outcome: "vedtatt" | "avvist" | "utsatt", q?: string) => a.recordDecision(s, id, outcome, q));
  const canDecide = can(session.role, "board:decide");
  const decided = decision.status !== "krever_beslutning";

  const modal = confirm && (
    <ConfirmModal
      title={`Registrere «${confirm.outcome}»?`}
      body={<p>Vedtaket loggføres med dato og navn. Det kan ikke slettes, bare omgjøres med nytt vedtak.</p>}
      confirmLabel="Registrer vedtak"
      pending={mut.pending}
      onCancel={() => setConfirm(null)}
      onConfirm={async () => {
        const r = await mut.run(decision.id, confirm.outcome, confirm.quoteId);
        setConfirm(null);
        if (r) {
          toast(`Vedtak registrert: ${decision.title}`);
          onDone?.();
        } else toast("Kunne ikke registrere vedtak", "error");
      }}
    />
  );

  if (compact) {
    return (
      <div className="card pad row decision-bar" data-testid="decision-panel">
        <Badge tone={decided ? (decision.status === "vedtatt" ? "done" : "neutral") : "decision"}>{decided ? (decision.status === "vedtatt" ? "Vedtatt" : decision.status === "avvist" ? "Avvist" : "Utsatt") : "Krever beslutning"}</Badge>
        <div className="grow">
          <strong>{decision.title}</strong>
          <div className="small muted">{decision.meetingDate ? `Styremøte ${formatDate(decision.meetingDate)} · ` : ""}{decided ? `${decision.status === "vedtatt" ? "Vedtatt" : decision.status} ${decision.decidedAt ? formatDate(decision.decidedAt) : ""}${decision.quoteId && quotes ? ` · ${lookup.supplier(quotes.find((q) => q.id === decision.quoteId)?.supplierId)}` : ""}` : "ERA velger ikke leverandør. Styret beslutter."}</div>
        </div>
        {!decided && canDecide && quotes && quotes.length > 0 && (
          <select value={quoteId} onChange={(e) => setQuoteId(e.target.value)} aria-label="Velg tilbud som legges til grunn" style={{ minHeight: 36, borderRadius: 6, border: "1px solid var(--line-strong)", background: "var(--card)", padding: "0 8px", maxWidth: 280 }}>
            {quotes.map((q) => (
              <option key={q.id} value={q.id}>{lookup.supplier(q.supplierId) ?? q.supplierId} · {formatNOK(q.totalIncVat, { compact: true })}</option>
            ))}
          </select>
        )}
        {!decided && canDecide ? (
          <div className="row" style={{ flexWrap: "nowrap" }}>
            <Button size="sm" onClick={() => setConfirm({ outcome: "vedtatt", quoteId: quotes?.length ? quoteId : undefined })} data-testid="decide-approve">Vedta</Button>
            <Button size="sm" variant="secondary" onClick={() => setConfirm({ outcome: "utsatt" })}>Utsett</Button>
            <Button size="sm" variant="ghost" onClick={() => setConfirm({ outcome: "avvist" })}>Avvis</Button>
          </div>
        ) : !decided ? <span className="small muted">Bare styreleder registrerer vedtak</span> : null}
        {modal}
      </div>
    );
  }

  return (
    <div className="card pad stack" data-testid="decision-panel">
      <div className="row">
        <div className="eyebrow">Beslutning</div>
        <Badge tone={decided ? (decision.status === "vedtatt" ? "done" : "neutral") : "decision"}>{decided ? (decision.status === "vedtatt" ? "Vedtatt" : decision.status === "avvist" ? "Avvist" : "Utsatt") : "Krever beslutning"}</Badge>
        {decision.meetingDate && <span className="small muted">Styremøte {formatDate(decision.meetingDate)}</span>}
      </div>
      <h3>{decision.title}</h3>
      <p className="small">{decision.summary}</p>
      {decided ? (
        <Callout tone={decision.status === "vedtatt" ? "good" : undefined}>
          {decision.status === "vedtatt" ? "Vedtatt" : decision.status === "avvist" ? "Avvist" : "Utsatt"} {decision.decidedAt ? formatDate(decision.decidedAt) : ""}
          {decision.quoteId && quotes && <> · valgt leverandør: {lookup.supplier(quotes.find((q) => q.id === decision.quoteId)?.supplierId)}</>}
        </Callout>
      ) : canDecide ? (
        <>
          {quotes && quotes.length > 0 && (
            <div className="field">
              <label htmlFor={`q-${decision.id}`}>Velg tilbud som legges til grunn</label>
              <select id={`q-${decision.id}`} value={quoteId} onChange={(e) => setQuoteId(e.target.value)}>
                {quotes.map((q) => (
                  <option key={q.id} value={q.id}>
                    {lookup.supplier(q.supplierId) ?? q.supplierId} · {formatNOK(q.totalIncVat, { compact: true })} inkl. mva
                  </option>
                ))}
              </select>
              <span className="hint">ERA velger ikke leverandør. Styret beslutter.</span>
            </div>
          )}
          <div className="row">
            <Button onClick={() => setConfirm({ outcome: "vedtatt", quoteId: quotes?.length ? quoteId : undefined })} data-testid="decide-approve">
              Vedta
            </Button>
            <Button variant="secondary" onClick={() => setConfirm({ outcome: "utsatt" })}>
              Utsett
            </Button>
            <Button variant="ghost" onClick={() => setConfirm({ outcome: "avvist" })}>
              Avvis
            </Button>
          </div>
        </>
      ) : (
        <Callout>Bare styreleder kan registrere vedtak. Du kan lese grunnlaget og kommentere i saken.</Callout>
      )}
      {modal}
    </div>
  );
}

/* ---------- CostResponsibilityBreakdown ---------- */
export function CostResponsibilityBreakdown({ project, showPrivate }: { project: Project; showPrivate: boolean }) {
  return (
    <div className="cost-split" data-testid="cost-split">
      <div className="box shared">
        <div className="eyebrow">Felles kostnad (borettslaget)</div>
        <div className="figure">{formatNOK(project.sharedCost ?? project.forecast, { compact: true })}</div>
        <div className="small muted">{project.budget ? `Vedtatt ramme ${formatNOK(project.budget, { compact: true })}` : "Ingen vedtatt ramme"}</div>
      </div>
      <div className="box private">
        <div className="eyebrow">Private tilvalg (betales av beboer)</div>
        {!project.hasPrivateUpgrades ? (
          <div className="muted">Ingen private tilvalg i dette prosjektet</div>
        ) : showPrivate && project.privateAggregate ? (
          <>
            <div className="figure">{formatNOK(project.privateAggregate.total, { compact: true })}</div>
            <div className="small muted">Aggregert for {project.privateAggregate.unitsOptingIn} boliger. Enkelttilbud er ikke synlige for styret.</div>
          </>
        ) : (
          <div className="muted">Aggregert beløp krever tilgang</div>
        )}
      </div>
    </div>
  );
}

export function Money({ v, compact = true }: { v: number | undefined; compact?: boolean }) {
  return <span className="num">{formatNOK(v, { compact })}</span>;
}

export function Empty({ children }: { children: ReactNode }) {
  return <span className="muted">{children}</span>;
}
