import type { Metadata } from "next";
import { ReactNode } from "react";

import "@/app/globals.css";
import { SiteHeader } from "@/components/chrome/site-header";
import { siteConfig } from "@/lib/constants/site";

export const metadata: Metadata = {
  metadataBase: new URL(siteConfig.siteUrl),
  title: siteConfig.defaultTitle,
  description: siteConfig.description,
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400..800&family=Nunito+Sans:ital,opsz,wght@0,6..12,200..1000;1,6..12,200..1000&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (() => {
                const storedTheme = localStorage.getItem("elbigotes-theme");
                const theme =
                  storedTheme ||
                  (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
                document.documentElement.dataset.theme = theme;
              })();
            `,
          }}
        />
        {/* El layout deja el header persistente para reforzar orientación cuando el usuario navega entre mapa, categorías y publicación. */}
        <SiteHeader />
        <main className="page-shell">{children}</main>
        <footer className="site-footer">
          Elbigotes está diseñado como infraestructura pública geolocalizada para el ecosistema pet,
          no como un tablero de avisos aislados.
        </footer>
      </body>
    </html>
  );
}
