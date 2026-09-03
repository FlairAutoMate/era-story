// POST /api/lead — the finale's intake. Stores one JSON document per lead in Vercel Blob
// (private access) and answers with a short confirmation. Nothing is sent anywhere else.
//
// Body: { audience: "owner" | "board" | "pro" | "partner", value: string, website?: string }
// `website` is a honeypot: humans never fill it, bots do.
//
// Read leads: `npx vercel blob list --prefix leads/` (or download with `vercel blob get`).
import { put } from "@vercel/blob";
import { randomUUID } from "node:crypto";

const AUDIENCES = new Set(["owner", "board", "pro", "partner"]);
const MAX_LEN = 200;

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
  const honeypot = String(body.website ?? "").trim();

  // Bots get a friendly 200 and nothing stored; humans need at least a few characters.
  if (honeypot) return res.status(200).json({ ok: true });
  if (value.length < 3) return res.status(400).json({ ok: false, error: "short" });

  const now = new Date();
  const id = randomUUID();
  const doc = {
    id,
    audience,
    value,
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
  return res.status(200).json({ ok: true, id });
}
