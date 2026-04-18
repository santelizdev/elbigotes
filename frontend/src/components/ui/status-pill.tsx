import { cn } from "@/lib/utils/cn";

interface StatusPillProps {
  label: string;
  tone?: "neutral" | "success" | "warning" | "critical";
}

export function StatusPill({ label, tone = "neutral" }: StatusPillProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold",
        tone === "neutral" && "bg-white/5 text-app-text-soft",
        tone === "success" && "bg-brand-primary/15 text-brand-primary",
        tone === "warning" && "bg-state-warning/15 text-state-warning",
        tone === "critical" && "bg-state-danger/20 text-state-danger",
      )}
    >
      {label}
    </span>
  );
}
