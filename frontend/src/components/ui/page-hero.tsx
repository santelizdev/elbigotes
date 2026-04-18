import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface PageHeroProps {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
}

export function PageHero({
  eyebrow,
  title,
  description,
  actions,
  className,
}: PageHeroProps) {
  return (
    <section
      className={cn(
        "grid gap-4 rounded-[1.75rem] border border-app-border-strong bg-[radial-gradient(circle_at_top_left,color-mix(in_srgb,var(--accent-emerald)_18%,transparent),transparent_30%),linear-gradient(180deg,color-mix(in_srgb,var(--surface-raised)_94%,transparent),var(--surface))] p-7 shadow-soft",
        className,
      )}
    >
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <div className="grid gap-3">
        <h1 className="page-title">{title}</h1>
        {description ? <p className="page-lead">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
    </section>
  );
}
