import { siteConfig } from "@/lib/constants/site";

interface RequestOptions extends RequestInit {
  query?: Record<string, string | number | boolean | undefined>;
}

export class ApiRequestError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.details = details;
  }
}

function buildUrl(path: string, query?: RequestOptions["query"]) {
  const baseUrl =
    typeof window === "undefined" ? siteConfig.internalApiBaseUrl : siteConfig.apiBaseUrl;
  const url = new URL(`${baseUrl}${path}`, siteConfig.siteUrl);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined || value === "" || value === false) {
        return;
      }
      url.searchParams.set(key, String(value));
    });
  }
  return url.toString();
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  // Centralizar la llamada HTTP simplifica futuras decisiones como auth, tracing o retries.
  const { query, headers, ...rest } = options;
  const isFormDataBody = rest.body instanceof FormData;
  const response = await fetch(buildUrl(path, query), {
    headers: isFormDataBody
      ? headers
      : {
          "Content-Type": "application/json",
          ...headers,
        },
    ...rest,
  });

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    let details: unknown = null;

    if (contentType.includes("application/json")) {
      details = await response.json();
    } else {
      details = await response.text();
    }

    throw new ApiRequestError(
      `API request failed with status ${response.status}`,
      response.status,
      details,
    );
  }

  if (response.status === 204) {
    return null as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  const rawBody = await response.text();
  if (!rawBody.trim()) {
    return null as T;
  }

  if (contentType.includes("application/json")) {
    try {
      return JSON.parse(rawBody) as T;
    } catch {
      return rawBody as T;
    }
  }

  return rawBody as T;
}

export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
  if (!(error instanceof ApiRequestError)) {
    return fallbackMessage;
  }

  if (typeof error.details === "string" && error.details.trim()) {
    return error.details;
  }

  if (error.details && typeof error.details === "object") {
    const entries = Object.entries(error.details as Record<string, unknown>);
    for (const [, value] of entries) {
      if (typeof value === "string" && value.trim()) {
        return value;
      }
      if (Array.isArray(value) && value.length && typeof value[0] === "string") {
        return value[0];
      }
    }
  }

  return fallbackMessage;
}
