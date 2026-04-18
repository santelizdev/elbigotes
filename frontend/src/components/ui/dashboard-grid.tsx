import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function DashboardGrid({
  main,
  aside,
  className,
}: {
  main: ReactNode;
  aside?: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "grid gap-4 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,0.85fr)]",
        className,
      )}
    >
      <div className="grid gap-4">{main}</div>
      {aside ? <aside className="grid gap-4">{aside}</aside> : null}
    </div>
  );
}
