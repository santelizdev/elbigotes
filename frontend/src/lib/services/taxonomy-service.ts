import {
  buildPlaceCategoryDefinitions,
  CategoryDefinition,
  PublicCategory,
} from "@/lib/constants/categories";
import { apiRequest } from "@/lib/services/api-client";

interface PublicCategoryApiResponse {
  name: string;
  slug: string;
  description?: string;
  icon_name?: string;
  sort_order?: number;
}

function mapPublicCategory(payload: PublicCategoryApiResponse): PublicCategory {
  return {
    name: payload.name,
    slug: payload.slug,
    description: payload.description,
    iconName: payload.icon_name,
    sortOrder: payload.sort_order,
  };
}

export async function getPublicCategories(): Promise<CategoryDefinition[]> {
  try {
    const response = await apiRequest<PublicCategoryApiResponse[]>("/taxonomy/categories/", {
      cache: "no-store",
    });
    return buildPlaceCategoryDefinitions(response.map(mapPublicCategory));
  } catch {
    return buildPlaceCategoryDefinitions();
  }
}
