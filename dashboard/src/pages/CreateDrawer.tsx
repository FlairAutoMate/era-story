/** «Opprett sak eller prosjekt»: én inngang som lager avvik eller prosjekt. */
import { useState } from "react";
import { useNavigate } from "react-router";
import { useMutation, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { Responsibility, Severity } from "@/domain/types";
import { useLookup } from "@/components/domain";
import { Button, Drawer } from "@/components/ui";
import { useToast } from "@/components/toast";

export function CreateDrawer({ onClose, defaultKind = "sak" }: { onClose: () => void; defaultKind?: "sak" | "prosjekt" }) {
  const session = useSession();
  const navigate = useNavigate();
  const toast = useToast();
  const lookup = useLookup();
  const [kind, setKind] = useState<"sak" | "prosjekt">(defaultKind);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [severity, setSeverity] = useState<Severity>("middels");
  const [responsibility, setResponsibility] = useState<Responsibility>("uavklart");
  const [buildingId, setBuildingId] = useState("");
  const [buildingIds, setBuildingIds] = useState<string[]>([]);

  const createIssue = useMutation((a, s, input: { title: string; description: string; severity: Severity; buildingId?: string; responsibility: Responsibility }) => a.createIssue(s, input));
  const createProject = useMutation((a, s, input: { title: string; purpose: string; scope: string; buildingIds: string[] }) => a.createProject(s, input));
  const canProject = can(session.role, "projects:write");
  const pending = createIssue.pending || createProject.pending;

  const submit = async () => {
    if (!title.trim()) return;
    if (kind === "sak") {
      const r = await createIssue.run({ title: title.trim(), description: desc.trim(), severity, buildingId: buildingId || undefined, responsibility });
      if (r) {
        toast(`Sak ${r.ref} opprettet`);
        onClose();
        navigate(`/saker?sak=${r.id}`);
      } else toast("Kunne ikke opprette saken", "error");
    } else {
      const r = await createProject.run({ title: title.trim(), purpose: desc.trim(), scope: "", buildingIds });
      if (r) {
        toast(`Prosjekt «${r.title}» opprettet`);
        onClose();
        navigate(`/prosjekter/${r.id}`);
      } else toast("Kunne ikke opprette prosjektet", "error");
    }
  };

  return (
    <Drawer
      title="Opprett sak eller prosjekt"
      onClose={onClose}
      footer={
        <>
          <Button onClick={() => void submit()} disabled={pending || !title.trim()} data-testid="create-submit">
            {pending ? "Oppretter …" : kind === "sak" ? "Opprett sak" : "Opprett prosjekt"}
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Avbryt
          </Button>
        </>
      }
    >
      <div className="stack">
        <div className="chips" role="group" aria-label="Type">
          <button className="chip" aria-pressed={kind === "sak"} onClick={() => setKind("sak")}>
            Sak eller avvik
          </button>
          <button className="chip" aria-pressed={kind === "prosjekt"} onClick={() => canProject && setKind("prosjekt")} aria-disabled={!canProject} title={canProject ? undefined : "Bare styreleder kan opprette prosjekter"}>
            Prosjekt
          </button>
        </div>
        {!canProject && <p className="small muted">Som {session.role === "styremedlem" ? "styremedlem" : "denne rollen"} kan du opprette saker. Prosjekter opprettes av styreleder.</p>}
        <div className="field">
          <label htmlFor="c-title">Tittel</label>
          <input id="c-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder={kind === "sak" ? "F.eks. Vannlekkasje i kjeller bygg B" : "F.eks. Utskifting av inngangsdører"} />
        </div>
        <div className="field">
          <label htmlFor="c-desc">{kind === "sak" ? "Beskrivelse" : "Formål"}</label>
          <textarea id="c-desc" value={desc} onChange={(e) => setDesc(e.target.value)} />
        </div>
        {kind === "sak" ? (
          <>
            <div className="field">
              <label htmlFor="c-sev">Alvorlighetsgrad</label>
              <select id="c-sev" value={severity} onChange={(e) => setSeverity(e.target.value as Severity)}>
                <option value="kritisk">Kritisk</option>
                <option value="hoy">Høy</option>
                <option value="middels">Middels</option>
                <option value="lav">Lav</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="c-bld">Bygg</label>
              <select id="c-bld" value={buildingId} onChange={(e) => setBuildingId(e.target.value)}>
                <option value="">Ikke valgt</option>
                {lookup.buildings.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name} · {b.address}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label htmlFor="c-resp">Ansvar</label>
              <select id="c-resp" value={responsibility} onChange={(e) => setResponsibility(e.target.value as Responsibility)}>
                <option value="uavklart">Uavklart</option>
                <option value="felles">Felles</option>
                <option value="privat">Privat</option>
              </select>
            </div>
          </>
        ) : (
          <div className="field">
            <span className="lbl">Berørte bygg</span>
            <div className="chips">
              {lookup.buildings.map((b) => (
                <button key={b.id} className="chip" aria-pressed={buildingIds.includes(b.id)} onClick={() => setBuildingIds((s) => (s.includes(b.id) ? s.filter((x) => x !== b.id) : [...s, b.id]))}>
                  {b.name}
                </button>
              ))}
            </div>
          </div>
        )}
        {(createIssue.error || createProject.error) && <div className="callout danger">{(createIssue.error ?? createProject.error)?.message}</div>}
      </div>
    </Drawer>
  );
}
