import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

function Spinner() {
  return (
    <div
      className="h-7 w-7 animate-spin rounded-full border-2 border-white/10 border-t-brand-primary"
      aria-hidden="true"
    />
  );
}

interface FeedbackPanelProps {
  title?: string;
  message: ReactNode;
  tone?: "default" | "error";
  loading?: boolean;
  className?: string;
}

export function FeedbackPanel({
  title,
  message,
  tone = "default",
  loading = false,
  className,
}: FeedbackPanelProps) {
  return (
    <div
      className={cn(
        "grid place-items-center gap-3 rounded-[1.15rem] border p-6 text-center",
        tone === "error"
          ? "border-state-danger/25 bg-state-danger/5 text-app-text-soft"
          : "border-dashed border-app-border-strong bg-white/5 text-app-text-soft",
        className,
      )}
    >
      {loading ? <Spinner /> : null}
      {title ? <p className="m-0 font-semibold text-app-text">{title}</p> : null}
      <div>{message}</div>
    </div>
  );
}
