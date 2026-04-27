import { Metadata } from "next";

import { Button } from "@/components/ui/button";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";

export const metadata: Metadata = {
  title: "Reclamar negocio | Elbigotes",
  description: "Guía rápida para reclamar la administración de una ficha comercial en Elbigotes.",
};

export default function ReclamarNegocioPage() {
  return (
    <PageShell className="gap-5 py-6 md:gap-6">
      <PageHero
        eyebrow="Propiedad comercial"
        title="Reclama la administración de tu negocio"
        description="Si ya existe una ficha pública de tu negocio en Elbigotes, puedes solicitar su administración desde el detalle del lugar."
        className="p-6"
      />

      <SurfaceCard className="grid gap-4 p-5 md:p-6">
        <h2 className="m-0 font-display-ui text-[1.85rem] leading-tight">Cómo hacerlo</h2>
        <p className="m-0 leading-7 text-app-text-soft">
          Busca tu negocio en el mapa, abre su ficha y usa el botón <strong>Reclamar propiedad</strong>.
          Ese flujo nos envía tus datos para validar la solicitud antes de transferir la administración.
        </p>
        <div className="flex flex-wrap gap-3">
          <Button href="/" variant="primary">
            Buscar mi ficha
          </Button>
          <Button href="/veterinarias" variant="secondary">
            Ver negocios en el mapa
          </Button>
        </div>
      </SurfaceCard>
    </PageShell>
  );
}
