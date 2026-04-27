"use client";

import { PetOwnerRegistrationPanel } from "@/components/accounts/pet-owner-registration-panel";
import { Button } from "@/components/ui/button";
import { DashboardGrid } from "@/components/ui/dashboard-grid";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";

export function PetOwnerRegistrationForm() {
  return (
    <PageShell className="gap-5 py-6 md:gap-6">
      <PageHero
        eyebrow="Registro de tutor"
        title="Alta de tutor y mascota"
        description="Este flujo deja lista la cuenta base del usuario, el perfil del tutor y la primera mascota, con espacio para sumar mejoras sin complicar el alta inicial."
        className="p-6"
        actions={
          <Button href="/ingresar" variant="ghost">
            Ir a acceso unificado
          </Button>
        }
      />

      <DashboardGrid
        main={
          <SurfaceCard className="grid gap-4 p-5 md:p-6">
            <div className="grid gap-2">
              <p className="eyebrow">Cuenta personal</p>
              <h2 className="m-0 font-display-ui text-3xl leading-tight">
                Crear tutor y primera mascota
              </h2>
            </div>

            <PetOwnerRegistrationPanel />
          </SurfaceCard>
        }
        aside={
          <>
            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">
                Base para marketing responsable
              </h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Conservamos el registro usable hoy, pero ya separado en capas para no mezclar la
                autenticación del usuario con las preferencias o condiciones de su mascota.
              </p>
            </SurfaceCard>

            <SurfaceCard className="grid gap-3">
              <h3 className="m-0 font-display-ui text-2xl leading-tight">Qué queda preparado</h3>
              <p className="m-0 leading-7 text-app-text-soft">
                Acceso con Google y expansión a múltiples mascotas por tutor sin cambiar el
                contrato visual del formulario.
              </p>
            </SurfaceCard>
          </>
        }
      />
    </PageShell>
  );
}
