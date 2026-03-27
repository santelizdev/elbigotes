import type { NextConfig } from "next";

const internalApiBaseUrl = (process.env.INTERNAL_API_BASE_URL ?? "http://web:8000/api/v1").replace(
  /\/$/,
  "",
);

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  output: "standalone",
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: "/api/v1",
        destination: `${internalApiBaseUrl}/`,
      },
      {
        source: "/api/v1/:path*",
        destination: `${internalApiBaseUrl}/:path*/`,
      },
    ];
  },
};

export default nextConfig;
