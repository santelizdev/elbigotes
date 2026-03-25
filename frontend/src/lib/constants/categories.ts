import { CategorySlug } from "@/lib/types";

export interface CategoryDefinition {
  slug: CategorySlug;
  apiCategory?: string;
  label: string;
  shortLabel: string;
  description: string;
  accent: string;
  route: string;
  kind: "place" | "lost-pets";
}

export const CATEGORY_DEFINITIONS: CategoryDefinition[] = [
  {
    slug: "veterinarias",
    apiCategory: "veterinarias",
    label: "Veterinarias",
    shortLabel: "Veterinarias",
    description: "Consultas, especialidades y atención preventiva para perros y gatos.",
    accent: "var(--accent-blue)",
    route: "/veterinarias",
    kind: "place",
  },
  {
    slug: "refugios-albergues",
    apiCategory: "refugios-albergues",
    label: "Refugios y albergues",
    shortLabel: "Refugios",
    description: "Organizaciones y espacios de rescate con información geolocalizada.",
    accent: "var(--accent-emerald)",
    route: "/refugios",
    kind: "place",
  },
  {
    slug: "parques-pet-friendly",
    apiCategory: "parques-pet-friendly",
    label: "Parques pet friendly",
    shortLabel: "Parques",
    description: "Zonas aptas para paseo, juego y encuentro seguro en ciudad.",
    accent: "var(--accent-sand)",
    route: "/parques-pet-friendly",
    kind: "place",
  },
  {
    slug: "emergencias-veterinarias",
    apiCategory: "emergencias-veterinarias",
    label: "Emergencias veterinarias 24/7",
    shortLabel: "Emergencias",
    description: "Atención crítica y hospitales veterinarios disponibles de forma continua.",
    accent: "var(--accent-red)",
    route: "/emergencias-veterinarias-24-7",
    kind: "place",
  },
  {
    slug: "guarderias",
    apiCategory: "guarderias",
    label: "Guarderías",
    shortLabel: "Guarderías",
    description: "Cuidado diario y estancias para mascotas con información clara y comparable.",
    accent: "var(--accent-orange)",
    route: "/guarderias",
    kind: "place",
  },
  {
    slug: "mascotas-perdidas",
    label: "Mascotas perdidas",
    shortLabel: "Perdidas",
    description: "Reportes activos con última ubicación conocida y acceso rápido a publicación.",
    accent: "var(--accent-gold)",
    route: "/mascotas-perdidas",
    kind: "lost-pets",
  },
];

export function getCategoryDefinition(slug: string) {
  return CATEGORY_DEFINITIONS.find((category) => category.slug === slug);
}

