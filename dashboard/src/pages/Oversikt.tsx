/**
 * BoardMissionControl: styrets startside. Tre nivåer: krever handling nå → aktivt arbeid og
 * kommende → historikk.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { PriorityItem, Project } from "@/domain/types";
import { formatDateTime, formatNOK, plural, relativeDeadline } from "@/lib/format";
import { SEVERITY_LABEL } from "@/lib/labels";
import { PageHead } from "@/shell/AppShell";
import { useAssistant } from "@/shell/assistant";
import { ActivityTimeline, MaintenanceTimeline, StageBadge, StageDots, useLookup, type Horizon } from "@/components/domain";
import { Button, Card, EmptyState, ErrorState, LinkButton, Progress, SectionHead, Skeleton } from "@/components/ui";
import { IconPlus } from "@/components/icons";
import { useUrlParam } from "@/lib/urlState";
import { CreateDrawer } from "./CreateDrawer";

const TYPE_LABEL: Record<PriorityItem["type"], string> = {
  kritisk_avvik: "Kritisk avvik",
  vedlikehold_naermer_seg: "Vedlikehold nærmer seg",
  tilbud_ma_vurderes: "Tilbud må vurderes",
  beslutning_mangler: "Beslutning mangler",
  frist_utloper: "Frist utløper",
  prosjekt_avvik: "Budsjettavvik i prosjekt",
  mangler_dokumentasjon: "Mangler dokumentasjon",
};

export function Oversikt() {
  const session = useSession();
  const navigate = useNavigate();
  const { ask } = useAssistant();
  const lookup = useLookup();
  const [horizon, setHorizon] = useUrlParam("horisont", "12");
  const [create, setCreate] = useState(false);

  const tenant = useQuery((a, s) => a.getTenant(s));
  const priorities = useQuery((a, s) => a.listPriorityItems(s));
  const summary = useQuery((a, s) => a.getBoardSummary(s));
  const calendar = useQuery((a, s) => a.listCalendar(s));
  const projects = useQuery((a, s) => a.listProjects(s));
  const activity = useQuery((a, s) => a.listActivity(s, 6));

  const t = tenant.data;
  return (
    <>
      <PageHead
        eyebrow={t?.kind === "sameie" ? "Sameie" : "Borettslag"}
        title={t?.name ?? "Laster …"}
        meta={t ? [`${t.address}, ${t.postal}`, `${plural(t.buildingCount, "bygg", "bygg")} · ${plural(t.unitCount, "bolig", "boliger")}`, `Sist oppdatert ${formatDateTime(t.lastUpdated)}`] : []}
        actions={
          <>
            <Button variant="secondary" era onClick={() => ask("Hva bør styret prioritere neste år?")}>
              Spør ERA
            </Button>
            {can(session.role, "issues:write") && (
              <Button onClick={() => setCreate(true)} data-testid="create-primary">
                <IconPlus /> Opprett sak eller prosjekt
              </Button>
            )}
          </>
        }
      />

      {/* Nivå 1: krever handling nå */}
      <section aria-labelledby="pri-h">
        <SectionHead title={<span id="pri-h">Dette trenger styret nå</span>} right={priorities.data && priorities.data.length > 0 ? <span className="muted">{priorities.data.length} av maks 3</span> : undefined} />
        {priorities.status === "loading" && !priorities.data ? (
          <div className="priority">
            <Skeleton lines={5} />
            <Skeleton lines={5} />
            <Skeleton lines={5} />
          </div>
        ) : priorities.status === "error" ? (
          <ErrorState error={priorities.error} retry={priorities.reload} />
        ) : priorities.data!.length === 0 ? (
          <EmptyState title="Ingenting krever styrets oppmerksomhet akkurat nå" what="ERA viser her de tre viktigste sakene når det finnes kritiske avvik, tilbud som må vurderes, beslutninger som mangler eller frister som nærmer seg." why="Legg inn tilstandsrapport og FDV-dokumenter, så får ERA grunnlag til å foreslå tiltak." action={<LinkButton to="/dokumenter" variant="secondary">Gå til dokumenter</LinkButton>} />
        ) : (
          <div className="priority" data-testid="priority-cards">
            {priorities.data!.map((p) => (
              <Card key={p.id} className={`pcard ${p.severity === "kritisk" ? "critical" : p.severity}`}>
                <div className="row">
                  <span className={`badge ${p.severity === "kritisk" ? "critical" : "decision"}`}>{SEVERITY_LABEL[p.severity]}</span>
                  <span className="small muted">{TYPE_LABEL[p.type]}</span>
                </div>
                <h3>{p.title}</h3>
                <p className="why">{p.why}</p>
                <div className="rec">
                  <strong>ERAs anbefalte neste handling</strong>
                  {p.recommendedAction}
                </div>
                <div className="facts">
                  <span>
                    Frist: <b>{relativeDeadline(p.dueDate)}</b>
                  </span>
                  {p.ownerId && (
                    <span>
                      Ansvarlig: <b>{lookup.person(p.ownerId)}</b>
                    </span>
                  )}
                  {p.buildingPartLabel && (
                    <span>
                      Gjelder: <b>{p.buildingPartLabel}</b>
                    </span>
                  )}
                </div>
                <div className="actions">
                  <LinkButton to={p.primary.to}>{p.primary.label}</LinkButton>
                  <Button variant="ghost" era onClick={() => ask(p.askEra)}>
                    Spør ERA
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Statusoversikt */}
      <section className="section" aria-labelledby="stat-h">
        <SectionHead title={<span id="stat-h">Eiendomsstatus</span>} />
        {summary.status === "error" ? (
          <ErrorState error={summary.error} retry={summary.reload} />
        ) : !summary.data ? (
          <div className="grid cols-6">{Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} lines={2} />)}</div>
        ) : (
          <div className="grid cols-6" data-testid="status-cards">
            <Stat to="/vedlikehold?status=krever_beslutning" n={summary.data.actionsRequiringDecision} label={summary.data.actionsRequiringDecision === 1 ? "tiltak krever beslutning" : "tiltak krever beslutning"} tone={summary.data.actionsRequiringDecision > 0 ? "decision" : undefined} />
            <Stat to="/saker" n={summary.data.openIssues} label="åpne avvik" sub={summary.data.criticalOpenIssues > 0 ? `${plural(summary.data.criticalOpenIssues, "kritisk", "kritiske")} åpne` : "Ingen kritiske"} tone={summary.data.criticalOpenIssues > 0 ? "critical" : undefined} />
            <Stat to="/prosjekter" n={summary.data.activeProjects} label="aktive prosjekter" />
            <Stat to="/tilbud" n={summary.data.quotesWaiting} label="tilbud venter på vurdering" tone={summary.data.quotesWaiting > 0 ? "decision" : undefined} />
            <Stat to="/?horisont=12#tidslinje" n={summary.data.upcomingDeadlines30d} label="frister neste 30 dager" />
            <Stat to="/vedlikehold?visning=bygningsdeler" n={summary.data.buildingAreasMapped.mapped} of={summary.data.buildingAreasMapped.total} label="bygningsområder kartlagt" sub={summary.data.documentsMissingLink > 0 ? `${plural(summary.data.documentsMissingLink, "dokument", "dokumenter")} mangler kobling` : "Alle dokumenter koblet"} />
          </div>
        )}
      </section>

      {/* Nivå 2: kommende og aktivt arbeid */}
      <section className="section" id="tidslinje" aria-labelledby="tl-h">
        <SectionHead title={<span id="tl-h">Kommende {horizon === "12" ? "12 måneder" : horizon === "36" ? "36 måneder" : "10 år"}</span>} right={<Link to="/vedlikehold?visning=tidslinje">Full vedlikeholdsplan</Link>} />
        <Card pad>
          {calendar.status === "error" ? <ErrorState error={calendar.error} retry={calendar.reload} /> : calendar.data ? <MaintenanceTimeline events={calendar.data} horizon={horizon as Horizon} onHorizon={(h) => setHorizon(h)} limitPerCol={3} /> : <Skeleton lines={4} />}
        </Card>
      </section>

      <div className="split section">
        <section aria-labelledby="prj-h">
          <SectionHead title={<span id="prj-h">Aktive prosjekter</span>} right={<Link to="/prosjekter">Alle prosjekter</Link>} />
          {projects.status === "error" ? (
            <ErrorState error={projects.error} retry={projects.reload} />
          ) : !projects.data ? (
            <Skeleton lines={6} />
          ) : projects.data.filter((p) => p.stage !== "dokumentert").length === 0 ? (
            <EmptyState title="Ingen aktive prosjekter" what="Prosjekter samler tilbud, vedtak, fremdrift, beboerkommunikasjon og dokumentasjon på ett sted." action={can(session.role, "projects:write") ? <Button onClick={() => setCreate(true)}>Opprett prosjekt</Button> : undefined} />
          ) : (
            <div className="stack">
              {projects.data
                .filter((p) => p.stage !== "dokumentert")
                .slice(0, 5)
                .map((p) => (
                  <ProjectCard key={p.id} p={p} supplier={lookup.supplier} onOpen={() => navigate(`/prosjekter/${p.id}`)} />
                ))}
            </div>
          )}
        </section>

        {/* Nivå 3: historikk */}
        <section aria-labelledby="act-h">
          <SectionHead title={<span id="act-h">Siste aktivitet</span>} right={<Link to="/aktivitet">Full historikk</Link>} />
          <Card pad>{activity.status === "error" ? <ErrorState error={activity.error} retry={activity.reload} /> : activity.data ? <ActivityTimeline items={activity.data} compact /> : <Skeleton lines={6} />}</Card>
        </section>
      </div>

      {create && <CreateDrawer onClose={() => setCreate(false)} />}
    </>
  );
}

function Stat({ to, n, of, label, sub, tone }: { to: string; n: number; of?: number; label: string; sub?: string; tone?: "critical" | "decision" }) {
  return (
    <Link to={to} className={`card statcard${tone ? ` ${tone}` : ""}`}>
      <span className="figure">
        {n}
        {of !== undefined && <span className="muted" style={{ fontSize: 15, fontWeight: 500 }}> av {of}</span>}
      </span>
      <span className="label">{label}</span>
      {sub && <span className="sub">{sub}</span>}
    </Link>
  );
}

export function ProjectCard({ p, supplier, onOpen }: { p: Project; supplier: (id?: string) => string | undefined; onOpen: () => void }) {
  const over = p.budget !== undefined && p.forecast !== undefined && p.forecast > p.budget;
  const next = p.milestones.find((m) => !m.done);
  return (
    <Card className="projcard">
      <div className="row">
        <StageBadge s={p.stage} />
        {over && <span className="badge critical plain">Over ramme</span>}
        {p.openIssueIds.length > 0 && <span className="badge decision plain">{plural(p.openIssueIds.length, "åpent avvik", "åpne avvik")}</span>}
      </div>
      <h3>
        <Link to={`/prosjekter/${p.id}`}>{p.title}</Link>
      </h3>
      <StageDots stage={p.stage} />
      <div className="row" style={{ gap: 12 }}>
        <div className="grow">
          <Progress pct={p.progressPct} tone={over ? "warn" : undefined} />
        </div>
        <span className="small muted nowrap">{p.progressPct !== undefined ? `${p.progressPct} % fremdrift` : "Fremdrift ikke registrert"}</span>
      </div>
      <dl className="kv kv-proj">
        <dt>Budsjett</dt>
        <dd>{formatNOK(p.budget, { compact: true })}</dd>
        <dt>Prognose</dt>
        <dd className={over ? "num" : "num"} style={over ? { color: "var(--danger)", fontWeight: 600 } : undefined}>{formatNOK(p.forecast, { compact: true })}</dd>
        <dt>Leverandør</dt>
        <dd>{p.supplierIds.length ? p.supplierIds.map(supplier).filter(Boolean).join(", ") : <span className="muted">Ikke valgt</span>}</dd>
        <dt>Neste milepæl</dt>
        <dd>{next ? `${next.title} · ${relativeDeadline(next.date)}` : <span className="muted">Ingen</span>}</dd>
        <dt>Berørte boliger</dt>
        <dd>{p.affectedUnitIds.length || <span className="muted">Ingen</span>}</dd>
      </dl>
      <div className="next">
        <strong>Styret må: </strong>
        {p.boardNextAction}
      </div>
      <div>
        <Button variant="secondary" size="sm" onClick={onOpen}>
          Åpne prosjekt
        </Button>
      </div>
    </Card>
  );
}
