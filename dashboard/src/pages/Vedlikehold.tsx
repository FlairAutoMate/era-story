/** Levende vedlikeholdsrom: prioritert liste, tidslinje, bygningsdeler, årsplan, 10-årsplan. */
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { useQuery } from "@/data/provider";
import type { BuildingPart, MaintenanceAction, MaintenanceStatus } from "@/domain/types";
import { formatRange } from "@/lib/format";
import { MAINT_STATUS_LABEL, PART_LABEL, SEVERITY_LABEL } from "@/lib/labels";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useAssistant, useAssistantSelection } from "@/shell/assistant";
import { MaintStatusBadge, MaintenanceTimeline, SeverityBadge, useLookup, type Horizon } from "@/components/domain";
import { Badge, Button, Card, ConfidenceBadge, Drawer, EmptyState, ErrorState, KV, LinkButton, Missing, NextBox, Skeleton, Tabs } from "@/components/ui";

type View = "liste" | "tidslinje" | "bygningsdeler" | "arsplan" | "tiarsplan";
const SEV_ORDER = { kritisk: 0, hoy: 1, middels: 2, lav: 3 } as const;
const STATUS_ORDER: Record<MaintenanceStatus, number> = { krever_beslutning: 0, pagar: 1, planlagt: 2, mangler_data: 3, forslag: 4, utsatt: 5, ferdig: 6 };

export function Vedlikehold() {
  const [view, setView] = useUrlParam("visning", "liste");
  const [status, setStatus] = useUrlParam("status");
  const [selected, setSelected] = useUrlParam("tiltak");
  const [horizon, setHorizon] = useUrlParam("horisont", "12");
  const lookup = useLookup();
  const actions = useQuery((a, s) => a.listMaintenance(s));
  const parts = useQuery((a, s) => a.listBuildingParts(s));
  const calendar = useQuery((a, s) => a.listCalendar(s));

  const rows = useMemo(() => {
    const list = (actions.data ?? []).filter((m) => !status || m.status === status);
    return [...list].sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status] || SEV_ORDER[a.priority] - SEV_ORDER[b.priority] || a.recommendedYear - b.recommendedYear);
  }, [actions.data, status]);
  const open = actions.data?.find((m) => m.id === selected);
  const counts = useMemo(() => {
    const c: Partial<Record<MaintenanceStatus, number>> = {};
    for (const m of actions.data ?? []) c[m.status] = (c[m.status] ?? 0) + 1;
    return c;
  }, [actions.data]);

  return (
    <>
      <PageHead title="Vedlikehold" meta={actions.data ? [`${actions.data.length} tiltak`, `${counts.krever_beslutning ?? 0} krever beslutning`, `${counts.mangler_data ?? 0} mangler grunnlag`] : []} actions={<LinkButton to="/?horisont=36#tidslinje" variant="secondary">Kommende på oversikten</LinkButton>} />
      <Tabs<View>
        label="Visning"
        value={view as View}
        onChange={(v) => setView(v)}
        items={[
          { id: "liste", label: "Prioritert liste", count: actions.data?.length },
          { id: "tidslinje", label: "Tidslinje" },
          { id: "bygningsdeler", label: "Bygningsdeler", count: parts.data?.length },
          { id: "arsplan", label: "Årsplan 2026" },
          { id: "tiarsplan", label: "10-årsplan" },
        ]}
      />

      {actions.status === "error" ? (
        <div className="section"><ErrorState error={actions.error} retry={actions.reload} /></div>
      ) : !actions.data ? (
        <div className="section"><Skeleton lines={8} /></div>
      ) : view === "liste" ? (
        <>
          <div className="filters">
            <label className="sr" htmlFor="f-status">Status</label>
            <select id="f-status" value={status} onChange={(e) => setStatus(e.target.value)} data-testid="filter-status">
              <option value="">Alle statuser</option>
              {(Object.keys(MAINT_STATUS_LABEL) as MaintenanceStatus[]).map((s) => (
                <option key={s} value={s}>
                  {MAINT_STATUS_LABEL[s]} ({counts[s] ?? 0})
                </option>
              ))}
            </select>
            {status && (
              <Button variant="ghost" size="sm" onClick={() => setStatus(null)}>
                Nullstill
              </Button>
            )}
          </div>
          {rows.length === 0 ? (
            <EmptyState title="Ingen tiltak i denne visningen" what="Vedlikeholdsplanen bygges av tilstandsrapporter, FDV og innmeldte avvik." why={status ? "Prøv et annet filter." : "Last opp en tilstandsrapport for å få ERAs forslag til tiltak."} action={<LinkButton to="/dokumenter" variant="secondary">Gå til dokumenter</LinkButton>} />
          ) : (
            <MaintenanceActionTable rows={rows} lookup={lookup} onOpen={(id) => setSelected(id)} selectedId={selected} />
          )}
        </>
      ) : view === "tidslinje" ? (
        <Card pad className="section">{calendar.data ? <MaintenanceTimeline events={calendar.data} horizon={horizon as Horizon} onHorizon={(h) => setHorizon(h)} limitPerCol={6} /> : <Skeleton lines={4} />}</Card>
      ) : view === "bygningsdeler" ? (
        <BuildingParts parts={parts.data ?? []} actions={actions.data} onOpen={(id) => setSelected(id)} lookup={lookup} />
      ) : (
        <YearPlan actions={actions.data} years={view === "arsplan" ? [2026] : Array.from({ length: 10 }, (_, i) => 2026 + i)} onOpen={(id) => setSelected(id)} lookup={lookup} />
      )}

      {open && <MaintenanceDetail m={open} lookup={lookup} onClose={() => setSelected(null)} />}
    </>
  );
}

type Lookup = ReturnType<typeof useLookup>;

const CLIP = 8;

function MaintenanceActionTable({ rows, lookup, onOpen, selectedId }: { rows: MaintenanceAction[]; lookup: Lookup; onOpen: (id: string) => void; selectedId: string }) {
  const [all, setAll] = useState(false);
  const shown = all ? rows : rows.slice(0, CLIP);
  const rest = rows.length - shown.length;
  return (
    <>
      <div className="fill desktop-only">
      <div className="table-wrap">
        <table className="tbl" data-testid="maintenance-table">
          <thead>
            <tr>
              <th>Tiltak</th>
              <th>Status</th>
              <th>Prioritet</th>
              <th>Anbefalt</th>
              <th className="num">Kostnad</th>
              <th>Grunnlag</th>
              <th>Ansvarlig</th>
              <th>Neste handling</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((m) => (
              <tr key={m.id} className="rowlink" tabIndex={0} aria-selected={selectedId === m.id} onClick={() => onOpen(m.id)} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onOpen(m.id))}>
                <td>
                  <span className="primary">{m.title}</span>
                  <span className="sub">{lookup.part(m.buildingPartId)}{m.buildingId ? ` · ${lookup.building(m.buildingId)}` : " · Hele eiendommen"}</span>
                </td>
                <td><MaintStatusBadge s={m.status} /></td>
                <td><SeverityBadge s={m.priority} /></td>
                <td className="nowrap">{m.recommendedYear}{m.recommendedQuarter ? ` Q${m.recommendedQuarter}` : ""}</td>
                <td className="num nowrap">{m.cost ? formatRange(m.cost.low, m.cost.high) : <Missing>Mangler grunnlag</Missing>}</td>
                <td><ConfidenceBadge value={m.basis.confidence} /></td>
                <td>{lookup.person(m.ownerId) ?? <span className="muted">Ikke satt</span>}</td>
                <td className="wrap">{m.nextAction}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rest > 0 ? (
        <div className="more-row" data-testid="more-row">
          <span>+ {rest} til</span>
          <button className="linkish" onClick={() => setAll(true)}>Vis alle {rows.length}</button>
        </div>
      ) : all && rows.length > CLIP ? (
        <div className="more-row"><span>Viser alle {rows.length}</span><button className="linkish" onClick={() => setAll(false)}>Vis færre</button></div>
      ) : null}
      </div>
      <div className="cardlist mobile-only">
        {rows.map((m) => (
          <button key={m.id} className="item" onClick={() => onOpen(m.id)}>
            <span className="t">{m.title}</span>
            <span className="m" style={{ marginBottom: 6 }}>
              <MaintStatusBadge s={m.status} />
              <SeverityBadge s={m.priority} />
            </span>
            <span className="m">
              <span>{m.recommendedYear}{m.recommendedQuarter ? ` Q${m.recommendedQuarter}` : ""}</span>
              <span>{m.cost ? formatRange(m.cost.low, m.cost.high) : "Mangler grunnlag"}</span>
            </span>
          </button>
        ))}
      </div>
    </>
  );
}

function BuildingParts({ parts, actions, onOpen, lookup }: { parts: BuildingPart[]; actions: MaintenanceAction[]; onOpen: (id: string) => void; lookup: Lookup }) {
  return (
    <div className="grid cols-3 section">
      {parts.map((p) => {
        const acts = actions.filter((a) => a.buildingPartId === p.id && a.status !== "ferdig");
        const tg = p.conditionGrade;
        return (
          <Card key={p.id} pad className="stack">
            <div className="row">
              <span className="eyebrow">{PART_LABEL[p.category]}</span>
              {p.mapped ? <Badge tone={tg === 3 ? "critical" : tg === 2 ? "decision" : "done"}>TG {tg}</Badge> : <Badge tone="neutral">Ikke kartlagt</Badge>}
            </div>
            <h3>{p.name}</h3>
            <KV
              items={[
                ["Bygg", p.buildingId ? lookup.building(p.buildingId) : "Hele eiendommen"],
                ["Montert", p.installedYear ?? <Missing />],
                ["Levetid", p.installedYear && p.expectedLifetimeYears ? `til ca. ${p.installedYear + p.expectedLifetimeYears}` : <Missing />],
                ["Grunnlag", p.conditionSource ?? <Missing>Mangler grunnlag</Missing>],
              ]}
            />
            {acts.length > 0 ? (
              <ul style={{ margin: 0, paddingLeft: 18 }} className="small">
                {acts.map((a) => (
                  <li key={a.id}>
                    <button className="linkbtn" onClick={() => onOpen(a.id)}>{a.title}</button> · {MAINT_STATUS_LABEL[a.status]}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="small muted">Ingen åpne tiltak.</p>
            )}
          </Card>
        );
      })}
    </div>
  );
}

function YearPlan({ actions, years, onOpen, lookup }: { actions: MaintenanceAction[]; years: number[]; onOpen: (id: string) => void; lookup: Lookup }) {
  const single = years.length === 1;
  return (
    <div className="stack section">
      {years.map((y) => {
        const rows = actions.filter((a) => a.recommendedYear === y && a.status !== "ferdig").sort((a, b) => (a.recommendedQuarter ?? 9) - (b.recommendedQuarter ?? 9));
        const low = rows.reduce((s, r) => s + (r.cost?.low ?? 0), 0);
        const high = rows.reduce((s, r) => s + (r.cost?.high ?? 0), 0);
        const unknown = rows.filter((r) => !r.cost).length;
        if (!single && rows.length === 0) return (
          <Card key={y} pad className="row">
            <strong style={{ width: 56 }}>{y}</strong>
            <span className="muted small">Ingen planlagte tiltak</span>
          </Card>
        );
        return (
          <Card key={y}>
            <div className="card-head">
              <h2>{y}</h2>
              <div className="right small muted">
                {rows.length} tiltak · {high > 0 ? formatRange(low, high) : "kostnad ikke registrert"}
                {unknown > 0 && ` · ${unknown} uten anslag`}
              </div>
            </div>
            <div className="card-body">
              {rows.length === 0 ? (
                <p className="muted small">Ingen tiltak planlagt i {y}.</p>
              ) : (
                <ul className="tasklist">
                  {rows.map((r) => (
                    <li key={r.id}>
                      <span className="mono small muted" style={{ width: 28 }}>{r.recommendedQuarter ? `Q${r.recommendedQuarter}` : ""}</span>
                      <button className="linkbtn grow" style={{ textAlign: "left", textDecoration: "none" }} onClick={() => onOpen(r.id)}>{r.title}</button>
                      <span className="small muted desktop-only">{lookup.part(r.buildingPartId)}</span>
                      <MaintStatusBadge s={r.status} />
                      <span className="small num nowrap">{r.cost ? formatRange(r.cost.low, r.cost.high) : "Mangler grunnlag"}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Card>
        );
      })}
    </div>
  );
}

function MaintenanceDetail({ m, lookup, onClose }: { m: MaintenanceAction; lookup: Lookup; onClose: () => void }) {
  const { ask } = useAssistant();
  useAssistantSelection({ type: "tiltak", id: m.id, label: m.title });
  const issues = useQuery((a, s) => a.listIssues(s));
  const docs = useQuery((a, s) => a.listDocuments(s));
  const related = (issues.data ?? []).filter((i) => m.relatedIssueIds.includes(i.id));
  const relDocs = (docs.data ?? []).filter((d) => m.relatedDocumentIds.includes(d.id));
  return (
    <Drawer
      eyebrow={`${lookup.part(m.buildingPartId) ?? ""}${m.buildingId ? ` · ${lookup.building(m.buildingId)}` : " · Hele eiendommen"}`}
      title={m.title}
      onClose={onClose}
      wide
      footer={
        <>
          {m.projectId ? <LinkButton to={`/prosjekter/${m.projectId}`}>Åpne prosjekt</LinkButton> : m.status === "krever_beslutning" ? <LinkButton to={`/tilbud/ny?tiltak=${m.id}`}>Lag tilbudsforespørsel</LinkButton> : null}
          <Button variant="secondary" era onClick={() => ask("Hva er risikoen ved å utsette dette tiltaket?")}>
            Spør ERA om risiko
          </Button>
        </>
      }
    >
      <div className="row" style={{ marginBottom: 12 }}>
        <MaintStatusBadge s={m.status} />
        <SeverityBadge s={m.priority} />
        <ConfidenceBadge value={m.basis.confidence} />
      </div>
      <NextBox>{m.nextAction}</NextBox>
      <div className="dsection">
        <h3>Risiko ved å vente</h3>
        <p>{m.riskIfDelayed}</p>
      </div>
      <div className="dsection">
        <h3>Nøkkelinformasjon</h3>
        <KV
          items={[
            ["Anbefalt tidspunkt", `${m.recommendedYear}${m.recommendedQuarter ? ` Q${m.recommendedQuarter}` : ""}`],
            ["Estimert kostnad", m.cost ? <>{formatRange(m.cost.low, m.cost.high)} <ConfidenceBadge value={m.cost.basis} />{m.cost.note ? <span className="muted small"> · {m.cost.note}</span> : null}</> : <Missing>Mangler grunnlag</Missing>],
            ["Ansvarlig", lookup.person(m.ownerId) ?? <Missing>Ikke satt</Missing>],
            ["Prioritet", SEVERITY_LABEL[m.priority]],
            ["Status", MAINT_STATUS_LABEL[m.status]],
          ]}
        />
      </div>
      <div className="dsection">
        <h3>Datagrunnlag</h3>
        <ul className="factlist">
          <li>
            <ConfidenceBadge value={m.basis.confidence} />
            <span>{m.basis.text}</span>
          </li>
        </ul>
      </div>
      <div className="dsection">
        <h3>Relaterte dokumenter</h3>
        {relDocs.length === 0 ? <p className="muted small">Ingen dokumenter er koblet til tiltaket.</p> : (
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {relDocs.map((d) => (
              <li key={d.id}><Link to={`/dokumenter?dok=${d.id}`}>{d.title}</Link> <span className="muted small">({d.source})</span></li>
            ))}
          </ul>
        )}
      </div>
      <div className="dsection">
        <h3>Relaterte avvik</h3>
        {related.length === 0 ? <p className="muted small">Ingen avvik er koblet til tiltaket.</p> : (
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {related.map((i) => (
              <li key={i.id}><Link to={`/saker?sak=${i.id}`}>{i.ref} {i.title}</Link></li>
            ))}
          </ul>
        )}
      </div>
    </Drawer>
  );
}
