import Link from "next/link";
import { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "secondary" | "ghost";
  fullWidth?: boolean;
}

export function Button({
  children,
  href,
  variant = "primary",
  fullWidth = false,
  className = "",
  ...props
}: ButtonProps) {
  const classes = cn(
    "inline-flex min-h-[2.9rem] items-center justify-center gap-2 rounded-full border px-4 py-3 text-sm font-semibold no-underline transition duration-150",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-bright/50 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent",
    "disabled:pointer-events-none disabled:opacity-60",
    fullWidth && "w-full",
    variant === "primary" &&
      "border-transparent bg-[linear-gradient(135deg,var(--accent-emerald),#106b78)] text-white shadow-[0_12px_24px_color-mix(in_srgb,var(--accent-emerald)_28%,transparent)] hover:-translate-y-px",
    variant === "secondary" &&
      "border-app-border-strong bg-[color-mix(in_srgb,var(--surface)_92%,transparent)] text-app-text hover:-translate-y-px",
    variant === "ghost" &&
      "border-app-border bg-transparent text-app-text-soft hover:-translate-y-px",
    className,
  );

  if (href) {
    if (!href.startsWith("/")) {
      return (
        <a href={href} className={classes}>
          {children}
        </a>
      );
    }

    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }

  return (
    <button className={classes} {...props}>
      {children}
    </button>
  );
}
