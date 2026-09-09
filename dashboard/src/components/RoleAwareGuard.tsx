import type { ReactNode } from "react";
import { can, canAny, type Permission } from "@/access/roles";
import { useSession } from "@/data/provider";
import { DeniedState } from "./ui";

/**
 * RoleAwareGuard: skjuler eller erstatter innhold uten tilgang. Frontend-vakt for UX;
 * adapteret/backend håndhever det samme uavhengig av denne.
 */
export function RoleAwareGuard({ permission, any, children, fallback, what }: { permission?: Permission; any?: Permission[]; children: ReactNode; fallback?: ReactNode; what?: string }) {
  const session = useSession();
  const ok = permission ? can(session.role, permission) : any ? canAny(session.role, any) : true;
  if (ok) return <>{children}</>;
  if (fallback !== undefined) return <>{fallback}</>;
  return <DeniedState what={what} />;
}

export function useCan(permission: Permission): boolean {
  return can(useSession().role, permission);
}
