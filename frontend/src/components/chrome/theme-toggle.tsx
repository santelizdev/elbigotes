"use client";

import { useEffect, useState } from "react";

type ThemeMode = "dark" | "light";

function getInitialTheme(): ThemeMode {
  if (typeof document === "undefined") {
    return "dark";
  }

  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function ThemeToggle() {
  return <ThemeToggleButton />;
}

export function ThemeToggleButton({ compact = false }: { compact?: boolean }) {
  const [theme, setTheme] = useState<ThemeMode>("dark");

  useEffect(() => {
    setTheme(getInitialTheme());
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
      aria-label={`Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}`}
      title={`Cambiar a tema ${theme === "dark" ? "claro" : "oscuro"}`}
    >
      <span className="theme-toggle__icon" aria-hidden="true">
        {theme === "dark" ? "☀" : "☾"}
      </span>
      <span className="theme-toggle__label">{theme === "dark" ? "Light" : "Dark"}</span>
    </button>
  );
}
