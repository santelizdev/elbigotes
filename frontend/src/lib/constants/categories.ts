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
  "emergencias-veterinarias": {
    label: "Emergencias veterinarias 24/7",
    shortLabel: "24 horas",
    description: "Atención crítica y hospitales veterinarios disponibles de forma continua.",
    accent: "var(--accent-coral)",
    route: "/emergencias-veterinarias-24-7",
  },
  "tiendas-de-alimentos": {
    label: "Tiendas de alimentos",
    shortLabel: "Alimentos",
    description: "Alimento, snacks y abastecimiento diario para perros y gatos.",
    accent: "var(--accent-gold)",
    route: "/?category=tiendas-de-alimentos",
  },
  peluquerias: {
    label: "Peluquerías",
    shortLabel: "Peluquerías",
    description: "Baño, corte y grooming con datos públicos comparables sobre el mapa.",
    accent: "var(--accent-emerald)",
    route: "/?category=peluquerias",
  },
  guarderias: {
    label: "Guarderías",
    shortLabel: "Guarderías",
    description: "Cuidado diario y estancias para mascotas con información clara y comparable.",
    accent: "var(--accent-orange)",
    route: "/guarderias",
  },
  "refugios-albergues": {
    label: "Refugios y albergues",
    shortLabel: "Refugios",
    description: "Organizaciones y espacios de rescate con información geolocalizada.",
    accent: "var(--accent-cyan)",
    route: "/refugios",
  },
  veterinarias: {
    label: "Veterinarias",
    shortLabel: "Veterinarias",
    description: "Consultas, especialidades y atención preventiva para perros y gatos.",
    accent: "var(--accent-blue)",
    route: "/veterinarias",
  },
  "parques-pet-friendly": {
    label: "Parques pet friendly",
    shortLabel: "Parques",
    description: "Zonas aptas para paseo, juego y encuentro seguro en ciudad.",
    accent: "var(--accent-lime)",
    route: "/parques-pet-friendly",
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
  { name: "Emergencias veterinarias 24/7", slug: "emergencias-veterinarias", sortOrder: 0 },
  { name: "Tiendas de alimentos", slug: "tiendas-de-alimentos", sortOrder: 1 },
  { name: "Peluquerías", slug: "peluquerias", sortOrder: 2 },
  { name: "Guarderías", slug: "guarderias", sortOrder: 3 },
  { name: "Refugios y albergues", slug: "refugios-albergues", sortOrder: 4 },
  { name: "Veterinarias", slug: "veterinarias", sortOrder: 5 },
  { name: "Parques pet friendly", slug: "parques-pet-friendly", sortOrder: 6 },
];

const CATEGORY_PRIORITY_ORDER = [
  "emergencias-veterinarias",
  "tiendas-de-alimentos",
  "peluquerias",
  "guarderias",
  "refugios-albergues",
  "veterinarias",
  "parques-pet-friendly",
] as const;

function getCategoryPriority(slug: string) {
  const index = CATEGORY_PRIORITY_ORDER.indexOf(slug as (typeof CATEGORY_PRIORITY_ORDER)[number]);
  return index === -1 ? Number.MAX_SAFE_INTEGER : index;
}

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
        const priorityDelta = getCategoryPriority(left.slug) - getCategoryPriority(right.slug);
        if (priorityDelta !== 0) {
          return priorityDelta;
        }
        const leftOrder = left.sortOrder ?? Number.MAX_SAFE_INTEGER;
        const rightOrder = right.sortOrder ?? Number.MAX_SAFE_INTEGER;
        return leftOrder - rightOrder || left.name.localeCompare(right.name, "es");
      })
    : FALLBACK_PLACE_CATEGORIES;
  return source.map((category, index) => buildPlaceCategoryDefinition(category, index));
}

export const CATEGORY_DEFINITIONS: CategoryDefinition[] = buildPlaceCategoryDefinitions();

export function getCategoryDefinition(
  slug: string,
  categories: CategoryDefinition[] = CATEGORY_DEFINITIONS,
) {
  return categories.find((category) => category.slug === slug);
}
