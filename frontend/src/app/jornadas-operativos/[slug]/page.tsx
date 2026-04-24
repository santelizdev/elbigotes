import { Metadata } from "next";
import { notFound } from "next/navigation";

import { PublicPetOperationProfile } from "@/components/operations/public-pet-operation-profile";
import { Button } from "@/components/ui/button";
import { loadPublicPetOperationDetailData } from "@/lib/services/server-loaders";

interface PublicPetOperationDetailPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({
  params,
}: PublicPetOperationDetailPageProps): Promise<Metadata> {
  const { slug } = await params;
  const { operation } = await loadPublicPetOperationDetailData(slug);

  if (!operation) {
    return {
      title: "Operativo no encontrado | Elbigotes",
    };
  }

  return {
    title: `${operation.title} | Elbigotes`,
    description: `${operation.creatorName} en ${operation.commune}, ${operation.region}.`,
  };
}

export default async function PublicPetOperationDetailPage({
  params,
}: PublicPetOperationDetailPageProps) {
  const { slug } = await params;
  const { operation, hasError } = await loadPublicPetOperationDetailData(slug);

  if (hasError) {
    return (
      <div className="feedback-panel feedback-panel--error">
        <p className="feedback-panel__title">No pudimos abrir este operativo</p>
        <p>El operativo existe, pero esta carga encontró un problema temporal con los datos.</p>
        <Button href="/jornadas-operativos" variant="secondary">
          Volver al listado
        </Button>
      </div>
    );
  }

  if (!operation) {
    notFound();
  }

  return <PublicPetOperationProfile operation={operation} />;
}
