"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import styles from "@/components/chrome/site-header.module.css";
import { ThemeToggleButton } from "@/components/chrome/theme-toggle";
import { Button } from "@/components/ui/button";
import { CategoryDefinition } from "@/lib/constants/categories";

interface SiteHeaderProps {
  categories: CategoryDefinition[];
}

export function SiteHeader({ categories }: SiteHeaderProps) {
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const placeNavItems = categories
    .filter((category) => category.kind === "place")
    .map((category) => ({
      href: category.route,
      label: category.shortLabel,
    }));
  const utilityNavItems = [
    { href: "/mascotas-perdidas", label: "Mascotas perdidas" },
    { href: "/registro", label: "Registro" },
  ];
  const navItems = [...placeNavItems, ...utilityNavItems];

  useEffect(() => {
    setIsMenuOpen(false);
  }, [pathname]);

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          <div className={styles.mark}>E</div>
          <div className={styles.brandBlock}>
            <span className={styles.brandTitle}>Elbigotes</span>
            {/*<span className={styles.brandSubtitle}>Mapa público del ecosistema pet</span> */}
          </div>
        </Link>

        <nav className={styles.desktopNav} aria-label="Navegación principal">
          <div className={styles.desktopNavInner}>
            {navItems.map((item) => (
              <Link key={item.href} href={item.href} className={styles.navLink}>
                {item.label}
              </Link>
            ))}
            <Button href="/publicar-mascota-perdida" variant="secondary">
              Publicar 📢
            </Button>
          </div>
        </nav>

        <div className={styles.actions}>
          <ThemeToggleButton compact />
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
          {navItems.map((item) => (
            <Link key={item.href} href={item.href} className={styles.mobileNavLink}>
              {item.label}
            </Link>
          ))}
          <Button href="/publicar-mascota-perdida" variant="secondary" fullWidth>
            Publicar 📢
          </Button>
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
