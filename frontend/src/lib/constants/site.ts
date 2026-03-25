export const siteConfig = {
  name: "Elbigotes",
  description:
    "Infraestructura pública del ecosistema pet en Chile: mapa, servicios y reportes con enfoque confiable.",
  defaultTitle: "Elbigotes | Mapa del ecosistema pet en Chile",
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
  siteUrl: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  defaultCenter: {
    lat: Number(process.env.NEXT_PUBLIC_DEFAULT_LAT ?? "-33.4489"),
    lng: Number(process.env.NEXT_PUBLIC_DEFAULT_LNG ?? "-70.6693"),
  },
  defaultZoom: Number(process.env.NEXT_PUBLIC_DEFAULT_ZOOM ?? "11"),
  useMocks: process.env.NEXT_PUBLIC_USE_MOCKS === "true",
};

