import { NextResponse } from "next/server";

import { siteConfig } from "@/lib/constants/site";

export async function GET() {
  // Este endpoint permite verificar rápido que Next está arriba y qué backend espera consumir.
  return NextResponse.json({
    status: "ok",
    service: "elbigotes-frontend",
    frontend_url: siteConfig.siteUrl,
    backend_api_base_url: siteConfig.apiBaseUrl,
    mocks_enabled: siteConfig.useMocks,
  });
}
