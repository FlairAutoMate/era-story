/** ProjectPortfolio: prosjektoversikt med statusflyt. */
import { useState } from "react";
import { useNavigate } from "react-router";
import { useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import { PROJECT_STAGES, type ProjectStage } from "@/domain/types";
import { STAGE_LABEL } from "@/lib/labels";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useLookup } from "@/components/domain";
import { Button, EmptyState, ErrorState, Skeleton } from "@/components/ui";
import { IconPlus } from "@/components/icons";
import { ProjectCard } from "./Oversikt";
import { CreateDrawer } from "./CreateDrawer";

export function Prosjekter() {
  const session = useSession();
  const navigate = useNavigate();
  const lookup = useLookup();
  const [stage, setStage] = useUrlParam("status");
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
      <div className="chips" style={{ marginBottom: 16 }} role="group" aria-label="Filtrer på status">
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
      {projects.status === "error" ? (
        <ErrorState error={projects.error} retry={projects.reload} />
      ) : !projects.data ? (
        <div className="grid cols-2"><Skeleton lines={7} /><Skeleton lines={7} /></div>
      ) : rows.length === 0 ? (
        <EmptyState title="Ingen prosjekter" what="Et prosjekt samler omfang, berørte boliger, tilbud, vedtak, fremdrift, kommunikasjon og sluttdokumentasjon." why="Prosjekter oppstår fra vedlikeholdstiltak eller avvik, eller opprettes direkte." action={can(session.role, "projects:write") ? <Button onClick={() => setCreate(true)}>Opprett prosjekt</Button> : undefined} />
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
