import { Button } from "@/components/ui/button";
import { PageHero } from "@/components/ui/page-hero";
import { PageShell } from "@/components/ui/page-shell";
import { SurfaceCard } from "@/components/ui/surface-card";

export function RegistrationHub() {
  return (
    <PageShell>
      <PageHero
        eyebrow="Alta inicial de cuentas"
        title="Registra tu perfil en Elbigotes"
        description={
          "Abrimos dos flujos distintos porque el producto tendrá necesidades muy diferentes: negocios y organizaciones del ecosistema pet por un lado, y tutores con sus mascotas por otro."
        }
        actions={
          <Button href="/ingresar" variant="ghost">
            Ya tengo cuenta
          </Button>
        }
      />

      <section className="grid gap-4 md:grid-cols-2">
        <SurfaceCard className="grid gap-4">
          <p className="eyebrow">Negocios y organizaciones</p>
          <div className="grid gap-3">
            <h3 className="m-0 font-display-ui text-2xl leading-tight">
              Veterinarias, guarderías, emergencias, refugios y parques
            </h3>
            <p className="m-0 leading-7 text-app-text-soft">
              Este registro crea la cuenta comercial y deja lista la base para membresías, periodo
              de gracia y gestión operativa desde admin.
            </p>
          </div>
          <div className="pt-2">
            <Button href="/registro/negocio" variant="primary">
              Registrar negocio
            </Button>
          </div>
        </SurfaceCard>

        <SurfaceCard className="grid gap-4">
          <p className="eyebrow">Tutores de mascotas</p>
          <div className="grid gap-3">
            <h3 className="m-0 font-display-ui text-2xl leading-tight">
              Cuenta personal más ficha inicial de mascota
            </h3>
            <p className="m-0 leading-7 text-app-text-soft">
              Este flujo deja creado el perfil del tutor y la primera ficha de mascota para futuras
              campañas, recordatorios, cumpleaños y comunicación segmentada.
            </p>
          </div>
          <div className="pt-2">
            <Button href="/registro/tutor" variant="primary">
              Registrar tutor
            </Button>
          </div>
        </SurfaceCard>
      </section>
    </PageShell>
  );
}
