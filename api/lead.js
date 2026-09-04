// POST /api/lead — the finale's intake. Stores one JSON document per lead in Vercel Blob
// (private access, EU region) and, when RESEND_API_KEY + LEAD_NOTIFY_TO are set, e-mails a
// notification. Nothing else is sent anywhere.
//
// Body: { audience: "owner" | "board" | "pro" | "partner", value: string, email: string, website?: string, page?: string }
// `website` is a honeypot: humans never fill it, bots do. `email` is optional — the forms only ask
// for an address today; sign-in via Vipps/Google comes later. A real-shaped e-mail is kept if sent.
//
// Read leads: `npm run leads`. Notify: `vercel env add RESEND_API_KEY` and `vercel env add LEAD_NOTIFY_TO`.
import { put } from "@vercel/blob";
import { randomUUID } from "node:crypto";

const AUDIENCES = new Set(["owner", "board", "pro", "partner"]);
const NAMES = { owner: "Boligeier", board: "Styret", pro: "Håndverker", partner: "Faghandel" };
const MAX_LEN = 200;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

async function notify(doc) {
  const key = process.env.RESEND_API_KEY;
  const to = process.env.LEAD_NOTIFY_TO;
  if (!key || !to) return "skipped";
  const from = process.env.LEAD_NOTIFY_FROM || "ERA <onboarding@resend.dev>";
  const who = NAMES[doc.audience] || doc.audience;
  const text = [
    `Ny henvendelse fra ${who.toLowerCase()} via era-story.`,
    ``,
    `${who}: ${doc.value}`,
    `E-post: ${doc.email || "-"}`,
    `Tidspunkt: ${doc.receivedAt}`,
    `Side: ${doc.page || "-"}`,
    ``,
    `Alle leads: npm run leads (i prosjektmappen) eller Vercel → Storage → era-leads-eu.`,
  ].join("\n");
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: to.split(",").map((s) => s.trim()), reply_to: doc.email || undefined, subject: `ERA lead · ${who} · ${doc.value.slice(0, 60)}`, text }),
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
  const honeypot = String(body.website ?? "").trim();

  // Bots get a friendly 200 and nothing stored; humans need at least a few characters and a
  // an e-mail is kept only if it looks real.
  if (honeypot) return res.status(200).json({ ok: true });
  if (value.length < 3) return res.status(400).json({ ok: false, error: "short" });

  const now = new Date();
  const id = randomUUID();
  const doc = {
    id,
    audience,
    value,
    email: EMAIL_RE.test(email) ? email : undefined,
    receivedAt: now.toISOString(),
    source: "era-story",
    page: typeof body.page === "string" ? body.page.slice(0, 200) : undefined,
    userAgent: (req.headers["user-agent"] || "").slice(0, 200),
  };
  const day = now.toISOString().slice(0, 10);
  const pathname = `leads/${audience}/${day}/${now.toISOString().replace(/[:.]/g, "-")}-${id.slice(0, 8)}.json`;

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
