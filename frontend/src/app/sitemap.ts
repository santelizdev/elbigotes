import type { MetadataRoute } from "next";

import { siteConfig } from "@/lib/constants/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    "",
    "/veterinarias",
    "/refugios",
    "/parques-pet-friendly",
    "/emergencias-veterinarias-24-7",
    "/guarderias",
    "/mascotas-perdidas",
    "/publicar-mascota-perdida",
  ];

  return routes.map((route) => ({
    url: `${siteConfig.siteUrl}${route}`,
    lastModified: new Date(),
  }));
}

