import { LoadingPanel } from "@/components/shared/loading-panel";

import { SkeletonCard } from "@/components/ui/skeleton-card";

export function MapLoadingShell({
  message = "Preparando mapa interactivo...",
}: {
  message?: string;
}) {
  return (
    <div className="grid h-full min-h-[20rem] content-center gap-4 p-5">
      <LoadingPanel message={message} />
      <div className="grid gap-3 md:grid-cols-3" aria-hidden="true">
        <SkeletonCard className="h-[5.5rem] rounded-[1.1rem] bg-white/6" />
        <SkeletonCard className="h-[5.5rem] rounded-[1.1rem] bg-white/6" />
        <SkeletonCard className="h-[5.5rem] rounded-[1.1rem] bg-white/6" />
      </div>
    </div>
  );
}
