// Tests api/lead.js against an in-memory stand-in for @vercel/blob. Nothing is stored anywhere and
// nothing is sent: the real handler runs, only its `put` is swapped.
//
//   node tools/test-lead-api.mjs
//
// Covers what the /ny two-step form depends on: old clients are unchanged, a picked address keeps
// only the allowed Kartverket fields, the e-mail follow-up is append-only and linked by leadId, and
// rejected or honeypot requests store nothing.
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import assert from "node:assert/strict";

const src = readFileSync(fileURLToPath(new URL("../api/lead.js", import.meta.url)), "utf8");
assert.ok(src.includes('import { put } from "@vercel/blob";'), "api/lead.js no longer imports put the way this test expects");
const dir = mkdtempSync(join(tmpdir(), "era-lead-test-"));
writeFileSync(join(dir, "lead.mjs"), src.replace('import { put } from "@vercel/blob";', "const put = async (p, b) => { globalThis.__stored.push({ path: p, body: JSON.parse(b) }); };"));
globalThis.__stored = [];
const { default: handler } = await import(pathToFileURL(join(dir, "lead.mjs")).href);

function call(body, method = "POST") {
  return new Promise((resolve) => {
    const res = { headers: {}, setHeader(k, v) { this.headers[k] = v; }, status(c) { this.code = c; return this; }, json(o) { resolve({ code: this.code, body: o }); return this; } };
    handler({ method, body, headers: { "user-agent": "test" } }, res);
  });
}
const last = () => globalThis.__stored.at(-1);

// 1. a client that sends none of the new fields behaves as before
let r = await call({ audience: "owner", value: "Storgata 1, Oslo", page: "https://x/boligeier" });
assert.equal(r.code, 200); assert.equal(r.body.ok, true);
assert.equal(last().body.value, "Storgata 1, Oslo");
assert.equal(last().body.address, undefined); assert.equal(last().body.kind, undefined);

// 2. a picked address keeps the allowed fields only, and values outside their ranges are dropped
await call({ audience: "owner", value: "Myrerveien 46A, 0000 Oslo", address: { text: "Myrerveien 46A", postnummer: "0000", poststed: "OSLO", kommunenummer: "0301", kommunenavn: "OSLO", gardsnummer: 12, bruksnummer: 34, lat: 59.9, lon: 10.7, evil: "<script>", extra: { a: 1 } } });
assert.deepEqual(Object.keys(last().body.address).sort(), ["bruksnummer", "gardsnummer", "kommunenavn", "kommunenummer", "lat", "lon", "postnummer", "poststed", "text"]);
await call({ audience: "owner", value: "Abc 1", address: { lat: 500, lon: -4, gardsnummer: "12; drop", text: 42 } });
assert.deepEqual(last().body.address, { text: "42" });
await call({ audience: "owner", value: "Abc 1", address: "not an object" });
assert.equal(last().body.address, undefined);

// 3. the e-mail follow-up is its own document, linked to the first and never rewriting it
const first = await call({ audience: "owner", value: "Myrerveien 46A, 0000 Oslo" });
const before = globalThis.__stored.length;
r = await call({ audience: "owner", followup: "email", leadId: first.body.id, value: "Myrerveien 46A, 0000 Oslo", email: "kari@example.no", page: "https://x/ny" });
assert.equal(r.code, 200);
assert.equal(globalThis.__stored.length, before + 1);
assert.ok(last().path.endsWith("-epost.json"));
assert.equal(last().body.kind, "email"); assert.equal(last().body.leadId, first.body.id); assert.equal(last().body.email, "kari@example.no");
assert.notEqual(last().body.id, first.body.id);

// 4. bad input is rejected before anything is stored, and a filled honeypot is silently dropped
const n = globalThis.__stored.length;
assert.equal((await call({ audience: "owner", followup: "email", leadId: first.body.id, email: "not-an-email" })).code, 400);
assert.equal((await call({ audience: "owner", followup: "email", leadId: "nope", email: "a@b.no" })).code, 400);
assert.equal((await call({ audience: "owner", followup: "email", email: "a@b.no" })).code, 400);
assert.equal((await call({ audience: "owner", value: "ab" })).code, 400);
assert.equal((await call({ audience: "owner", followup: "email", leadId: first.body.id, email: "a@b.no", website: "http://spam" })).code, 200);
assert.equal(globalThis.__stored.length, n, "nothing is stored for rejected or honeypot requests");
assert.equal((await call({}, "GET")).code, 405);

console.log("lead api: ok");
