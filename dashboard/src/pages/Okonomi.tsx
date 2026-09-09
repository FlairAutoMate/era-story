/** Økonomi v1: budsjett, vedtatt, prognose, faktisk, avvik, per prosjekt, per bygningsdel, felles vs privat. */
import { useMemo } from "react";
import { Link } from "react-router";
import { useQuery } from "@/data/provider";
import type { BudgetLine, BuildingPartCategory } from "@/domain/types";
import { formatNOK } from "@/lib/format";
import { PART_LABEL } from "@/lib/labels";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { Callout, Card, ComingLater, EmptyState, ErrorState, SectionHead, Skeleton } from "@/components/ui";

export function Okonomi() {
  const [year, setYear] = useUrlParam("aar", "2026");
  const budget = useQuery((a, s) => a.listBudget(s));
  const projects = useQuery((a, s) => a.listProjects(s));
  const y = Number(year);
  const rows = useMemo(() => (budget.data ?? []).filter((b) => b.year === y), [budget.data, y]);
  const shared = rows.filter((r) => r.scope === "felles");
  const sum = (k: keyof BudgetLine) => shared.reduce((s, r) => s + ((r[k] as number | undefined) ?? 0), 0);
  const hasForecast = shared.some((r) => r.forecast !== undefined);
  const hasActual = shared.some((r) => r.actual !== undefined);
  const privateSum = rows.filter((r) => r.scope === "privat").reduce((s, r) => s + (r.forecast ?? 0), 0);
  const years = Array.from(new Set((budget.data ?? []).map((b) => b.year))).sort();

  const byPart = useMemo(() => {
    const m = new Map<BuildingPartCategory | "annet", { budget: number; forecast: number; actual: number }>();
    for (const r of shared) {
      const k = r.buildingPartCategory ?? "annet";
      const cur = m.get(k) ?? { budget: 0, forecast: 0, actual: 0 };
      cur.budget += r.budget;
      cur.forecast += r.forecast ?? 0;
      cur.actual += r.actual ?? 0;
      m.set(k, cur);
    }
    return Array.from(m.entries()).sort((a, b) => b[1].budget - a[1].budget);
  }, [shared]);

  if (budget.status === "error") return <ErrorState error={budget.error} retry={budget.reload} />;
  if (!budget.data) return <Skeleton lines={10} />;

  const dev = hasForecast ? sum("forecast") - sum("budget") : undefined;
  return (
    <>
      <PageHead title="Økonomi" meta={["Vedlikeholdsøkonomi, ikke regnskap. Regnskapet føres av forretningsfører."]} actions={
        <div className="timeline-toggle" role="group" aria-label="År">
          {years.map((yy) => <button key={yy} aria-pressed={y === yy} onClick={() => setYear(String(yy))}>{yy}</button>)}
        </div>
      } />
      {rows.length === 0 ? <EmptyState title={`Ingen budsjettlinjer for ${y}`} what="Vedlikeholdsbudsjettet bygges fra vedtatte prosjekter og tiltak i planen." /> : (
        <>
          <div className="grid cols-4" data-testid="economy-cards">
            <Card className="statcard"><span className="label">Vedlikeholdsbudsjett {y}</span><span className="figure">{formatNOK(sum("budget"), { compact: true })}</span></Card>
            <Card className="statcard"><span className="label">Vedtatte kostnader</span><span className="figure">{formatNOK(sum("approved"), { compact: true })}</span><span className="sub">{shared.filter((r) => r.approved === undefined).length} linjer venter på vedtak</span></Card>
            <Card className={`statcard${dev && dev > 0 ? " critical" : ""}`}><span className="label">Prognose</span><span className="figure">{hasForecast ? formatNOK(sum("forecast"), { compact: true }) : "Ikke registrert"}</span>{dev !== undefined && <span className="sub">{dev > 0 ? `${formatNOK(dev, { compact: true })} over budsjett` : dev < 0 ? `${formatNOK(-dev, { compact: true })} under budsjett` : "I tråd med budsjett"}</span>}</Card>
            <Card className="statcard"><span className="label">Faktisk kostnad hittil</span><span className="figure">{hasActual ? formatNOK(sum("actual"), { compact: true }) : "Ikke registrert"}</span>{hasActual && <span className="sub">{Math.round((sum("actual") / Math.max(1, sum("budget"))) * 100)} % av budsjett</span>}</Card>
          </div>

          <div className="section">
            <SectionHead title="Felles kostnad og private tillegg" />
            <div className="cost-split">
              <div className="box shared"><div className="eyebrow">Felles (borettslaget)</div><div className="figure">{formatNOK(hasForecast ? sum("forecast") : sum("budget"), { compact: true })}</div><div className="small muted">Finansieres over felleskostnader eller lån</div></div>
              <div className="box private"><div className="eyebrow">Private tilvalg (beboerne)</div><div className="figure">{privateSum > 0 ? formatNOK(privateSum, { compact: true }) : "Ingen"}</div><div className="small muted">Aggregert. Faktureres av leverandøren direkte til beboer. Ikke en kostnad for borettslaget.</div></div>
            </div>
          </div>

          <div className="section">
            <SectionHead title="Kostnad per prosjekt og linje" />
            <div className="table-wrap">
              <table className="tbl" data-testid="budget-table">
                <thead><tr><th>Linje</th><th>Bygningsdel</th><th className="num">Budsjett</th><th className="num">Vedtatt</th><th className="num">Prognose</th><th className="num">Faktisk</th><th className="num">Avvik</th></tr></thead>
                <tbody>
                  {rows.map((r) => {
                    const d = r.forecast !== undefined ? r.forecast - r.budget : undefined;
                    return (
                      <tr key={r.id}>
                        <td><span className="primary">{r.projectId ? <Link to={`/prosjekter/${r.projectId}`}>{r.label}</Link> : r.label}</span>{r.scope === "privat" && <span className="sub">Privat, betales av beboer</span>}</td>
                        <td>{r.buildingPartCategory ? PART_LABEL[r.buildingPartCategory] : <span className="muted">Flere</span>}</td>
                        <td className="num">{r.scope === "privat" ? <span className="muted">–</span> : formatNOK(r.budget)}</td>
                        <td className="num">{r.approved !== undefined ? formatNOK(r.approved) : <span className="muted">Ikke vedtatt</span>}</td>
                        <td className="num">{r.forecast !== undefined ? formatNOK(r.forecast) : <span className="muted">Ikke registrert</span>}</td>
                        <td className="num">{r.actual !== undefined ? formatNOK(r.actual) : <span className="muted">Ikke registrert</span>}</td>
                        <td className="num" style={d && d > 0 ? { color: "var(--danger)", fontWeight: 600 } : d && d < 0 ? { color: "var(--good)" } : undefined}>{d === undefined || r.scope === "privat" ? <span className="muted">–</span> : d === 0 ? "0 kr" : `${d > 0 ? "+" : ""}${formatNOK(d)}`}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div className="section">
            <SectionHead title="Kostnad per bygningsdel" />
            <Card pad className="stack">
              {byPart.map(([k, v]) => {
                const max = byPart[0]?.[1].budget || 1;
                return (
                  <div key={k} className="row">
                    <span style={{ width: 140 }}>{k === "annet" ? "Drift og annet" : PART_LABEL[k]}</span>
                    <div className="grow bar" aria-hidden="true"><i style={{ width: `${(v.budget / max) * 100}%`, background: "var(--planned)" }} /></div>
                    <span className="num small" style={{ width: 130, textAlign: "right" }}>{formatNOK(v.budget, { compact: true })}</span>
                  </div>
                );
              })}
            </Card>
          </div>
        </>
      )}
      <div className="section">
        <SectionHead title="Kommer senere" />
        <Callout>Funksjoner under er forberedt i datamodellen, men ikke bygget. De vises ikke som aktive valg før de gir reell verdi.</Callout>
        <div className="row" style={{ marginTop: 10 }}>
          {["Likviditetsprognose", "Effekt på felleskostnader", "Lånescenarioer", "Tilskudd", "Fakturakontroll", "Benchmarking"].map((x) => <ComingLater key={x}>{x}</ComingLater>)}
        </div>
        {projects.data && <p className="small muted" style={{ marginTop: 10 }}>Datagrunnlag: {projects.data.length} prosjekter og {rows.length} budsjettlinjer.</p>}
      </div>
    </>
  );
}
