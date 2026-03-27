"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import styles from "@/components/chrome/site-header.module.css";
import { ThemeToggleButton } from "@/components/chrome/theme-toggle";
import { CategoryDefinition } from "@/lib/constants/categories";

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
      className={open ? styles.chevronOpen : ""}
    >
      <path
        d="M7.47 9.97a.75.75 0 0 1 1.06 0L12 13.44l3.47-3.47a.75.75 0 1 1 1.06 1.06l-4 4a.75.75 0 0 1-1.06 0l-4-4a.75.75 0 0 1 0-1.06Z"
        fill="currentColor"
      />
    </svg>
  );
}

export function SiteHeader({ categories }: SiteHeaderProps) {
  const pathname = usePathname();
  const categoriesMenuRef = useRef<HTMLDivElement | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCategoriesOpen, setIsCategoriesOpen] = useState(false);
  const [theme, setTheme] = useState<ThemeMode>(() => getCurrentTheme());

  const placeNavItems = categories
    .filter((category) => category.kind === "place")
    .map((category) => ({
      href: category.route,
      label: category.shortLabel,
    }));

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

  const publishButtonClass =
    theme === "dark" ? styles.publishButtonLight : styles.publishButtonMint;

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          <div className={styles.logoFrame}>
            <Image
              src="/logo-placeholder.svg"
              alt="Logo temporal de Elbigotes"
              width={52}
              height={52}
              className={styles.logoImage}
              priority
            />
          </div>
          <div className={styles.brandBlock}>
            <span className={styles.brandTitle}>Elbigotes</span>
          </div>
        </Link>

        <nav className={styles.desktopNav} aria-label="Navegación principal">
          <div className={styles.desktopNavInner}>
            <div className={styles.dropdown} ref={categoriesMenuRef}>
              <button
                type="button"
                className={styles.dropdownTrigger}
                aria-expanded={isCategoriesOpen}
                aria-controls="desktop-categories-menu"
                onClick={() => setIsCategoriesOpen((current) => !current)}
              >
                <span className={styles.navIcon}>
                  <CategoriesIcon />
                </span>
                <span>Categorías</span>
                <ChevronIcon open={isCategoriesOpen} />
              </button>

              {isCategoriesOpen ? (
                <div id="desktop-categories-menu" className={styles.dropdownPanel}>
                  <ul className={styles.dropdownList}>
                    {placeNavItems.map((item) => (
                      <li key={item.href}>
                        <Link href={item.href} className={styles.dropdownLink}>
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>

            <Link href="/mascotas-perdidas" className={styles.navLink}>
              Mascotas perdidas
            </Link>

            <Link href="/reviews" className={styles.navLink}>
              Reviews
            </Link>

            <Link href="/ingresar" className={styles.iconLink}>
              <span className={styles.navIcon}>
                <UserIcon />
              </span>
              <span>Ingresar</span>
            </Link>

            <ThemeToggleButton compact />

            <Link
              href="/publicar-mascota-perdida"
              className={`${styles.publishButton} ${publishButtonClass}`}
            >
              Publicar
            </Link>
          </div>
        </nav>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.menuButton}
            aria-expanded={isMenuOpen}
            aria-controls="mobile-site-nav"
            aria-label={isMenuOpen ? "Cerrar menú principal" : "Abrir menú principal"}
            onClick={() => setIsMenuOpen((current) => !current)}
          >
            <span className={styles.menuLine} />
            <span className={styles.menuLine} />
            <span className={styles.menuLine} />
          </button>
        </div>
      </div>

      <nav
        id="mobile-site-nav"
        className={`${styles.mobileNav} ${isMenuOpen ? styles.mobileNavOpen : ""}`.trim()}
        aria-label="Navegación principal móvil"
      >
        <div className={styles.mobileNavInner}>
          <div className={styles.mobileSection}>
            <span className={styles.mobileSectionTitle}>Categorías</span>
            <ul className={styles.mobileCategoryList}>
              {placeNavItems.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className={styles.mobileNavLink}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <Link href="/mascotas-perdidas" className={styles.mobileNavLink}>
            Mascotas perdidas
          </Link>

          <Link href="/reviews" className={styles.mobileNavLink}>
            Reviews
          </Link>

          <Link href="/ingresar" className={styles.mobileNavLink}>
            <span className={styles.navIcon}>
              <UserIcon />
            </span>
            <span>Ingresar</span>
          </Link>

          <div className={styles.mobileFooterActions}>
            <ThemeToggleButton compact />
            <Link
              href="/publicar-mascota-perdida"
              className={`${styles.publishButton} ${publishButtonClass} ${styles.publishButtonBlock}`}
            >
              Publicar
            </Link>
          </div>
        </div>
      </nav>

      {isMenuOpen ? (
        <button
          type="button"
          className={styles.backdrop}
          aria-label="Cerrar menú"
          onClick={() => setIsMenuOpen(false)}
        />
      ) : null}
    </header>
  );
}
