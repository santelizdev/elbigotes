"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { ThemeToggleButton } from "@/components/chrome/theme-toggle";
import { CategoryDefinition } from "@/lib/constants/categories";
import {
  clearStoredAccessToken,
  getStoredAccessToken,
} from "@/lib/services/accounts-service";
import { cn } from "@/lib/utils/cn";

interface SiteHeaderProps {
  categories: CategoryDefinition[];
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

function LogoutIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M13.25 4a.75.75 0 0 1 .75-.75h3A2.75 2.75 0 0 1 19.75 6v12A2.75 2.75 0 0 1 17 20.75h-3a.75.75 0 0 1 0-1.5h3A1.25 1.25 0 0 0 18.25 18V6A1.25 1.25 0 0 0 17 4.75h-3a.75.75 0 0 1-.75-.75Zm-6.22 7.47a.75.75 0 0 0 0 1.06l2.75 2.75a.75.75 0 1 0 1.06-1.06l-1.47-1.47H15a.75.75 0 0 0 0-1.5H9.37l1.47-1.47a.75.75 0 0 0-1.06-1.06l-2.75 2.75Z"
        fill="currentColor"
      />
    </svg>
  );
}

function RegisterIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M12 12.25a4.25 4.25 0 1 0-4.25-4.25A4.25 4.25 0 0 0 12 12.25Zm0 1.5c-4.22 0-7.75 2.47-7.75 5.5a.75.75 0 0 0 1.5 0c0-2 2.62-4 6.25-4 1.03 0 2 .16 2.87.46a.75.75 0 1 0 .5-1.41 10.06 10.06 0 0 0-3.37-.55Zm6-2a.75.75 0 0 0-.75.75V14h-1.5a.75.75 0 0 0 0 1.5h1.5V17a.75.75 0 0 0 1.5 0v-1.5h1.5a.75.75 0 0 0 0-1.5h-1.5v-1.5a.75.75 0 0 0-.75-.75Z"
        fill="currentColor"
      />
    </svg>
  );
}

function ClaimBusinessIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M4.75 5A2.75 2.75 0 0 1 7.5 2.25h9A2.75 2.75 0 0 1 19.25 5v2.47l.53.53a.75.75 0 0 1 0 1.06l-1.03 1.03V18A2.75 2.75 0 0 1 16 20.75H7.5A2.75 2.75 0 0 1 4.75 18V5Zm1.5 0A1.25 1.25 0 0 0 7.5 6.25h9A1.25 1.25 0 0 0 17.75 5 1.25 1.25 0 0 0 16.5 3.75h-9A1.25 1.25 0 0 0 6.25 5Zm0 3.37V18A1.25 1.25 0 0 0 7.5 19.25H16A1.25 1.25 0 0 0 17.25 18v-6.47l-1.72 1.72a.75.75 0 0 1-.53.22h-1.5a.75.75 0 0 1-.75-.75v-1.5a.75.75 0 0 1 .22-.53l4.69-4.69V7.75h-11Zm8 3.59v.01h.01l3.93-3.94-.01-.01-3.93 3.94Z"
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
  const router = useRouter();
  const categoriesMenuRef = useRef<HTMLDivElement | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCategoriesOpen, setIsCategoriesOpen] = useState(false);
  const [isMobileCategoriesOpen, setIsMobileCategoriesOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

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
    setIsMobileCategoriesOpen(false);
  }, [pathname]);

  useEffect(() => {
    function syncAuthState() {
      setIsAuthenticated(Boolean(getStoredAccessToken()));
    }

    syncAuthState();
    window.addEventListener("storage", syncAuthState);
    window.addEventListener("elbigotes-auth-changed", syncAuthState);

    return () => {
      window.removeEventListener("storage", syncAuthState);
      window.removeEventListener("elbigotes-auth-changed", syncAuthState);
    };
  }, []);

  useEffect(() => {
    setIsAuthenticated(Boolean(getStoredAccessToken()));
  }, [pathname]);

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

  function handleLogout() {
    clearStoredAccessToken();
    setIsMenuOpen(false);
    setIsCategoriesOpen(false);
    setIsMobileCategoriesOpen(false);
    router.push("/");
    router.refresh();
  }

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

            {isAuthenticated ? (
              <button type="button" className={navLinkClass} onClick={handleLogout}>
                <span className="grid h-4 w-4 place-items-center">
                  <LogoutIcon />
                </span>
                <span>Salir</span>
              </button>
            ) : (
              <Link href="/ingresar" className={navLinkClass}>
                <span className="grid h-4 w-4 place-items-center">
                  <UserIcon />
                </span>
                <span>Ingresar</span>
              </Link>
            )}

            <ThemeToggleButton compact />

            <Link
              href="/registro/negocio"
              className={cn(
                "site-header-business-cta inline-flex min-h-[2.9rem] items-center justify-center rounded-full px-4 py-3 font-semibold no-underline transition duration-150 hover:-translate-y-px",
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
            <button
              type="button"
              className="inline-flex w-full items-center justify-between rounded-2xl bg-white/5 px-4 py-3 text-app-text"
              aria-expanded={isMobileCategoriesOpen}
              aria-controls="mobile-categories-menu"
              onClick={() => setIsMobileCategoriesOpen((current) => !current)}
            >
              <span className="inline-flex items-center gap-2">
                <span className="grid h-4 w-4 place-items-center">
                  <CategoriesIcon />
                </span>
                <span>Categorías</span>
              </span>
              <ChevronIcon open={isMobileCategoriesOpen} />
            </button>

            {isMobileCategoriesOpen ? (
              <ul id="mobile-categories-menu" className="m-0 grid list-none gap-1 p-0">
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
            ) : null}

            <Link
              href="/reviews"
              className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
            >
              Reviews
            </Link>

            {isAuthenticated ? (
              <button
                type="button"
                className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
                onClick={handleLogout}
              >
                <span className="grid h-4 w-4 place-items-center">
                  <LogoutIcon />
                </span>
                <span>Salir</span>
              </button>
            ) : (
              <Link
                href="/ingresar"
                className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
              >
                <span className="grid h-4 w-4 place-items-center">
                  <UserIcon />
                </span>
                <span>Iniciar sesión</span>
              </Link>
            )}

            <Link
              href="/registro"
              className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
            >
              <span className="grid h-4 w-4 place-items-center">
                <RegisterIcon />
              </span>
              <span>Registrarse</span>
            </Link>

            <Link
              href="/reclamar-negocio"
              className="inline-flex w-full items-center gap-2 rounded-2xl bg-white/5 px-4 py-3 text-app-text no-underline"
            >
              <span className="grid h-4 w-4 place-items-center">
                <ClaimBusinessIcon />
              </span>
              <span>Reclamar negocio</span>
            </Link>

            <div className="grid gap-3">
              <ThemeToggleButton compact />
              <Link
                href="/registro/negocio"
                className={cn(
                  "site-header-business-cta inline-flex min-h-[2.9rem] w-full items-center justify-center rounded-full px-4 py-3 font-semibold no-underline",
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
