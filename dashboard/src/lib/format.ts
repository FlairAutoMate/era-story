const nb = "nb-NO";

/** Fast «i dag» for demo-tenanten slik at fixtures og frister henger sammen. */
export const TODAY = new Date("2026-09-09T08:00:00");

export function formatNOK(value: number | undefined | null, opts?: { compact?: boolean }): string {
  if (value === undefined || value === null || Number.isNaN(value)) return "Ikke registrert";
  if (opts?.compact && Math.abs(value) >= 1_000_000) {
    const m = value / 1_000_000;
    return `${m.toLocaleString(nb, { maximumFractionDigits: 2 })} mill. kr`;
  }
  return `${Math.round(value).toLocaleString(nb)} kr`;
}

export function formatRange(low: number, high: number): string {
  return `${formatNOK(low, { compact: true })} – ${formatNOK(high, { compact: true })}`;
}

export function formatDate(iso: string | undefined, style: "short" | "long" = "short"): string {
  if (!iso) return "Ikke satt";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "Ikke satt";
  return d.toLocaleDateString(
    nb,
    style === "long" ? { day: "numeric", month: "long", year: "numeric" } : { day: "numeric", month: "short", year: "numeric" },
  );
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(nb, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export function formatMonthYear(iso: string): string {
  return new Date(iso).toLocaleDateString(nb, { month: "short", year: "numeric" });
}

export function formatPct(value: number | undefined): string {
  if (value === undefined) return "Ikke registrert";
  return `${Math.round(value).toLocaleString(nb)} %`;
}

export function formatNumber(value: number): string {
  return value.toLocaleString(nb);
}

export function daysUntil(iso: string, today: Date = TODAY): number {
  const d = new Date(iso);
  const t = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((d.getTime() - t.getTime()) / 86_400_000);
}

export function relativeDeadline(iso: string | undefined, today: Date = TODAY): string {
  if (!iso) return "Ingen frist";
  const n = daysUntil(iso, today);
  if (n < 0) return `Passert med ${Math.abs(n)} d.`;
  if (n === 0) return "I dag";
  if (n === 1) return "I morgen";
  if (n < 14) return `Om ${n} dager`;
  return formatDate(iso);
}

export function plural(n: number, one: string, many: string): string {
  return `${formatNumber(n)} ${n === 1 ? one : many}`;
}
