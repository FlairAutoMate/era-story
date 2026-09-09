import { useQuery } from "@/data/provider";
import { PageHead } from "@/shell/AppShell";
import { ActivityTimeline } from "@/components/domain";
import { Card, ErrorState, Skeleton } from "@/components/ui";

export function Aktivitet() {
  const act = useQuery((a, s) => a.listActivity(s));
  return (
    <>
      <PageHead title="Aktivitet" meta={act.data ? [`${act.data.length} hendelser`] : []} />
      <Card pad>{act.status === "error" ? <ErrorState error={act.error} retry={act.reload} /> : act.data ? <ActivityTimeline items={act.data} /> : <Skeleton lines={10} />}</Card>
    </>
  );
}
