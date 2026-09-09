/**
 * Tema: system (følger enhetens innstilling), lys eller mørk. Valget lagres lokalt og settes
 * som `data-theme` på <html>, som app.css bruker til å overstyre `prefers-color-scheme`.
 */
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

export type ThemeChoice = "system" | "light" | "dark";
const KEY = "era-theme";

function readStored(): ThemeChoice {
  try {
    const v = localStorage.getItem(KEY);
    return v === "light" || v === "dark" ? v : "system";
  } catch {
    return "system";
  }
}

interface ThemeCtx {
  theme: ThemeChoice;
  setTheme: (t: ThemeChoice) => void;
}
const Ctx = createContext<ThemeCtx | null>(null);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<ThemeChoice>(readStored);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(KEY, theme);
    } catch {
      /* privat modus */
    }
  }, [theme]);

  const setTheme = useCallback((t: ThemeChoice) => setThemeState(t), []);
  const value = useMemo(() => ({ theme, setTheme }), [theme, setTheme]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useTheme(): ThemeCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useTheme må brukes innenfor ThemeProvider");
  return ctx;
}

const OPTIONS: [ThemeChoice, string][] = [
  ["system", "System"],
  ["light", "Lys"],
  ["dark", "Mørk"],
];

/** Segmentert bryter, samme mønster som mobilens visningsvalg. Brukes i lyse lag (drawer). */
export function ThemeToggle({ label = "Tema" }: { label?: string }) {
  const { theme, setTheme } = useTheme();
  return (
    <div className="field">
      <span className="lbl">{label}</span>
      <div className="seg" role="group" aria-label={label}>
        {OPTIONS.map(([id, l]) => (
          <button key={id} type="button" aria-pressed={theme === id} onClick={() => setTheme(id)} data-testid={`theme-${id}`}>
            {l}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Samme bryter, stylet for den alltid-mørke sidemenyen. */
export function ThemeToggleNav() {
  const { theme, setTheme } = useTheme();
  return (
    <div className="seg-nav" role="group" aria-label="Tema">
      {OPTIONS.map(([id, l]) => (
        <button key={id} type="button" aria-pressed={theme === id} onClick={() => setTheme(id)} data-testid={`theme-${id}`}>
          {l}
        </button>
      ))}
    </div>
  );
}
