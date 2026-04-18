import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface SectionHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  compact?: boolean;
  className?: string;
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  action,
  compact = false,
  className,
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 md:flex-row md:items-start md:justify-between",
        className,
      )}
    >
      <div className="grid gap-1">
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <h2
          className={cn(
            "m-0 font-display-ui leading-[0.98]",
            compact ? "text-[clamp(1.15rem,2.2vw,1.6rem)]" : "text-[clamp(1.5rem,2.8vw,2.25rem)]",
          )}
        >
          {title}
        </h2>
        {description ? (
          <p className="m-0 max-w-[70ch] text-sm leading-7 text-app-text-soft md:text-base">
            {description}
          </p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
