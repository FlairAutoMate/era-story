/**
 * BoardMissionControl som cockpit: én fast flate i viewport-høyde. Tre saker står fast til
 * venstre, et firefanet panel (status, kommende, prosjekter, aktivitet) til høyre, ERA som felt
 * i bunn. Lister klippes med «+ N til» som åpner fullvisning i et lag. På mobil er sakene en
 * kortstokk man sveiper gjennom, og segmentkontrollen bytter panel.
 */
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Link } from "react-router";
import { useQuery, useSession, type QueryState } from "@/data/provider";
import { can } from "@/access/roles";
import type { Activity, BoardSummary, CalendarEvent, PriorityItem, Project } from "@/domain/types";
import { daysUntil, formatDate, formatDateTime, formatNOK, plural, relativeDeadline } from "@/lib/format";
import { SEVERITY_LABEL, STAGE_LABEL } from "@/lib/labels";
import { PageHead } from "@/shell/AppShell";
import { useAssistant } from "@/shell/assistant";
import { ActivityTimeline, MaintenanceTimeline, StageBadge, StageDots, useLookup, type Horizon } from "@/components/domain";
import { Badge, Button, Card, Drawer, EmptyState, ErrorState, LinkButton, Progress, Skeleton } from "@/components/ui";
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

type Panel = "status" | "kommende" | "prosjekter" | "aktivitet";
const EVENT_KIND: Record<CalendarEvent["kind"], [string, "critical" | "decision" | "planned" | "active" | "done" | "neutral"]> = {
  frist: ["Frist", "critical"],
  beslutning: ["Beslutning", "decision"],
  vedlikehold: ["Vedlikehold", "planned"],
  kontroll: ["Kontroll", "active"],
  milepael: ["Milepæl", "done"],
  garanti: ["Garanti", "decision"],
};

export function Oversikt() {
  const session = useSession();
  const { ask } = useAssistant();
  const lookup = useLookup();
  const [panel, setPanel] = useUrlParam("panel", "status");
  const [horizon, setHorizon] = useUrlParam("horisont", "12");
  const [mobileSeg, setMobileSeg] = useUrlParam("vis", "na");
  const [create, setCreate] = useState(false);
  const [layer, setLayer] = useState<null | "kommende" | "aktivitet">(null);

  const tenant = useQuery((a, s) => a.getTenant(s));
  const priorities = useQuery((a, s) => a.listPriorityItems(s));
  const summary = useQuery((a, s) => a.getBoardSummary(s));
  const calendar = useQuery((a, s) => a.listCalendar(s));
  const projects = useQuery((a, s) => a.listProjects(s));
  const activity = useQuery((a, s) => a.listActivity(s));

  const t = tenant.data;
  const upcoming = useMemo(() => {
    const months = horizon === "12" ? 12 : horizon === "36" ? 36 : 120;
    return (calendar.data ?? []).filter((e) => daysUntil(e.date) >= -1 && daysUntil(e.date) <= months * 30.5);
  }, [calendar.data, horizon]);
  const activeProjects = (projects.data ?? []).filter((p) => p.stage !== "dokumentert");

  const priorityCards = (
    <>
      {priorities.status === "loading" && !priorities.data ? (
        <div className="decks">
          <Skeleton lines={3} />
          <Skeleton lines={3} />
          <Skeleton lines={3} />
        </div>
      ) : priorities.status === "error" ? (
        <ErrorState error={priorities.error} retry={priorities.reload} />
      ) : priorities.data!.length === 0 ? (
        <EmptyState title="Ingenting krever styrets oppmerksomhet akkurat nå" what="ERA viser her de tre viktigste sakene når det finnes kritiske avvik, tilbud som må vurderes, beslutninger som mangler eller frister som nærmer seg." why="Legg inn tilstandsrapport og FDV-dokumenter, så får ERA grunnlag til å foreslå tiltak." action={<LinkButton to="/dokumenter" variant="secondary">Gå til dokumenter</LinkButton>} />
      ) : (
        <>
          <div className="decks desktop-only" data-testid="priority-cards">
            {priorities.data!.map((p) => (
              <article key={p.id} className={`deck ${p.severity === "kritisk" ? "critical" : "decision"}`}>
                <i aria-hidden="true" />
                <div className="dk-body">
                  <div className="row" style={{ gap: 6 }}>
                    <span className={`badge ${p.severity === "kritisk" ? "critical" : "decision"}`}>{SEVERITY_LABEL[p.severity]}</span>
                    <span className="small muted">{TYPE_LABEL[p.type]}</span>
                  </div>
                  <h3>{p.title}</h3>
                  <p className="why">{p.why}</p>
                  <div className="rec">
                    <b>ERA anbefaler</b>
                    {p.recommendedAction}
                  </div>
                  <div className="facts">
                    <span>Frist <b>{relativeDeadline(p.dueDate)}</b></span>
                    {p.ownerId && <span><b>{lookup.person(p.ownerId)}</b></span>}
                    {p.buildingPartLabel && <span>{p.buildingPartLabel}</span>}
                  </div>
                </div>
                <div className="act">
                  <LinkButton to={p.primary.to} size="sm">{p.primary.label}</LinkButton>
                  <Button variant="secondary" size="sm" era onClick={() => ask(p.askEra)}>Spør ERA</Button>
                </div>
              </article>
            ))}
          </div>
          <MobileStack items={priorities.data!} person={lookup.person} onAsk={ask} />
        </>
      )}
    </>
  );

  const rightPanel = (
    <div className="cpanel" data-testid="cockpit-panel">
      {panel === "status" && <StatusPanel summary={summary} projects={activeProjects} />}
      {panel === "kommende" && (
        <>
          <div className="row" style={{ gap: 6 }}>
            <div className="timeline-toggle" role="group" aria-label="Tidshorisont">
              {(["12", "36", "120"] as const).map((h) => (
                <button key={h} aria-pressed={horizon === h} onClick={() => setHorizon(h)}>{h === "12" ? "12 mnd" : h === "36" ? "36 mnd" : "10 år"}</button>
              ))}
            </div>
            <Link to="/vedlikehold?visning=tidslinje" className="small right">Full plan</Link>
          </div>
          {calendar.status === "error" ? <ErrorState error={calendar.error} retry={calendar.reload} /> : !calendar.data ? <Skeleton lines={6} /> : upcoming.length === 0 ? <EmptyState title="Ingen hendelser i perioden" what="Frister, kontroller, styrebeslutninger, milepæler og garantier vises her." /> : (
            <ClippedList
              rows={upcoming}
              limit={8}
              onMore={() => setLayer("kommende")}
              render={(e) => {
                const [label, tone] = EVENT_KIND[e.kind];
                return (
                  <Link key={e.id} to={eventTo(e)}>
                    <span className="d">{formatDate(e.date).replace(/\. \d{4}$/, ".")}</span>
                    <span className="t">{e.title}</span>
                    <Badge tone={tone} plain>{label}</Badge>
                  </Link>
                );
              }}
            />
          )}
        </>
      )}
      {panel === "prosjekter" && (
        <>
          <div className="row small muted">
            <span>{activeProjects.length} aktive · {activeProjects.filter((p) => p.budget && p.forecast && p.forecast > p.budget).length} over ramme · sortert etter hva styret må gjøre</span>
            <Link to="/prosjekter" className="right">Alle</Link>
          </div>
          {projects.status === "error" ? <ErrorState error={projects.error} retry={projects.reload} /> : !projects.data ? <Skeleton lines={6} /> : activeProjects.length === 0 ? <EmptyState title="Ingen aktive prosjekter" what="Prosjekter samler tilbud, vedtak, fremdrift og dokumentasjon." /> : (
            <div className="clist" style={{ display: "block", overflow: "hidden" }}>
              {activeProjects.slice(0, 5).map((p) => {
                const over = !!(p.budget && p.forecast && p.forecast > p.budget);
                return (
                  <Link key={p.id} to={`/prosjekter/${p.id}`} className="cproj">
                    <b>{p.title}</b>
                    <Badge tone={over ? "critical" : p.stage === "til_beslutning" ? "decision" : p.stage === "gjennomforing" || p.stage === "kontroll" ? "active" : "planned"}>{over ? "Over ramme" : STAGE_LABEL[p.stage]}</Badge>
                    <Progress pct={p.progressPct ?? 0} tone={over ? "warn" : undefined} />
                    <small>{p.progressPct !== undefined ? `${p.progressPct} %` : "Ikke startet"} · {p.supplierIds.map(lookup.supplier).filter(Boolean).join(", ") || "leverandør ikke valgt"} · Styret må: {p.boardNextAction}</small>
                  </Link>
                );
              })}
            </div>
          )}
        </>
      )}
      {panel === "aktivitet" && (
        <>
          <div className="row small muted">
            <span>Siste hendelser</span>
            <button className="linkish right" onClick={() => setLayer("aktivitet")}>Full historikk</button>
          </div>
          {activity.status === "error" ? <ErrorState error={activity.error} retry={activity.reload} /> : !activity.data ? <Skeleton lines={6} /> : (
            <ClippedList rows={activity.data} limit={7} onMore={() => setLayer("aktivitet")} render={(a) => <ActivityRow key={a.id} a={a} />} />
          )}
        </>
      )}
    </div>
  );

  const tabs: [Panel, string][] = [["status", "Status"], ["kommende", "Kommende"], ["prosjekter", "Prosjekter"], ["aktivitet", "Aktivitet"]];

  return (
    <div className="cockpit">
      <PageHead
        eyebrow={t?.kind === "sameie" ? "Sameie" : "Borettslag"}
        title={t?.name ?? "Laster …"}
        meta={t ? [`${t.address}, ${t.postal}`, `${plural(t.buildingCount, "bygg", "bygg")} · ${plural(t.unitCount, "bolig", "boliger")}`, `Oppdatert ${formatDateTime(t.lastUpdated)}`] : []}
        actions={
          <>
            {summary.data && (
              <span className="row desktop-only" style={{ gap: 6 }}>
                {summary.data.criticalOpenIssues > 0 && <Badge tone="critical">{plural(summary.data.criticalOpenIssues, "kritisk avvik", "kritiske avvik")}</Badge>}
                {summary.data.actionsRequiringDecision > 0 && <Badge tone="decision">{summary.data.actionsRequiringDecision} krever beslutning</Badge>}
              </span>
            )}
            {can(session.role, "issues:write") && (
              <Button onClick={() => setCreate(true)} data-testid="create-primary"><IconPlus /> Opprett sak eller prosjekt</Button>
            )}
          </>
        }
      />

      {/* Mobil: segmentkontroll bytter mellom kortstokk og panel */}
      <div className="mobile-only">
        <div className="seg" role="group" aria-label="Visning">
          <button aria-pressed={mobileSeg === "na"} onClick={() => setMobileSeg("na")}>Nå{priorities.data ? ` · ${priorities.data.length}` : ""}</button>
          {tabs.map(([id, label]) => (
            <button key={id} aria-pressed={mobileSeg === id} onClick={() => { setMobileSeg(id); setPanel(id); }}>{label}</button>
          ))}
        </div>
      </div>

      <div className="cockpit-body">
        <section className={`ccol${mobileSeg !== "na" ? " desktop-only" : ""}`} aria-labelledby="pri-h">
          <div className="h desktop-only"><span id="pri-h">Dette trenger styret nå</span>{priorities.data && <span className="n">{priorities.data.length} av 3</span>}</div>
          {priorityCards}
        </section>
        <section className={`ccol${mobileSeg === "na" ? " desktop-only" : ""}`} aria-label="Panel">
          <div className="tabs desktop-only" role="tablist" aria-label="Panel">
            {tabs.map(([id, label]) => (
              <button key={id} role="tab" aria-selected={panel === id} onClick={() => setPanel(id)}>{label}</button>
            ))}
          </div>
          {rightPanel}
        </section>
      </div>

      {create && <CreateDrawer onClose={() => setCreate(false)} />}
      {layer === "kommende" && calendar.data && (
        <Drawer title="Kommende hendelser" sub={`${upcoming.length} hendelser i perioden`} onClose={() => setLayer(null)} wide>
          <MaintenanceTimeline events={calendar.data} horizon={horizon as Horizon} onHorizon={(h) => setHorizon(h)} limitPerCol={8} />
        </Drawer>
      )}
      {layer === "aktivitet" && activity.data && (
        <Drawer title="Aktivitet" sub={`${activity.data.length} hendelser`} onClose={() => setLayer(null)}>
          <ActivityTimeline items={activity.data} />
        </Drawer>
      )}
    </div>
  );
}

function eventTo(e: CalendarEvent): string {
  if (!e.link) return "/vedlikehold?visning=tidslinje";
  switch (e.link.type) {
    case "prosjekt": return `/prosjekter/${e.link.id}`;
    case "tiltak": return `/vedlikehold?tiltak=${e.link.id}`;
    case "avvik": return `/saker?sak=${e.link.id}`;
    case "tilbud": return "/tilbud";
    case "dokument": return `/dokumenter?dok=${e.link.id}`;
  }
}

function ActivityRow({ a }: { a: Activity }) {
  return (
    <div>
      <span className="d">{formatDateTime(a.at).replace(/^(\d+)\. (\w+)\.? /, "$1. $2 ")}</span>
      <span className="t">{a.text}</span>
      <span className="small muted">{a.actor}</span>
    </div>
  );
}

/** Liste som klippes ved N rader og viser «+ N til» i stedet for å scrolle. */
function ClippedList<T>({ rows, limit, render, onMore }: { rows: T[]; limit: number; render: (row: T) => ReactNode; onMore: () => void }) {
  const rest = rows.length - limit;
  return (
    <div className="clist">
      {rows.slice(0, limit).map(render)}
      {rest > 0 && (
        <div className="more">
          <span className="d" />
          <span>+ {rest} til i perioden</span>
          <button onClick={onMore}>Vis alle</button>
        </div>
      )}
    </div>
  );
}

function StatusPanel({ summary, projects }: { summary: QueryState<BoardSummary> & { reload: () => void }; projects: Project[] }) {
  if (summary.status === "error") return <ErrorState error={summary.error} retry={summary.reload} />;
  if (!summary.data) return <Skeleton lines={6} />;
  const s = summary.data;
  const over = projects.filter((p) => p.budget && p.forecast && p.forecast > p.budget);
  const fdv = projects.filter((p) => p.fdvStatus === "mangler" && (p.stage === "gjennomforing" || p.stage === "kontroll"));
  const rows: { k: string; text: string; tone: "critical" | "decision" | "neutral"; label: string; to: string }[] = [
    ...over.map((p) => ({ k: "Budsjett", text: `${p.title}: prognose ${formatNOK(p.forecast, { compact: true })} mot ramme ${formatNOK(p.budget, { compact: true })}`, tone: "critical" as const, label: `+${formatNOK((p.forecast ?? 0) - (p.budget ?? 0), { compact: true })}`, to: `/prosjekter/${p.id}?fane=tilbud` })),
    ...fdv.map((p) => ({ k: "FDV", text: `${p.title} mangler sluttdokumentasjon`, tone: "decision" as const, label: "Mangler", to: `/prosjekter/${p.id}?fane=dokumenter` })),
    ...(s.buildingAreasMapped.mapped < s.buildingAreasMapped.total ? [{ k: "Data", text: `${s.buildingAreasMapped.total - s.buildingAreasMapped.mapped} bygningsområder er ikke kartlagt`, tone: "neutral" as const, label: "Kartlegg", to: "/vedlikehold?visning=bygningsdeler" }] : []),
    ...(s.documentsMissingLink > 0 ? [{ k: "Dok", text: `${plural(s.documentsMissingLink, "dokument", "dokumenter")} mangler kobling til bygg eller prosjekt`, tone: "neutral" as const, label: "Koble", to: "/dokumenter?status=mangler" }] : []),
  ];
  return (
    <>
      <div className="cstats" data-testid="status-cards">
        <Link to="/vedlikehold?status=krever_beslutning" className={`cstat${s.actionsRequiringDecision ? " decision" : ""}`}><b>{s.actionsRequiringDecision}</b>tiltak krever beslutning</Link>
        <Link to="/saker" className={`cstat${s.criticalOpenIssues ? " critical" : ""}`}><b>{s.openIssues}</b>åpne avvik{s.criticalOpenIssues ? ` · ${s.criticalOpenIssues} kritisk` : ""}</Link>
        <Link to="/prosjekter" className="cstat"><b>{s.activeProjects}</b>aktive prosjekter</Link>
        <Link to="/tilbud" className={`cstat${s.quotesWaiting ? " decision" : ""}`}><b>{s.quotesWaiting}</b>tilbud venter</Link>
        <Link to="/?panel=kommende" className="cstat"><b>{s.upcomingDeadlines30d}</b>frister neste 30 dager</Link>
        <Link to="/vedlikehold?visning=bygningsdeler" className="cstat"><b>{s.buildingAreasMapped.mapped}<span className="muted" style={{ fontSize: 12, fontWeight: 500 }}> av {s.buildingAreasMapped.total}</span></b>områder kartlagt</Link>
      </div>
      {rows.length === 0 ? (
        <div className="state" role="status"><h3>Ingen avvik mot plan</h3><p>Budsjett, dokumentasjon og datagrunnlag er i orden.</p></div>
      ) : (
        <div className="clist">
          {rows.slice(0, 5).map((r, i) => (
            <Link key={i} to={r.to}>
              <span className="d">{r.k}</span>
              <span className="t">{r.text}</span>
              <Badge tone={r.tone} plain>{r.label}</Badge>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}

/** Mobil: ett kort per skjerm, sveip til neste. */
function MobileStack({ items, person, onAsk }: { items: PriorityItem[]; person: (id?: string) => string | undefined; onAsk: (q: string) => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onScroll = () => setIdx(Math.round(el.scrollLeft / Math.max(1, el.clientWidth + 12)));
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <div className="mobile-only" data-testid="priority-stack">
      <div className="cardstack" ref={ref} aria-label="Saker som krever handling">
        {items.map((p) => (
          <article key={p.id} className={`mcard ${p.severity === "kritisk" ? "critical" : "decision"}`}>
            <span className={`badge ${p.severity === "kritisk" ? "critical" : "decision"}`}>{SEVERITY_LABEL[p.severity]} · {TYPE_LABEL[p.type]}</span>
            <h3>{p.title}</h3>
            <p className="why">{p.why}</p>
            <p className="small muted">Frist {relativeDeadline(p.dueDate)}{p.ownerId ? ` · ${person(p.ownerId)}` : ""}</p>
            <div className="rec"><b>ERAs anbefalte neste handling</b>{p.recommendedAction}</div>
            <LinkButton to={p.primary.to} block>{p.primary.label}</LinkButton>
            <Button variant="ghost" era block onClick={() => onAsk(p.askEra)}>Spør ERA</Button>
          </article>
        ))}
      </div>
      <div className="dots" aria-hidden="true">{items.map((p, i) => <i key={p.id} className={i === idx ? "on" : ""} />)}</div>
    </div>
  );
}

/** Prosjektkort brukes fortsatt på prosjektoversikten. */
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
      <h3><Link to={`/prosjekter/${p.id}`}>{p.title}</Link></h3>
      <StageDots stage={p.stage} />
      <div className="row" style={{ gap: 12 }}>
        <div className="grow"><Progress pct={p.progressPct} tone={over ? "warn" : undefined} /></div>
        <span className="small muted nowrap">{p.progressPct !== undefined ? `${p.progressPct} % fremdrift` : "Fremdrift ikke registrert"}</span>
      </div>
      <dl className="kv kv-proj">
        <dt>Budsjett</dt><dd>{formatNOK(p.budget, { compact: true })}</dd>
        <dt>Prognose</dt><dd className="num" style={over ? { color: "var(--danger)", fontWeight: 600 } : undefined}>{formatNOK(p.forecast, { compact: true })}</dd>
        <dt>Leverandør</dt><dd>{p.supplierIds.length ? p.supplierIds.map(supplier).filter(Boolean).join(", ") : <span className="muted">Ikke valgt</span>}</dd>
        <dt>Neste milepæl</dt><dd>{next ? `${next.title} · ${relativeDeadline(next.date)}` : <span className="muted">Ingen</span>}</dd>
        <dt>Berørte boliger</dt><dd>{p.affectedUnitIds.length || <span className="muted">Ingen</span>}</dd>
      </dl>
      <div className="next"><strong>Styret må: </strong>{p.boardNextAction}</div>
      <div><Button variant="secondary" size="sm" onClick={onOpen}>Åpne prosjekt</Button></div>
    </Card>
  );
}

