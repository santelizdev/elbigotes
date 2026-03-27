import { Metadata } from "next";
import { notFound } from "next/navigation";

import { ClaimRequestForm } from "@/components/claims/claim-request-form";
import { Button } from "@/components/ui/button";
import { loadPlaceDetailData } from "@/lib/services/server-loaders";

interface ClaimPlacePageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: ClaimPlacePageProps): Promise<Metadata> {
  const { slug } = await params;
  const { place } = await loadPlaceDetailData(slug);

  return {
    title: place ? `Reclamar ${place.name} | Elbigotes` : "Reclamar ficha | Elbigotes",
    description:
      "Solicitud pública para reclamar la administración de una ficha no verificada.",
  };
}

export default async function ClaimPlacePage({ params }: ClaimPlacePageProps) {
  const { slug } = await params;
  const { place, hasError } = await loadPlaceDetailData(slug);

  if (hasError) {
    return (
      <div className="feedback-panel feedback-panel--error">
        <p className="feedback-panel__title">No pudimos abrir el formulario de reclamo</p>
        <p>Intenta nuevamente en unos minutos o vuelve a la ficha pública.</p>
        <Button href={`/lugares/${slug}`} variant="secondary">
          Volver a la ficha
        </Button>
      </div>
    );
  }

  if (!place) {
    notFound();
  }

  return <ClaimRequestForm place={place} />;
}
