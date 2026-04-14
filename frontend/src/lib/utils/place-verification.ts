import { Place } from "@/lib/types";

export function getPlaceVerificationTone(place: Place): "neutral" | "success" | "warning" {
  const verificationStatus =
    place.verificationStatus ?? (place.isPremiumVerified ? "verified_premium" : place.isVerified ? "verified" : "unverified");

  if (verificationStatus === "verified_premium" || verificationStatus === "verified") {
    return "success";
  }
  if (verificationStatus === "claim_requested") {
    return "warning";
  }
  return "neutral";
}

export function getPlaceVerificationLabel(place: Place): string {
  const verificationStatus =
    place.verificationStatus ?? (place.isPremiumVerified ? "verified_premium" : place.isVerified ? "verified" : "unverified");

  switch (verificationStatus) {
    case "verified_premium":
      return "Verificado Premium";
    case "verified":
      return "Verificado";
    case "claim_requested":
      return "Reclamado";
    default:
      return "Pendiente";
  }
}
