from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.accounts.models import BusinessProfile, PetOwnerProfile
from apps.memberships.models import (
    MembershipAssignment,
    MembershipAssignmentStatus,
    MembershipPlan,
)

PET_OWNER_FREE_PLAN_SLUG = "pet-owner-free"
BUSINESS_TRIAL_PLAN_SLUG = "business-trial"
BUSINESS_FREE_LIFETIME_PLAN_SLUG = "business-free-lifetime"
BUSINESS_PREMIUM_PLAN_SLUG = "business-basic"
BUSINESS_TRIAL_DAYS = 30


def get_membership_access_tier(assignment: MembershipAssignment) -> str:
    lifecycle = (assignment.plan.metadata or {}).get("lifecycle")
    if lifecycle:
        return str(lifecycle)

    if assignment.plan.slug == PET_OWNER_FREE_PLAN_SLUG:
        return "pet_owner_free"
    if assignment.plan.slug == BUSINESS_FREE_LIFETIME_PLAN_SLUG:
        return "business_free_lifetime"
    if assignment.plan.slug == BUSINESS_TRIAL_PLAN_SLUG:
        return "business_trial"
    if assignment.plan.slug == BUSINESS_PREMIUM_PLAN_SLUG or assignment.plan.price_amount > 0:
        return "business_paid"
    return "generic"


def is_membership_current(assignment: MembershipAssignment) -> bool:
    return assignment.status in {
        MembershipAssignmentStatus.TRIAL,
        MembershipAssignmentStatus.ACTIVE,
    }


def is_membership_renewal_required(assignment: MembershipAssignment) -> bool:
    if get_membership_access_tier(assignment) == "business_free_lifetime":
        return False

    return assignment.status in {
        MembershipAssignmentStatus.TRIAL,
        MembershipAssignmentStatus.PAST_DUE,
        MembershipAssignmentStatus.EXPIRED,
    }


def get_plan_by_slug(slug: str) -> MembershipPlan:
    return MembershipPlan.objects.get(slug=slug, is_active=True)


def sync_membership_assignment_status(
    assignment: MembershipAssignment,
    *,
    reference_time=None,
) -> MembershipAssignment:
    reference_time = reference_time or timezone.now()
    next_status = assignment.status

    if (
        assignment.status == MembershipAssignmentStatus.TRIAL
        and assignment.ends_at
        and assignment.ends_at <= reference_time
    ):
        next_status = MembershipAssignmentStatus.EXPIRED
    elif (
        assignment.status == MembershipAssignmentStatus.ACTIVE
        and assignment.renews_at
        and assignment.renews_at <= reference_time
    ):
        next_status = MembershipAssignmentStatus.PAST_DUE
    elif (
        assignment.status == MembershipAssignmentStatus.PAST_DUE
        and assignment.ends_at
        and assignment.ends_at <= reference_time
    ):
        next_status = MembershipAssignmentStatus.EXPIRED

    if next_status != assignment.status:
        assignment.status = next_status
        assignment.save(update_fields=["status", "updated_at"])

    return assignment


def sync_memberships_for_owner(owner) -> list[MembershipAssignment]:
    assignments = list(MembershipAssignment.objects.for_owner(owner))
    for assignment in assignments:
        sync_membership_assignment_status(assignment)
    return assignments


def assign_default_pet_owner_membership(
    profile: PetOwnerProfile,
    *,
    reference_time=None,
) -> MembershipAssignment:
    reference_time = reference_time or timezone.now()
    plan = get_plan_by_slug(PET_OWNER_FREE_PLAN_SLUG)
    return MembershipAssignment.objects.create(
        plan=plan,
        owner=profile,
        status=MembershipAssignmentStatus.ACTIVE,
        starts_at=reference_time,
        notes="Plan gratuito base asignado automaticamente al registrar tutor.",
        metadata={"assigned_by": "system"},
    )


def assign_default_business_membership(
    profile: BusinessProfile,
    *,
    reference_time=None,
) -> MembershipAssignment:
    reference_time = reference_time or timezone.now()

    if profile.is_billable:
        ends_at = reference_time + timedelta(days=BUSINESS_TRIAL_DAYS)
        plan = get_plan_by_slug(BUSINESS_TRIAL_PLAN_SLUG)
        return MembershipAssignment.objects.create(
            plan=plan,
            owner=profile,
            status=MembershipAssignmentStatus.TRIAL,
            starts_at=reference_time,
            ends_at=ends_at,
            renews_at=ends_at,
            notes="Trial comercial inicial asignado automaticamente al registrar negocio.",
            metadata={
                "assigned_by": "system",
                "trial_days": BUSINESS_TRIAL_DAYS,
            },
        )

    plan = get_plan_by_slug(BUSINESS_FREE_LIFETIME_PLAN_SLUG)
    return MembershipAssignment.objects.create(
        plan=plan,
        owner=profile,
        status=MembershipAssignmentStatus.ACTIVE,
        starts_at=reference_time,
        notes="Plan gratuito permanente asignado a categoria no facturable.",
        metadata={"assigned_by": "system"},
    )


def ensure_default_membership_for_owner(owner) -> MembershipAssignment:
    existing_assignment = MembershipAssignment.objects.for_owner(owner).first()
    if existing_assignment is not None:
        return existing_assignment

    if isinstance(owner, BusinessProfile):
        return assign_default_business_membership(owner)
    if isinstance(owner, PetOwnerProfile):
        return assign_default_pet_owner_membership(owner)

    raise TypeError(f"Unsupported membership owner type: {owner.__class__.__name__}")
