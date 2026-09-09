/**
 * Prosjektdetalj med faner: Oversikt, Fremdrift, Berørte boliger, Tilbud og økonomi,
 * Kommunikasjon, Dokumenter, Aktivitet. Soilrørprosjektet viser skillet mellom fellesarbeid
 * og private tilvalg, uten at styret ser enkelttilbud.
 */
import { useMemo, useState } from "react";
import { Link, useParams } from "react-router";
import { useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { Project, UnitParticipation } from "@/domain/types";
import { formatDate, formatNOK, plural, relativeDeadline } from "@/lib/format";
import { READINESS_LABEL, RESPONSE_LABEL, STAGE_LABEL, TIER_LABEL } from "@/lib/labels";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useAssistant, useAssistantSelection } from "@/shell/assistant";
import { ActivityTimeline, CostResponsibilityBreakdown, DecisionPanel, StageBadge, StageBar, useLookup } from "@/components/domain";
import { Badge, Button, Callout, Card, ConfirmModal, DeniedState, EmptyState, ErrorState, KV, LinkButton, Missing, Progress, SectionHead, Skeleton, Tabs } from "@/components/ui";
import { useToast } from "@/components/toast";
import { CommunicationComposer } from "./Beboere";
import { QuoteComparison } from "./Tilbud";

type Tab = "oversikt" | "fremdrift" | "boliger" | "tilbud" | "kommunikasjon" | "dokumenter" | "aktivitet";

export function ProsjektDetalj() {
  const { id = "" } = useParams();
  const { ask } = useAssistant();
  const lookup = useLookup();
  const [tab, setTab] = useUrlParam("fane", "oversikt");
  const projects = useQuery((a, s) => a.listProjects(s));
  const p = projects.data?.find((x) => x.id === id);
  useAssistantSelection(p ? { type: "prosjekt", id: p.id, label: p.title } : undefined);

  if (projects.status === "error") return <ErrorState error={projects.error} retry={projects.reload} />;
  if (!projects.data) return <Skeleton lines={10} />;
  if (!p) return <DeniedState what="dette prosjektet" />;

  const over = p.budget !== undefined && p.forecast !== undefined && p.forecast > p.budget;
  return (
    <>
      <PageHead
        eyebrow={<Link to="/prosjekter">Prosjekter</Link>}
        title={p.title}
        meta={[<StageBadge s={p.stage} />, `${p.buildingIds.map(lookup.building).filter(Boolean).join(", ") || "Ingen bygg"} · ${plural(p.affectedUnitIds.length, "berørt bolig", "berørte boliger")}`, `Prosjekteier ${lookup.person(p.ownerId)}`]}
        actions={
          <Button variant="secondary" era onClick={() => ask(`Oppsummer status på ${p.title.toLowerCase()}`)}>
            Spør ERA
          </Button>
        }
      />
      <div style={{ marginBottom: 14 }}>
        <StageBar stage={p.stage} />
      </div>
      <Callout tone="warn" title="Styret må">
        {p.boardNextAction}
      </Callout>
      <div style={{ marginTop: 14 }}>
        <Tabs<Tab>
          label="Prosjektseksjoner"
          value={tab as Tab}
          onChange={(t) => setTab(t)}
          items={[
            { id: "oversikt", label: "Oversikt" },
            { id: "fremdrift", label: "Fremdrift", count: p.milestones.filter((m) => !m.done).length },
            { id: "boliger", label: "Berørte boliger", count: p.affectedUnitIds.length },
            { id: "tilbud", label: "Tilbud og økonomi" },
            { id: "kommunikasjon", label: "Kommunikasjon" },
            { id: "dokumenter", label: "Dokumenter", count: p.documentIds.length },
            { id: "aktivitet", label: "Aktivitet" },
          ]}
        />
      </div>
      <div className="section" style={{ marginTop: 18 }}>
        {tab === "oversikt" && <Overview p={p} over={over} />}
        {tab === "fremdrift" && <ProgressTab p={p} />}
        {tab === "boliger" && <AffectedUnits p={p} />}
        {tab === "tilbud" && <QuotesEconomy p={p} over={over} />}
        {tab === "kommunikasjon" && <Communication p={p} />}
        {tab === "dokumenter" && <Documents p={p} />}
        {tab === "aktivitet" && <Activity p={p} />}
      </div>
    </>
  );
}

function Overview({ p, over }: { p: Project; over: boolean }) {
  const session = useSession();
  const lookup = useLookup();
  const issues = useQuery((a, s) => a.listIssues(s));
  const open = (issues.data ?? []).filter((i) => p.openIssueIds.includes(i.id));
  return (
    <div className="split">
      <div className="stack">
        <Card pad className="stack">
          <h2>Formål og omfang</h2>
          <p>{p.purpose}</p>
          <p className="muted">{p.scope || <Missing>Omfang ikke beskrevet</Missing>}</p>
        </Card>
        {p.hasPrivateUpgrades && p.packages && (
          <Card pad className="stack" data-testid="package-split">
            <h2>Fellesarbeid og private tilvalg</h2>
            <p className="small muted">Borettslaget dekker fellesarbeidet. Alt annet er frivillig for hver beboer og faktureres privat av leverandøren.</p>
            <div className="grid cols-2">
              {p.packages.map((pk) => (
                <div key={pk.tier} className="pkg" style={{ cursor: "default" }} aria-pressed={pk.coveredByTenant}>
                  <div className="row">
                    <h3>{pk.name}</h3>
                    {pk.coveredByTenant ? <Badge tone="planned" plain>Dekkes av borettslaget</Badge> : <Badge tone="neutral" plain>Privat tilvalg</Badge>}
                  </div>
                  <p className="small">{pk.description}</p>
                  <ul>
                    {pk.includes.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                  {!pk.coveredByTenant && (
                    <div className="small">
                      <span className="price">{formatNOK(pk.priceFrom)} – {formatNOK(pk.priceTo)}</span> <span className="muted">inkl. mva · samkjøringsbesparelse {formatNOK(pk.coordinationDiscount)}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        )}
        <Card pad className="stack">
          <h2>Åpne avvik i prosjektet</h2>
          {open.length === 0 ? <p className="muted small">Ingen åpne avvik.</p> : open.map((i) => (
            <div key={i.id} className="row">
              <Link to={`/saker?sak=${i.id}`}>{i.ref} {i.title}</Link>
              <span className="small muted">· {relativeDeadline(i.dueDate)}</span>
            </div>
          ))}
        </Card>
      </div>
      <div className="stack">
        <Card pad>
          <KV
            tight
            items={[
              ["Status", STAGE_LABEL[p.stage]],
              ["Fremdrift", p.progressPct !== undefined ? <><Progress pct={p.progressPct} tone={over ? "warn" : undefined} /><span className="small">{p.progressPct} %</span></> : <Missing />],
              ["Budsjett (vedtatt ramme)", formatNOK(p.budget)],
              ["Prognose", <span style={over ? { color: "var(--danger)", fontWeight: 600 } : undefined}>{formatNOK(p.forecast)}{over && p.budget ? ` (+${formatNOK(p.forecast! - p.budget)})` : ""}</span>],
              ["Faktisk kostnad", formatNOK(p.actual)],
              ["Leverandører", p.supplierIds.length ? p.supplierIds.map(lookup.supplier).join(", ") : <Missing>Ikke valgt</Missing>],
              ["Berørte bygg", p.buildingIds.map(lookup.building).join(", ") || <Missing />],
              ["Periode", p.startDate ? `${formatDate(p.startDate)} – ${formatDate(p.endDate)}` : <Missing>Ikke fastsatt</Missing>],
              ["FDV-status", <Badge tone={p.fdvStatus === "komplett" ? "done" : p.fdvStatus === "delvis" ? "decision" : p.fdvStatus === "mangler" ? "critical" : "neutral"}>{{ mangler: "Mangler", delvis: "Delvis", komplett: "Komplett", ikke_relevant: "Ikke relevant ennå" }[p.fdvStatus]}</Badge>],
            ]}
          />
        </Card>
        <CostResponsibilityBreakdown project={p} showPrivate={can(session.role, "economy:read")} />
      </div>
    </div>
  );
}

function ProgressTab({ p }: { p: Project }) {
  return (
    <div className="split">
      <Card>
        <div className="card-head"><h2>Milepæler</h2></div>
        <div className="card-body">
          {p.milestones.length === 0 ? <EmptyState title="Ingen milepæler" what="Milepæler gir styret og beboerne en felles tidslinje." /> : (
            <ol className="history">
              {p.milestones.map((m) => (
                <li key={m.id}>
                  <time>{formatDate(m.date)} · {{ milepael: "Milepæl", beslutning: "Styrebeslutning", kontroll: "Kontroll", frist: "Frist" }[m.kind]}</time>
                  <span className={m.done ? "muted" : ""}>{m.title}</span> {m.done ? <Badge tone="done">Fullført</Badge> : <Badge tone={m.kind === "beslutning" ? "decision" : "planned"}>{relativeDeadline(m.date)}</Badge>}
                </li>
              ))}
            </ol>
          )}
        </div>
      </Card>
      <div className="stack">
        <Card pad className="stack">
          <h2>Fremdrift</h2>
          <Progress pct={p.progressPct} />
          <p className="small muted">{p.progressPct !== undefined ? `${p.progressPct} % av planlagt arbeid` : "Fremdrift er ikke registrert av leverandøren."}</p>
        </Card>
        <Card pad className="stack">
          <h2>Endringsordrer</h2>
          {p.changeOrders.length === 0 ? <p className="muted small">Ingen endringsordrer.</p> : p.changeOrders.map((c) => (
            <div key={c.id} className="row">
              <span className="mono small">{c.ref}</span>
              <span className="grow">{c.title}</span>
              <span className="num small">{formatNOK(c.amount)}</span>
              <Badge tone={c.status === "godkjent" ? "done" : c.status === "avvist" ? "neutral" : "decision"}>{{ foreslatt: "Foreslått", godkjent: "Godkjent", avvist: "Avvist" }[c.status]}</Badge>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
}

/** AffectedUnitsTable + ProjectProgress per bolig. */
function AffectedUnits({ p }: { p: Project }) {
  const session = useSession();
  const lookup = useLookup();
  const units = useQuery((a, s) => a.listUnits(s));
  const part = useQuery((a, s) => a.listParticipation(s, p.id), [p.id]);
  const [filter, setFilter] = useUrlParam("svar");
  const [showList, setShowList] = useUrlParam("liste");
  const rows = useMemo(() => {
    const byUnit = new Map((part.data ?? []).map((r) => [r.unitId, r]));
    return (units.data ?? []).filter((u) => p.affectedUnitIds.includes(u.id)).map((u) => ({ u, r: byUnit.get(u.id) })).filter((x) => !filter || x.r?.responseStatus === filter || (filter === "ikke_klar" && x.r && x.r.readiness !== "klar"));
  }, [units.data, part.data, p.affectedUnitIds, filter]);

  if (part.status === "error") return <ErrorState error={part.error} retry={part.reload} />;
  if (!part.data || !units.data) return <Skeleton lines={8} />;
  if (p.affectedUnitIds.length === 0) return <EmptyState title="Ingen berørte boliger registrert" what="Når prosjektet berører enkeltboliger, vises svar, valg og produksjonsklarhet per bolig her." />;

  const rs = part.data;
  const count = (f: (r: UnitParticipation) => boolean) => rs.filter(f).length;
  const answered = count((r) => !["ikke_kontaktet", "ikke_svart"].includes(r.responseStatus));
  const onlyShared = count((r) => r.responseStatus === "avslatt");
  const considering = count((r) => ["vurderer", "valgt", "akseptert"].includes(r.responseStatus));
  const ready = count((r) => r.readiness === "klar");
  const noAccess = count((r) => r.readiness === "mangler_tilgang");
  const pending = count((r) => r.readiness === "mangler_avklaring");

  return (
    <div className="stack">
      {p.hasPrivateUpgrades && (
        <div className="grid cols-6" data-testid="unit-summary">
          <Card className="statcard" style={{ pointerEvents: "none" }}><span className="figure">{answered}<span className="muted" style={{ fontSize: 15, fontWeight: 500 }}> av {rs.length}</span></span><span className="label">har svart</span></Card>
          <Card className="statcard"><span className="figure">{onlyShared}</span><span className="label">velger kun fellesarbeid</span></Card>
          <Card className="statcard"><span className="figure">{considering}</span><span className="label">vurderer eller har valgt privat oppgradering</span></Card>
          <Card className="statcard"><span className="figure" style={{ color: "var(--good)" }}>{ready}</span><span className="label">klare for produksjon</span></Card>
          <Card className="statcard"><span className="figure" style={{ color: "var(--danger)" }}>{noAccess}</span><span className="label">mangler tilgang</span></Card>
          <Card className="statcard"><span className="figure" style={{ color: "var(--decision)" }}>{pending}</span><span className="label">mangler avklaring</span></Card>
        </div>
      )}
      <Card pad>
        <SectionHead title="Produksjonsklarhet per bolig" right={<span className="small muted">Grønn = klar · Rød = mangler tilgang · Oransje = mangler avklaring</span>} />
        <div className="unitgrid" aria-label="Boliger">
          {units.data.filter((u) => p.affectedUnitIds.includes(u.id)).map((u) => {
            const r = rs.find((x) => x.unitId === u.id);
            return (
              <div key={u.id} className={`unit ${r?.readiness ?? ""}`} title={`${u.label} · ${r ? READINESS_LABEL[r.readiness] : "Ingen data"}`}>
                <b>{u.label}</b>
                <span className="muted">{lookup.entrance(u.entranceId)?.replace("Oppgang ", "")}</span>
              </div>
            );
          })}
        </div>
      </Card>
      <div className="filters">
        <Button variant={showList ? "secondary" : "primary"} size="sm" onClick={() => setShowList(showList ? null : "1")} data-testid="toggle-list">{showList ? "Skjul liste" : `Vis liste (${rows.length})`}</Button>
        <select value={filter} onChange={(e) => setFilter(e.target.value)} aria-label="Filtrer på svar">
          <option value="">Alle svar</option>
          {Object.entries(RESPONSE_LABEL).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
          <option value="ikke_klar">Ikke klare for produksjon</option>
        </select>
        {can(session.role, "messages:send") && <LinkButton to={`/beboere?ny=1&prosjekt=${p.id}&segment=berorte`} variant="secondary" size="sm">Send melding til berørte</LinkButton>}
      </div>
      {showList && <>
      <div className="table-wrap desktop-only">
        <table className="tbl" data-testid="units-table">
          <thead>
            <tr>
              <th>Bolig</th>
              <th>Oppgang</th>
              <th>Svar</th>
              {p.hasPrivateUpgrades && <th>Valgt pakke</th>}
              <th>Produksjonsklarhet</th>
              <th>Uke</th>
              <th>Produksjon</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ u, r }) => (
              <tr key={u.id}>
                <td className="primary mono">{u.label}</td>
                <td>{lookup.entrance(u.entranceId)}</td>
                <td>{r ? <Badge tone={r.responseStatus === "akseptert" || r.responseStatus === "avslatt" ? "done" : r.responseStatus === "ikke_svart" || r.responseStatus === "ikke_kontaktet" ? "critical" : "planned"}>{RESPONSE_LABEL[r.responseStatus]}</Badge> : <Missing />}</td>
                {p.hasPrivateUpgrades && <td>{r?.tier ? TIER_LABEL[r.tier] : <span className="muted">Ikke valgt</span>}</td>}
                <td>
                  {r ? <Badge tone={r.readiness === "klar" ? "done" : r.readiness === "mangler_tilgang" ? "critical" : r.readiness === "mangler_avklaring" ? "decision" : "neutral"}>{READINESS_LABEL[r.readiness]}</Badge> : <Missing />}
                  {r?.readinessNote && <span className="sub">{r.readinessNote}</span>}
                </td>
                <td>{r?.scheduledWeek ? `Uke ${r.scheduledWeek}` : <span className="muted">Ikke satt</span>}</td>
                <td>{r?.productionStatus ? { ikke_startet: "Ikke startet", pagar: "Pågår", ferdig: "Ferdig" }[r.productionStatus] : <span className="muted">Ikke startet</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="cardlist mobile-only">
        {rows.map(({ u, r }) => (
          <div key={u.id} className="item">
            <span className="t">{u.label} · {lookup.entrance(u.entranceId)}</span>
            <span className="m">
              {r && <Badge tone={r.responseStatus === "akseptert" || r.responseStatus === "avslatt" ? "done" : "planned"}>{RESPONSE_LABEL[r.responseStatus]}</Badge>}
              {r && <Badge tone={r.readiness === "klar" ? "done" : r.readiness === "mangler_tilgang" ? "critical" : "decision"}>{READINESS_LABEL[r.readiness]}</Badge>}
              {r?.tier && <span>{TIER_LABEL[r.tier]}</span>}
            </span>
          </div>
        ))}
      </div>
      </>}
      <p className="small muted">Styret ser status per bolig, ikke innholdet i private tilbud. Enkelttilbud er kun synlige for beboeren selv og leverandøren.</p>
    </div>
  );
}

function QuotesEconomy({ p, over }: { p: Project; over: boolean }) {
  const session = useSession();
  const toast = useToast();
  const decisions = useQuery((a, s) => a.listDecisions(s));
  const quotes = useQuery((a, s) => a.listQuotes(s));
  const qrs = useQuery((a, s) => a.listQuoteRequests(s));
  const [confirmCo, setConfirmCo] = useState<{ id: string; approve: boolean } | null>(null);
  const decideCo = useMutation((a, s, coId: string, approve: boolean) => a.decideChangeOrder(s, p.id, coId, approve));
  const qr = (qrs.data ?? []).find((q) => q.id === p.quoteRequestId);
  const qs = (quotes.data ?? []).filter((q) => q.quoteRequestId === p.quoteRequestId);
  const decs = (decisions.data ?? []).filter((d) => p.decisionIds.includes(d.id) || d.projectId === p.id);
  const canDecide = can(session.role, "board:decide");

  return (
    <div className="stack">
      <div className="grid cols-4">
        <Card className="statcard"><span className="label">Budsjett (vedtatt)</span><span className="figure">{formatNOK(p.budget, { compact: true })}</span></Card>
        <Card className={`statcard${over ? " critical" : ""}`}><span className="label">Prognose</span><span className="figure">{formatNOK(p.forecast, { compact: true })}</span>{over && p.budget && <span className="sub">{formatNOK(p.forecast! - p.budget, { compact: true })} over ramme</span>}</Card>
        <Card className="statcard"><span className="label">Faktisk</span><span className="figure">{formatNOK(p.actual, { compact: true })}</span></Card>
        <Card className="statcard"><span className="label">Endringsordrer</span><span className="figure">{p.changeOrders.length}</span><span className="sub">{p.changeOrders.filter((c) => c.status === "foreslatt").length} venter på beslutning</span></Card>
      </div>
      <CostResponsibilityBreakdown project={p} showPrivate={can(session.role, "economy:read")} />

      {p.changeOrders.filter((c) => c.status === "foreslatt").length > 0 && (
        <Card pad className="stack" data-testid="change-orders">
          <h2>Endringsordrer som krever beslutning</h2>
          {p.changeOrders.filter((c) => c.status === "foreslatt").map((c) => (
            <div key={c.id} className="callout warn">
              <div className="row">
                <strong style={{ margin: 0 }}>{c.ref} · {c.title}</strong>
                <span className="num right" style={{ fontWeight: 700 }}>{formatNOK(c.amount)}</span>
              </div>
              <p className="small muted">{c.scope === "felles" ? "Felles kostnad" : "Privat"} · mottatt {formatDate(c.at)}</p>
              {canDecide ? (
                <div className="row" style={{ marginTop: 8 }}>
                  <Button size="sm" onClick={() => setConfirmCo({ id: c.id, approve: true })} data-testid="co-approve">Godkjenn</Button>
                  <Button size="sm" variant="secondary" onClick={() => setConfirmCo({ id: c.id, approve: false })}>Avvis</Button>
                </div>
              ) : (
                <p className="small" style={{ marginTop: 6 }}>Styreleder godkjenner endringsordrer.</p>
              )}
            </div>
          ))}
        </Card>
      )}

      {decs.length > 0 && (
        <div className="stack" data-testid="decisions">
          {decs.map((d) => (
            <DecisionPanel key={d.id} decision={d} quotes={d.quoteId === undefined && qs.length > 0 && d.status === "krever_beslutning" && d.title.toLowerCase().includes("leverand") ? qs : undefined} />
          ))}
        </div>
      )}

      {qr ? (
        <Card>
          <div className="card-head">
            <h2>Tilbud · {qr.title}</h2>
            <div className="right"><LinkButton to={`/tilbud/${qr.id}`} variant="secondary" size="sm">Åpne i tilbudsmodulen</LinkButton></div>
          </div>
          <div className="card-body">
            {qs.length === 0 ? <p className="muted small">Forespørselen er {qr.status === "utkast" ? "et utkast som ikke er sendt" : "sendt"}. Ingen tilbud mottatt ennå.</p> : <QuoteComparison quotes={qs} request={qr} compact />}
          </div>
        </Card>
      ) : (
        <EmptyState title="Ingen tilbudsforespørsel" what="Lag en forespørsel basert på eiendomsdataene, inviter leverandører og sammenlign tilbud på likt grunnlag." action={can(session.role, "quotes:request") ? <LinkButton to={`/tilbud/ny?prosjekt=${p.id}`}>Lag tilbudsforespørsel</LinkButton> : undefined} />
      )}

      {confirmCo && (
        <ConfirmModal
          title={confirmCo.approve ? "Godkjenne endringsordren?" : "Avvise endringsordren?"}
          body={<p>{confirmCo.approve ? "Godkjenning er bindende overfor leverandøren og øker prosjektets prognose." : "Leverandøren får beskjed om at arbeidet ikke skal utføres."}</p>}
          confirmLabel={confirmCo.approve ? "Godkjenn" : "Avvis"}
          danger={!confirmCo.approve}
          pending={decideCo.pending}
          onCancel={() => setConfirmCo(null)}
          onConfirm={async () => {
            const r = await decideCo.run(confirmCo.id, confirmCo.approve);
            setConfirmCo(null);
            toast(r ? (confirmCo.approve ? "Endringsordre godkjent" : "Endringsordre avvist") : "Kunne ikke lagre", r ? undefined : "error");
          }}
        />
      )}
    </div>
  );
}

function Communication({ p }: { p: Project }) {
  const session = useSession();
  const messages = useQuery((a, s) => (can(s.role, "residents:read") || can(s.role, "messages:send") ? a.listMessages(s) : Promise.resolve([])));
  const [compose, setCompose] = useState(false);
  const rows = (messages.data ?? []).filter((m) => m.linkedTo?.id === p.id);
  return (
    <div className="stack">
      <div className="row">
        <h2>Beboerkommunikasjon</h2>
        {can(session.role, "messages:send") && <Button className="right" onClick={() => setCompose(true)}>Ny melding til berørte</Button>}
      </div>
      {rows.length === 0 ? <EmptyState title="Ingen meldinger sendt i dette prosjektet" what="Meldinger til berørte boliger knyttes til prosjektet, med svarfrist, bekreftelse og påmelding." /> : rows.map((m) => (
        <Card key={m.id} pad className="stack">
          <div className="row">
            <Badge tone={m.status === "sendt" ? "done" : m.status === "planlagt" ? "planned" : "neutral"}>{{ sendt: "Sendt", planlagt: "Planlagt", utkast: "Utkast" }[m.status]}</Badge>
            <span className="small muted">{m.sentAt ? formatDate(m.sentAt) : ""} · {plural(m.recipients, "mottaker", "mottakere")}</span>
          </div>
          <h3>{m.subject}</h3>
          <p className="small">{m.body}</p>
          {m.stats && <p className="small muted">Levert {m.stats.delivered} · lest {m.stats.read} · bekreftet {m.stats.confirmed} · svart {m.stats.replied}{m.replyDeadline ? ` · frist ${formatDate(m.replyDeadline)}` : ""}</p>}
        </Card>
      ))}
      {compose && <CommunicationComposer onClose={() => setCompose(false)} presetProjectId={p.id} presetSegment="berorte" />}
    </div>
  );
}

function Documents({ p }: { p: Project }) {
  const docs = useQuery((a, s) => a.listDocuments(s));
  const rows = (docs.data ?? []).filter((d) => p.documentIds.includes(d.id) || d.links.projectId === p.id);
  return (
    <div className="stack">
      <Callout tone={p.fdvStatus === "mangler" ? "danger" : p.fdvStatus === "delvis" ? "warn" : p.fdvStatus === "komplett" ? "good" : undefined} title="Sluttdokumentasjon og FDV">
        {{ mangler: "FDV mangler. Kontrakten krever FDV ved ferdigstillelse.", delvis: "FDV er delvis mottatt.", komplett: "FDV er komplett.", ikke_relevant: "FDV blir relevant når arbeidet starter." }[p.fdvStatus]}
      </Callout>
      {rows.length === 0 ? <EmptyState title="Ingen dokumenter" what="Tilbud, kontrakt, bilder, protokoller og FDV kobles til prosjektet." /> : (
        <div className="cardlist">
          {rows.map((d) => (
            <Link key={d.id} to={`/dokumenter?dok=${d.id}`} className="item">
              <span className="t">{d.title}</span>
              <span className="m"><span>{d.type}</span><span>{formatDate(d.date)}</span><span>{d.source}</span></span>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Activity({ p }: { p: Project }) {
  const act = useQuery((a, s) => a.listActivity(s));
  const rows = (act.data ?? []).filter((a) => a.link?.id === p.id || p.openIssueIds.includes(a.link?.id ?? "") || p.documentIds.includes(a.link?.id ?? ""));
  return <Card pad>{act.data ? <ActivityTimeline items={rows} /> : <Skeleton lines={6} />}</Card>;
}
