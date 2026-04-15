"use client";

import { useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";

import { siteConfig } from "@/lib/constants/site";

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function AppRouteAnalytics() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const ga4MeasurementId = siteConfig.ga4MeasurementId;
  const search = searchParams?.toString() ?? "";
  const hasMountedRef = useRef(false);

  useEffect(() => {
    if (!hasMountedRef.current) {
      hasMountedRef.current = true;
      return;
    }

    if (
      !ga4MeasurementId ||
      typeof window === "undefined" ||
      typeof window.gtag !== "function"
    ) {
      return;
    }

    const pagePath = search ? `${pathname}?${search}` : pathname;

    // En App Router necesitamos emitir pageviews manualmente para evitar
    // depender del comportamiento implícito del snippet en navegación SPA.
    window.gtag("config", ga4MeasurementId, {
      page_path: pagePath,
      page_location: window.location.href,
      page_title: document.title,
    });
  }, [ga4MeasurementId, pathname, search]);

  return null;
}
