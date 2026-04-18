import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface TagProps {
  children: ReactNode;
  tone?: "neutral" | "accent" | "success" | "warning";
}

export function Tag({ children, tone = "neutral" }: TagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold",
        tone === "neutral" && "bg-white/5 text-app-text-soft",
        tone === "accent" && "bg-brand-bright/15 text-brand-blue",
        tone === "success" && "bg-brand-primary/15 text-brand-primary",
        tone === "warning" && "bg-state-warning/15 text-state-warning",
      )}
    >
      {children}
    </span>
  );
}
