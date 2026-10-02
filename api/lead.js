// POST /api/lead — the finale's intake. Stores one JSON document per lead in Vercel Blob
// (private access, EU region) and, when RESEND_API_KEY + LEAD_NOTIFY_TO are set, e-mails a
// notification. Nothing else is sent anywhere.
//
// Body: { audience: "owner" | "board" | "pro" | "partner", value: string, email?: string, intent?: "interest" | "demo", website?: string, page?: string,
//         address?: { ...Geonorge fields, see cleanAddress }, leadId?: string, followup?: "email" }
// `website` is a honeypot: humans never fill it, bots do. `email` is optional. A real-shaped e-mail is
// kept if sent.
//
// Two steps on /ny: first the address (with the structured fields of the suggestion the visitor picked,
// when they picked one), then optionally an e-mail. The e-mail arrives as `followup: "email"` with the
// `leadId` the first call returned, and is stored as its own small document next to the first one
// (append-only; nothing already stored is ever rewritten). leads.mjs joins them again.
//
// Read leads: `npm run leads`. Notify: `vercel env add RESEND_API_KEY` and `vercel env add LEAD_NOTIFY_TO`.
import { put } from "@vercel/blob";
import { randomUUID } from "node:crypto";

const AUDIENCES = new Set(["owner", "board", "pro", "partner"]);
const NAMES = { owner: "Boligeier", board: "Styret", pro: "Håndverker", partner: "Faghandel" };
const MAX_LEN = 200;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

// Only these Geonorge fields are ever stored, each cut to a safe length or range, so the document
// cannot be used to smuggle arbitrary data into the store.
function cleanAddress(a) {
  if (!a || typeof a !== "object") return undefined;
  const str = (v, n) => (typeof v === "string" || typeof v === "number" ? String(v).trim().slice(0, n) : undefined);
  const num = (v, lo, hi) => (typeof v === "number" && Number.isFinite(v) && v >= lo && v <= hi ? v : undefined);
  const out = {
    text: str(a.text, MAX_LEN),
    postnummer: str(a.postnummer, 10),
    poststed: str(a.poststed, 60),
    kommunenummer: str(a.kommunenummer, 6),
    kommunenavn: str(a.kommunenavn, 60),
    gardsnummer: num(a.gardsnummer, 0, 99999),
    bruksnummer: num(a.bruksnummer, 0, 99999),
    festenummer: num(a.festenummer, 0, 99999),
    seksjonsnummer: num(a.seksjonsnummer, 0, 99999),
    lat: num(a.lat, 57, 72),
    lon: num(a.lon, 4, 32),
  };
  for (const k of Object.keys(out)) if (out[k] === undefined || out[k] === "") delete out[k];
  return Object.keys(out).length ? out : undefined;
}

async function notify(doc) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.LEAD_NOTIFY_TO;
  if (!key || !to) return "skipped";
  const from = process.env.LEAD_NOTIFY_FROM || "ERA <onboarding@resend.dev>";
  const who = NAMES[doc.audience] || doc.audience;
  const a = doc.address;
  const matrikkel = a && a.gardsnummer !== undefined ? `gnr ${a.gardsnummer} / bnr ${a.bruksnummer ?? "-"}` : undefined;
  const text = doc.kind === "email" ? [
    `E-post lagt igjen etter en adresse via era-story.`,
    ``,
    `${who}: ${doc.value || "-"}`,
    `E-post: ${doc.email}`,
    `Hører til innsending: ${doc.leadId}`,
    `Tidspunkt: ${doc.receivedAt}`,
    `Side: ${doc.page || "-"}`,
  ].join("\n") : [
    `Ny henvendelse fra ${who.toLowerCase()} via era-story.`,
    ``,
    `${who}: ${doc.value}`,
    ...(a ? [`Adresse bekreftet mot Kartverket: ${[a.kommunenavn, matrikkel].filter(Boolean).join(", ") || "ja"}`] : []),
    `Ønsker: ${doc.intent === "demo" ? "demo" : "å bli kontaktet"}`,
    `E-post: ${doc.email || "-"}`,
    `Tidspunkt: ${doc.receivedAt}`,
    `Side: ${doc.page || "-"}`,
    ``,
    `Alle leads: npm run leads (i prosjektmappen) eller Vercel → Storage → era-leads-eu.`,
  ].join("\n");
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: to.split(",").map((s) => s.trim()), reply_to: doc.email || undefined, subject: doc.kind === "email" ? `ERA lead · e-post · ${who}` : `ERA lead · ${who} · ${doc.value.slice(0, 60)}`, text }),
  });
  if (!r.ok) throw new Error(`resend ${r.status}: ${(await r.text()).slice(0, 200)}`);
  return "sent";
}

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method" });
  }
  let body = req.body;
  if (typeof body === "string") {
    try { body = JSON.parse(body); } catch { body = null; }
  }
  if (!body || typeof body !== "object") return res.status(400).json({ ok: false, error: "body" });

  const audience = AUDIENCES.has(body.audience) ? body.audience : "owner";
  const value = String(body.value ?? "").trim().replace(/\s+/g, " ").slice(0, MAX_LEN);
  const email = String(body.email ?? "").trim().slice(0, MAX_LEN);
  const intent = body.intent === "demo" ? "demo" : "interest";
  const honeypot = String(body.website ?? "").trim();
  const followup = body.followup === "email";
  const leadId = typeof body.leadId === "string" && UUID_RE.test(body.leadId) ? body.leadId : undefined;

  // Bots get a friendly 200 and nothing stored; humans need at least a few characters and a
  // an e-mail is kept only if it looks real.
  if (honeypot) return res.status(200).json({ ok: true });
  if (followup) {
    if (!leadId) return res.status(400).json({ ok: false, error: "lead" });
    if (!EMAIL_RE.test(email)) return res.status(400).json({ ok: false, error: "email" });
  } else if (value.length < 3) {
    return res.status(400).json({ ok: false, error: "short" });
  }

  const now = new Date();
  const id = randomUUID();
  const common = {
    id,
    audience,
    receivedAt: now.toISOString(),
    source: "era-story",
    page: typeof body.page === "string" ? body.page.slice(0, 200) : undefined,
    userAgent: (req.headers["user-agent"] || "").slice(0, 200),
  };
  const doc = followup
    ? { ...common, kind: "email", leadId, value: value || undefined, email }
    : { ...common, value, email: EMAIL_RE.test(email) ? email : undefined, intent, address: cleanAddress(body.address) };
  const day = now.toISOString().slice(0, 10);
  const pathname = `leads/${audience}/${day}/${now.toISOString().replace(/[:.]/g, "-")}-${id.slice(0, 8)}${followup ? "-epost" : ""}.json`;

  try {
    await put(pathname, JSON.stringify(doc, null, 2), {
      access: "private",
      contentType: "application/json",
      addRandomSuffix: false,
    });
  } catch (err) {
    console.error("[lead] store failed", err);
    return res.status(500).json({ ok: false, error: "store" });
  }

  // The notification must never cost the visitor their confirmation.
  let notified = "skipped";
  try { notified = await notify(doc); } catch (err) { console.error("[lead] notify failed", err); notified = "failed"; }
  return res.status(200).json({ ok: true, id, notified });
}
