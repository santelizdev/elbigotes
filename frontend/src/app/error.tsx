"use client";

import { Button } from "@/components/ui/button";

export default function GlobalError() {
  return (
    <div className="feedback-panel feedback-panel--error">
      <p className="feedback-panel__title">La experiencia pública tuvo un problema inesperado</p>
      <p>
        El frontend está preparado para crecer sobre el backend, pero esta vista encontró un error
        no controlado.
      </p>
      <Button href="/" variant="secondary">
        Volver al mapa
      </Button>
    </div>
  );
}
