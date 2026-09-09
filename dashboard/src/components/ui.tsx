/**
 * Globale UI-primitiver for ERA-dashboardet. Én fil for å holde bundle og API lite.
 */
import { useEffect, useId, useRef, type ReactNode } from "react";
import { Link } from "react-router";
import type { Confidence } from "@/domain/types";
import { CONFIDENCE_LABEL, type Tone } from "@/lib/labels";
import { IconClose } from "./icons";

/* ---------- Badges ---------- */
export function Badge({ tone = "neutral", children, plain }: { tone?: Tone; children: ReactNode; plain?: boolean }) {
  return <span className={`badge ${tone}${plain ? " plain" : ""}`}>{children}</span>;
}

/** DataConfidenceBadge: skiller bekreftede fakta, ERA-forslag, antakelser og manglende grunnlag. */
export function ConfidenceBadge({ value, title }: { value: Confidence; title?: string }) {
  return (
    <span className={`confidence ${value}`} title={title ?? CONFIDENCE_LABEL[value]}>
      {CONFIDENCE_LABEL[value]}
    </span>
  );
}

/** MissingDataState (inline): aldri vis falske nullverdier. */
export function Missing({ children = "Ikke registrert" }: { children?: ReactNode }) {
  return <span className="missing">{children}</span>;
}

/* ---------- Knapper ---------- */
type BtnVariant = "primary" | "secondary" | "ghost" | "danger";
type BtnProps = {
  variant?: BtnVariant;
  size?: "sm" | "md" | "lg";
  block?: boolean;
  era?: boolean;
  children: ReactNode;
  className?: string;
};

export function Button({ variant = "primary", size = "md", block, era, children, className = "", ...rest }: BtnProps & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const cls = ["btn", variant !== "primary" ? variant : "", size !== "md" ? size : "", block ? "block" : "", era ? "era" : "", className].filter(Boolean).join(" ");
  return (
    <button type="button" className={cls} {...rest}>
      {children}
    </button>
  );
}

export function LinkButton({ to, variant = "primary", size = "md", block, era, children, className = "" }: BtnProps & { to: string }) {
  const cls = ["btn", variant !== "primary" ? variant : "", size !== "md" ? size : "", block ? "block" : "", era ? "era" : "", className].filter(Boolean).join(" ");
  return (
    <Link to={to} className={cls}>
      {children}
    </Link>
  );
}

/** Funksjon som ikke er klar. Ingen døde knapper: dette er tydelig deaktivert. */
export function ComingLater({ children = "Kommer senere" }: { children?: ReactNode }) {
  return (
    <span className="coming" aria-disabled="true">
      {children}
    </span>
  );
}

/* ---------- Kort ---------- */
export function Card({ children, className = "", pad, flat, ...rest }: { children: ReactNode; className?: string; pad?: boolean; flat?: boolean } & React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div {...rest} className={`card${pad ? " pad" : ""}${flat ? " flat" : ""} ${className}`}>
      {children}
    </div>
  );
}

export function CardHead({ title, right, id }: { title: ReactNode; right?: ReactNode; id?: string }) {
  return (
    <div className="card-head">
      <h2 id={id}>{title}</h2>
      {right && <div className="right">{right}</div>}
    </div>
  );
}

export function SectionHead({ title, right, count }: { title: ReactNode; right?: ReactNode; count?: number }) {
  return (
    <div className="section-head">
      <h2>
        {title}
        {count !== undefined && <span className="muted"> · {count}</span>}
      </h2>
      {right && <div className="right">{right}</div>}
    </div>
  );
}

/* ---------- Tilstander ---------- */
export function EmptyState({ title, what, why, action }: { title: string; what: string; why?: string; action?: ReactNode }) {
  return (
    <div className="state" role="status">
      <h3>{title}</h3>
      <p>{what}</p>
      {why && <p>{why}</p>}
      {action && <div className="actions">{action}</div>}
    </div>
  );
}

export function ErrorState({ error, retry }: { error: Error; retry?: () => void }) {
  return (
    <div className="state error" role="alert">
      <h3>Kunne ikke hente data</h3>
      <p>{error.message}</p>
      <p>Resten av siden fungerer. Prøv igjen om et øyeblikk.</p>
      {retry && (
        <div className="actions">
          <Button variant="secondary" onClick={retry}>
            Prøv igjen
          </Button>
        </div>
      )}
    </div>
  );
}

export function DeniedState({ what = "dette innholdet" }: { what?: string }) {
  return (
    <div className="state denied" role="status">
      <h3>Du har ikke tilgang til {what}</h3>
      <p>Innholdet er forbeholdt styret. Kontakt styreleder hvis du mener du skal ha tilgang.</p>
    </div>
  );
}

export function Skeleton({ lines = 3, className = "" }: { lines?: number; className?: string }) {
  return (
    <div className={`skel-card card ${className}`} aria-busy="true" aria-label="Laster">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton" style={{ width: `${90 - i * 18}%` }} />
      ))}
    </div>
  );
}

/* ---------- Tabs (URL-styrt av kalleren) ---------- */
export function Tabs<T extends string>({ value, onChange, items, label }: { value: T; onChange: (v: T) => void; items: { id: T; label: string; count?: number }[]; label: string }) {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <div className="tabs" role="tablist" aria-label={label} ref={ref}
      onKeyDown={(e) => {
        const idx = items.findIndex((i) => i.id === value);
        if (e.key === "ArrowRight") onChange(items[(idx + 1) % items.length]!.id);
        if (e.key === "ArrowLeft") onChange(items[(idx - 1 + items.length) % items.length]!.id);
      }}
    >
      {items.map((it) => (
        <button key={it.id} role="tab" aria-selected={value === it.id} tabIndex={value === it.id ? 0 : -1} onClick={() => onChange(it.id)}>
          {it.label}
          {it.count !== undefined && <span className="n">{it.count}</span>}
        </button>
      ))}
    </div>
  );
}

/* ---------- Drawer ---------- */
export function Drawer({ title, sub, onClose, children, footer, wide, eyebrow }: { title: ReactNode; sub?: ReactNode; eyebrow?: ReactNode; onClose: () => void; children: ReactNode; footer?: ReactNode; wide?: boolean }) {
  const id = useId();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    ref.current?.querySelector<HTMLElement>("button, a, input")?.focus();
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [onClose]);
  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} aria-hidden="true" />
      <div className={`drawer${wide ? " wide" : ""}`} role="dialog" aria-modal="true" aria-labelledby={id} ref={ref}>
        <div className="drawer-head">
          <div className="grow">
            {eyebrow && <div className="eyebrow">{eyebrow}</div>}
            <h2 id={id}>{title}</h2>
            {sub && <div className="muted small" style={{ marginTop: 4 }}>{sub}</div>}
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Lukk">
            <IconClose />
          </button>
        </div>
        <div className="drawer-body">{children}</div>
        {footer && <div className="drawer-foot">{footer}</div>}
      </div>
    </>
  );
}

/* ---------- Bekreftelsesmodal for irreversible handlinger ---------- */
export function ConfirmModal({ title, body, confirmLabel = "Bekreft", danger, onConfirm, onCancel, pending }: { title: string; body: ReactNode; confirmLabel?: string; danger?: boolean; onConfirm: () => void; onCancel: () => void; pending?: boolean }) {
  const id = useId();
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onCancel();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onCancel]);
  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal" role="alertdialog" aria-modal="true" aria-labelledby={id} onClick={(e) => e.stopPropagation()}>
        <h2 id={id}>{title}</h2>
        <div>{body}</div>
        <div className="actions">
          <Button variant="secondary" onClick={onCancel} disabled={pending}>
            Avbryt
          </Button>
          <Button variant={danger ? "danger" : "primary"} onClick={onConfirm} disabled={pending} autoFocus>
            {pending ? "Lagrer …" : confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ---------- Progress ---------- */
export function Progress({ pct, tone }: { pct: number | undefined; tone?: "good" | "warn" }) {
  if (pct === undefined) return <Missing />;
  return (
    <div className={`progress${tone ? ` ${tone}` : ""}`} role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
      <i style={{ width: `${Math.max(0, Math.min(100, pct))}%` }} />
    </div>
  );
}

/* ---------- Definisjonsliste ---------- */
export function KV({ items, tight }: { items: [ReactNode, ReactNode][]; tight?: boolean }) {
  return (
    <dl className={`kv${tight ? " tight" : ""}`}>
      {items.map(([k, v], i) => (
        <div key={i} style={{ display: "contents" }}>
          <dt>{k}</dt>
          <dd>{v}</dd>
        </div>
      ))}
    </dl>
  );
}

export function Callout({ tone, title, children }: { tone?: "warn" | "danger" | "good"; title?: string; children: ReactNode }) {
  return (
    <div className={`callout${tone ? ` ${tone}` : ""}`}>
      {title && <strong>{title}</strong>}
      {children}
    </div>
  );
}

export function NextBox({ children, label = "Neste anbefalte handling" }: { children: ReactNode; label?: string }) {
  return (
    <div className="next-box">
      <div className="eyebrow">{label}</div>
      <p>{children}</p>
    </div>
  );
}
