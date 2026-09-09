/**
 * DEMO-DATA: Solvang sameie. Liten andre-tenant som finnes for å bevise tenant-isolasjon
 * (ingen data herfra skal vises når Perrongen er aktiv, og omvendt).
 */
import type { Building, Document, Issue, Person, Project, Tenant, Unit } from "@/domain/types";

export const T2 = "solvang";

export const tenant2: Tenant = {
  id: T2,
  name: "Solvang sameie",
  kind: "sameie",
  address: "Solvangveien 11",
  postal: "1400 Ski",
  buildingCount: 1,
  unitCount: 12,
  lastUpdated: "2026-09-08T16:10:00",
  isDemo: true,
};

export const people2: Person[] = [{ id: "p2-leder", name: "Bente Kvam", role: "styreleder", tenantId: T2 }];

export const buildings2: Building[] = [
  { id: "b2-a", tenantId: T2, name: "Hovedbygg", address: "Solvangveien 11", yearBuilt: 1984, floors: 3, entrances: [{ id: "e2-1", buildingId: "b2-a", name: "Oppgang 11", unitCount: 12 }] },
];

export const units2: Unit[] = [1, 2, 3].flatMap((floor) =>
  [1, 2, 3, 4].map((n) => ({ id: `u2-H0${floor}0${n}`, tenantId: T2, buildingId: "b2-a", entranceId: "e2-1", label: `H0${floor}0${n}`, floor, sizeM2: 65 })),
);

export const issues2: Issue[] = [
  {
    id: "iss2-1",
    tenantId: T2,
    ref: "AV-3",
    title: "Solvang: knust rute i inngangsdør",
    description: "Solvang sameie – skal aldri vises i Perrongen.",
    severity: "middels",
    status: "ny",
    buildingId: "b2-a",
    responsibility: "felles",
    source: "beboer",
    reportedAt: "2026-09-08T16:10:00",
    reportedBy: "Bente Kvam",
    photos: 1,
    facts: [],
    history: [],
    comments: [],
    tasks: [],
    documentIds: [],
    nextAction: "Bestille glassmester.",
  },
];

export const projects2: Project[] = [
  {
    id: "prj2-1",
    tenantId: T2,
    title: "Solvang: drenering",
    purpose: "Fukt i kjeller.",
    scope: "Ny drenering rundt hovedbygg.",
    stage: "planlagt",
    buildingIds: ["b2-a"],
    affectedUnitIds: [],
    ownerId: "p2-leder",
    supplierIds: [],
    milestones: [],
    openIssueIds: [],
    decisionIds: [],
    changeOrders: [],
    documentIds: [],
    fdvStatus: "ikke_relevant",
    boardNextAction: "Innhente tilbud.",
    hasPrivateUpgrades: false,
  },
];

export const documents2: Document[] = [
  {
    id: "doc2-1",
    tenantId: T2,
    title: "Solvang: tilstandsrapport 2023",
    type: "tilstandsrapport",
    date: "2023-05-01",
    source: "Takstmann",
    status: "analysert",
    analysisPct: 100,
    missingMetadata: [],
    access: "styret",
    links: {},
    findings: [],
  },
];
