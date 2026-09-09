/** Leverandørens flyt: bare tildelte prosjekter og boliger. Styrets saksbehandling er ikke synlig. */
import { useQuery, useSession } from "@/data/provider";
import type { Project } from "@/domain/types";
import { formatDate, formatNOK } from "@/lib/format";
import { READINESS_LABEL, RESPONSE_LABEL, TIER_LABEL } from "@/lib/labels";
import { PageHead } from "@/shell/AppShell";
import { useLookup } from "@/components/domain";
import { RoleAwareGuard } from "@/components/RoleAwareGuard";
import { Badge, Callout, Card, EmptyState, ErrorState, KV, SectionHead, Skeleton } from "@/components/ui";

export function Leverandor() {
  return (
    <RoleAwareGuard permission="supplier:read_assigned" what="leverandørvisningen">
      <Inner />
    </RoleAwareGuard>
  );
}

function Inner() {
  const session = useSession();
  const projects = useQuery((a, s) => a.listProjects(s));
  if (projects.status === "error") return <ErrorState error={projects.error} retry={projects.reload} />;
  if (!projects.data) return <Skeleton lines={8} />;
  return (
    <>
      <PageHead eyebrow="Leverandør" title="Mine oppdrag" meta={[session.name, `${projects.data.length} tildelte prosjekter`]} />
      {projects.data.length === 0 ? <EmptyState title="Ingen tildelte oppdrag" what="Her ser du berørte boliger, kartleggingsstatus, valgte pakker, tilvalg, tilgang, manglende beslutninger, produksjonsstatus, endringsordrer og dokumentasjonskrav for prosjektene du er tildelt." /> : projects.data.map((p) => <SupplierProject key={p.id} p={p} />)}
    </>
  );
}

function SupplierProject({ p }: { p: Project }) {
  const lookup = useLookup();
  const units = useQuery((a, s) => a.listUnits(s));
  const part = useQuery((a, s) => a.listParticipation(s, p.id), [p.id]);
  const rows = part.data ?? [];
  const ready = rows.filter((r) => r.readiness === "klar").length;
  const missingDecision = rows.filter((r) => ["vurderer", "valgt", "kartlegging_pagar", "ikke_svart", "ikke_kontaktet"].includes(r.responseStatus)).length;
  const noAccess = rows.filter((r) => r.readiness === "mangler_tilgang").length;
  const privateTotal = rows.reduce((s, r) => (r.privateQuote?.accepted ? s + r.privateQuote.basePrice + r.privateQuote.options.filter((o) => o.selected).reduce((x, o) => x + o.price, 0) - r.privateQuote.coordinationDiscount : s), 0);

  return (
    <div className="stack section" data-testid="supplier-project">
      <Card pad className="stack">
        <SectionHead title={p.title} right={<Badge tone="planned">{p.stage}</Badge>} />
        <p className="small">{p.scope}</p>
        <KV items={[["Oppdragsgiver", "Styret, " + (lookup.person(p.ownerId) ?? "")], ["Berørte boliger", p.affectedUnitIds.length], ["Fellesarbeid (kontrakt)", formatNOK(p.sharedCost)], ["Private avtaler akseptert", rows.length ? formatNOK(privateTotal) : "–"], ["Neste milepæl", (() => { const m = p.milestones.find((x) => !x.done); return m ? `${m.title} · ${formatDate(m.date)}` : "Ingen"; })()]]} />
        <Callout title="Dokumentasjonskrav">FDV-dokumentasjon, bilder før og etter, og våtromsdokumentasjon per bolig leveres digitalt i ERA før sluttoppgjør.</Callout>
        {p.changeOrders.length > 0 && <KV items={p.changeOrders.map((c) => [`${c.ref} ${c.title}`, `${formatNOK(c.amount)} · ${{ foreslatt: "Venter på styret", godkjent: "Godkjent", avvist: "Avvist" }[c.status]}`])} />}
      </Card>
      {p.affectedUnitIds.length > 0 && (
        <>
          <div className="grid cols-4">
            <Card className="statcard"><span className="figure" style={{ color: "var(--good)" }}>{ready}</span><span className="label">klare for produksjon</span></Card>
            <Card className="statcard"><span className="figure" style={{ color: "var(--decision)" }}>{missingDecision}</span><span className="label">mangler beslutning fra beboer</span></Card>
            <Card className="statcard"><span className="figure" style={{ color: "var(--danger)" }}>{noAccess}</span><span className="label">mangler tilgang</span></Card>
            <Card className="statcard"><span className="figure">{rows.filter((r) => r.privateQuote?.accepted).length}</span><span className="label">private avtaler</span></Card>
          </div>
          {part.status === "error" ? <ErrorState error={part.error} retry={part.reload} /> : !part.data || !units.data ? <Skeleton lines={8} /> : (
            <div className="table-wrap">
              <table className="tbl" data-testid="supplier-units">
                <thead><tr><th>Bolig</th><th>Kartlegging</th><th>Pakke</th><th>Tilvalg</th><th>Tilgang</th><th>Uke</th><th>Produksjon</th><th className="num">Privat sum</th></tr></thead>
                <tbody>
                  {rows.map((r) => {
                    const u = units.data!.find((x) => x.id === r.unitId);
                    const q = r.privateQuote;
                    return (
                      <tr key={r.unitId}>
                        <td className="primary mono">{u?.label} <span className="sub">{lookup.entrance(u?.entranceId)}</span></td>
                        <td><Badge tone={r.surveyAnswers ? "done" : "decision"}>{r.surveyAnswers ? `Besvart · ${r.photos ?? 0} bilder` : RESPONSE_LABEL[r.responseStatus]}</Badge></td>
                        <td>{r.tier ? TIER_LABEL[r.tier] : <span className="muted">Ikke valgt</span>}</td>
                        <td className="wrap small">{q ? q.options.filter((o) => o.selected).map((o) => o.name).join(", ") || <span className="muted">Standard</span> : <span className="muted">–</span>}</td>
                        <td><Badge tone={r.readiness === "klar" ? "done" : r.readiness === "mangler_tilgang" ? "critical" : "decision"}>{r.accessConfirmed ? `Bekreftet ${formatDate(r.accessConfirmed)}` : READINESS_LABEL[r.readiness]}</Badge></td>
                        <td>{r.scheduledWeek ? `Uke ${r.scheduledWeek}` : "–"}</td>
                        <td>{r.productionStatus ? { ikke_startet: "Ikke startet", pagar: "Pågår", ferdig: "Ferdig" }[r.productionStatus] : "Ikke startet"}</td>
                        <td className="num">{q?.accepted ? formatNOK(q.basePrice + q.options.filter((o) => o.selected).reduce((s, o) => s + o.price, 0) - q.coordinationDiscount) : q ? <span className="muted">Ikke akseptert</span> : <span className="muted">–</span>}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
