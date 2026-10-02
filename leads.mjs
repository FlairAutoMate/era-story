// Lists (and optionally downloads) the leads stored by /api/lead.
//   node leads.mjs            → table of leads, newest first
//   node leads.mjs --json     → all leads as a JSON array on stdout
//   node leads.mjs --csv      → CSV on stdout
// Needs BLOB_READ_WRITE_TOKEN — `npx vercel env pull .env.local` writes it locally.
import { list, get } from "@vercel/blob";
import { readFileSync, existsSync } from "node:fs";

if (!process.env.BLOB_READ_WRITE_TOKEN && existsSync(".env.local")) {
  for (const line of readFileSync(".env.local", "utf8").split(/\r?\n/)) {
    const m = line.match(/^BLOB_READ_WRITE_TOKEN="?([^"]+)"?/);
    if (m) process.env.BLOB_READ_WRITE_TOKEN = m[1];
  }
}
if (!process.env.BLOB_READ_WRITE_TOKEN) {
  console.error("BLOB_READ_WRITE_TOKEN mangler. Kjør `npx vercel env pull .env.local` først.");
  process.exit(1);
}

const mode = process.argv.includes("--json") ? "json" : process.argv.includes("--csv") ? "csv" : "table";
const leads = [];
let cursor;
do {
  const page = await list({ prefix: "leads/", cursor, limit: 1000 });
  for (const blob of page.blobs) {
    const res = await get(blob.pathname, { access: "private" });
    if (!res || !res.stream) continue;
    const text = await new Response(res.stream).text();
    try { leads.push({ pathname: blob.pathname, ...JSON.parse(text) }); } catch { /* skip malformed */ }
  }
  cursor = page.hasMore ? page.cursor : undefined;
} while (cursor);
// /ny asks for an e-mail after the address, stored as a separate "email" document that points back at
// the first one with leadId. Join them here so each lead is one row. A follow-up whose first document
// is gone (deleted on request, say) stays as a row of its own.
const followups = leads.filter((l) => l.kind === "email");
const rows = leads.filter((l) => l.kind !== "email");
const byId = new Map(rows.map((l) => [l.id, l]));
for (const f of followups) {
  const lead = byId.get(f.leadId);
  if (lead) lead.email = lead.email || f.email;
  else rows.push({ ...f, value: f.value ? `${f.value} (kun e-post)` : "(kun e-post)" });
}
leads.length = 0;
leads.push(...rows);
leads.sort((a, b) => (b.receivedAt || "").localeCompare(a.receivedAt || ""));
const where = (l) => (l.address ? [l.address.kommunenavn, l.address.gardsnummer !== undefined ? `gnr ${l.address.gardsnummer}/bnr ${l.address.bruksnummer ?? "-"}` : ""].filter(Boolean).join(" ") : "");

const names = { owner: "Boligeier", board: "Styret", pro: "Håndverker", partner: "Faghandel" };
if (mode === "json") {
  console.log(JSON.stringify(leads, null, 2));
} else if (mode === "csv") {
  const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  console.log(["receivedAt", "audience", "value", "email", "kommune", "gnr", "bnr", "page", "id"].join(","));
  for (const l of leads) console.log([l.receivedAt, names[l.audience] || l.audience, l.value, l.email, l.address?.kommunenavn, l.address?.gardsnummer, l.address?.bruksnummer, l.page, l.id].map(esc).join(","));
} else {
  if (!leads.length) console.log("Ingen leads ennå.");
  for (const l of leads) console.log(`${(l.receivedAt || "").slice(0, 16).replace("T", " ")}  ${(names[l.audience] || l.audience).padEnd(11)} ${l.value}  ${where(l) ? `[${where(l)}]  ` : ""}${l.email || ""}`);
  console.log(`\n${leads.length} lead(s).`);
}
