from __future__ import annotations

from apps.claims.choices import ClaimRequestStatus
from apps.memberships.models import MembershipAssignment
from apps.memberships.services import get_membership_access_tier, is_membership_current
from apps.places.choices import PlaceVerificationStatus
from apps.places.models import Place

PLACE_EFFECTIVE_VERIFICATION_PREMIUM = "verified_premium"
OPEN_CLAIM_STATUSES = {ClaimRequestStatus.PENDING, ClaimRequestStatus.UNDER_REVIEW}


def has_open_claim_request(place: Place) -> bool:
    prefetched_claims = getattr(place, "_prefetched_objects_cache", {}).get("claim_requests")
    if prefetched_claims is not None:
        return any(claim.status in OPEN_CLAIM_STATUSES for claim in prefetched_claims)

    return place.claim_requests.filter(status__in=OPEN_CLAIM_STATUSES).exists()


def get_place_effective_verification_status(place: Place) -> str:
    if place.verification_status == PlaceVerificationStatus.CLAIM_REQUESTED:
        return PlaceVerificationStatus.CLAIM_REQUESTED

    if place.verification_status == PlaceVerificationStatus.VERIFIED:
        if has_active_premium_membership(place):
            return PLACE_EFFECTIVE_VERIFICATION_PREMIUM
        return PlaceVerificationStatus.VERIFIED

    if has_open_claim_request(place):
        return PlaceVerificationStatus.CLAIM_REQUESTED

    return PlaceVerificationStatus.UNVERIFIED


def has_active_premium_membership(place: Place) -> bool:
    if not place.owner_business_profile_id:
        return False

    assignments = MembershipAssignment.objects.for_owner(place.owner_business_profile)
    return any(
        get_membership_access_tier(assignment) == "business_paid"
        and is_membership_current(assignment)
        for assignment in assignments
    )


def is_place_claimable(place: Place) -> bool:
    return get_place_effective_verification_status(place) == PlaceVerificationStatus.UNVERIFIED


def mark_place_claim_requested(place: Place) -> Place:
    if place.verification_status != PlaceVerificationStatus.VERIFIED:
        place.verification_status = PlaceVerificationStatus.CLAIM_REQUESTED
        place.save(update_fields=["verification_status", "is_verified", "updated_at"])
    return place


def mark_place_verified(place: Place) -> Place:
    place.verification_status = PlaceVerificationStatus.VERIFIED
    place.save(update_fields=["verification_status", "is_verified", "updated_at"])
    return place


def reset_place_verification_if_unclaimed(place: Place) -> Place:
    if not has_open_claim_request(place) and place.verification_status == PlaceVerificationStatus.CLAIM_REQUESTED:
        place.verification_status = PlaceVerificationStatus.UNVERIFIED
        place.save(update_fields=["verification_status", "is_verified", "updated_at"])
    return place
