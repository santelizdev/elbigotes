import { CategorySlug } from "@/lib/types";

export interface PublicCategory {
  name: string;
  slug: string;
  description?: string;
  iconName?: string;
  sortOrder?: number;
}

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

const KNOWN_CATEGORY_PRESETS: Record<string, Partial<CategoryDefinition>> = {
  veterinarias: {
    label: "Veterinarias",
    shortLabel: "Veterinarias",
    description: "Consultas, especialidades y atención preventiva para perros y gatos.",
    accent: "var(--accent-blue)",
    route: "/veterinarias",
  },
  "refugios-albergues": {
    label: "Refugios y albergues",
    shortLabel: "Refugios",
    description: "Organizaciones y espacios de rescate con información geolocalizada.",
    accent: "var(--accent-cyan)",
    route: "/refugios",
  },
  "parques-pet-friendly": {
    label: "Parques pet friendly",
    shortLabel: "Parques",
    description: "Zonas aptas para paseo, juego y encuentro seguro en ciudad.",
    accent: "var(--accent-lime)",
    route: "/parques-pet-friendly",
  },
  "emergencias-veterinarias": {
    label: "Emergencias veterinarias 24/7",
    shortLabel: "Emergencias",
    description: "Atención crítica y hospitales veterinarios disponibles de forma continua.",
    accent: "var(--accent-coral)",
    route: "/emergencias-veterinarias-24-7",
  },
  guarderias: {
    label: "Guarderías",
    shortLabel: "Guarderías",
    description: "Cuidado diario y estancias para mascotas con información clara y comparable.",
    accent: "var(--accent-orange)",
    route: "/guarderias",
  },
  peluquerias: {
    label: "Peluquerías",
    shortLabel: "Peluquerías",
    description: "Baño, corte y grooming con datos públicos comparables sobre el mapa.",
    accent: "var(--accent-emerald)",
    route: "/?category=peluquerias",
  },
};

const PLACE_ACCENTS = [
  "var(--accent-blue)",
  "var(--accent-emerald)",
  "var(--accent-sand)",
  "var(--accent-red)",
  "var(--accent-orange)",
  "var(--accent-gold)",
];

const FALLBACK_PLACE_CATEGORIES: PublicCategory[] = [
  { name: "Veterinarias", slug: "veterinarias", sortOrder: 0 },
  { name: "Refugios y albergues", slug: "refugios-albergues", sortOrder: 1 },
  { name: "Parques pet friendly", slug: "parques-pet-friendly", sortOrder: 2 },
  { name: "Emergencias veterinarias 24/7", slug: "emergencias-veterinarias", sortOrder: 3 },
  { name: "Guarderías", slug: "guarderias", sortOrder: 4 },
];

const LOST_PETS_CATEGORY: CategoryDefinition = {
  slug: "mascotas-perdidas",
  label: "Mascotas perdidas",
  shortLabel: "Perdidas",
  description: "Reportes activos con última ubicación conocida y acceso rápido a publicación.",
  accent: "var(--accent-gold)",
  route: "/mascotas-perdidas",
  kind: "lost-pets",
};

function fallbackShortLabel(name: string) {
  return name.split(" y ")[0]?.trim() || name;
}

function buildCategoryRoute(slug: string) {
  return KNOWN_CATEGORY_PRESETS[slug]?.route ?? `/?category=${slug}`;
}

export function buildPlaceCategoryDefinition(
  category: PublicCategory,
  index: number,
): CategoryDefinition {
  const preset = KNOWN_CATEGORY_PRESETS[category.slug] ?? {};
  return {
    slug: category.slug,
    apiCategory: category.slug,
    label: preset.label ?? category.name,
    shortLabel: preset.shortLabel ?? fallbackShortLabel(category.name),
    description:
      preset.description ??
      category.description?.trim() ??
      "Categoría pública disponible sobre mapa con filtros y lectura territorial.",
    accent: preset.accent ?? PLACE_ACCENTS[index % PLACE_ACCENTS.length],
    route: buildCategoryRoute(category.slug),
    kind: "place",
  };
}

export function buildPlaceCategoryDefinitions(categories?: PublicCategory[]): CategoryDefinition[] {
  const source = categories?.length
    ? [...categories].sort((left, right) => {
        const leftOrder = left.sortOrder ?? Number.MAX_SAFE_INTEGER;
        const rightOrder = right.sortOrder ?? Number.MAX_SAFE_INTEGER;
        return leftOrder - rightOrder || left.name.localeCompare(right.name, "es");
      })
    : FALLBACK_PLACE_CATEGORIES;
  return source.map((category, index) => buildPlaceCategoryDefinition(category, index));
}

export const CATEGORY_DEFINITIONS: CategoryDefinition[] = [
  ...buildPlaceCategoryDefinitions(),
  LOST_PETS_CATEGORY,
];

export function getCategoryDefinition(
  slug: string,
  categories: CategoryDefinition[] = CATEGORY_DEFINITIONS,
) {
  return categories.find((category) => category.slug === slug);
}
