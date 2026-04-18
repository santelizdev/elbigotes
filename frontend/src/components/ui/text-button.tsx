import { ButtonHTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils/cn";

interface TextButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
}

export function TextButton({
  children,
  className,
  type = "button",
  ...props
}: TextButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "appearance-none border-none bg-transparent p-0 font-semibold text-brand-bright transition duration-150 hover:text-brand-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-bright/50 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
