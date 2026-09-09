/**
 * ERA-assistenten: globalt panel som ikke dekker arbeidsflaten på desktop (egen kolonne),
 * fullskjerm på mobil. Kjenner aktivt borettslag, rolle, side og valgt objekt.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useLocation } from "react-router";
import type { AssistantAnswer } from "@/domain/types";
import { useData } from "@/data/provider";
import { suggestionsFor } from "@/data/fixtures/assistant";
import { ROLE_LABEL } from "@/access/roles";
import { Button, Drawer } from "@/components/ui";
import { useToast } from "@/components/toast";

type Selected = { type: string; id: string; label: string } | undefined;
type Turn = { q: string; a?: AssistantAnswer; error?: string };

interface AssistantCtx {
  open: boolean;
  setOpen: (v: boolean) => void;
  ask: (question: string) => void;
  selected: Selected;
  setSelected: (s: Selected) => void;
}

const Ctx = createContext<AssistantCtx | null>(null);

export function AssistantProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Selected>(undefined);
  const [queue, setQueue] = useState<string | null>(null);
  const ask = useCallback((q: string) => {
    setOpen(true);
    setQueue(q);
  }, []);
  const value = useMemo(() => ({ open, setOpen, ask, selected, setSelected }), [open, ask, selected]);
  return (
    <Ctx.Provider value={value}>
      {children}
      <QueueBridge queue={queue} clear={() => setQueue(null)} />
    </Ctx.Provider>
  );
}

/** Videresender spørsmål fra `ask()` til panelet via en liten hendelseskø. */
function QueueBridge({ queue, clear }: { queue: string | null; clear: () => void }) {
  useEffect(() => {
    if (queue) {
      window.dispatchEvent(new CustomEvent("era-ask", { detail: queue }));
      clear();
    }
  }, [queue, clear]);
  return null;
}

export function useAssistant(): AssistantCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAssistant må brukes innenfor AssistantProvider");
  return ctx;
}

/** Sider kaller denne for å fortelle assistenten hva som er valgt. */
export function useAssistantSelection(sel: Selected) {
  const { setSelected } = useAssistant();
  const key = sel ? `${sel.type}:${sel.id}:${sel.label}` : "";
  useEffect(() => {
    setSelected(sel);
    return () => setSelected(undefined);
  }, [key, setSelected]);
}

export function EraAssistantPanel() {
  const { open, setOpen, selected } = useAssistant();
  const { adapter, session } = useData();
  const location = useLocation();
  const toast = useToast();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = useCallback(
    async (q: string) => {
      const question = q.trim();
      if (!question || busy) return;
      setText("");
      setBusy(true);
      setTurns((t) => [...t, { q: question }]);
      try {
        const a = await adapter.askEra(session, question, { tenantId: session.tenantId, role: session.role, page: location.pathname, selected });
        setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, a } : x)));
      } catch (e) {
        setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, error: e instanceof Error ? e.message : "Ukjent feil" } : x)));
      } finally {
        setBusy(false);
      }
    },
    [adapter, session, location.pathname, selected, busy],
  );

  useEffect(() => {
    const h = (e: Event) => void submit((e as CustomEvent<string>).detail);
    window.addEventListener("era-ask", h);
    return () => window.removeEventListener("era-ask", h);
  }, [submit]);

  if (!open) return null;
  const suggestions = suggestionsFor(location.pathname, session.role);

  return (
    <Drawer title="Spør ERA" onClose={() => setOpen(false)} eyebrow="ERA-assistent" footer={
      <form
        className="assist-form"
        onSubmit={(e) => {
          e.preventDefault();
          void submit(text);
        }}
      >
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Still et spørsmål om eiendommen" aria-label="Spørsmål til ERA" />
        <Button type="submit" disabled={busy || !text.trim()}>
          Spør
        </Button>
      </form>
    }>
    <div className="assist" aria-label="ERA-assistent" data-testid="era-assistant">
      <div className="assist-ctx">
        <span>
          Rolle: <b>{ROLE_LABEL[session.role]}</b>
        </span>
        <span>
          Side: <b>{location.pathname === "/" ? "Oversikt" : location.pathname}</b>
        </span>
        {selected && (
          <span>
            Valgt: <b>{selected.label}</b>
          </span>
        )}
      </div>
      <div className="assist-body">
        {turns.length === 0 && (
          <>
            <p className="small muted">ERA svarer med konklusjon først, deretter grunnlag, kilder, antakelser og hva som mangler. ERA utfører ingen kostnadsdrivende, juridiske eller eksterne handlinger uten at du godkjenner.</p>
            <div className="suggest">
              {suggestions.map((s) => (
                <button key={s} onClick={() => void submit(s)}>
                  {s}
                </button>
              ))}
            </div>
          </>
        )}
        {turns.map((t, i) => (
          <div key={i} className="stack">
            <div className="q">{t.q}</div>
            {t.a ? <Answer a={t.a} onAction={(label) => toast(`Opprettet: ${label}`)} /> : t.error ? <div className="callout danger">{t.error}</div> : <div className="thinking" aria-label="ERA arbeider"><i /><i /><i /></div>}
          </div>
        ))}
        {turns.length > 0 && !busy && (
          <div className="suggest">
            {suggestions.slice(0, 2).map((s) => (
              <button key={s} onClick={() => void submit(s)}>
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
    </Drawer>
  );
}

/** Bunnfelt på desktop: ERA som felt, ikke kolonne. Svaret åpner som lag. */
export function EraBar() {
  const { ask, setOpen } = useAssistant();
  const { session } = useData();
  const location = useLocation();
  const [text, setText] = useState("");
  const hint = suggestionsFor(location.pathname, session.role)[0];
  return (
    <form
      className="erabar"
      onSubmit={(e) => {
        e.preventDefault();
        if (text.trim()) {
          ask(text.trim());
          setText("");
        }
      }}
    >
      <button type="button" className="erabar-label" onClick={() => setOpen(true)} data-testid="ask-era">
        Spør ERA
      </button>
      {hint && (
        <button type="button" className="erabar-hint" onClick={() => ask(hint)}>
          Forslag: «{hint}»
        </button>
      )}
      <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Still et spørsmål om eiendommen" aria-label="Spørsmål til ERA" />
      <Button type="submit" size="sm" disabled={!text.trim()}>
        Spør
      </Button>
    </form>
  );
}

function Answer({ a, onAction }: { a: AssistantAnswer; onAction: (label: string) => void }) {
  return (
    <div className="a" data-testid="era-answer">
      <p className="concl">{a.conclusion}</p>
      {a.reasoning.length > 0 && (
        <div>
          <h4>Begrunnelse</h4>
          <ul>
            {a.reasoning.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
      <div>
        <h4>Kilder</h4>
        {a.sources.length === 0 ? (
          <p className="muted small">Ingen kilder. Svaret bygger ikke på registrerte data.</p>
        ) : (
          <ul data-testid="era-sources">
            {a.sources.map((s, i) => (
              <li key={i}>{s.documentId ? <Link to={`/dokumenter?dok=${s.documentId}`}>{s.label}</Link> : s.link ? <Link to={s.link}>{s.label}</Link> : s.label}</li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h4>Antakelser</h4>
        {a.assumptions.length === 0 ? (
          <p className="muted small">Ingen antakelser.</p>
        ) : (
          <ul data-testid="era-assumptions">
            {a.assumptions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h4>Mangler</h4>
        {a.missing.length === 0 ? (
          <p className="muted small">Ingen kjente hull.</p>
        ) : (
          <ul>
            {a.missing.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <h4>Foreslått neste handling</h4>
        <p>{a.nextAction}</p>
      </div>
      {a.actions.length > 0 && (
        <div className="acts">
          {a.actions.map((x, i) =>
            x.to ? (
              <Link key={i} to={x.to} className="btn secondary sm">
                {x.label}
              </Link>
            ) : (
              <Button key={i} variant="secondary" size="sm" onClick={() => onAction(x.label)}>
                {x.label}
              </Button>
            ),
          )}
        </div>
      )}
    </div>
  );
}
