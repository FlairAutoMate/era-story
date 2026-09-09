/**
 * DataProvider: én adapter-instans og én sesjon for hele appen. Komponentene bruker `useQuery`
 * for lesing og `useAdapter()` for mutasjoner. Ingen komponent importerer fixtures direkte.
 *
 * Demo-styring via URL ved første last (kun fixture-adapter):
 *   ?rolle=styreleder|styremedlem|forretningsforer|vaktmester|beboer|leverandor|era_admin
 *   ?tenant=perrongen|solvang
 *   ?tilstand=tom|feil|treg
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import type { Role, Session } from "@/domain/types";
import { ALL_ROLES } from "@/access/roles";
import type { DataAdapter } from "./adapters";
import { createFixtureAdapter, type FixtureOptions } from "./fixtureAdapter";

/** Demo-brukere per rolle. En ekte backend leverer sesjonen fra innlogging. */
const DEMO_SESSIONS: Record<Role, Omit<Session, "tenantId">> = {
  styreleder: { userId: "p-kari", name: "Kari Nordvik", role: "styreleder" },
  styremedlem: { userId: "p-jonas", name: "Jonas Berge", role: "styremedlem" },
  forretningsforer: { userId: "p-sigrid", name: "Sigrid Foss", role: "forretningsforer" },
  vaktmester: { userId: "p-rune", name: "Rune Skog", role: "vaktmester" },
  beboer: { userId: "p-mette", name: "Mette Larsen", role: "beboer", unitId: "u-4-H0301" },
  leverandor: { userId: "p-erik", name: "Erik Moen", role: "leverandor", supplierId: "s-moen" },
  era_admin: { userId: "p-era", name: "ERA-administrator", role: "era_admin" },
};

interface DataContextValue {
  adapter: DataAdapter;
  session: Session;
  setRole: (role: Role) => void;
  setTenant: (tenantId: string) => void;
  demoMode: FixtureOptions["mode"];
  /** Endres ved hver mutasjon slik at spørringer kan lastes på nytt. */
  version: number;
  invalidate: () => void;
}

const DataContext = createContext<DataContextValue | null>(null);

function readInitial(): { role: Role; tenantId: string; mode: FixtureOptions["mode"] } {
  const params = new URLSearchParams(window.location.search);
  const stored = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("era-demo-session") ?? "null") as { role?: Role; tenantId?: string } | null;
    } catch {
      return null;
    }
  })();
  const roleParam = params.get("rolle");
  const role = ALL_ROLES.includes(roleParam as Role) ? (roleParam as Role) : (stored?.role ?? "styreleder");
  const tenantId = params.get("tenant") ?? stored?.tenantId ?? "perrongen";
  const modeParam = params.get("tilstand");
  const mode = modeParam === "tom" || modeParam === "feil" || modeParam === "treg" ? modeParam : "normal";
  return { role, tenantId, mode };
}

export function DataProvider({ children, adapter: given }: { children: ReactNode; adapter?: DataAdapter }) {
  const initial = useMemo(readInitial, []);
  const adapter = useMemo(() => given ?? createFixtureAdapter({ mode: initial.mode }), [given, initial.mode]);
  const [role, setRoleState] = useState<Role>(initial.role);
  const [tenantId, setTenantState] = useState(initial.tenantId);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    try {
      sessionStorage.setItem("era-demo-session", JSON.stringify({ role, tenantId }));
    } catch {
      /* privat modus */
    }
  }, [role, tenantId]);

  const session = useMemo<Session>(() => ({ ...DEMO_SESSIONS[role], tenantId }), [role, tenantId]);
  const invalidate = useCallback(() => setVersion((v) => v + 1), []);
  const value = useMemo<DataContextValue>(
    () => ({ adapter, session, setRole: setRoleState, setTenant: setTenantState, demoMode: initial.mode, version, invalidate }),
    [adapter, session, initial.mode, version, invalidate],
  );
  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
}

export function useData(): DataContextValue {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData må brukes innenfor DataProvider");
  return ctx;
}

export function useSession(): Session {
  return useData().session;
}

export type QueryState<T> = { status: "loading"; data?: T } | { status: "error"; error: Error; data?: T } | { status: "ready"; data: T };

/**
 * Enkel spørrings-hook: laster på mount, ved sesjonsbytte og ved `invalidate()`.
 * Beholder forrige data under omlasting så tabeller ikke blinker.
 */
export function useQuery<T>(fn: (adapter: DataAdapter, session: Session) => Promise<T>, deps: unknown[] = []): QueryState<T> & { reload: () => void } {
  const { adapter, session, version } = useData();
  const [state, setState] = useState<QueryState<T>>({ status: "loading" });
  const [tick, setTick] = useState(0);
  const fnRef = useRef(fn);
  fnRef.current = fn;
  const depKey = JSON.stringify(deps);

  useEffect(() => {
    let alive = true;
    setState((s) => ({ status: "loading", data: s.data }));
    fnRef
      .current(adapter, session)
      .then((data) => alive && setState({ status: "ready", data }))
      .catch((error: unknown) => alive && setState((s) => ({ status: "error", error: error instanceof Error ? error : new Error(String(error)), data: s.data })));
    return () => {
      alive = false;
    };
  }, [adapter, session, version, tick, depKey]);

  const reload = useCallback(() => setTick((t) => t + 1), []);
  return { ...state, reload };
}

/** Kjør en mutasjon og last spørringer på nytt. Returnerer status for knappetilstander. */
export function useMutation<A extends unknown[], R>(fn: (adapter: DataAdapter, session: Session, ...args: A) => Promise<R>) {
  const { adapter, session, invalidate } = useData();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const run = useCallback(
    async (...args: A): Promise<R | undefined> => {
      setPending(true);
      setError(null);
      try {
        const r = await fn(adapter, session, ...args);
        invalidate();
        return r;
      } catch (e) {
        setError(e instanceof Error ? e : new Error(String(e)));
        return undefined;
      } finally {
        setPending(false);
      }
    },
    [adapter, session, fn, invalidate],
  );
  return { run, pending, error };
}
