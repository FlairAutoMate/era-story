/**
 * ResidentUpgradeFlow (beboer): se fellesarbeidet → hva som dekkes → kartlegging → bilder → pakke →
 * tilvalg → egen kostnad → aksept → fremdrift → dokumentasjon. Styredata er ikke tilgjengelig her.
 */
import { useState } from "react";
import { useMutation, useQuery, useSession } from "@/data/provider";
import type { UpgradeTier } from "@/domain/types";
import { formatDate, formatNOK } from "@/lib/format";
import { RESPONSE_LABEL, TIER_LABEL } from "@/lib/labels";
import { PageHead } from "@/shell/AppShell";
import { useAssistant } from "@/shell/assistant";
import { useLookup } from "@/components/domain";
import { RoleAwareGuard } from "@/components/RoleAwareGuard";
import { Badge, Button, Callout, Card, ConfirmModal, EmptyState, ErrorState, KV, Progress, SectionHead, Skeleton } from "@/components/ui";
import { useToast } from "@/components/toast";

export function MinBolig() {
  return (
    <RoleAwareGuard permission="resident:read_own" what="beboerens boligvisning">
      <Inner />
    </RoleAwareGuard>
  );
}

function Inner() {
  const session = useSession();
  const toast = useToast();
  const { ask } = useAssistant();
  const lookup = useLookup();
  const my = useQuery((a, s) => a.getMyParticipation(s));
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [photos, setPhotos] = useState(0);
  const [tier, setTier] = useState<UpgradeTier | null>(null);
  const [options, setOptions] = useState<string[]>([]);
  const [confirm, setConfirm] = useState(false);
  const [view, setView] = useState<number | null>(null);
  const survey = useMutation((a, s, pid: string, ans: Record<string, string>, ph: number) => a.answerSurvey(s, pid, ans, ph));
  const choose = useMutation((a, s, pid: string, t: UpgradeTier, o: string[]) => a.chooseTier(s, pid, t, o));
  const accept = useMutation((a, s, pid: string) => a.acceptPrivateQuote(s, pid));

  if (my.status === "error") return <ErrorState error={my.error} retry={my.reload} />;
  if (!my.data && my.status === "loading") return <Skeleton lines={10} />;
  if (!my.data) return <EmptyState title="Ingen pågående prosjekter for din bolig" what="Når borettslaget planlegger arbeid som berører boligen din, ser du hva som skal gjøres, hva som dekkes, og hva du kan velge selv." />;

  const { project: p, participation: r, unit } = my.data;
  const q = r.privateQuote;
  const quoteTotal = q ? q.basePrice + q.options.filter((o) => o.selected).reduce((s, o) => s + o.price, 0) - q.coordinationDiscount : 0;
  const answered = !!r.surveyAnswers && Object.keys(r.surveyAnswers).length > 0;
  const step = r.responseStatus === "akseptert" || r.responseStatus === "avslatt" ? 4 : r.tier || q ? 3 : answered ? 2 : 1;
  const covered = p.packages?.find((pk) => pk.coveredByTenant);
  const priv = (p.packages ?? []).filter((pk) => !pk.coveredByTenant);
  const selectedPkg = p.packages?.find((pk) => pk.tier === (tier ?? r.tier ?? q?.tier));
  const current = view ?? step;
  const go = (n: number) => setView(Math.max(1, Math.min(4, n)));
  const previewTotal = selectedPkg && !selectedPkg.coveredByTenant ? Math.round(((selectedPkg.priceFrom ?? 0) + (selectedPkg.priceTo ?? 0)) / 2) + (p.productOptions ?? []).filter((o) => options.includes(o.id)).reduce((s, o) => s + o.price, 0) - (selectedPkg.coordinationDiscount ?? 0) : 0;

  return (
    <>
      <PageHead eyebrow="Min bolig" title={`${unit.label} · ${lookup.entrance(unit.entranceId) ?? ""}`} meta={[`${session.name}`, `${p.title} · ${{ planlagt: "planlagt", kartlegging: "kartlegging pågår", til_tilbud: "tilbud innhentes", til_beslutning: "til beslutning", vedtatt: "vedtatt", gjennomforing: "arbeid pågår", kontroll: "kontroll", dokumentert: "ferdig" }[p.stage]}`]} actions={<Button variant="secondary" era onClick={() => ask("Hva skal borettslaget gjøre i badet mitt?")}>Spør ERA</Button>} />

      <ol className="steps" aria-label="Steg">
        {["Kartlegging", "Velg pakke", "Aksepter tilbud", "Følg arbeidet"].map((s, i) => (
          <li key={s} aria-current={current === i + 1 ? "step" : undefined} className={step > i + 1 ? "done" : ""} style={{ cursor: "pointer" }} onClick={() => go(i + 1)}><span className="n">{i + 1}</span>{s}</li>
        ))}
      </ol>

      <div className="split">
        <div className="stack">
          <Card pad className="stack" data-testid="resident-shared">
            <SectionHead title="Dette skal borettslaget gjøre" />
            <p>{p.purpose}</p>
            <p className="small muted">{p.scope}</p>
            {covered && (
              <div className="pkg" style={{ cursor: "default" }} aria-pressed="true">
                <div className="row"><h3>{covered.name}</h3><Badge tone="planned" plain>Dekkes av borettslaget</Badge></div>
                <ul>{covered.includes.map((x) => <li key={x}>{x}</li>)}</ul>
                <p className="small muted">Ikke inkludert: {covered.excludes.join(", ")}</p>
              </div>
            )}
            <KV items={[["Planlagt oppstart i din oppgang", r.scheduledWeek ? `Uke ${r.scheduledWeek} 2027` : "Ikke fastsatt"], ["Din status", RESPONSE_LABEL[r.responseStatus]]]} />
          </Card>

          {current === 1 && <Card pad className="stack">
            <SectionHead title="Kartlegging av badet ditt" right={answered ? <Badge tone="done">Besvart</Badge> : <Badge tone="decision">Svar innen {formatDate(p.milestones.find((m) => m.kind === "frist" && !m.done)?.date)}</Badge>} />
            {answered ? (
              <KV items={(p.surveyQuestions ?? []).map((sq) => [sq.text, r.surveyAnswers?.[sq.id] ?? "–"])} />
            ) : (
              <form className="stack" onSubmit={async (e) => { e.preventDefault(); const res = await survey.run(p.id, answers, photos); if (res) toast("Takk, svaret er registrert"); }} data-testid="survey-form">
                {(p.surveyQuestions ?? []).map((sq) => (
                  <div key={sq.id} className="field"><label htmlFor={sq.id}>{sq.text}</label><input id={sq.id} value={answers[sq.id] ?? ""} onChange={(e) => setAnswers((a) => ({ ...a, [sq.id]: e.target.value }))} /></div>
                ))}
                <div className="field"><span className="lbl">Bilder av rørsjakt og bad</span><div className="row"><Button variant="secondary" size="sm" onClick={() => setPhotos((n) => n + 1)}>Legg til bilde</Button><span className="small muted">{photos ? `${photos} bilder valgt` : "Ingen bilder ennå"}</span></div></div>
                <div><Button type="submit" disabled={survey.pending || Object.keys(answers).length < (p.surveyQuestions?.length ?? 0)}>Send svar</Button></div>
              </form>
            )}
            {r.photos ? <p className="small muted">{r.photos} bilder lastet opp.</p> : null}
            <div><Button variant="secondary" onClick={() => go(2)}>Neste: velg pakke</Button></div>
          </Card>}

          {p.hasPrivateUpgrades && current === 2 && (
            <Card pad className="stack" data-testid="resident-packages">
              <SectionHead title="Valgfri privat oppgradering" />
              <p className="small muted">Frivillig. Betales av deg, faktureres av {lookup.supplier(p.supplierIds[0])}. Samkjøringsbesparelsen får du fordi badet uansett åpnes.</p>
              <div className="grid cols-2">
                <button className="pkg" aria-pressed={(tier ?? r.tier) === "kun_felles"} onClick={() => setTier("kun_felles")} disabled={r.responseStatus === "akseptert"}>
                  <h3>Kun fellesarbeid</h3>
                  <p className="small">Ingen private tilvalg. Badet lukkes med enkel flislapping.</p>
                  <span className="price">0 kr</span>
                </button>
                {priv.map((pk) => (
                  <button key={pk.tier} className="pkg" aria-pressed={(tier ?? r.tier ?? q?.tier) === pk.tier} onClick={() => setTier(pk.tier)} disabled={r.responseStatus === "akseptert"} data-testid={`pkg-${pk.tier}`}>
                    <h3>{pk.name}</h3>
                    <p className="small">{pk.description}</p>
                    <ul>{pk.includes.slice(0, 4).map((x) => <li key={x}>{x}</li>)}</ul>
                    <span className="price">{formatNOK(pk.priceFrom)} – {formatNOK(pk.priceTo)}</span>
                    <span className="small muted">inkl. mva · samkjøringsbesparelse {formatNOK(pk.coordinationDiscount)} er trukket fra</span>
                  </button>
                ))}
              </div>
              {selectedPkg && !selectedPkg.coveredByTenant && (tier ?? r.tier) !== "kun_felles" && r.responseStatus !== "akseptert" && (
                <div className="stack">
                  <span className="lbl">Produkt- og materialtilvalg</span>
                  {(p.productOptions ?? []).filter((o) => o.price > 0).map((o) => (
                    <label key={o.id} className="check"><input type="checkbox" checked={options.includes(o.id)} onChange={() => setOptions((s) => (s.includes(o.id) ? s.filter((x) => x !== o.id) : [...s, o.id]))} /><span className="grow">{o.name} <span className="muted small">· {o.group}</span></span><span className="num">+{formatNOK(o.price)}</span></label>
                  ))}
                </div>
              )}
              {tier && r.responseStatus !== "akseptert" && (
                <div className="sticky-cta row">
                  <div className="grow"><div className="eyebrow">Din kostnad</div><div className="figure sm">{tier === "kun_felles" ? "0 kr" : formatNOK(previewTotal)}</div></div>
                  <Button disabled={choose.pending} data-testid="choose-tier" onClick={async () => { const res = await choose.run(p.id, tier, options); if (res) toast(tier === "kun_felles" ? "Registrert: kun fellesarbeid" : `Valgt: ${TIER_LABEL[tier]}`); setTier(null); }}>{tier === "kun_felles" ? "Bekreft kun fellesarbeid" : "Be om tilbud på dette"}</Button>
                </div>
              )}
            </Card>
          )}
          {current === 2 && <div className="row"><Button variant="ghost" onClick={() => go(1)}>Tilbake</Button><Button variant="secondary" onClick={() => go(3)}>Neste: tilbud</Button></div>}
        </div>

        <div className="stack">
          {current === 3 && <Card pad className="stack" data-testid="resident-quote">
            <SectionHead title="Ditt private tilbud" />
            {!q ? (
              <p className="muted small">{r.responseStatus === "avslatt" ? "Du har valgt kun fellesarbeid. Ingen privat kostnad." : "Velg en pakke for å få et tilbud."}</p>
            ) : (
              <>
                <KV items={[["Pakke", TIER_LABEL[q.tier]], ["Grunnpris", formatNOK(q.basePrice)], ...q.options.filter((o) => o.selected).map((o) => [o.name, `+${formatNOK(o.price)}`] as [string, string]), ["Samkjøringsbesparelse", `−${formatNOK(q.coordinationDiscount)}`]]} />
                <div className="figure" data-testid="resident-total">{formatNOK(quoteTotal)} <span className="small muted" style={{ fontFamily: "var(--font)", fontWeight: 400 }}>inkl. mva</span></div>
                {q.accepted ? <Callout tone="good">Akseptert {formatDate(q.accepted)}. Leverandøren tar kontakt om tidspunkt.</Callout> : (
                  <>
                    <Callout tone="warn">Dette er ditt private tilbud. Styret ser bare at du har valgt en pakke, ikke innholdet.</Callout>
                    <Button block onClick={() => setConfirm(true)} data-testid="accept-quote">Aksepter tilbudet</Button>
                  </>
                )}
              </>
            )}
            <div className="row"><Button variant="ghost" onClick={() => go(2)}>Tilbake</Button><Button variant="secondary" onClick={() => go(4)}>Neste: følg arbeidet</Button></div>
          </Card>}
          {current === 4 && <Card pad className="stack">
            <SectionHead title="Fremdrift" />
            <Progress pct={p.progressPct} />
            <KV items={[["Prosjekt", `${p.progressPct ?? 0} % · ${p.stage === "kartlegging" ? "kartlegging" : p.stage}`], ["Din bolig", r.productionStatus ? { ikke_startet: "Ikke startet", pagar: "Pågår", ferdig: "Ferdig" }[r.productionStatus] : "Ikke startet"], ["Tilgang", r.accessConfirmed ? `Bekreftet ${formatDate(r.accessConfirmed)}` : "Ikke bekreftet"]]} />
            {!r.accessConfirmed && <Callout tone="warn">Bekreft at håndverker kan få tilgang på dagtid i arbeidsperioden. Uten det kan ikke din bolig planlegges.</Callout>}
            <SectionHead title="Dokumentasjon" />
            <p className="muted small">Ferdig dokumentasjon (bilder, våtromsdokumentasjon, garanti) legges i boligmappen din når arbeidet er ferdig.</p>
            <div><Button variant="ghost" onClick={() => go(3)}>Tilbake</Button></div>
          </Card>}
          {current !== 3 && q && (
            <Card pad className="row" data-testid="resident-quote-mini">
              <div className="grow"><div className="eyebrow">Ditt private tilbud</div><div className="figure sm" data-testid="resident-total">{formatNOK(quoteTotal)}</div></div>
              <Button variant="secondary" size="sm" onClick={() => go(3)}>{q.accepted ? "Se tilbudet" : "Gå til tilbudet"}</Button>
            </Card>
          )}
        </div>
      </div>

      {confirm && (
        <ConfirmModal title="Aksepter tilbudet?" body={<p>Du inngår en avtale med {lookup.supplier(p.supplierIds[0])} om {q ? TIER_LABEL[q.tier].toLowerCase() : "valgt pakke"} for {formatNOK(quoteTotal)} inkl. mva. Borettslaget er ikke part i avtalen.</p>} confirmLabel="Aksepter" pending={accept.pending} onCancel={() => setConfirm(false)} onConfirm={async () => { const res = await accept.run(p.id); setConfirm(false); toast(res ? "Tilbudet er akseptert" : "Kunne ikke akseptere", res ? undefined : "error"); }} />
      )}
    </>
  );
}
