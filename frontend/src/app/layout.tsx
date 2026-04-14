import type { Metadata } from "next";
import { ReactNode } from "react";
import Script from "next/script";

import "@/app/globals.css";
import { SiteHeader } from "@/components/chrome/site-header";
import { siteConfig } from "@/lib/constants/site";
import { getPublicCategories } from "@/lib/services/taxonomy-service";


export const metadata = {
  metadataBase: new URL('https://www.elbigotes.cl'),
  title: {
    default: 'Elbigotes | Ecosistema pet en Chile',
    template: '%s | Elbigotes',
  },
  description: 'Directorio geolocalizado de servicios para mascotas en Chile',
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const categories = await getPublicCategories();

  return (
    <html lang="es" suppressHydrationWarning data-theme="light">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@400..800&family=Nunito+Sans:ital,opsz,wght@0,6..12,200..1000;1,6..12,200..1000&display=swap"
          rel="stylesheet"
        />
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            (() => {
              const storedTheme = localStorage.getItem("elbigotes-theme");
              const theme = storedTheme || "light";
              document.documentElement.dataset.theme = theme;
            })();
          `}
        </Script>
        <Script id="ga4">
              {`
              window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', 'G-Q31EB1NWRV');
              `}
      </Script>
import Script from "next/script";

<Script id="clarity" strategy="afterInteractive">
{`
(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window, document, "clarity", "script", "wbmwz86s1d");
`}
</Script>
      </head>
      <body>
        {/* El layout deja el header persistente para reforzar orientación cuando el usuario navega entre mapa, categorías y publicación. */}
        <SiteHeader categories={categories} />
        <main className="page-shell">{children}</main>
        <footer className="site-footer">
          Elbigotes está diseñado como infraestructura pública geolocalizada para el ecosistema pet,
          no como un tablero de avisos aislados.
          <br />
          <strong>
            Los datos de este directorio provienen de fuentes públicas. Si eres el titular y deseas modificar o eliminar la información, contáctanos en <a href="mailto:elbigoteslatam@gmail.com">elbigoteslatam@gmail.com</a> .
          </strong>
        </footer>
      </body>
    </html>
  );
}
