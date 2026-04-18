import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function SurfaceCard({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={cn(
        "rounded-[1.4rem] border border-app-border bg-app-surface p-6 shadow-soft",
        className,
      )}
    >
      {children}
    </section>
  );
}
