import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router";
import { useQuery, useSession } from "@/data/provider";
import { can } from "@/access/roles";
import { IconSearch } from "@/components/icons";

type Hit = { kind: string; label: string; to: string };

/** Global søk/kommando: søker på tvers av saker, tiltak, prosjekter, dokumenter og boliger. */
export function GlobalSearch() {
  const session = useSession();
  const board = can(session.role, "board:read");
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const index = useQuery(async (a, s) => {
    if (!board) return [] as Hit[];
    const [issues, maint, projects, docs, units] = await Promise.all([a.listIssues(s), a.listMaintenance(s), a.listProjects(s), a.listDocuments(s), a.listUnits(s)]);
    return [
      ...issues.map((i) => ({ kind: "Avvik", label: `${i.ref} ${i.title}`, to: `/saker?sak=${i.id}` })),
      ...maint.map((m) => ({ kind: "Tiltak", label: m.title, to: `/vedlikehold?tiltak=${m.id}` })),
      ...projects.map((p) => ({ kind: "Prosjekt", label: p.title, to: `/prosjekter/${p.id}` })),
      ...docs.map((d) => ({ kind: "Dokument", label: d.title, to: `/dokumenter?dok=${d.id}` })),
      ...units.map((u) => ({ kind: "Bolig", label: `${u.label} (${u.entranceId.replace("e-", "oppgang ")})`, to: `/beboere?bolig=${u.id}` })),
    ] as Hit[];
  }, [board]);

  const hits = useMemo(() => {
    const s = q.trim().toLowerCase();
    if (!s || !index.data) return [];
    return index.data.filter((h) => h.label.toLowerCase().includes(s)).slice(0, 8);
  }, [q, index.data]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    const onClick = (e: MouseEvent) => !ref.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onClick);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onClick);
    };
  }, []);

  if (!board) return null;
  return (
    <div className="search" ref={ref}>
      <IconSearch />
      <input
        ref={inputRef}
        type="search"
        value={q}
        onChange={(e) => {
          setQ(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => e.key === "Escape" && setOpen(false)}
        placeholder="Søk i saker, tiltak, prosjekter, dokumenter og boliger"
        aria-label="Søk"
        aria-expanded={open && hits.length > 0}
      />
      <kbd aria-hidden="true">Ctrl K</kbd>
      {open && q.trim() && (
        <div className="search-results" role="listbox">
          {hits.length === 0 ? (
            <div className="muted small" style={{ padding: 10 }}>
              Ingen treff på «{q}».
            </div>
          ) : (
            hits.map((h) => (
              <Link key={h.to} to={h.to} role="option" onClick={() => { setOpen(false); setQ(""); }}>
                <span className="kind">{h.kind}</span>
                <div>{h.label}</div>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
}
