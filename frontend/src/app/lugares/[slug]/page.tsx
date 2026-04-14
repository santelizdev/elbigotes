import { Metadata } from "next";
import { notFound } from "next/navigation";

import { PlaceViewTracker } from "@/components/analytics/place-view-tracker";
import { PlaceProfile } from "@/components/places/place-profile";
import { Button } from "@/components/ui/button";
import { loadPlaceDetailData } from "@/lib/services/server-loaders";

interface PlaceDetailPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({
  params,
}: PlaceDetailPageProps): Promise<Metadata> {
  const { slug } = await params;
  const { place } = await loadPlaceDetailData(slug);

  if (!place) {
    return {
      title: "Lugar no encontrado | Elbigotes",
    };
  }

  return {
    title: `${place.name} | Elbigotes`,
    description: place.summary,
  };
}

export default async function PlaceDetailPage({ params }: PlaceDetailPageProps) {
  const { slug } = await params;
  const { place, hasError } = await loadPlaceDetailData(slug);

  if (hasError) {
    return (
      <div className="feedback-panel feedback-panel--error">
        <p className="feedback-panel__title">No pudimos abrir esta ficha</p>
        <p>
          La ficha existe, pero esta carga encontró un problema temporal con los datos del backend.
        </p>
        <Button href="/" variant="secondary">
          Volver al mapa principal
        </Button>
      </div>
    );
  }

  if (!place) {
    notFound();
  }

  return (
    <>
      <PlaceViewTracker placeSlug={place.slug} />
      <PlaceProfile place={place} />
    </>
  );
}
