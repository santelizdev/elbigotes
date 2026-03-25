export function formatCategoryLabel(category: string) {
  return category.replaceAll("-", " ");
}

export function formatDistance(value?: number | null) {
  if (value === null || value === undefined) {
    return "Sin distancia";
  }
  return `${value.toFixed(1)} km`;
}

export function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat("es-CL", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function titleCase(value: string) {
  return value
    .replaceAll("-", " ")
    .split(" ")
    .filter(Boolean)
    .map((chunk) => chunk.charAt(0).toUpperCase() + chunk.slice(1))
    .join(" ");
}

