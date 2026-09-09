/**
 * Tilbud og innkjøp: oversikt, QuoteRequestFlow (ny forespørsel) og QuoteComparison.
 * ERA gir beslutningsstøtte; styret velger leverandør i DecisionPanel.
 */
import { useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import { useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { Quote, QuoteRequest } from "@/domain/types";
import { formatDate, formatNOK, plural, relativeDeadline } from "@/lib/format";
import { useUrlParam } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useAssistant, useAssistantSelection } from "@/shell/assistant";
import { DecisionPanel, useLookup } from "@/components/domain";
import { Badge, Button, Callout, Card, DeniedState, EmptyState, ErrorState, KV, LinkButton, Skeleton } from "@/components/ui";
import { useToast } from "@/components/toast";
import { RoleAwareGuard } from "@/components/RoleAwareGuard";

const QR_STATUS: Record<QuoteRequest["status"], [string, "neutral" | "planned" | "decision" | "done"]> = {
  utkast: ["Utkast", "neutral"],
  sendt: ["Sendt, venter på tilbud", "planned"],
  tilbud_mottatt: ["Tilbud mottatt, krever beslutning", "decision"],
  besluttet: ["Besluttet", "done"],
};

export function Tilbud() {
  const session = useSession();
  const lookup = useLookup();
  const qrs = useQuery((a, s) => a.listQuoteRequests(s));
  const quotes = useQuery((a, s) => a.listQuotes(s));
  return (
    <>
      <PageHead title="Tilbud" meta={qrs.data ? [`${qrs.data.length} forespørsler`, `${qrs.data.filter((q) => q.status === "tilbud_mottatt").length} krever beslutning`] : []} actions={can(session.role, "quotes:request") && <LinkButton to="/tilbud/ny">Ny tilbudsforespørsel</LinkButton>} />
      {qrs.status === "error" ? <ErrorState error={qrs.error} retry={qrs.reload} /> : !qrs.data ? <Skeleton lines={6} /> : qrs.data.length === 0 ? (
        <EmptyState title="Ingen tilbudsforespørsler" what="Lag en forespørsel fra et tiltak eller prosjekt. ERA fyller inn omfang fra eiendomsdataene, og tilbudene kommer inn i standardisert form slik at de kan sammenlignes på likt grunnlag." action={can(session.role, "quotes:request") ? <LinkButton to="/tilbud/ny">Ny tilbudsforespørsel</LinkButton> : undefined} />
      ) : (
        <div className="stack">
          {qrs.data.map((qr) => {
            const qs = (quotes.data ?? []).filter((q) => q.quoteRequestId === qr.id);
            const [label, tone] = QR_STATUS[qr.status];
            return (
              <Card key={qr.id} pad className="stack">
                <div className="row">
                  <Badge tone={tone}>{label}</Badge>
                  <span className="small muted">Frist {formatDate(qr.deadline)} · {plural(qr.invitedSupplierIds.length, "leverandør invitert", "leverandører invitert")}</span>
                </div>
                <h2><Link to={`/tilbud/${qr.id}`}>{qr.title}</Link></h2>
                <div className="row small">
                  <span>{qr.scopeItems.filter((s) => s.included).length} poster i omfang</span>
                  <span>·</span>
                  <span>{qs.length === 0 ? "Ingen tilbud mottatt" : `${qs.length} tilbud: ${qs.map((q) => `${lookup.supplier(q.supplierId)} ${formatNOK(q.totalIncVat, { compact: true })}`).join(", ")}`}</span>
                </div>
                <div className="row">
                  <LinkButton to={`/tilbud/${qr.id}`} variant="secondary" size="sm">{qs.length > 1 ? "Sammenlign tilbud" : "Åpne forespørsel"}</LinkButton>
                  {qr.projectId && <Link to={`/prosjekter/${qr.projectId}`} className="small">Prosjekt</Link>}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}

export function TilbudSammenligning() {
  const { id = "" } = useParams();
  const { ask } = useAssistant();
  const lookup = useLookup();
  const qrs = useQuery((a, s) => a.listQuoteRequests(s));
  const quotes = useQuery((a, s) => a.listQuotes(s));
  const decisions = useQuery((a, s) => a.listDecisions(s));
  const qr = qrs.data?.find((q) => q.id === id);
  const qs = (quotes.data ?? []).filter((q) => q.quoteRequestId === id);
  const dec = (decisions.data ?? []).find((d) => d.projectId === qr?.projectId && d.title.toLowerCase().includes("leverand"));
  useAssistantSelection(qr ? { type: "tilbud", id: qr.id, label: qr.title } : undefined);

  if (qrs.status === "error") return <ErrorState error={qrs.error} retry={qrs.reload} />;
  if (!qrs.data || !quotes.data) return <Skeleton lines={10} />;
  if (!qr) return <DeniedState what="denne forespørselen" />;

  return (
    <>
      <PageHead eyebrow={<Link to="/tilbud">Tilbud</Link>} title={qr.title} meta={[`Frist ${formatDate(qr.deadline)}`, `${qs.length} av ${qr.invitedSupplierIds.length} inviterte har levert`, qr.projectId ? <Link to={`/prosjekter/${qr.projectId}`}>Prosjekt</Link> : "Ikke koblet til prosjekt"]} actions={<Button variant="secondary" era onClick={() => ask("Sammenlign disse tilbudene")}>Be ERA analysere tilbudene</Button>} />
      <div className="stack">
        <Card pad>
          <h2 style={{ marginBottom: 8 }}>Omfang i forespørselen</h2>
          <ul className="factlist">
            {qr.scopeItems.map((s) => (
              <li key={s.id}>
                <Badge tone={s.included ? "planned" : "neutral"} plain>{s.included ? "Inngår" : "Utenfor"}</Badge>
                <span>{s.text}</span>
              </li>
            ))}
          </ul>
        </Card>
        {qs.length === 0 ? (
          <EmptyState title="Ingen tilbud mottatt ennå" what={`Inviterte: ${qr.invitedSupplierIds.map(lookup.supplier).join(", ") || "ingen"}. Tilbud vises her i standardisert form når de kommer inn.`} />
        ) : (
          <>
            <QuoteComparison quotes={qs} request={qr} />
            {dec && <DecisionPanel decision={dec} quotes={qs} />}
            {!dec && <Callout>Ingen beslutning er registrert for denne forespørselen. Styreleder kan koble tilbudet til vedtak i prosjektet.</Callout>}
          </>
        )}
      </div>
    </>
  );
}

/** QuoteComparison: sammenligning på likt grunnlag med ERAs forklarbare vurdering. */
export function QuoteComparison({ quotes, request, compact }: { quotes: Quote[]; request: QuoteRequest; compact?: boolean }) {
  const lookup = useLookup();
  const lineKeys = useMemo(() => Array.from(new Set(quotes.flatMap((q) => q.lines.map((l) => l.key)))), [quotes]);
  const minTotal = Math.min(...quotes.map((q) => q.totalIncVat));
  const maxTotal = Math.max(...quotes.map((q) => q.totalIncVat));
  const cell = (q: Quote, key: string) => {
    const l = q.lines.find((x) => x.key === key);
    if (!l) return <span className="muted">Ikke nevnt</span>;
    return (
      <>
        <span className={l.included === true ? "yes" : l.included === "forbehold" ? "res" : "no"}>{l.included === true ? "Inngår" : l.included === "forbehold" ? "Forbehold" : "Inngår ikke"}</span>
        {l.note && <span className="line-note">{l.note}</span>}
      </>
    );
  };
  return (
    <div className="compare-wrap" data-testid="quote-comparison">
      <table className="compare">
        <thead>
          <tr>
            <th className="rowh">Sammenligning</th>
            {quotes.map((q) => (
              <th key={q.id}>
                <span className="sup">{lookup.supplier(q.supplierId)}</span>
                <span className="line-note">{lookup.suppliers.find((s) => s.id === q.supplierId)?.trade} · mottatt {formatDate(q.receivedAt)}</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <th className="rowh">Totalpris inkl. mva</th>
            {quotes.map((q) => (
              <td key={q.id} className={`num ${q.totalIncVat === minTotal ? "best" : q.totalIncVat === maxTotal ? "worst" : ""}`} style={{ fontWeight: 700 }}>{formatNOK(q.totalIncVat)}</td>
            ))}
          </tr>
          <tr>
            <th className="rowh">Ekskl. mva</th>
            {quotes.map((q) => <td key={q.id} className="num">{formatNOK(q.totalExVat)}</td>)}
          </tr>
          {lineKeys.map((k) => (
            <tr key={k}>
              <th className="rowh">{quotes.flatMap((q) => q.lines).find((l) => l.key === k)?.label ?? k}</th>
              {quotes.map((q) => <td key={q.id}>{cell(q, k)}</td>)}
            </tr>
          ))}
          <tr>
            <th className="rowh">Forbehold</th>
            {quotes.map((q) => (
              <td key={q.id}>{q.reservations.length === 0 ? <span className="yes">Ingen</span> : <ul style={{ margin: 0, paddingLeft: 16 }}>{q.reservations.map((r) => <li key={r}>{r}</li>)}</ul>}</td>
            ))}
          </tr>
          <tr>
            <th className="rowh">Leveringstid</th>
            {quotes.map((q) => <td key={q.id}>{q.deliveryWeeks} uker · tidligst {formatDate(q.startEarliest)}</td>)}
          </tr>
          <tr>
            <th className="rowh">Garanti</th>
            {quotes.map((q) => <td key={q.id} className={q.warrantyYears === Math.max(...quotes.map((x) => x.warrantyYears)) ? "best" : ""}>{q.warrantyYears} år</td>)}
          </tr>
          <tr>
            <th className="rowh">Dokumentasjonskrav</th>
            {quotes.map((q) => <td key={q.id}><span className={q.documentationCommitment === "full_fdv" ? "yes" : q.documentationCommitment === "delvis" ? "res" : "no"}>{{ full_fdv: "Full FDV", delvis: "Delvis", ikke_spesifisert: "Ikke spesifisert" }[q.documentationCommitment]}</span></td>)}
          </tr>
          <tr>
            <th className="rowh">Endringsrisiko</th>
            {quotes.map((q) => (
              <td key={q.id} className={q.changeRisk === "lav" ? "best" : q.changeRisk === "hoy" ? "worst" : ""}>
                <span className={q.changeRisk === "lav" ? "yes" : q.changeRisk === "hoy" ? "no" : "res"}>{{ lav: "Lav", middels: "Middels", hoy: "Høy" }[q.changeRisk]}</span>
                <span className="line-note">{q.changeRiskNote}</span>
              </td>
            ))}
          </tr>
          <tr>
            <th className="rowh">Leverandørstatus</th>
            {quotes.map((q) => {
              const s = lookup.suppliers.find((x) => x.id === q.supplierId);
              return <td key={q.id}><span className={s?.status === "godkjent" ? "yes" : "res"}>{s ? { godkjent: "Godkjent", ny: "Ny", avventer_dokumentasjon: "Avventer dokumentasjon" }[s.status] : "Ukjent"}</span></td>;
            })}
          </tr>
          {!compact && (
            <tr>
              <th className="rowh">Mangler mot forespørselen</th>
              {quotes.map((q) => {
                const m = q.eraAssessment.missing;
                return <td key={q.id}>{m.length === 0 ? <span className="yes">Ingen av de {request.scopeItems.filter((s) => s.included).length} postene mangler</span> : <ul style={{ margin: 0, paddingLeft: 16 }}>{m.map((x) => <li key={x} className="no" style={{ fontWeight: 400 }}>{x}</li>)}</ul>}</td>;
              })}
            </tr>
          )}
          <tr>
            <th className="rowh">ERAs vurdering</th>
            {quotes.map((q) => (
              <td key={q.id} data-testid="era-assessment">
                <p style={{ fontWeight: 500 }}>{q.eraAssessment.summary}</p>
                {!compact && (
                  <>
                    {q.eraAssessment.strengths.length > 0 && <p className="line-note"><span className="yes">Styrker:</span> {q.eraAssessment.strengths.join(", ")}</p>}
                    {q.eraAssessment.concerns.length > 0 && <p className="line-note"><span className="res">Å merke seg:</span> {q.eraAssessment.concerns.join(", ")}</p>}
                  </>
                )}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
      <p className="small muted" style={{ padding: "10px 12px" }}>ERA vurderer, styret beslutter. Vurderingen bygger på tilbudsdokumentene og forespørselen; den erstatter ikke fagkontroll.</p>
    </div>
  );
}

/** QuoteRequestFlow: behov → omfang → leverandører → frist → send. */
export function TilbudNy() {
  const navigate = useNavigate();
  const toast = useToast();
  const lookup = useLookup();
  const [projectId, setProjectId] = useUrlParam("prosjekt");
  const [actionId] = useUrlParam("tiltak");
  const projects = useQuery((a, s) => a.listProjects(s));
  const actions = useQuery((a, s) => a.listMaintenance(s));
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState("");
  const [scope, setScope] = useState<{ id: string; text: string; included: boolean }[]>([]);
  const [invited, setInvited] = useState<string[]>([]);
  const [deadline, setDeadline] = useState("2026-10-20");
  const create = useMutation((a, s, input: Parameters<typeof a.createQuoteRequest>[1]) => a.createQuoteRequest(s, input));

  const project = projects.data?.find((p) => p.id === projectId);
  const action = actions.data?.find((m) => m.id === actionId) ?? actions.data?.find((m) => m.projectId === projectId);

  const suggestScope = () => {
    const base = project?.scope ?? action?.title ?? "";
    const items = base
      .split(/[.,]/)
      .map((s) => s.trim())
      .filter((s) => s.length > 6)
      .map((text, i) => ({ id: `s-${i}`, text, included: true }));
    setScope(items.length ? [...items, { id: "s-fdv", text: "FDV-dokumentasjon", included: true }, { id: "s-stillas", text: "Stillas og rigg", included: true }] : [{ id: "s-1", text: "Beskriv omfang", included: true }, { id: "s-fdv", text: "FDV-dokumentasjon", included: true }]);
    if (!title) setTitle(project?.title ?? action?.title ?? "");
  };

  const steps = ["Behov", "Omfang", "Leverandører", "Frist og send"];
  return (
    <RoleAwareGuard permission="quotes:request" what="å opprette tilbudsforespørsler">
      <PageHead eyebrow={<Link to="/tilbud">Tilbud</Link>} title="Ny tilbudsforespørsel" meta={["ERA foreslår omfang fra eiendomsdataene. Du redigerer og godkjenner før utsendelse."]} />
      <ol className="steps">
        {steps.map((s, i) => (
          <li key={s} aria-current={step === i + 1 ? "step" : undefined} className={step > i + 1 ? "done" : ""}>
            <span className="n">{i + 1}</span>
            {s}
          </li>
        ))}
      </ol>
      <Card pad className="stack" style={{ maxWidth: 760 }}>
        {step === 1 && (
          <>
            <div className="field">
              <label htmlFor="q-prj">Behov eller prosjekt</label>
              <select id="q-prj" value={projectId} onChange={(e) => setProjectId(e.target.value)} data-testid="qr-project">
                <option value="">Velg prosjekt</option>
                {(projects.data ?? []).map((p) => (
                  <option key={p.id} value={p.id}>{p.title}</option>
                ))}
              </select>
              <span className="hint">Forespørselen kobles til prosjektet, slik at tilbud, vedtak og kontrakt henger sammen.</span>
            </div>
            {project && <KV items={[["Formål", project.purpose], ["Berørte bygg", project.buildingIds.map(lookup.building).join(", ")], ["Berørte boliger", project.affectedUnitIds.length], ["Budsjett", formatNOK(project.budget)]]} />}
            {action && <Callout title="Fra vedlikeholdsplanen">{action.title} · anbefalt {action.recommendedYear} · {action.cost ? `${formatNOK(action.cost.low, { compact: true })} – ${formatNOK(action.cost.high, { compact: true })}` : "kostnad ikke anslått"}</Callout>}
            <div className="field">
              <label htmlFor="q-title">Tittel på forespørselen</label>
              <input id="q-title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder={project?.title ?? "F.eks. Utskifting av inngangsdører"} />
            </div>
            <div><Button onClick={() => { suggestScope(); setStep(2); }} disabled={!projectId && !title} data-testid="qr-next-1">Neste: omfang</Button></div>
          </>
        )}
        {step === 2 && (
          <>
            <h2>Velg omfang</h2>
            <p className="small muted">ERA har foreslått poster fra prosjektbeskrivelsen. Fjern det som ikke skal prises, og legg til egne poster.</p>
            <ul className="tasklist">
              {scope.map((s) => (
                <li key={s.id}>
                  <label className="check grow">
                    <input type="checkbox" checked={s.included} onChange={() => setScope((sc) => sc.map((x) => (x.id === s.id ? { ...x, included: !x.included } : x)))} />
                    <input value={s.text} onChange={(e) => setScope((sc) => sc.map((x) => (x.id === s.id ? { ...x, text: e.target.value } : x)))} style={{ flex: 1, minHeight: 34, border: "1px solid var(--line)", borderRadius: 6, padding: "0 8px", background: "var(--card)" }} aria-label="Post" />
                  </label>
                </li>
              ))}
            </ul>
            <div className="row">
              <Button variant="secondary" size="sm" onClick={() => setScope((sc) => [...sc, { id: `s-${Date.now()}`, text: "", included: true }])}>Legg til post</Button>
            </div>
            <div className="row"><Button variant="ghost" onClick={() => setStep(1)}>Tilbake</Button><Button onClick={() => setStep(3)} disabled={scope.filter((s) => s.included && s.text.trim()).length === 0} data-testid="qr-next-2">Neste: leverandører</Button></div>
          </>
        )}
        {step === 3 && (
          <>
            <h2>Inviter leverandører</h2>
            <p className="small muted">Leverandører uten godkjent dokumentasjon kan inviteres, men merkes i sammenligningen.</p>
            <div className="stack">
              {lookup.suppliers.map((s) => (
                <label key={s.id} className="check">
                  <input type="checkbox" checked={invited.includes(s.id)} onChange={() => setInvited((v) => (v.includes(s.id) ? v.filter((x) => x !== s.id) : [...v, s.id]))} />
                  <span className="grow">{s.name} <span className="muted small">· {s.trade}</span></span>
                  <Badge tone={s.status === "godkjent" ? "done" : "decision"}>{{ godkjent: "Godkjent", ny: "Ny", avventer_dokumentasjon: "Avventer dokumentasjon" }[s.status]}</Badge>
                </label>
              ))}
            </div>
            <div className="row"><Button variant="ghost" onClick={() => setStep(2)}>Tilbake</Button><Button onClick={() => setStep(4)} disabled={invited.length === 0} data-testid="qr-next-3">Neste: frist</Button></div>
          </>
        )}
        {step === 4 && (
          <>
            <h2>Frist og utsendelse</h2>
            <div className="field" style={{ maxWidth: 240 }}>
              <label htmlFor="q-deadline">Tilbudsfrist</label>
              <input id="q-deadline" type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} />
              <span className="hint">{relativeDeadline(deadline)}</span>
            </div>
            <KV items={[["Tittel", title || project?.title], ["Poster", scope.filter((s) => s.included).length], ["Leverandører", invited.map(lookup.supplier).join(", ")]]} />
            <Callout tone="warn">Utsendelse gjøres av styret. ERA sender ingenting før du bekrefter her.</Callout>
            <div className="row">
              <Button variant="ghost" onClick={() => setStep(3)}>Tilbake</Button>
              <Button
                disabled={create.pending}
                data-testid="qr-send"
                onClick={async () => {
                  const r = await create.run({ title: title || project?.title || "Tilbudsforespørsel", projectId: projectId || undefined, scopeItems: scope.filter((s) => s.text.trim()), invitedSupplierIds: invited, deadline });
                  if (r) {
                    toast(`Forespørsel sendt til ${plural(invited.length, "leverandør", "leverandører")}`);
                    navigate(`/tilbud/${r.id}`);
                  } else toast("Kunne ikke sende forespørselen", "error");
                }}
              >
                {create.pending ? "Sender …" : "Send forespørsel"}
              </Button>
            </div>
          </>
        )}
      </Card>
    </RoleAwareGuard>
  );
}
