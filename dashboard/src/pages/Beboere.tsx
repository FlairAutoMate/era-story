/** Beboeroversikt og CommunicationComposer. Kontaktinfo krever `residents:contact`. */
import { useEffect, useMemo, useState } from "react";
import { useData, useMutation, useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import type { MessageSegment } from "@/domain/types";
import { formatDate, formatDateTime, plural } from "@/lib/format";
import { useUrlParam, useUrlParams } from "@/lib/urlState";
import { PageHead } from "@/shell/AppShell";
import { useLookup } from "@/components/domain";
import { Badge, Button, Callout, Card, Drawer, EmptyState, ErrorState, KV, Skeleton, Tabs } from "@/components/ui";
import { useToast } from "@/components/toast";

const CLIP = 12;

export function Beboere() {
  const session = useSession();
  const [all, setAll] = useState(false);
  const lookup = useLookup();
  const [params, patch] = useUrlParams();
  const [tab, setTab] = useUrlParam("fane", "beboere");
  const [msgList, setMsgList] = useUrlParam("mvisning");
  const residents = useQuery((a, s) => a.listResidents(s));
  const units = useQuery((a, s) => a.listUnits(s));
  const messages = useQuery((a, s) => a.listMessages(s));
  const q = params.get("q") ?? "";
  const bygg = params.get("bygg") ?? "";
  const compose = params.get("ny") === "1";
  const bolig = params.get("bolig") ?? "";
  const canContact = can(session.role, "residents:contact");

  const rows = useMemo(() => {
    const unitOf = (id: string) => units.data?.find((u) => u.id === id);
    return (residents.data ?? [])
      .map((r) => ({ r, u: unitOf(r.unitId) }))
      .filter(({ r, u }) => (!q || `${r.name} ${u?.label ?? ""}`.toLowerCase().includes(q.toLowerCase())) && (!bygg || u?.buildingId === bygg) && (!bolig || r.unitId === bolig))
      .sort((a, b) => (a.u?.entranceId ?? "").localeCompare(b.u?.entranceId ?? "") || (a.u?.label ?? "").localeCompare(b.u?.label ?? ""));
  }, [residents.data, units.data, q, bygg, bolig]);

  return (
    <>
      <PageHead
        title="Beboere"
        meta={residents.data ? [`${residents.data.length} beboere`, `${residents.data.filter((r) => r.hasApp).length} bruker ERA-appen`, `${residents.data.filter((r) => !r.hasApp).length} nås bare via oppslag eller brev`] : []}
        actions={
          <>
            {tab === "meldinger" && messages.data && messages.data.length > 0 && (
              <Button variant={msgList ? "secondary" : "primary"} onClick={() => setMsgList(msgList ? null : "1")} data-testid="toggle-msg-list">
                {msgList ? "Vis kort" : `Vis liste (${messages.data.length})`}
              </Button>
            )}
            {can(session.role, "messages:send") && <Button onClick={() => patch({ ny: "1" })} data-testid="new-message">Ny melding</Button>}
          </>
        }
      />
      <Tabs label="Visning" value={tab} onChange={(v) => setTab(v)} items={[{ id: "beboere", label: "Beboere", count: residents.data?.length }, { id: "meldinger", label: "Meldinger", count: messages.data?.length }]} />
      {tab === "beboere" ? (
        <>
          <div className="filters">
            <input type="search" value={q} onChange={(e) => patch({ q: e.target.value })} placeholder="Søk på navn eller bolig" aria-label="Søk beboere" />
            <select value={bygg} onChange={(e) => patch({ bygg: e.target.value })} aria-label="Bygg">
              <option value="">Alle bygg</option>
              {lookup.buildings.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
            {bolig && <Button variant="ghost" size="sm" onClick={() => patch({ bolig: null })}>Vis alle boliger</Button>}
          </div>
          {!canContact && <Callout>Kontaktinformasjon vises bare for styreleder. Du ser navn, bolig og rolle.</Callout>}
          {residents.status === "error" ? <ErrorState error={residents.error} retry={residents.reload} /> : !residents.data ? <Skeleton lines={8} /> : rows.length === 0 ? <EmptyState title="Ingen beboere funnet" what="Beboerlisten hentes fra andelseierregisteret og ERA-appen." /> : (
            <>
              <div className="fill desktop-only" style={{ marginTop: 12 }}>
              <div className="table-wrap">
                <table className="tbl" data-testid="residents-table">
                  <thead>
                    <tr>
                      <th>Navn</th>
                      <th>Bolig</th>
                      <th>Oppgang</th>
                      <th>Rolle</th>
                      <th>ERA-app</th>
                      {canContact && <th>E-post</th>}
                      {canContact && <th>Telefon</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {(all ? rows : rows.slice(0, CLIP)).map(({ r, u }) => (
                      <tr key={r.id}>
                        <td className="primary">{r.name}</td>
                        <td className="mono">{u?.label}</td>
                        <td>{lookup.entrance(u?.entranceId)}</td>
                        <td>{{ eier: "Eier", leietaker: "Leietaker", styremedlem: "Styremedlem", styreleder: "Styreleder" }[r.role]}</td>
                        <td>{r.hasApp ? <Badge tone="done" plain>Ja</Badge> : <Badge tone="neutral" plain>Nei</Badge>}</td>
                        {canContact && <td>{r.email ?? <span className="muted">Ikke registrert</span>}</td>}
                        {canContact && <td className="mono">{r.phone ?? <span className="muted">Ikke registrert</span>}</td>}
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
              <div className="cardlist mobile-only" style={{ marginTop: 12 }}>
                {rows.map(({ r, u }) => (
                  <div key={r.id} className="item">
                    <span className="t">{r.name}</span>
                    <span className="m"><span>{u?.label} · {lookup.entrance(u?.entranceId)}</span><span>{r.hasApp ? "ERA-app" : "Uten app"}</span>{canContact && r.phone && <span>{r.phone}</span>}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      ) : messages.status === "error" ? (
        <div style={{ marginTop: 14 }}><ErrorState error={messages.error} retry={messages.reload} /></div>
      ) : !messages.data ? (
        <div style={{ marginTop: 14 }}><Skeleton lines={6} /></div>
      ) : messages.data.length === 0 ? (
        <div style={{ marginTop: 14 }}><EmptyState title="Ingen meldinger" what="Meldinger til hele borettslaget, ett bygg, en oppgang, berørte boliger eller én beboer, alltid knyttet til en sak eller et prosjekt." /></div>
      ) : msgList ? (
        <>
          <div className="fill desktop-only" style={{ marginTop: 14 }}>
            <div className="table-wrap">
              <table className="tbl" data-testid="messages-table">
                <thead>
                  <tr>
                    <th>Melding</th>
                    <th>Status</th>
                    <th>Sendt</th>
                    <th>Mottakere</th>
                    <th>Svarfrist</th>
                    <th>Oppfølging</th>
                  </tr>
                </thead>
                <tbody>
                  {messages.data.map((m) => (
                    <tr key={m.id}>
                      <td>
                        <span className="primary">{m.subject}</span>
                        <span className="sub">{m.body}</span>
                      </td>
                      <td><Badge tone={m.status === "sendt" ? "done" : m.status === "planlagt" ? "planned" : "neutral"}>{{ sendt: "Sendt", planlagt: "Planlagt", utkast: "Utkast" }[m.status]}</Badge></td>
                      <td className="nowrap">{m.sentAt ? formatDateTime(m.sentAt) : <span className="muted">Ikke sendt</span>}</td>
                      <td className="nowrap">{segmentLabel(m.segment, lookup)} · {plural(m.recipients, "mottaker", "mottakere")}</td>
                      <td className="nowrap">{m.replyDeadline ? formatDate(m.replyDeadline) : <span className="muted">Ingen</span>}</td>
                      <td className="wrap">{m.stats ? `Levert ${m.stats.delivered} · lest ${m.stats.read} · bekreftet ${m.stats.confirmed}` : <span className="muted">Ikke sendt</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="cardlist mobile-only" style={{ marginTop: 14 }}>
            {messages.data.map((m) => (
              <div key={m.id} className="item">
                <span className="t">{m.subject}</span>
                <span className="m">
                  <Badge tone={m.status === "sendt" ? "done" : m.status === "planlagt" ? "planned" : "neutral"}>{{ sendt: "Sendt", planlagt: "Planlagt", utkast: "Utkast" }[m.status]}</Badge>
                  <span>{plural(m.recipients, "mottaker", "mottakere")}</span>
                </span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="stack" style={{ marginTop: 14 }}>
          {messages.data.map((m) => (
            <Card key={m.id} pad className="stack">
              <div className="row">
                <Badge tone={m.status === "sendt" ? "done" : m.status === "planlagt" ? "planned" : "neutral"}>{{ sendt: "Sendt", planlagt: "Planlagt", utkast: "Utkast" }[m.status]}</Badge>
                <span className="small muted">{m.sentAt ? formatDateTime(m.sentAt) : "Ikke sendt"} · {segmentLabel(m.segment, lookup)} · {plural(m.recipients, "mottaker", "mottakere")}</span>
              </div>
              <h3>{m.subject}</h3>
              <p className="small">{m.body}</p>
              <KV items={[["Knyttet til", m.linkedTo ? `${m.linkedTo.type} ${m.linkedTo.id}` : "Ingen"], ["Svarfrist", m.replyDeadline ? formatDate(m.replyDeadline) : "Ingen"], ["Bekreftelse", m.requiresConfirmation ? "Kreves" : "Nei"], ["Status", m.stats ? `Levert ${m.stats.delivered} · lest ${m.stats.read} · bekreftet ${m.stats.confirmed} · svart ${m.stats.replied}` : "Ikke sendt"]]} />
            </Card>
          ))}
        </div>
      )}
      {compose && <CommunicationComposer onClose={() => patch({ ny: null, prosjekt: null, segment: null })} presetProjectId={params.get("prosjekt") ?? undefined} presetSegment={(params.get("segment") as MessageSegment["kind"] | null) ?? undefined} />}
    </>
  );
}

function segmentLabel(seg: MessageSegment, lookup: ReturnType<typeof useLookup>): string {
  switch (seg.kind) {
    case "alle":
      return "Hele borettslaget";
    case "bygg":
      return lookup.building(seg.buildingId) ?? "Bygg";
    case "oppgang":
      return lookup.entrance(seg.entranceId) ?? "Oppgang";
    case "berorte":
      return "Berørte boliger";
    case "beboer":
      return "Én beboer";
  }
}

/** CommunicationComposer: segment, forhåndsvisning, vedlegg, svarfrist, bekreftelse, påmelding. ERA foreslår tekst, styret godkjenner. */
export function CommunicationComposer({ onClose, presetProjectId, presetSegment }: { onClose: () => void; presetProjectId?: string; presetSegment?: MessageSegment["kind"] }) {
  const toast = useToast();
  const lookup = useLookup();
  const { adapter, session } = useData();
  const tenant = useQuery((a, s) => a.getTenant(s));
  const projects = useQuery((a, s) => a.listProjects(s));
  const residents = useQuery((a, s) => a.listResidents(s));
  const [kind, setKind] = useState<MessageSegment["kind"]>(presetSegment ?? (presetProjectId ? "berorte" : "alle"));
  const [buildingId, setBuildingId] = useState("");
  const [entranceId, setEntranceId] = useState("");
  const [projectId, setProjectId] = useState(presetProjectId ?? "");
  const [residentId, setResidentId] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [deadline, setDeadline] = useState("");
  const [confirmReq, setConfirmReq] = useState(true);
  const [signup, setSignup] = useState(false);
  const [slots, setSlots] = useState("Tirsdag 08–12, Tirsdag 12–16, Onsdag 08–12");
  const [attachments, setAttachments] = useState<string[]>([]);
  const [preview, setPreview] = useState(false);
  const [count, setCount] = useState<number | null>(null);

  const segment: MessageSegment = useMemo(() => {
    switch (kind) {
      case "alle": return { kind };
      case "bygg": return { kind, buildingId };
      case "oppgang": return { kind, entranceId };
      case "berorte": return { kind, projectId };
      case "beboer": return { kind, residentId };
    }
  }, [kind, buildingId, entranceId, projectId, residentId]);

  useEffect(() => {
    let alive = true;
    adapter.countRecipients(session, segment).then((n) => alive && setCount(n)).catch(() => alive && setCount(null));
    return () => { alive = false; };
  }, [adapter, session, segment]);

  const send = useMutation((a, s, when: "na" | "utkast") => a.sendMessage(s, { subject, body, segment, linkedTo: projectId ? { type: "prosjekt", id: projectId } : undefined, replyDeadline: deadline || undefined, requiresConfirmation: confirmReq, signup: signup ? { label: "Velg tidspunkt for tilgang", slots: slots.split(",").map((s) => s.trim()).filter(Boolean) } : undefined, attachments }, when));

  const project = projects.data?.find((p) => p.id === projectId);
  const suggest = () => {
    if (project?.id === "prj-soil") {
      setSubject("Påminnelse: svar på kartleggingen før 15. september");
      setBody("Borettslaget skal skifte soilrørene i alle boliger i 2027. Vi mangler fortsatt svar fra din bolig. Svar på de fire spørsmålene og last opp bilder av rørsjakten i ERA-appen innen 15. september. Det tar under fem minutter, og svaret avgjør hvordan arbeidet i din bolig planlegges.");
      setDeadline("2026-09-15");
    } else if (project?.id === "prj-fasade") {
      setSubject("Stillas flyttes til bygg B fra 28. september");
      setBody("Stillas monteres rundt bygg B mandag 28. september. Balkonger må ryddes innen søndag 27. Arbeidet varer til midten av november. Vi ber om at vinduer holdes lukket når det males.");
      setDeadline("");
    } else {
      setSubject(project ? `Informasjon om ${project.title.toLowerCase()}` : "Informasjon fra styret");
      setBody(project ? `${project.purpose} Styret informerer om videre fremdrift så snart det er avklart.` : "Styret informerer om ...");
    }
    toast("ERA har foreslått tekst. Rediger og godkjenn før utsendelse.");
  };

  const valid = subject.trim() && body.trim() && (kind !== "bygg" || buildingId) && (kind !== "oppgang" || entranceId) && (kind !== "berorte" || projectId) && (kind !== "beboer" || residentId);

  return (
    <Drawer
      title="Ny melding til beboere"
      sub={count !== null ? plural(count, "mottaker", "mottakere") : "Beregner mottakere …"}
      onClose={onClose}
      wide
      footer={
        <>
          <Button disabled={!valid || send.pending} data-testid="send-message" onClick={async () => { const r = await send.run("na"); if (r) { toast(`Melding sendt til ${plural(r.recipients, "mottaker", "mottakere")}`); onClose(); } else toast("Kunne ikke sende", "error"); }}>
            {send.pending ? "Sender …" : "Send nå"}
          </Button>
          <Button variant="secondary" disabled={!subject.trim() || send.pending} onClick={async () => { const r = await send.run("utkast"); if (r) { toast("Lagret som utkast"); onClose(); } }}>
            Lagre utkast
          </Button>
          <Button variant="ghost" onClick={() => setPreview((p) => !p)}>{preview ? "Rediger" : "Forhåndsvis"}</Button>
        </>
      }
    >
      {preview ? (
        <div className="stack">
          <Callout>Slik ser meldingen ut for mottakeren i ERA-appen.</Callout>
          <Card pad className="stack">
            <div className="eyebrow">{tenant.data?.name ?? "Borettslaget"} · Styret</div>
            <h2>{subject || "(uten emne)"}</h2>
            <p style={{ whiteSpace: "pre-wrap" }}>{body}</p>
            {deadline && <p className="small"><strong>Svarfrist:</strong> {formatDate(deadline)}</p>}
            {confirmReq && <Button variant="secondary" size="sm" disabled>Bekreft at du har lest</Button>}
            {signup && <KV items={[["Velg tidspunkt", slots]]} />}
            {attachments.length > 0 && <p className="small muted">Vedlegg: {attachments.join(", ")}</p>}
          </Card>
        </div>
      ) : (
        <div className="stack">
          <div className="field">
            <span className="lbl">Mottakere</span>
            <div className="chips" role="group" aria-label="Mottakersegment">
              {([["alle", "Hele borettslaget"], ["bygg", "Ett bygg"], ["oppgang", "En oppgang"], ["berorte", "Berørte boliger"], ["beboer", "Én beboer"]] as [MessageSegment["kind"], string][]).map(([k, l]) => (
                <button key={k} className="chip" aria-pressed={kind === k} onClick={() => setKind(k)} data-testid={`segment-${k}`}>{l}</button>
              ))}
            </div>
          </div>
          {kind === "bygg" && <div className="field"><label htmlFor="m-b">Bygg</label><select id="m-b" value={buildingId} onChange={(e) => setBuildingId(e.target.value)}><option value="">Velg bygg</option>{lookup.buildings.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}</select></div>}
          {kind === "oppgang" && <div className="field"><label htmlFor="m-e">Oppgang</label><select id="m-e" value={entranceId} onChange={(e) => setEntranceId(e.target.value)}><option value="">Velg oppgang</option>{lookup.buildings.flatMap((b) => b.entrances).map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}</select></div>}
          {kind === "berorte" && <div className="field"><label htmlFor="m-p">Prosjekt</label><select id="m-p" value={projectId} onChange={(e) => setProjectId(e.target.value)}><option value="">Velg prosjekt</option>{(projects.data ?? []).map((p) => <option key={p.id} value={p.id}>{p.title} ({p.affectedUnitIds.length} boliger)</option>)}</select></div>}
          {kind === "beboer" && <div className="field"><label htmlFor="m-r">Beboer</label><select id="m-r" value={residentId} onChange={(e) => setResidentId(e.target.value)}><option value="">Velg beboer</option>{(residents.data ?? []).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}</select></div>}
          {kind !== "berorte" && (
            <div className="field"><label htmlFor="m-link">Knytt til prosjekt (valgfritt)</label><select id="m-link" value={projectId} onChange={(e) => setProjectId(e.target.value)}><option value="">Ingen</option>{(projects.data ?? []).map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></div>
          )}
          <div className="row"><Button variant="secondary" size="sm" era onClick={suggest} data-testid="suggest-text">La ERA foreslå tekst</Button><span className="small muted">Du redigerer og godkjenner før utsendelse.</span></div>
          <div className="field"><label htmlFor="m-s">Emne</label><input id="m-s" value={subject} onChange={(e) => setSubject(e.target.value)} /></div>
          <div className="field"><label htmlFor="m-body">Melding</label><textarea id="m-body" value={body} onChange={(e) => setBody(e.target.value)} /></div>
          <div className="grid cols-2">
            <div className="field"><label htmlFor="m-d">Svarfrist</label><input id="m-d" type="date" value={deadline} onChange={(e) => setDeadline(e.target.value)} /></div>
            <div className="field"><span className="lbl">Vedlegg</span><div className="row"><Button variant="secondary" size="sm" onClick={() => setAttachments((a) => [...a, `Vedlegg ${a.length + 1}.pdf`])}>Legg til vedlegg</Button><span className="small muted">{attachments.length ? attachments.join(", ") : "Ingen"}</span></div></div>
          </div>
          <label className="check"><input type="checkbox" checked={confirmReq} onChange={(e) => setConfirmReq(e.target.checked)} /> Be om bekreftelse på mottak</label>
          <label className="check"><input type="checkbox" checked={signup} onChange={(e) => setSignup(e.target.checked)} /> Påmelding eller valg av tidspunkt</label>
          {signup && <div className="field"><label htmlFor="m-slots">Tidspunkter (kommaseparert)</label><input id="m-slots" value={slots} onChange={(e) => setSlots(e.target.value)} /></div>}
          {send.error && <Callout tone="danger">{send.error.message}</Callout>}
        </div>
      )}
    </Drawer>
  );
}

