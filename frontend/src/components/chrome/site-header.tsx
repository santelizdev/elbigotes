"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { ThemeToggleButton } from "@/components/chrome/theme-toggle";
import { CategoryDefinition } from "@/lib/constants/categories";
import { cn } from "@/lib/utils/cn";

interface SiteHeaderProps {
  categories: CategoryDefinition[];
}

type ThemeMode = "dark" | "light";

function getCurrentTheme(): ThemeMode {
  if (typeof document === "undefined") {
    return "light";
  }

  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M12 12.25a4.25 4.25 0 1 0-4.25-4.25A4.25 4.25 0 0 0 12 12.25Zm0 1.5c-4.22 0-7.75 2.47-7.75 5.5a.75.75 0 0 0 1.5 0c0-2 2.62-4 6.25-4s6.25 2 6.25 4a.75.75 0 0 0 1.5 0c0-3.03-3.53-5.5-7.75-5.5Z"
        fill="currentColor"
      />
    </svg>
  );
}

function CategoriesIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M5 6.25A1.25 1.25 0 1 1 6.25 7.5 1.25 1.25 0 0 1 5 6.25Zm0 5.75A1.25 1.25 0 1 1 6.25 13.25 1.25 1.25 0 0 1 5 12Zm0 5.75A1.25 1.25 0 1 1 6.25 19 1.25 1.25 0 0 1 5 17.75ZM9.5 7a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5A.75.75 0 0 1 9.5 7Zm0 5.75a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1-.75-.75Zm0 5.75a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1-.75-.75Z"
        fill="currentColor"
      />
    </svg>
  );
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      role="presentation"
      focusable="false"
      className={cn("h-4 w-4 transition-transform duration-150", open && "rotate-180")}
    >
      <path
        d="M7.47 9.97a.75.75 0 0 1 1.06 0L12 13.44l3.47-3.47a.75.75 0 1 1 1.06 1.06l-4 4a.75.75 0 0 1-1.06 0l-4-4a.75.75 0 0 1 0-1.06Z"
        fill="currentColor"
      />
    </svg>
  );
}

function MenuIcon() {
  return (
    <span className="flex flex-col items-center justify-center gap-1">
      <span className="h-0.5 w-4 rounded-full bg-current" />
      <span className="h-0.5 w-4 rounded-full bg-current" />
      <span className="h-0.5 w-4 rounded-full bg-current" />
    </span>
  );
}

const navLinkClass =
  "inline-flex min-h-[2.9rem] items-center gap-2 rounded-full border border-transparent px-4 py-2.5 text-[0.94rem] text-app-text-muted transition duration-150 hover:bg-white/5 hover:text-app-text";

export function SiteHeader({ categories }: SiteHeaderProps) {
  const pathname = usePathname();
  const categoriesMenuRef = useRef<HTMLDivElement | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCategoriesOpen, setIsCategoriesOpen] = useState(false);
  // Keep the initial render SSR-safe, then hydrate the real client theme.
  const [theme, setTheme] = useState<ThemeMode>("light");

  const placeNavItems = categories
    .filter((category) => category.kind === "place")
    .map((category) => ({
      href: category.route,
      label: category.shortLabel,
    }))
    .concat({
      href: "/jornadas-operativos",
      label: "Jornadas/Operativos",
    });

  useEffect(() => {
    setIsMenuOpen(false);
    setIsCategoriesOpen(false);
  }, [pathname]);

  useEffect(() => {
    setTheme(getCurrentTheme());
    const observer = new MutationObserver(() => {
      setTheme(getCurrentTheme());
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (!categoriesMenuRef.current?.contains(event.target as Node)) {
        setIsCategoriesOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (!isMenuOpen) {
      return;
    }

    // Keep the mobile drawer easy to dismiss even when the overlay is open.
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsMenuOpen(false);
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isMenuOpen]);

  const publishButtonClass =
    theme === "dark"
      ? "border border-[#123038]/10 bg-white text-[#123038]"
      : "border-transparent bg-[linear-gradient(135deg,var(--accent-emerald),#106b78)] text-white";

  return (
    <header className="sticky top-0 z-40 overflow-visible border-b border-app-border-strong bg-[color-mix(in_srgb,var(--surface)_88%,transparent)] backdrop-blur-[18px]">
      <div className="mx-auto flex w-[min(1440px,calc(100vw-2rem))] items-center justify-between gap-4 py-3 max-[860px]:py-3">
        <Link href="/" className="flex min-w-0 items-center gap-4 text-inherit no-underline">
          <div className="grid h-[3.35rem] w-[3.35rem] shrink-0 place-items-center rounded-[1.15rem] max-[560px]:h-[3.05rem] max-[560px]:w-[3.05rem]">
            <Image
              src="/icon-elbigotes.png"
              alt="Logo de Elbigotes"
              width={52}
              height={52}
              className="h-[2.65rem] w-[2.65rem]"
              priority
            />
          </div>
          <div className="grid gap-0.5">
            <span className="font-display-ui text-[1.04rem] font-bold max-[560px]:text-[0.98rem]">
              ElBigotes
            </span>
          </div>
        </Link>

        <nav className="min-w-0 flex-1 max-[860px]:hidden" aria-label="Navegación principal">
          <div className="flex items-center justify-end gap-2 whitespace-nowrap max-[980px]:gap-1">
            <div className="relative" ref={categoriesMenuRef}>
              <button
                type="button"
                className={navLinkClass}
                aria-expanded={isCategoriesOpen}
                aria-controls="desktop-categories-menu"
                onClick={() => setIsCategoriesOpen((current) => !current)}
              >
                <span className="grid h-4 w-4 place-items-center">
                  <CategoriesIcon />
                </span>
                <span>Categorías</span>
                <ChevronIcon open={isCategoriesOpen} />
              </button>

              {isCategoriesOpen ? (
                <div
                  id="desktop-categories-menu"
                  className="absolute right-0 top-[calc(100%+0.55rem)] min-w-56 rounded-[1.2rem] border border-app-border-strong bg-[color-mix(in_srgb,var(--surface-raised)_96%,transparent)] p-2 shadow-[0_22px_48px_rgba(0,0,0,0.24)]"
                >
                  <ul className="grid list-none gap-1 p-0 m-0">
                    {placeNavItems.map((item) => (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          className="block rounded-2xl px-4 py-3 text-app-text no-underline transition duration-150 hover:bg-white/5"
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>

            <Link href="/reviews" className={navLinkClass}>
              Reviews
            </Link>

            <Link href="/ingresar" className={navLinkClass}>
              <span className="grid h-4 w-4 place-items-center">
                <UserIcon />
              </span>
              <span>Ingresar</span>
            </Link>

            <ThemeToggleButton compact />

            <Link
              href="/registro/negocio"
              className={cn(
                "inline-flex min-h-[2.9rem] items-center justify-center rounded-full border px-4 py-3 font-semibold no-underline shadow-[0_14px_28px_rgba(7,20,25,0.08)] transition duration-150 hover:-translate-y-px",
                publishButtonClass,
              )}
            >
              Registrar negocio
            </Link>
          </div>
        </nav>

        <div className="relative z-[43] flex shrink-0 items-center gap-2 min-[861px]:hidden">
          <button
            type="button"
            className="inline-flex h-[2.9rem] w-[2.9rem] items-center justify-center rounded-full border border-app-border-strong bg-white/5 text-app-text"
            aria-expanded={isMenuOpen}
            aria-controls="mobile-site-nav"
            aria-label={isMenuOpen ? "Cerrar menú principal" : "Abrir menú principal"}
            onClick={() => setIsMenuOpen((current) => !current)}
          >
            <MenuIcon />
          </button>
        </div>
      </div>

      {isMenuOpen ? (
        <nav
          id="mobile-site-nav"
          className="absolute left-2 right-2 top-[calc(100%+0.35rem)] z-[42] min-[861px]:hidden"
          aria-label="Navegación principal móvil"
        >
          <div className="grid gap-3 rounded-[1.35rem] border border-app-border-strong bg-[color-mix(in_srgb,var(--surface-raised)_95%,transparent)] p-4 shadow-[0_20px_48px_rgba(0,0,0,0.24)]">
            <div className="grid gap-2">
              <span className="text-[0.76rem] uppercase tracking-[0.14em] text-app-text-muted">
                Categorías
              </span>
              <ul className="m-0 grid list-none gap-1 p-0">
                {placeNavItems.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
                    >
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <Link
              href="/reviews"
              className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
            >
              Reviews
            </Link>

            <Link
              href="/ingresar"
              className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
            >
              <span className="grid h-4 w-4 place-items-center">
                <UserIcon />
              </span>
              <span>Ingresar</span>
            </Link>

            <div className="grid gap-3">
              <ThemeToggleButton compact />
              <Link
                href="/registro/negocio"
                className={cn(
                  "inline-flex min-h-[2.9rem] w-full items-center justify-center rounded-full border px-4 py-3 font-semibold no-underline shadow-[0_14px_28px_rgba(7,20,25,0.08)]",
                  publishButtonClass,
                )}
              >
                Registrar negocio
              </Link>
            </div>
          </div>
        </nav>
      ) : null}

      {isMenuOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-[41] border-0 bg-transparent min-[861px]:hidden"
          aria-label="Cerrar menú"
          onClick={() => setIsMenuOpen(false)}
        />
      ) : null}
    </header>
  );
}
