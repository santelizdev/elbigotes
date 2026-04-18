import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function PageShell({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn("grid gap-6 py-8 md:gap-8", className)}>{children}</div>;
}
