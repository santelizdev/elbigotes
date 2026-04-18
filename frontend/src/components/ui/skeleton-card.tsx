import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function SkeletonCard({
  className,
  children,
}: {
  className?: string;
  children?: ReactNode;
}) {
  return (
    <article
      className={cn(
        "grid gap-4 rounded-[1.35rem] border border-app-border bg-[color-mix(in_srgb,var(--surface)_88%,transparent)] p-4",
        className,
      )}
      aria-hidden="true"
    >
      {children}
    </article>
  );
}

export function SkeletonLine({
  width = "full",
  size = "body",
}: {
  width?: "full" | "eyebrow" | "title";
  size?: "body" | "title";
}) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-full bg-white/6 after:absolute after:inset-0 after:translate-x-[-100%] after:bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.14),transparent)] after:content-[''] after:animate-[shimmer_1.2s_ease-in-out_infinite]",
        size === "body" && "h-[0.9rem]",
        size === "title" && "h-[1.25rem]",
        width === "full" && "w-full",
        width === "eyebrow" && "w-[35%]",
        width === "title" && "w-[72%]",
      )}
    />
  );
}
