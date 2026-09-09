/** IssueRegister + IssueDetailDrawer: operativ saksliste med URL-filtre, tabell/kortliste og bred detalj. */
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { Issue, IssueStatus, Responsibility, Severity } from "@/domain/types";
import { formatDate, formatDateTime } from "@/lib/format";
import { ISSUE_STATUS_LABEL, RESPONSIBILITY_LABEL, SEVERITY_LABEL, SOURCE_LABEL } from "@/lib/labels";
import { useUrlParams } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useAssistant, useAssistantSelection } from "@/shell/assistant";
import { Deadline, IssueStatusBadge, SeverityBadge, useLookup } from "@/components/domain";
import { Badge, Button, ConfidenceBadge, Drawer, EmptyState, ErrorState, KV, LinkButton, Missing, NextBox, Skeleton } from "@/components/ui";
import { useToast } from "@/components/toast";
import { IconPlus } from "@/components/icons";
import { CreateDrawer } from "./CreateDrawer";

const SEV_ORDER = { kritisk: 0, hoy: 1, middels: 2, lav: 3 } as const;
type SortKey = "alvor" | "frist" | "dato";

const CLIP = 8;

export function Saker() {
  const session = useSession();
  const [all, setAll] = useState(false);
  const [moreFilters, setMoreFilters] = useState(false);
  const [params, patch] = useUrlParams();
  const lookup = useLookup();
  const issues = useQuery((a, s) => a.listIssues(s));
  const [create, setCreate] = useState(false);

  const f = {
    q: params.get("q") ?? "",
    sev: params.get("alvor") ?? "",
    status: params.get("status") ?? "",
    bygg: params.get("bygg") ?? "",
    oppgang: params.get("oppgang") ?? "",
    del: params.get("del") ?? "",
    ansvar: params.get("ansvar") ?? "",
    eier: params.get("eier") ?? "",
    kilde: params.get("kilde") ?? "",
    lev: params.get("lev") ?? "",
    frist: params.get("frist") ?? "",
    sort: (params.get("sort") ?? "alvor") as SortKey,
  };
  const selectedId = params.get("sak") ?? "";
  const activeFilters = Object.entries(f).filter(([k, v]) => k !== "sort" && v).length;

  const rows = useMemo(() => {
    const list = (issues.data ?? []).filter((i) => {
      if (f.q && !`${i.ref} ${i.title} ${i.description}`.toLowerCase().includes(f.q.toLowerCase())) return false;
      if (f.sev && i.severity !== f.sev) return false;
      if (f.status ? i.status !== f.status : i.status === "lost" || i.status === "avvist") return false;
      if (f.bygg && i.buildingId !== f.bygg) return false;
      if (f.oppgang && i.entranceId !== f.oppgang) return false;
      if (f.del && i.buildingPartId !== f.del) return false;
      if (f.ansvar && i.responsibility !== f.ansvar) return false;
      if (f.eier && i.ownerId !== f.eier) return false;
      if (f.kilde && i.source !== f.kilde) return false;
      if (f.lev && i.supplierId !== f.lev) return false;
      if (f.frist === "passert" && !(i.dueDate && i.dueDate < "2026-09-09")) return false;
      if (f.frist === "uke" && !(i.dueDate && i.dueDate >= "2026-09-09" && i.dueDate <= "2026-09-16")) return false;
      return true;
    });
    return list.sort((a, b) =>
      f.sort === "alvor" ? SEV_ORDER[a.severity] - SEV_ORDER[b.severity] || (a.dueDate ?? "9").localeCompare(b.dueDate ?? "9") : f.sort === "frist" ? (a.dueDate ?? "9").localeCompare(b.dueDate ?? "9") : b.reportedAt.localeCompare(a.reportedAt),
    );
  }, [issues.data, f.q, f.sev, f.status, f.bygg, f.oppgang, f.del, f.ansvar, f.eier, f.kilde, f.lev, f.frist, f.sort]);

  const open = issues.data?.find((i) => i.id === selectedId);
  const entrances = lookup.buildings.flatMap((b) => b.entrances);

  return (
    <>
      <PageHead
        title="Saker og avvik"
        meta={issues.data ? [`${issues.data.filter((i) => i.status !== "lost" && i.status !== "avvist").length} åpne`, `${issues.data.filter((i) => i.severity === "kritisk" && i.status !== "lost").length} kritiske`, `${issues.data.filter((i) => i.responsibility === "uavklart" && i.status !== "lost").length} med uavklart ansvar`] : []}
        actions={can(session.role, "issues:write") && <Button onClick={() => setCreate(true)}><IconPlus /> Ny sak</Button>}
      />
      <div className="filters" role="search">
        <input type="search" value={f.q} onChange={(e) => patch({ q: e.target.value })} placeholder="Søk i saker" aria-label="Søk i saker" />
        <Sel label="Alvorlighet" value={f.sev} onChange={(v) => patch({ alvor: v })} options={Object.entries(SEVERITY_LABEL)} />
        <Sel label="Status" value={f.status} onChange={(v) => patch({ status: v })} options={Object.entries(ISSUE_STATUS_LABEL)} allLabel="Åpne" />
        <Button variant="secondary" size="sm" onClick={() => setMoreFilters(true)} data-testid="more-filters">
          Flere filtre{[f.bygg, f.oppgang, f.del, f.ansvar, f.eier, f.frist, f.kilde, f.lev].filter(Boolean).length > 0 ? ` (${[f.bygg, f.oppgang, f.del, f.ansvar, f.eier, f.frist, f.kilde, f.lev].filter(Boolean).length})` : ""}
        </Button>
        {activeFilters > 0 && (
          <Button variant="ghost" size="sm" onClick={() => patch({ q: null, alvor: null, status: null, bygg: null, oppgang: null, del: null, ansvar: null, eier: null, kilde: null, lev: null, frist: null })}>
            Nullstill ({activeFilters})
          </Button>
        )}
      </div>

      {issues.status === "error" ? (
        <ErrorState error={issues.error} retry={issues.reload} />
      ) : !issues.data ? (
        <Skeleton lines={8} />
      ) : rows.length === 0 ? (
        <EmptyState title={activeFilters ? "Ingen saker matcher filtrene" : "Ingen åpne saker"} what="Her samles avvik fra beboere, vaktmester, leverandører og kontroller, med ansvar, frist og neste handling." why={activeFilters ? "Nullstill filtrene eller søk på noe annet." : "Beboere melder inn via ERA-appen. Styret kan også opprette saker her."} action={activeFilters ? undefined : can(session.role, "issues:write") ? <Button onClick={() => setCreate(true)}>Ny sak</Button> : undefined} />
      ) : (
        <>
          <div className="fill desktop-only">
          <div className="table-wrap">
            <table className="tbl" data-testid="issue-table">
              <thead>
                <tr>
                  <th>Sak</th>
                  <th>Alvor</th>
                  <th>Status</th>
                  <th>Sted</th>
                  <th>Ansvar</th>
                  <th>Ansvarlig</th>
                  <th>Frist</th>
                  <th>Kilde</th>
                </tr>
              </thead>
              <tbody>
                {(all ? rows : rows.slice(0, CLIP)).map((i) => (
                  <tr key={i.id} className="rowlink" tabIndex={0} aria-selected={selectedId === i.id} onClick={() => patch({ sak: i.id })} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), patch({ sak: i.id }))}>
                    <td>
                      <span className="primary">{i.ref} · {i.title}</span>
                      <span className="sub">{formatDate(i.reportedAt)} · {i.reportedBy}</span>
                    </td>
                    <td><SeverityBadge s={i.severity} /></td>
                    <td><IssueStatusBadge s={i.status} /></td>
                    <td className="nowrap">{[lookup.building(i.buildingId), lookup.entrance(i.entranceId)].filter(Boolean).join(" · ") || <span className="muted">Ikke satt</span>}</td>
                    <td><Badge tone={i.responsibility === "uavklart" ? "decision" : "neutral"} plain>{RESPONSIBILITY_LABEL[i.responsibility]}</Badge></td>
                    <td>{lookup.person(i.ownerId) ?? <span className="muted">Ikke satt</span>}</td>
                    <td><Deadline date={i.dueDate} /></td>
                    <td className="nowrap">{SOURCE_LABEL[i.source]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {rows.length > CLIP && (
            <div className="more-row" data-testid="more-row">
              <span>{all ? `Viser alle ${rows.length}` : `+ ${rows.length - CLIP} til`}</span>
              <button className="linkish" onClick={() => setAll((v) => !v)}>{all ? "Vis færre" : `Vis alle ${rows.length}`}</button>
            </div>
          )}
          </div>
          <div className="cardlist mobile-only">
            {rows.map((i) => (
              <button key={i.id} className="item" onClick={() => patch({ sak: i.id })}>
                <span className="t">{i.ref} · {i.title}</span>
                <span className="m" style={{ marginBottom: 6 }}>
                  <SeverityBadge s={i.severity} />
                  <IssueStatusBadge s={i.status} />
                </span>
                <span className="m">
                  <span>{[lookup.building(i.buildingId), lookup.entrance(i.entranceId)].filter(Boolean).join(" · ") || "Sted ikke satt"}</span>
                  <Deadline date={i.dueDate} />
                </span>
              </button>
            ))}
          </div>
        </>
      )}

      {moreFilters && (
        <Drawer title="Flere filtre" sub={`${rows.length} saker matcher`} onClose={() => setMoreFilters(false)} footer={<><Button onClick={() => setMoreFilters(false)}>Vis {rows.length} saker</Button><Button variant="ghost" onClick={() => patch({ bygg: null, oppgang: null, del: null, ansvar: null, eier: null, kilde: null, lev: null, frist: null })}>Nullstill disse</Button></>}>
          <div className="stack filters-layer">
        <Sel label="Bygg" value={f.bygg} onChange={(v) => patch({ bygg: v })} options={lookup.buildings.map((b) => [b.id, b.name])} />
        <Sel label="Oppgang" value={f.oppgang} onChange={(v) => patch({ oppgang: v })} options={entrances.map((e) => [e.id, e.name])} />
        <Sel label="Bygningsdel" value={f.del} onChange={(v) => patch({ del: v })} options={lookup.parts.map((p) => [p.id, p.name])} />
        <Sel label="Ansvar" value={f.ansvar} onChange={(v) => patch({ ansvar: v })} options={Object.entries(RESPONSIBILITY_LABEL)} />
        <Sel label="Ansvarlig" value={f.eier} onChange={(v) => patch({ eier: v })} options={lookup.people.filter((p) => p.tenantId).map((p) => [p.id, p.name])} />
        <Sel label="Frist" value={f.frist} onChange={(v) => patch({ frist: v })} options={[["passert", "Passert"], ["uke", "Neste 7 dager"]]} />
        <Sel label="Kilde" value={f.kilde} onChange={(v) => patch({ kilde: v })} options={Object.entries(SOURCE_LABEL)} />
        <Sel label="Leverandør" value={f.lev} onChange={(v) => patch({ lev: v })} options={lookup.suppliers.map((s) => [s.id, s.name])} />
        <Sel label="Sorter" value={f.sort} onChange={(v) => patch({ sort: v || "alvor" })} options={[["alvor", "Alvorlighet"], ["frist", "Frist"], ["dato", "Nyeste"]]} allLabel="Alvorlighet" />
          </div>
        </Drawer>
      )}
      {open && <IssueDetailDrawer issue={open} onClose={() => patch({ sak: null })} />}
      {create && <CreateDrawer onClose={() => setCreate(false)} />}
    </>
  );
}

function Sel({ label, value, onChange, options, allLabel = "Alle" }: { label: string; value: string; onChange: (v: string) => void; options: [string, string][]; allLabel?: string }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} aria-label={label} title={label}>
      <option value="">{label}: {allLabel}</option>
      {options.map(([v, l]) => (
        <option key={v} value={v}>
          {l}
        </option>
      ))}
    </select>
  );
}

export function IssueDetailDrawer({ issue, onClose }: { issue: Issue; onClose: () => void }) {
  const session = useSession();
  const lookup = useLookup();
  const toast = useToast();
  const { ask } = useAssistant();
  useAssistantSelection({ type: "avvik", id: issue.id, label: `${issue.ref} ${issue.title}` });
  const docs = useQuery((a, s) => a.listDocuments(s));
  const [comment, setComment] = useState("");
  const [internal, setInternal] = useState(true);
  const addComment = useMutation((a, s, id: string, text: string, i: boolean) => a.addIssueComment(s, id, text, i));
  const toggle = useMutation((a, s, id: string, t: string) => a.toggleIssueTask(s, id, t));
  const write = can(session.role, "issues:write");
  const relDocs = (docs.data ?? []).filter((d) => issue.documentIds.includes(d.id));

  return (
    <Drawer
      eyebrow={`${issue.ref} · meldt ${formatDate(issue.reportedAt)} av ${issue.reportedBy}`}
      title={issue.title}
      onClose={onClose}
      wide
      footer={
        <>
          {issue.projectId && <LinkButton to={`/prosjekter/${issue.projectId}`}>Åpne prosjekt</LinkButton>}
          {issue.maintenanceActionId && <LinkButton to={`/vedlikehold?tiltak=${issue.maintenanceActionId}`} variant="secondary">Åpne tiltak</LinkButton>}
          <Button variant="secondary" era onClick={() => ask(`Hva er status på ${issue.ref}?`)}>
            Spør ERA
          </Button>
        </>
      }
    >
      <div className="row" style={{ marginBottom: 12 }}>
        <SeverityBadge s={issue.severity} />
        <IssueStatusBadge s={issue.status} />
        <Badge tone={issue.responsibility === "uavklart" ? "decision" : "neutral"}>{RESPONSIBILITY_LABEL[issue.responsibility]} ansvar</Badge>
        <Deadline date={issue.dueDate} />
      </div>
      <NextBox>{issue.nextAction}</NextBox>

      <div className="dsection">
        <h3>Beskrivelse</h3>
        <p>{issue.description}</p>
        <p className="small muted" style={{ marginTop: 6 }}>{issue.photos > 0 ? `${issue.photos} bilder lagt ved` : "Ingen bilder"}</p>
      </div>
      <div className="dsection">
        <h3>Berørt lokasjon</h3>
        <KV items={[["Bygg", lookup.building(issue.buildingId) ?? <Missing />], ["Oppgang", lookup.entrance(issue.entranceId) ?? <Missing />], ["Bolig", issue.unitId ? issue.unitId.split("-").pop() : <Missing>Ikke knyttet til bolig</Missing>], ["Bygningsdel", lookup.part(issue.buildingPartId) ?? <Missing />]]} />
      </div>
      <div className="dsection">
        <h3>ERAs forslag til kategori</h3>
        {issue.suggestedCategory ? (
          <ul className="factlist">
            <li>
              <ConfidenceBadge value={issue.suggestedCategory.confidence} />
              <span>{issue.suggestedCategory.value}</span>
            </li>
          </ul>
        ) : (
          <Missing>Ingen forslag ennå</Missing>
        )}
      </div>
      <div className="dsection">
        <h3>Ansvarsavklaring</h3>
        <ul className="factlist">
          <li>
            <ConfidenceBadge value={issue.responsibility === "uavklart" ? "mangler" : "bekreftet"} />
            <span>{issue.responsibilityNote ?? (issue.responsibility === "uavklart" ? "Ansvar er ikke avklart. Sjekk vedtektene § 5." : `${RESPONSIBILITY_LABEL[issue.responsibility]} ansvar.`)}</span>
          </li>
        </ul>
      </div>
      <div className="dsection">
        <h3>Fakta, forslag og antakelser</h3>
        {issue.facts.length === 0 ? (
          <p className="muted small">Ingen registrerte fakta ennå.</p>
        ) : (
          <ul className="factlist" data-testid="issue-facts">
            {issue.facts.map((f, i) => (
              <li key={i}>
                <ConfidenceBadge value={f.confidence} />
                <span>{f.text}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="dsection">
        <h3>Oppgaver</h3>
        {issue.tasks.length === 0 ? (
          <p className="muted small">Ingen oppgaver.</p>
        ) : (
          <ul className="tasklist">
            {issue.tasks.map((t) => (
              <li key={t.id} className={t.done ? "done" : ""}>
                <label className="check grow">
                  <input type="checkbox" checked={t.done} disabled={!write || toggle.pending} onChange={() => void toggle.run(issue.id, t.id).then((r) => r && toast(t.done ? "Oppgave gjenåpnet" : "Oppgave fullført"))} />
                  {t.text}
                </label>
                <span className="small muted">{lookup.person(t.ownerId)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="dsection">
        <h3>Dokumenter</h3>
        {relDocs.length === 0 ? <p className="muted small">Ingen dokumenter koblet.</p> : (
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {relDocs.map((d) => (
              <li key={d.id}><Link to={`/dokumenter?dok=${d.id}`}>{d.title}</Link></li>
            ))}
          </ul>
        )}
      </div>
      <div className="dsection">
        <h3>Relatert</h3>
        <KV items={[["Prosjekt", issue.projectId ? <Link to={`/prosjekter/${issue.projectId}`}>{issue.projectId}</Link> : <Missing>Ikke koblet</Missing>], ["Tiltak", issue.maintenanceActionId ? <Link to={`/vedlikehold?tiltak=${issue.maintenanceActionId}`}>{issue.maintenanceActionId}</Link> : <Missing>Ikke koblet</Missing>], ["Leverandør", lookup.supplier(issue.supplierId) ?? <Missing>Ingen</Missing>]]} />
      </div>
      <div className="dsection">
        <h3>Kommentarer</h3>
        <div className="stack">
          {issue.comments.map((c, i) => (
            <div key={i} className={`comment${c.internal ? " internal" : ""}`}>
              <div className="by">
                {c.by} <span className="muted">· {formatDateTime(c.at)}{c.internal ? " · internt styrenotat" : ""}</span>
              </div>
              <div>{c.text}</div>
            </div>
          ))}
          {write && (
            <form
              className="stack"
              onSubmit={(e) => {
                e.preventDefault();
                if (!comment.trim()) return;
                void addComment.run(issue.id, comment.trim(), internal).then((r) => {
                  if (r) {
                    setComment("");
                    toast("Kommentar lagt til");
                  }
                });
              }}
            >
              <div className="field">
                <label htmlFor="cmt">Ny kommentar</label>
                <textarea id="cmt" value={comment} onChange={(e) => setComment(e.target.value)} style={{ minHeight: 64 }} />
              </div>
              <div className="row">
                <label className="check">
                  <input type="checkbox" checked={internal} onChange={(e) => setInternal(e.target.checked)} /> Internt styrenotat (skjult for beboere og leverandør)
                </label>
                <Button type="submit" size="sm" className="right" disabled={addComment.pending || !comment.trim()}>
                  Legg til
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
      <div className="dsection">
        <h3>Historikk</h3>
        <ol className="history">
          {issue.history.map((h, i) => (
            <li key={i}>
              <time dateTime={h.at}>{formatDateTime(h.at)} · {h.by}</time>
              {h.text}
            </li>
          ))}
        </ol>
      </div>
    </Drawer>
  );
}

export type { IssueStatus, Responsibility, Severity };
