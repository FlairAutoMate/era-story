/** ProjectPortfolio: prosjektoversikt med statusflyt. Kortnett som standard, «Vis liste» for en kompakt tabell. */
import { useState } from "react";
import { useNavigate } from "react-router";
import { useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import { PROJECT_STAGES, type ProjectStage } from "@/domain/types";
import { formatNOK } from "@/lib/format";
import { STAGE_LABEL } from "@/lib/labels";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { StageBadge, useLookup } from "@/components/domain";
import { Badge, Button, EmptyState, ErrorState, Progress, Skeleton } from "@/components/ui";
import { IconPlus } from "@/components/icons";
import { ProjectCard } from "./Oversikt";
import { CreateDrawer } from "./CreateDrawer";

export function Prosjekter() {
  const session = useSession();
  const navigate = useNavigate();
  const lookup = useLookup();
  const [stage, setStage] = useUrlParam("status");
  const [showList, setShowList] = useUrlParam("liste");
  const [create, setCreate] = useState(false);
  const projects = useQuery((a, s) => a.listProjects(s));
  const rows = (projects.data ?? []).filter((p) => !stage || p.stage === stage);

  return (
    <>
      <PageHead
        title="Prosjekter"
        meta={projects.data ? [`${projects.data.length} prosjekter`, `${projects.data.filter((p) => p.budget && p.forecast && p.forecast > p.budget).length} over ramme`, `${projects.data.filter((p) => p.hasPrivateUpgrades).length} med private tilvalg`] : []}
        actions={can(session.role, "projects:write") && <Button onClick={() => setCreate(true)}><IconPlus /> Nytt prosjekt</Button>}
      />
      <div className="row" style={{ marginBottom: 16, gap: 10 }}>
        <div className="chips" role="group" aria-label="Filtrer på status">
          <button className="chip" aria-pressed={!stage} onClick={() => setStage(null)}>
            Alle
          </button>
          {PROJECT_STAGES.map((s) => {
            const n = (projects.data ?? []).filter((p) => p.stage === s).length;
            return (
              <button key={s} className="chip" aria-pressed={stage === s} onClick={() => setStage(s)} disabled={n === 0 && stage !== s}>
                {STAGE_LABEL[s as ProjectStage]} {n > 0 && <span className="muted">{n}</span>}
              </button>
            );
          })}
        </div>
        {rows.length > 0 && (
          <Button variant={showList ? "secondary" : "primary"} size="sm" className="right" onClick={() => setShowList(showList ? null : "1")} data-testid="toggle-list">
            {showList ? "Vis kort" : `Vis liste (${rows.length})`}
          </Button>
        )}
      </div>
      {projects.status === "error" ? (
        <ErrorState error={projects.error} retry={projects.reload} />
      ) : !projects.data ? (
        <div className="grid cols-2"><Skeleton lines={7} /><Skeleton lines={7} /></div>
      ) : rows.length === 0 ? (
        <EmptyState title="Ingen prosjekter" what="Et prosjekt samler omfang, berørte boliger, tilbud, vedtak, fremdrift, kommunikasjon og sluttdokumentasjon." why="Prosjekter oppstår fra vedlikeholdstiltak eller avvik, eller opprettes direkte." action={can(session.role, "projects:write") ? <Button onClick={() => setCreate(true)}>Opprett prosjekt</Button> : undefined} />
      ) : showList ? (
        <>
          <div className="fill desktop-only">
            <div className="table-wrap">
              <table className="tbl" data-testid="projects-table">
                <thead>
                  <tr>
                    <th>Prosjekt</th>
                    <th>Status</th>
                    <th>Fremdrift</th>
                    <th className="num">Budsjett</th>
                    <th className="num">Prognose</th>
                    <th>Neste milepæl</th>
                    <th>Styret må</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((p) => {
                    const over = !!(p.budget && p.forecast && p.forecast > p.budget);
                    const next = p.milestones.find((m) => !m.done);
                    return (
                      <tr key={p.id} className="rowlink" tabIndex={0} onClick={() => navigate(`/prosjekter/${p.id}`)} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), navigate(`/prosjekter/${p.id}`))}>
                        <td>
                          <span className="primary">{p.title}</span>
                          <span className="sub">{p.buildingIds.map(lookup.building).filter(Boolean).join(", ") || "Hele eiendommen"}</span>
                        </td>
                        <td>
                          <StageBadge s={p.stage} />
                          {over && <Badge tone="critical" plain>Over ramme</Badge>}
                        </td>
                        <td style={{ minWidth: 110 }}>
                          <Progress pct={p.progressPct} tone={over ? "warn" : undefined} />
                          <span className="small muted">{p.progressPct !== undefined ? `${p.progressPct} %` : "Ikke registrert"}</span>
                        </td>
                        <td className="num nowrap">{formatNOK(p.budget, { compact: true })}</td>
                        <td className="num nowrap" style={over ? { color: "var(--danger)", fontWeight: 600 } : undefined}>{formatNOK(p.forecast, { compact: true })}</td>
                        <td className="nowrap">{next ? next.title : <span className="muted">Ingen</span>}</td>
                        <td className="wrap">{p.boardNextAction}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
          <div className="cardlist mobile-only">
            {rows.map((p) => {
              const over = !!(p.budget && p.forecast && p.forecast > p.budget);
              return (
                <button key={p.id} className="item" onClick={() => navigate(`/prosjekter/${p.id}`)}>
                  <span className="t">{p.title}</span>
                  <span className="m" style={{ marginBottom: 6 }}>
                    <StageBadge s={p.stage} />
                    {over && <Badge tone="critical" plain>Over ramme</Badge>}
                  </span>
                  <span className="m">
                    <span>{p.progressPct !== undefined ? `${p.progressPct} % fremdrift` : "Fremdrift ikke registrert"}</span>
                    <span>{formatNOK(p.forecast ?? p.budget, { compact: true })}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </>
      ) : (
        <div className="grid cols-2">
          {rows.map((p) => (
            <ProjectCard key={p.id} p={p} supplier={lookup.supplier} onOpen={() => navigate(`/prosjekter/${p.id}`)} />
          ))}
        </div>
      )}
      {create && <CreateDrawer onClose={() => setCreate(false)} defaultKind="prosjekt" />}
    </>
  );
}
