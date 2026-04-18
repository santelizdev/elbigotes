import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { SurfaceCard } from "@/components/ui/surface-card";

export function AccountAccessNotice({
  title = "Necesitas iniciar sesión",
  message = "Ingresa con tu cuenta comercial para administrar tu perfil y tus sucursales.",
}: {
  title?: string;
  message?: string;
}) {
  return (
    <SurfaceCard className="grid gap-4">
      <SectionHeader
        eyebrow="Acceso requerido"
        title={title}
        description={message}
      />
      <div className="flex flex-wrap gap-3">
        <Button href="/ingresar" variant="primary">
          Ingresar
        </Button>
        <Button href="/registro/negocio" variant="ghost">
          Crear cuenta comercial
        </Button>
      </div>
    </SurfaceCard>
  );
}
