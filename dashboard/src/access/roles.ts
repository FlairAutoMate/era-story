import type { Role } from "@/domain/types";

/**
 * Tilgangsmodell. Frontend bruker denne for å skjule/vise, men backend må håndheve det samme.
 * Ingen backend finnes ennå (se README «Backend-gap»), så dette er referansen for kontrakten.
 */
export type Permission =
  | "board:read"
  | "board:decide"
  | "board:admin"
  | "issues:read"
  | "issues:write"
  | "projects:read"
  | "projects:write"
  | "quotes:read"
  | "quotes:request"
  | "quotes:decide"
  | "residents:read"
  | "residents:contact"
  | "messages:send"
  | "documents:read"
  | "documents:correct"
  | "economy:read"
  | "private_quotes:read_all"
  | "private_quotes:read_own"
  | "supplier:read_assigned"
  | "resident:read_own"
  | "assistant:use"
  | "tenant:switch";

const BOARD_MEMBER: Permission[] = [
  "board:read",
  "issues:read",
  "issues:write",
  "projects:read",
  "quotes:read",
  "residents:read",
  "documents:read",
  "economy:read",
  "assistant:use",
];

const BOARD_LEADER: Permission[] = [
  ...BOARD_MEMBER,
  "board:decide",
  "board:admin",
  "projects:write",
  "quotes:request",
  "quotes:decide",
  "residents:contact",
  "messages:send",
  "documents:correct",
];

const PERMISSIONS: Record<Role, Permission[]> = {
  styreleder: BOARD_LEADER,
  styremedlem: BOARD_MEMBER,
  forretningsforer: [
    "board:read",
    "issues:read",
    "projects:read",
    "quotes:read",
    "residents:read",
    "documents:read",
    "economy:read",
    "messages:send",
    "assistant:use",
  ],
  vaktmester: ["issues:read", "issues:write", "projects:read", "documents:read", "assistant:use"],
  beboer: ["resident:read_own", "private_quotes:read_own", "assistant:use"],
  leverandor: ["supplier:read_assigned", "assistant:use"],
  era_admin: [...BOARD_LEADER, "private_quotes:read_all", "tenant:switch", "supplier:read_assigned", "resident:read_own"],
};

export function can(role: Role, permission: Permission): boolean {
  return PERMISSIONS[role].includes(permission);
}

export function canAny(role: Role, permissions: Permission[]): boolean {
  return permissions.some((p) => can(role, p));
}

export const ROLE_LABEL: Record<Role, string> = {
  styreleder: "Styreleder",
  styremedlem: "Styremedlem",
  forretningsforer: "Forretningsfører",
  vaktmester: "Vaktmester",
  beboer: "Beboer",
  leverandor: "Leverandør",
  era_admin: "ERA-administrator",
};

export const ALL_ROLES: Role[] = [
  "styreleder",
  "styremedlem",
  "forretningsforer",
  "vaktmester",
  "beboer",
  "leverandor",
  "era_admin",
];

export function isBoardRole(role: Role): boolean {
  return can(role, "board:read");
}

/** Startside per rolle. */
export function homeFor(role: Role): string {
  if (role === "beboer") return "/min-bolig";
  if (role === "leverandor") return "/leverandor";
  if (role === "vaktmester") return "/saker";
  return "/";
}
