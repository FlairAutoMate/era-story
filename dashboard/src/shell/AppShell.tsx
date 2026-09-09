/**
 * Rollebasert AppShell: fast venstremeny på desktop, bunnfaner på mobil (som ERA bolig-appen),
 * topplinje med aktivt borettslag, rolle og global søk. Skallet er låst til viewport-høyde;
 * ERA-assistenten er et felt i bunnlinjen på desktop og svarer i et lag over arbeidsflaten.
 */
import { useEffect, useState, type ComponentType, type ReactNode, type SVGProps } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router";
import { ALL_ROLES, ROLE_LABEL, can, homeFor, type Permission } from "@/access/roles";
import { useData, useQuery } from "@/data/provider";
import type { Role } from "@/domain/types";
import { IconAlert, IconBuilding, IconDoc, IconEra, IconHome, IconMoney, IconMore, IconPeople, IconProject, IconQuote, IconTruck, IconWrench } from "@/components/icons";
import { Drawer } from "@/components/ui";
import { EraAssistantPanel, EraBar, useAssistant } from "./assistant";
import { GlobalSearch } from "./GlobalSearch";

type NavItem = { to: string; label: string; icon: ComponentType<SVGProps<SVGSVGElement>>; perm?: Permission; any?: Permission[]; end?: boolean; badge?: "decisions" | "issues" | "quotes" };

const NAV: NavItem[] = [
  { to: "/", label: "Oversikt", icon: IconHome, perm: "board:read", end: true },
  { to: "/vedlikehold", label: "Vedlikehold", icon: IconWrench, perm: "board:read", badge: "decisions" },
  { to: "/saker", label: "Saker og avvik", icon: IconAlert, perm: "issues:read", badge: "issues" },
  { to: "/prosjekter", label: "Prosjekter", icon: IconProject, perm: "projects:read" },
  { to: "/tilbud", label: "Tilbud", icon: IconQuote, perm: "quotes:read", badge: "quotes" },
  { to: "/beboere", label: "Beboere", icon: IconPeople, perm: "residents:read" },
  { to: "/dokumenter", label: "Dokumenter", icon: IconDoc, perm: "documents:read" },
  { to: "/okonomi", label: "Økonomi", icon: IconMoney, perm: "economy:read" },
  { to: "/min-bolig", label: "Min bolig", icon: IconBuilding, perm: "resident:read_own" },
  { to: "/leverandor", label: "Mine oppdrag", icon: IconTruck, perm: "supplier:read_assigned" },
];

function visibleNav(role: Role): NavItem[] {
  return NAV.filter((n) => (n.perm ? can(role, n.perm) : n.any ? n.any.some((p) => can(role, p)) : true)).filter((n) => !(role === "era_admin" && (n.to === "/min-bolig" || n.to === "/leverandor")));
}

export function AppShell() {
  const { session, setRole, setTenant, demoMode } = useData();
  const { open, setOpen } = useAssistant();
  const location = useLocation();
  const navigate = useNavigate();
  const [more, setMore] = useState(false);
  const nav = visibleNav(session.role);

  const tenant = useQuery((a, s) => a.getTenant(s));
  const tenants = useQuery((a, s) => a.listTenantsFor(s));
  const counts = useQuery(async (a, s) => {
    if (!can(s.role, "board:read")) return null;
    const sum = await a.getBoardSummary(s);
    return { decisions: sum.actionsRequiringDecision, issues: sum.openIssues, quotes: sum.quotesWaiting };
  });

  useEffect(() => setMore(false), [location.pathname]);

  const changeRole = (role: Role) => {
    setRole(role);
    navigate(homeFor(role));
  };

  const renderLink = (n: NavItem) => (
    <NavLink key={n.to} to={n.to} end={n.end} className="navlink">
      <n.icon />
      <span>{n.label}</span>
      {n.badge && counts.data && counts.data[n.badge] > 0 && <span className="badge-count">{counts.data[n.badge]}</span>}
    </NavLink>
  );

  const mobileMain = nav.slice(0, 2);
  const mobileRest = nav.slice(2);

  return (
    <div className="shell">
      <nav className="sidenav" aria-label="Hovedmeny">
        <div className="brand">
          era<span>.</span>
        </div>
        <div className="tenant-switch">
          <div className="eyebrow">Aktivt borettslag</div>
          {tenants.data && tenants.data.length > 1 ? (
            <select className="role-select" value={session.tenantId} onChange={(e) => setTenant(e.target.value)} aria-label="Bytt borettslag">
              {tenants.data.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          ) : (
            <strong>{tenant.data?.name ?? "…"}</strong>
          )}
          <div className="sub">{tenant.data ? `${tenant.data.address}, ${tenant.data.postal}` : ""}</div>
        </div>
        {nav.map(renderLink)}
        <button className="navlink" onClick={() => setOpen(!open)} aria-pressed={open} style={{ background: "none", border: 0, cursor: "pointer", width: "100%", textAlign: "left" }}>
          <IconEra />
          <span>ERA-assistent</span>
        </button>
        <div className="spacer" />
        <div className="role-box">
          <strong>{session.name}</strong>
          {ROLE_LABEL[session.role]}
          <label className="sr" htmlFor="role-select">
            Demo: vis som rolle
          </label>
          <select id="role-select" className="role-select" value={session.role} onChange={(e) => changeRole(e.target.value as Role)} data-testid="role-select">
            {ALL_ROLES.map((r) => (
              <option key={r} value={r}>
                Vis som: {ROLE_LABEL[r]}
              </option>
            ))}
          </select>
        </div>
      </nav>

      <div className="main">
        <header className="topbar">
          <span className="brand-m">
            era<span>.</span>
          </span>
          <div className="crumb desktop-only ellipsis" data-testid="active-context">
            {tenant.data?.name ?? "…"} <span className="muted">· {ROLE_LABEL[session.role]}</span>
          </div>
          <GlobalSearch />
          {tenant.data?.isDemo && <span className="demo-pill" title="Alle data er oppdiktede demo-data">Demo-data</span>}
          {demoMode !== "normal" && <span className="demo-pill">Tilstand: {demoMode}</span>}
        </header>
        <main className="content" id="main">
          <Outlet />
        </main>
        <div className="desktop-only erabar-wrap">
          <EraBar />
        </div>
      </div>

      <EraAssistantPanel />

      <nav className="bottomnav" aria-label="Hovedmeny (mobil)">
        {mobileMain.map((n) => (
          <NavLink key={n.to} to={n.to} end={n.end}>
            <n.icon />
            {n.label.split(" ")[0]}
          </NavLink>
        ))}
        <button className="fab" onClick={() => setOpen(!open)} aria-label="Spør ERA" aria-pressed={open}>
          <span className="icon">
            <IconEra />
          </span>
          ERA
        </button>
        {mobileRest.slice(0, 1).map((n) => (
          <NavLink key={n.to} to={n.to}>
            <n.icon />
            {n.label.split(" ")[0]}
          </NavLink>
        ))}
        <button onClick={() => setMore(true)} aria-label="Flere sider">
          <IconMore />
          Mer
        </button>
      </nav>

      {more && (
        <Drawer title="Meny" onClose={() => setMore(false)} sub={`${tenant.data?.name ?? ""} · ${ROLE_LABEL[session.role]}`}>
          <div className="sheet-nav">
            {nav.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end}>
                <n.icon />
                {n.label}
              </NavLink>
            ))}
          </div>
          <div className="dsection">
            <h3>Demo: vis som rolle</h3>
            <select className="filters-select field" style={{ width: "100%", minHeight: 42, borderRadius: 6, border: "1px solid var(--line-strong)", padding: "0 10px", background: "var(--card)" }} value={session.role} onChange={(e) => changeRole(e.target.value as Role)} aria-label="Bytt rolle">
              {ALL_ROLES.map((r) => (
                <option key={r} value={r}>
                  {ROLE_LABEL[r]}
                </option>
              ))}
            </select>
          </div>
          {tenants.data && tenants.data.length > 1 && (
            <div className="dsection">
              <h3>Bytt borettslag</h3>
              <select style={{ width: "100%", minHeight: 42, borderRadius: 6, border: "1px solid var(--line-strong)", padding: "0 10px", background: "var(--card)" }} value={session.tenantId} onChange={(e) => setTenant(e.target.value)} aria-label="Bytt borettslag">
                {tenants.data.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </Drawer>
      )}
    </div>
  );
}

/** Sideoverskrift: rolig, ikke hero. */
export function PageHead({ title, meta, actions, eyebrow }: { title: ReactNode; meta?: ReactNode[]; actions?: ReactNode; eyebrow?: ReactNode }) {
  return (
    <div className="page-head">
      <div className="title">
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        {meta && meta.length > 0 && (
          <div className="meta">
            {meta.map((m, i) => (
              <span key={i}>{m}</span>
            ))}
          </div>
        )}
      </div>
      {actions && <div className="actions">{actions}</div>}
    </div>
  );
}
