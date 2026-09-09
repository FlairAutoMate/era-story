import { describe, expect, it } from "vitest";
import { can, homeFor } from "./roles";

describe("tilgangsmodell", () => {
  it("styreleder har administrative rettigheter", () => {
    expect(can("styreleder", "board:decide")).toBe(true);
    expect(can("styreleder", "messages:send")).toBe(true);
    expect(can("styreleder", "residents:contact")).toBe(true);
    expect(can("styreleder", "quotes:request")).toBe(true);
  });
  it("styremedlem mangler administrative handlinger", () => {
    expect(can("styremedlem", "board:read")).toBe(true);
    expect(can("styremedlem", "board:decide")).toBe(false);
    expect(can("styremedlem", "messages:send")).toBe(false);
    expect(can("styremedlem", "residents:contact")).toBe(false);
    expect(can("styremedlem", "quotes:request")).toBe(false);
    expect(can("styremedlem", "documents:correct")).toBe(false);
  });
  it("beboer får ikke styredata", () => {
    for (const p of ["board:read", "issues:read", "quotes:read", "residents:read", "economy:read", "documents:read"] as const) expect(can("beboer", p)).toBe(false);
    expect(can("beboer", "resident:read_own")).toBe(true);
    expect(can("beboer", "private_quotes:read_own")).toBe(true);
  });
  it("leverandør ser bare tildelte prosjekter", () => {
    expect(can("leverandor", "supplier:read_assigned")).toBe(true);
    expect(can("leverandor", "board:read")).toBe(false);
    expect(can("leverandor", "projects:read")).toBe(false);
  });
  it("startside per rolle", () => {
    expect(homeFor("beboer")).toBe("/min-bolig");
    expect(homeFor("leverandor")).toBe("/leverandor");
    expect(homeFor("styreleder")).toBe("/");
  });
});
