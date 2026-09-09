/** Strukturert eiendomsarkiv + DocumentIntelligence (ERAs funn med kilde, bekreftelse og korrigering). */
import { useMemo, useState } from "react";
import { Link } from "react-router";
import { useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { Document, DocumentType } from "@/domain/types";
import { formatDate } from "@/lib/format";
import { DOC_TYPE_LABEL } from "@/lib/labels";
import { useUrlParams } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useAssistant, useAssistantSelection } from "@/shell/assistant";
import { useLookup } from "@/components/domain";
import { Badge, Button, Callout, ConfidenceBadge, Drawer, EmptyState, ErrorState, KV, Progress, Skeleton } from "@/components/ui";
import { useToast } from "@/components/toast";

const STATUS: Record<Document["status"], [string, "done" | "active" | "neutral" | "critical"]> = {
  analysert: ["Analysert", "done"],
  under_analyse: ["Under analyse", "active"],
  ikke_analysert: ["Ikke analysert", "neutral"],
  feil: ["Analyse feilet", "critical"],
};

const ACCESS: Record<Document["access"], string> = { styret: "Styret", alle_beboere: "Alle beboere", privat: "Privat (én bolig)", leverandor: "Leverandør" };

const CLIP = 8;

export function Dokumenter() {
  const lookup = useLookup();
  const [all, setAll] = useState(false);
  const [params, patch] = useUrlParams();
  const docs = useQuery((a, s) => a.listDocuments(s));
  const q = params.get("q") ?? "";
  const type = params.get("type") ?? "";
  const status = params.get("status") ?? "";
  const kobling = params.get("kobling") ?? "";
  const selected = params.get("dok") ?? "";

  const rows = useMemo(
    () =>
      (docs.data ?? [])
        .filter((d) => {
          if (q && !`${d.title} ${d.source}`.toLowerCase().includes(q.toLowerCase())) return false;
          if (type && d.type !== type) return false;
          if (status === "mangler" ? !(d.missingMetadata.length > 0 || Object.keys(d.links).length === 0) : status && d.status !== status) return false;
          if (kobling) {
            const [k, v] = kobling.split(":");
            if ((d.links as Record<string, string | undefined>)[k ?? ""] !== v) return false;
          }
          return true;
        })
        .sort((a, b) => b.date.localeCompare(a.date)),
    [docs.data, q, type, status, kobling],
  );
  const open = docs.data?.find((d) => d.id === selected);
  const linkLabel = (d: Document) => {
    const l = d.links;
    const parts = [l.projectId && `Prosjekt: ${l.projectId}`, l.buildingPartId && lookup.part(l.buildingPartId), l.buildingId && lookup.building(l.buildingId), l.issueId && `Avvik ${l.issueId}`, l.unitId && `Bolig ${l.unitId.split("-").pop()}`, l.supplierId && lookup.supplier(l.supplierId), l.warrantyUntil && `Garanti til ${formatDate(l.warrantyUntil)}`].filter(Boolean);
    return parts;
  };

  return (
    <>
      <PageHead title="Dokumenter" meta={docs.data ? [`${docs.data.length} dokumenter`, `${docs.data.filter((d) => d.status === "analysert").length} analysert`, `${docs.data.filter((d) => d.missingMetadata.length > 0 || Object.keys(d.links).length === 0).length} mangler kobling eller metadata`] : []} actions={<Button variant="secondary" disabled title="Opplasting krever backend (kommer)">Last opp dokument</Button>} />
      <Callout>Opplasting og automatisk analyse krever backend som ikke finnes ennå. Arkivet under viser hvordan ERA-tolkede dokumenter presenteres.</Callout>
      <div className="filters">
        <input type="search" value={q} onChange={(e) => patch({ q: e.target.value })} placeholder="Søk i dokumenter" aria-label="Søk i dokumenter" />
        <select value={type} onChange={(e) => patch({ type: e.target.value })} aria-label="Dokumenttype">
          <option value="">Alle typer</option>
          {(Object.keys(DOC_TYPE_LABEL) as DocumentType[]).map((t) => (
            <option key={t} value={t}>{DOC_TYPE_LABEL[t]}</option>
          ))}
        </select>
        <select value={status} onChange={(e) => patch({ status: e.target.value })} aria-label="Status" data-testid="doc-status">
          <option value="">Alle statuser</option>
          <option value="analysert">Analysert</option>
          <option value="under_analyse">Under analyse</option>
          <option value="ikke_analysert">Ikke analysert</option>
          <option value="feil">Analyse feilet</option>
          <option value="mangler">Mangler kobling eller metadata</option>
        </select>
        <select value={kobling} onChange={(e) => patch({ kobling: e.target.value })} aria-label="Tilknytning">
          <option value="">Alle tilknytninger</option>
          <optgroup label="Bygningsdel">{lookup.parts.map((p) => <option key={p.id} value={`buildingPartId:${p.id}`}>{p.name}</option>)}</optgroup>
          <optgroup label="Bygg">{lookup.buildings.map((b) => <option key={b.id} value={`buildingId:${b.id}`}>{b.name}</option>)}</optgroup>
          <optgroup label="Leverandør">{lookup.suppliers.map((s) => <option key={s.id} value={`supplierId:${s.id}`}>{s.name}</option>)}</optgroup>
        </select>
        {(q || type || status || kobling) && <Button variant="ghost" size="sm" onClick={() => patch({ q: null, type: null, status: null, kobling: null })}>Nullstill</Button>}
      </div>
      {docs.status === "error" ? <ErrorState error={docs.error} retry={docs.reload} /> : !docs.data ? <Skeleton lines={8} /> : rows.length === 0 ? (
        <EmptyState title="Ingen dokumenter" what="Dokumentarkivet kobler tilstandsrapporter, FDV, tilbud, kontrakter, garantier og protokoller til bygg, bygningsdel, sak og prosjekt." why="ERA leser dokumentene og foreslår tiltak, frister og garantier. Du bekrefter eller korrigerer." />
      ) : (
        <>
          <div className="fill desktop-only">
          <div className="table-wrap">
            <table className="tbl" data-testid="doc-table">
              <thead>
                <tr><th>Dokument</th><th>Type</th><th>Tilknytning</th><th>Dato</th><th>Status</th><th>Analyse</th><th>Mangler</th><th>Tilgang</th></tr>
              </thead>
              <tbody>
                {(all ? rows : rows.slice(0, CLIP)).map((d) => {
                  const [sl, st] = STATUS[d.status];
                  const links = linkLabel(d);
                  return (
                    <tr key={d.id} className="rowlink" tabIndex={0} aria-selected={selected === d.id} onClick={() => patch({ dok: d.id })} onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), patch({ dok: d.id }))}>
                      <td><span className="primary">{d.title}</span><span className="sub">{d.source}{d.pages ? ` · ${d.pages} sider` : ""}</span></td>
                      <td>{DOC_TYPE_LABEL[d.type]}</td>
                      <td className="wrap">{links.length ? links.join(" · ") : <Badge tone="decision" plain>Ikke koblet</Badge>}</td>
                      <td className="nowrap">{formatDate(d.date)}</td>
                      <td><Badge tone={st}>{sl}</Badge></td>
                      <td style={{ minWidth: 90 }}>{d.analysisPct !== undefined ? <><Progress pct={d.analysisPct} /><span className="small muted">{d.analysisPct} % · {d.findings.length} funn</span></> : <span className="muted">Ikke startet</span>}</td>
                      <td className="wrap">{d.missingMetadata.length ? <span style={{ color: "var(--decision)" }}>{d.missingMetadata.join(", ")}</span> : <span className="muted">Ingen</span>}</td>
                      <td className="nowrap">{ACCESS[d.access]}</td>
                    </tr>
                  );
                })}
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
            {rows.map((d) => (
              <button key={d.id} className="item" onClick={() => patch({ dok: d.id })}>
                <span className="t">{d.title}</span>
                <span className="m"><span>{DOC_TYPE_LABEL[d.type]}</span><span>{formatDate(d.date)}</span><Badge tone={STATUS[d.status][1]}>{STATUS[d.status][0]}</Badge>{d.missingMetadata.length > 0 && <span style={{ color: "var(--decision)" }}>Mangler {d.missingMetadata.join(", ")}</span>}</span>
              </button>
            ))}
          </div>
        </>
      )}
      {open && <DocumentIntelligence doc={open} onClose={() => patch({ dok: null })} />}
    </>
  );
}

function DocumentIntelligence({ doc, onClose }: { doc: Document; onClose: () => void }) {
  const session = useSession();
  const lookup = useLookup();
  const toast = useToast();
  const { ask } = useAssistant();
  useAssistantSelection({ type: "dokument", id: doc.id, label: doc.title });
  const [editing, setEditing] = useState<string | null>(null);
  const [text, setText] = useState("");
  const confirm = useMutation((a, s, fid: string, corrected?: string) => a.confirmFinding(s, doc.id, fid, corrected));
  const canCorrect = can(session.role, "documents:correct");
  const [sl, st] = STATUS[doc.status];
  const l = doc.links;

  return (
    <Drawer eyebrow={`${DOC_TYPE_LABEL[doc.type]} · ${doc.source} · ${formatDate(doc.date, "long")}`} title={doc.title} onClose={onClose} wide footer={<><Button variant="secondary" disabled title="Krever lagring i backend">Åpne originalfil</Button><Button variant="secondary" era onClick={() => ask("Hva mangler vi av dokumentasjon?")}>Spør ERA</Button></>}>
      <div className="row" style={{ marginBottom: 12 }}>
        <Badge tone={st}>{sl}</Badge>
        <Badge tone="neutral" plain>Tilgang: {ACCESS[doc.access]}</Badge>
        {doc.pages && <span className="small muted">{doc.pages} sider</span>}
      </div>
      {doc.status === "feil" && <Callout tone="danger" title="Analysen feilet">Filen kunne ikke leses (skannet uten tekstlag). Last opp på nytt med OCR, eller legg inn metadata manuelt.</Callout>}
      {doc.status === "under_analyse" && <Callout title="Forsinket behandling">Analysen er {doc.analysisPct} % ferdig. Funn under kan endres til analysen er fullført.</Callout>}
      <div className="dsection">
        <h3>Tilknytning</h3>
        <KV items={[
          ["Prosjekt", l.projectId ? <Link to={`/prosjekter/${l.projectId}`}>{l.projectId}</Link> : <span className="muted">Ikke koblet</span>],
          ["Bygningsdel", lookup.part(l.buildingPartId) ?? <span className="muted">Ikke koblet</span>],
          ["Bygg", lookup.building(l.buildingId) ?? <span className="muted">Hele eiendommen / ikke satt</span>],
          ["Sak", l.issueId ? <Link to={`/saker?sak=${l.issueId}`}>{l.issueId}</Link> : <span className="muted">Ingen</span>],
          ["Tiltak", l.maintenanceActionId ? <Link to={`/vedlikehold?tiltak=${l.maintenanceActionId}`}>{l.maintenanceActionId}</Link> : <span className="muted">Ingen</span>],
          ["Leverandør", lookup.supplier(l.supplierId) ?? <span className="muted">Ingen</span>],
          ["Garanti", l.warrantyUntil ? <strong>Utløper {formatDate(l.warrantyUntil, "long")}</strong> : <span className="muted">Ingen</span>],
        ]} />
        {doc.missingMetadata.length > 0 && <Callout tone="warn" title="Manglende metadata">{doc.missingMetadata.join(", ")}. {canCorrect ? "Legg inn manuelt, så prioriteres det over senere maskinell tolkning." : "Styreleder kan legge inn manuelt."}</Callout>}
      </div>
      <div className="dsection">
        <h3>Hva ERA har funnet</h3>
        {doc.findings.length === 0 ? <p className="muted small">Ingen funn registrert{doc.status === "ikke_analysert" ? " – dokumentet er ikke analysert" : ""}.</p> : (
          <div className="stack" data-testid="findings">
            {doc.findings.map((f) => (
              <div key={f.id} className="finding">
                <div className="row">
                  <strong>{f.field}</strong>
                  <ConfidenceBadge value={f.confidence} />
                  {f.confirmedBy && <span className="small muted">bekreftet av {f.confirmedBy}</span>}
                </div>
                {f.correctedText ? (
                  <>
                    <div className="corr">{f.correctedText}</div>
                    <div className="old small">{f.text}</div>
                  </>
                ) : (
                  <div>{f.text}</div>
                )}
                <div className="loc">Kilde: {f.location}</div>
                {canCorrect && !f.confirmedBy && (
                  editing === f.id ? (
                    <div className="stack">
                      <textarea value={text} onChange={(e) => setText(e.target.value)} aria-label="Korrigert tekst" style={{ minHeight: 64, borderRadius: 6, border: "1px solid var(--line-strong)", padding: 8 }} />
                      <div className="row">
                        <Button size="sm" disabled={confirm.pending} onClick={async () => { const r = await confirm.run(f.id, text.trim() || undefined); if (r) { toast("Funn korrigert og bekreftet"); setEditing(null); } }}>Lagre korrigering</Button>
                        <Button size="sm" variant="ghost" onClick={() => setEditing(null)}>Avbryt</Button>
                      </div>
                    </div>
                  ) : (
                    <div className="row">
                      <Button size="sm" variant="secondary" disabled={confirm.pending} onClick={async () => { const r = await confirm.run(f.id); if (r) toast("Funn bekreftet"); }} data-testid="confirm-finding">Bekreft</Button>
                      <Button size="sm" variant="ghost" onClick={() => { setEditing(f.id); setText(f.correctedText ?? f.text); }}>Korriger</Button>
                    </div>
                  )
                )}
              </div>
            ))}
          </div>
        )}
        <p className="small muted" style={{ marginTop: 8 }}>Menneskelig korrigering veier alltid tyngre enn senere maskinell tolkning.</p>
      </div>
    </Drawer>
  );
}
