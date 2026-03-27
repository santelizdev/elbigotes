"use client";

import { useEffect, useState } from "react";

type ThemeMode = "dark" | "light";

function getInitialTheme(): ThemeMode {
  if (typeof document === "undefined") {
    return "light";
  }

  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function ThemeToggle() {
  return <ThemeToggleButton />;
}

export function ThemeToggleButton({ compact = false }: { compact?: boolean }) {
  const [theme, setTheme] = useState<ThemeMode>(() => getInitialTheme());
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setTheme(getInitialTheme());
    setMounted(true);
  }, []);

  function handleToggle() {
    const nextTheme: ThemeMode = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem("elbigotes-theme", nextTheme);
    setTheme(nextTheme);
  }

  return (
    <button
      type="button"
      className={`theme-toggle ${compact ? "theme-toggle--compact" : ""}`.trim()}
      onClick={handleToggle}
      aria-label={
        mounted ? `Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}` : "Cambiar tema"
      }
      title={mounted ? `Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}` : "Cambiar tema"}
    >
      <span className="theme-toggle__icon" aria-hidden="true">
        {mounted ? (
          theme === "dark" ? (
            <svg viewBox="0 0 24 24" role="presentation" focusable="false">
              <path
                d="M12 4.75a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V5.5a.75.75 0 0 1 .75-.75Zm0 12.75a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-1.5 0V18.25a.75.75 0 0 1 .75-.75Zm7.25-6.25a.75.75 0 0 1 0 1.5h-1.5a.75.75 0 0 1 0-1.5h1.5Zm-12.75 0a.75.75 0 0 1 0 1.5H5a.75.75 0 0 1 0-1.5h1.5Zm10.02-4.77a.75.75 0 0 1 1.06 1.06l-1.06 1.06a.75.75 0 0 1-1.06-1.06l1.06-1.06Zm-9.04 9.04a.75.75 0 1 1 1.06 1.06l-1.06 1.06a.75.75 0 0 1-1.06-1.06l1.06-1.06Zm10.1 1.06a.75.75 0 0 1-1.06 0l-1.06-1.06a.75.75 0 0 1 1.06-1.06l1.06 1.06a.75.75 0 0 1 0 1.06Zm-9.04-9.04a.75.75 0 0 1-1.06 0L6.42 7.54a.75.75 0 0 1 1.06-1.06l1.06 1.06a.75.75 0 0 1 0 1.06ZM12 8.25A3.75 3.75 0 1 1 8.25 12 3.75 3.75 0 0 1 12 8.25Z"
                fill="currentColor"
              />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" role="presentation" focusable="false">
              <path
                d="M14.8 3.3a.75.75 0 0 1 .84.95 7.25 7.25 0 0 0 8.11 9.11.75.75 0 0 1 .74 1.18A10.25 10.25 0 1 1 13.46 2.56a.75.75 0 0 1 1.34.74Z"
                fill="currentColor"
              />
            </svg>
          )
        ) : (
          <svg viewBox="0 0 24 24" role="presentation" focusable="false">
            <path
              d="M12 3.75a8.25 8.25 0 1 0 0 16.5V3.75Z"
              fill="currentColor"
              opacity=".9"
            />
            <path
              d="M12 3.75a8.25 8.25 0 0 1 0 16.5V3.75Z"
              fill="currentColor"
              opacity=".35"
            />
          </svg>
        )}
      </span>
      <span className="theme-toggle__label">
        {mounted ? (theme === "dark" ? "Light" : "Dark") : "Tema"}
      </span>
    </button>
  );
}
