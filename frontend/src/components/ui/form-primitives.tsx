import { ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

export function FormGrid({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn("grid gap-4 md:grid-cols-2", className)}>{children}</div>;
}

export function FormField({
  label,
  htmlFor,
  helper,
  fullWidth = false,
  children,
  className,
}: {
  label: string;
  htmlFor?: string;
  helper?: string;
  fullWidth?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("grid gap-2", fullWidth && "md:col-span-2", className)}>
      <label htmlFor={htmlFor} className="text-[0.92rem] font-semibold">
        {label}
      </label>
      {children}
      {helper ? <span className="text-sm leading-6 text-app-text-muted">{helper}</span> : null}
    </div>
  );
}

export function FormCheckbox({
  htmlFor,
  children,
  className,
}: {
  htmlFor: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <label htmlFor={htmlFor} className={cn("flex items-center gap-3 text-app-text-soft", className)}>
      {children}
    </label>
  );
}

export function InfoBox({
  children,
  tone = "brand",
  className,
}: {
  children: ReactNode;
  tone?: "brand" | "muted";
  className?: string;
}) {
  return (
    <div
      className={cn(
        "rounded-2xl border p-4 text-sm leading-7",
        tone === "brand"
          ? "border-brand-primary/20 bg-brand-primary/10 text-app-text-soft"
          : "border-app-border bg-app-surface-raised text-app-text-soft",
        className,
      )}
    >
      {children}
    </div>
  );
}
