import { describe, expect, it } from "vitest";
import type { Session } from "@/domain/types";
import { AccessDeniedError } from "./adapters";
import { createFixtureAdapter } from "./fixtureAdapter";

const leader: Session = { userId: "p-kari", name: "Kari Nordvik", role: "styreleder", tenantId: "perrongen" };
const member: Session = { userId: "p-jonas", name: "Jonas Berge", role: "styremedlem", tenantId: "perrongen" };
const resident: Session = { userId: "p-mette", name: "Mette Larsen", role: "beboer", tenantId: "perrongen", unitId: "u-4-H0301" };
const otherResident: Session = { userId: "p-x", name: "Ola Hansen", role: "beboer", tenantId: "perrongen", unitId: "u-4-H0201" };
const supplier: Session = { userId: "p-erik", name: "Erik Moen", role: "leverandor", tenantId: "perrongen", supplierId: "s-moen" };
const otherSupplier: Session = { userId: "p-y", name: "Ali Rahimi", role: "leverandor", tenantId: "perrongen", supplierId: "s-takteam" };
const solvang: Session = { userId: "p2-leder", name: "Bente Kvam", role: "styreleder", tenantId: "solvang" };

const a = () => createFixtureAdapter({ latency: 0 });

describe("tenant-isolasjon", () => {
  it("Perrongen ser aldri Solvang-data og omvendt", async () => {
    const ad = a();
    const [pi, si, pp, sp, pd, sd] = await Promise.all([ad.listIssues(leader), ad.listIssues(solvang), ad.listProjects(leader), ad.listProjects(solvang), ad.listDocuments(leader), ad.listDocuments(solvang)]);
    expect(pi.every((i) => i.tenantId === "perrongen")).toBe(true);
    expect(si.every((i) => i.tenantId === "solvang")).toBe(true);
    expect(pi.some((i) => i.title.includes("Solvang"))).toBe(false);
    expect(pp.some((p) => p.tenantId === "solvang")).toBe(false);
    expect(sp).toHaveLength(1);
    expect(pd.some((d) => d.tenantId === "solvang")).toBe(false);
    expect(sd).toHaveLength(1);
  });
  it("ukjent tenant gir tilgang nektet", async () => {
    await expect(a().getTenant({ ...leader, tenantId: "finnes-ikke" })).rejects.toBeInstanceOf(AccessDeniedError);
  });
  it("bare ERA-admin kan liste flere tenants", async () => {
    const ad = a();
    expect(await ad.listTenantsFor(leader)).toHaveLength(1);
    expect((await ad.listTenantsFor({ ...leader, role: "era_admin" })).length).toBeGreaterThan(1);
  });
});

describe("rolletilgang i adapteret", () => {
  it("beboer nektes styredata", async () => {
    const ad = a();
    await expect(ad.getBoardSummary(resident)).rejects.toBeInstanceOf(AccessDeniedError);
    await expect(ad.listIssues(resident)).rejects.toBeInstanceOf(AccessDeniedError);
    await expect(ad.listQuotes(resident)).rejects.toBeInstanceOf(AccessDeniedError);
    await expect(ad.listResidents(resident)).rejects.toBeInstanceOf(AccessDeniedError);
    await expect(ad.listBudget(resident)).rejects.toBeInstanceOf(AccessDeniedError);
  });
  it("beboer ser bare egen bolig og egne dokumenter", async () => {
    const ad = a();
    const units = await ad.listUnits(resident);
    expect(units.map((u) => u.id)).toEqual(["u-4-H0301"]);
    const docs = await ad.listDocuments(resident);
    expect(docs.every((d) => d.access === "alle_beboere" || d.links.unitId === "u-4-H0301")).toBe(true);
  });
  it("styremedlem kan ikke registrere vedtak, styreleder kan", async () => {
    const ad = a();
    await expect(ad.recordDecision(member, "d-elektro", "vedtatt")).rejects.toBeInstanceOf(AccessDeniedError);
    const d = await ad.recordDecision(leader, "d-elektro", "vedtatt");
    expect(d.status).toBe("vedtatt");
  });
  it("kontaktinfo strippes uten residents:contact", async () => {
    const ad = a();
    const asMember = await ad.listResidents(member);
    expect(asMember.every((r) => r.email === undefined && r.phone === undefined)).toBe(true);
    const asLeader = await ad.listResidents(leader);
    expect(asLeader.some((r) => r.email)).toBe(true);
  });
});

describe("private tilbud", () => {
  it("styret ser aldri private tilbud, bare aggregert", async () => {
    const ad = a();
    const rows = await ad.listParticipation(leader, "prj-soil");
    expect(rows.length).toBe(48);
    expect(rows.every((r) => r.privateQuote === undefined)).toBe(true);
    const p = (await ad.listProjects(leader)).find((x) => x.id === "prj-soil")!;
    expect(p.privateAggregate?.total).toBeGreaterThan(0);
  });
  it("beboer ser bare eget private tilbud", async () => {
    const ad = a();
    const mine = await ad.listParticipation(resident, "prj-soil");
    expect(mine).toHaveLength(1);
    expect(mine[0]!.unitId).toBe("u-4-H0301");
    expect(mine[0]!.privateQuote).toBeDefined();
    const other = await ad.listParticipation(otherResident, "prj-soil");
    expect(other.every((r) => r.unitId === "u-4-H0201")).toBe(true);
    expect(other.some((r) => r.unitId === "u-4-H0301")).toBe(false);
  });
  it("leverandør ser tildelte prosjekter og boliger, ikke andre", async () => {
    const ad = a();
    const mine = await ad.listProjects(supplier);
    expect(mine.map((p) => p.id)).toEqual(["prj-soil"]);
    const rows = await ad.listParticipation(supplier, "prj-soil");
    expect(rows.length).toBe(48);
    expect(rows.some((r) => r.privateQuote)).toBe(true);
    await expect(ad.listParticipation(otherSupplier, "prj-soil")).rejects.toBeInstanceOf(AccessDeniedError);
    expect(await ad.listProjects(otherSupplier)).toHaveLength(0);
  });
});

describe("soilrør/baderom-flyt ende til ende", () => {
  it("beboer svarer, velger pakke, aksepterer; styret ser status, ikke innhold", async () => {
    const ad = a();
    const fresh: Session = { ...resident, unitId: "u-8b-H0402" };
    let row = await ad.answerSurvey(fresh, "prj-soil", { "sq-1": "2001", "sq-2": "Nei", "sq-3": "Ja", "sq-4": "Ja" }, 2);
    expect(row.responseStatus).toBe("vurderer");
    row = await ad.chooseTier(fresh, "prj-soil", "oppgradering", ["po-varme"]);
    expect(row.responseStatus).toBe("valgt");
    expect(row.privateQuote?.tier).toBe("oppgradering");
    expect(row.privateQuote?.options.find((o) => o.id === "po-varme")?.selected).toBe(true);
    row = await ad.acceptPrivateQuote(fresh, "prj-soil");
    expect(row.responseStatus).toBe("akseptert");
    expect(row.privateQuote?.accepted).toBeDefined();
    const board = (await ad.listParticipation(leader, "prj-soil")).find((r) => r.unitId === "u-8b-H0402")!;
    expect(board.responseStatus).toBe("akseptert");
    expect(board.tier).toBe("oppgradering");
    expect(board.privateQuote).toBeUndefined();
  });
});

describe("beregnede data", () => {
  it("prioriterte saker er maks 3 og forklarbare", async () => {
    const items = await a().listPriorityItems(leader);
    expect(items.length).toBeLessThanOrEqual(3);
    expect(items.length).toBeGreaterThan(0);
    for (const it of items) {
      expect(it.why.length).toBeGreaterThan(10);
      expect(it.recommendedAction.length).toBeGreaterThan(10);
      expect(it.primary.to.startsWith("/")).toBe(true);
    }
  });
  it("statusoversikt bruker faktiske antall", async () => {
    const s = await a().getBoardSummary(leader);
    expect(s.actionsRequiringDecision).toBe(3);
    expect(s.criticalOpenIssues).toBe(1);
    expect(s.buildingAreasMapped).toEqual({ mapped: 10, total: 12 });
  });
  it("tom tilstand gir tomme lister, feiltilstand kaster", async () => {
    const empty = createFixtureAdapter({ latency: 0, mode: "tom" });
    expect(await empty.listIssues(leader)).toHaveLength(0);
    expect((await empty.listPriorityItems(leader)).length).toBe(0);
    const failing = createFixtureAdapter({ latency: 0, mode: "feil" });
    await expect(failing.listIssues(leader)).rejects.toThrow();
  });
  it("assistenten svarer med kilder og antakelser", async () => {
    const ans = await a().askEra(leader, "Sammenlign disse tilbudene", { tenantId: "perrongen", role: "styreleder", page: "/tilbud" });
    expect(ans.sources.length).toBeGreaterThan(0);
    expect(ans.assumptions.length).toBeGreaterThan(0);
    expect(ans.conclusion.length).toBeGreaterThan(0);
  });
});
