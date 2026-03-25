import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="feedback-panel">
      <p className="feedback-panel__title">No encontramos esa ficha</p>
      <p>Puede que la ruta haya cambiado o que el punto todavía no esté publicado.</p>
      <Button href="/" variant="secondary">
        Volver al mapa principal
      </Button>
    </div>
  );
}

