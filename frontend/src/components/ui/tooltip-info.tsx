"use client";

import { useId, useState } from "react";
import { FaCircleInfo } from "react-icons/fa6";

import { cn } from "@/lib/utils/cn";

interface TooltipInfoProps {
  label: string;
  content: string;
  className?: string;
}

export function TooltipInfo({ label, content, className }: TooltipInfoProps) {
  const [isOpen, setIsOpen] = useState(false);
  const tooltipId = useId();

  return (
    <span
      className={cn("relative inline-flex items-center", className)}
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      <button
        type="button"
        aria-label={label}
        aria-describedby={tooltipId}
        aria-expanded={isOpen}
        className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-app-border bg-app-surface-raised text-[0.72rem] text-app-text-soft transition hover:text-app-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-bright/50"
        onFocus={() => setIsOpen(true)}
        onBlur={() => setIsOpen(false)}
        onClick={() => setIsOpen((current) => !current)}
      >
        <FaCircleInfo className="h-3.5 w-3.5" aria-hidden="true" />
      </button>

      <span
        id={tooltipId}
        role="tooltip"
        className={cn(
          "pointer-events-none absolute left-0 top-[calc(100%+0.5rem)] z-20 w-72 rounded-2xl border border-app-border-strong bg-app-surface-raised p-3 text-xs leading-6 text-app-text-soft shadow-soft transition duration-150",
          isOpen ? "translate-y-0 opacity-100" : "translate-y-1 opacity-0",
        )}
      >
        {content}
      </span>
    </span>
  );
}
