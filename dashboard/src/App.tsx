import { Component, lazy, Suspense, type ErrorInfo, type ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";
import { DataProvider, useSession } from "@/data/provider";
import { homeFor } from "@/access/roles";
import { ToastProvider } from "@/components/toast";
import { Button, Skeleton } from "@/components/ui";
import { RoleAwareGuard } from "@/components/RoleAwareGuard";
import { AppShell } from "@/shell/AppShell";
import { AssistantProvider } from "@/shell/assistant";
import { ThemeProvider } from "@/shell/theme";
import { Oversikt } from "@/pages/Oversikt";
import { Saker } from "@/pages/Saker";

/* Tunge sider lastes ved behov. */
const Vedlikehold = lazy(() => import("@/pages/Vedlikehold").then((m) => ({ default: m.Vedlikehold })));
const Prosjekter = lazy(() => import("@/pages/Prosjekter").then((m) => ({ default: m.Prosjekter })));
const ProsjektDetalj = lazy(() => import("@/pages/ProsjektDetalj").then((m) => ({ default: m.ProsjektDetalj })));
const Tilbud = lazy(() => import("@/pages/Tilbud").then((m) => ({ default: m.Tilbud })));
const TilbudSammenligning = lazy(() => import("@/pages/Tilbud").then((m) => ({ default: m.TilbudSammenligning })));
const TilbudNy = lazy(() => import("@/pages/Tilbud").then((m) => ({ default: m.TilbudNy })));
const Beboere = lazy(() => import("@/pages/Beboere").then((m) => ({ default: m.Beboere })));
const Dokumenter = lazy(() => import("@/pages/Dokumenter").then((m) => ({ default: m.Dokumenter })));
const Okonomi = lazy(() => import("@/pages/Okonomi").then((m) => ({ default: m.Okonomi })));
const MinBolig = lazy(() => import("@/pages/MinBolig").then((m) => ({ default: m.MinBolig })));
const Leverandor = lazy(() => import("@/pages/Leverandor").then((m) => ({ default: m.Leverandor })));
const Aktivitet = lazy(() => import("@/pages/Aktivitet").then((m) => ({ default: m.Aktivitet })));

/** Error boundary per side: en feil låser aldri hele AppShell. */
class PageBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  override state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  override componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Sidefeil", error, info.componentStack);
  }
  override render() {
    if (this.state.error) {
      return (
        <div className="state error" role="alert">
          <h3>Noe gikk galt på denne siden</h3>
          <p>{this.state.error.message}</p>
          <div className="actions">
            <Button variant="secondary" onClick={() => this.setState({ error: null })}>Prøv igjen</Button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function Page({ children }: { children: ReactNode }) {
  return (
    <PageBoundary>
      <Suspense fallback={<Skeleton lines={8} />}>{children}</Suspense>
    </PageBoundary>
  );
}

function Home() {
  const session = useSession();
  const home = homeFor(session.role);
  if (home !== "/") return <Navigate to={home} replace />;
  return (
    <RoleAwareGuard permission="board:read" what="styrets oversikt">
      <Oversikt />
    </RoleAwareGuard>
  );
}

export function App() {
  return (
    <ThemeProvider>
    <BrowserRouter basename="/app">
      <DataProvider>
        <ToastProvider>
          <AssistantProvider>
            <Routes>
              <Route element={<AppShell />}>
                <Route index element={<Page><Home /></Page>} />
                <Route path="vedlikehold" element={<Page><RoleAwareGuard permission="board:read"><Vedlikehold /></RoleAwareGuard></Page>} />
                <Route path="saker" element={<Page><RoleAwareGuard permission="issues:read"><Saker /></RoleAwareGuard></Page>} />
                <Route path="prosjekter" element={<Page><RoleAwareGuard permission="projects:read"><Prosjekter /></RoleAwareGuard></Page>} />
                <Route path="prosjekter/:id" element={<Page><RoleAwareGuard permission="projects:read"><ProsjektDetalj /></RoleAwareGuard></Page>} />
                <Route path="tilbud" element={<Page><RoleAwareGuard permission="quotes:read"><Tilbud /></RoleAwareGuard></Page>} />
                <Route path="tilbud/ny" element={<Page><TilbudNy /></Page>} />
                <Route path="tilbud/:id" element={<Page><RoleAwareGuard permission="quotes:read"><TilbudSammenligning /></RoleAwareGuard></Page>} />
                <Route path="beboere" element={<Page><RoleAwareGuard permission="residents:read"><Beboere /></RoleAwareGuard></Page>} />
                <Route path="dokumenter" element={<Page><RoleAwareGuard permission="documents:read"><Dokumenter /></RoleAwareGuard></Page>} />
                <Route path="okonomi" element={<Page><RoleAwareGuard permission="economy:read"><Okonomi /></RoleAwareGuard></Page>} />
                <Route path="aktivitet" element={<Page><RoleAwareGuard permission="board:read"><Aktivitet /></RoleAwareGuard></Page>} />
                <Route path="min-bolig" element={<Page><MinBolig /></Page>} />
                <Route path="leverandor" element={<Page><Leverandor /></Page>} />
                <Route path="*" element={<div className="state"><h3>Siden finnes ikke</h3><p>Bruk menyen for å gå videre.</p></div>} />
              </Route>
            </Routes>
          </AssistantProvider>
        </ToastProvider>
      </DataProvider>
    </BrowserRouter>
    </ThemeProvider>
  );
}
