from django.db import migrations


def seed_base_membership_plans(apps, schema_editor):
    MembershipPlan = apps.get_model("memberships", "MembershipPlan")

    plans = [
        {
            "slug": "pet-owner-free",
            "defaults": {
                "name": "Pet Owner Free",
                "audience": "pet_owner",
                "billing_interval": "one_time",
                "price_amount": 0,
                "currency": "CLP",
                "grace_days": 0,
                "max_places": 1,
                "max_pets": 5,
                "is_public": True,
                "is_active": True,
                "description": "",
                "metadata": {},
            },
        },
        {
            "slug": "business-trial",
            "defaults": {
                "name": "Business Trial",
                "audience": "business",
                "billing_interval": "monthly",
                "price_amount": 0,
                "currency": "CLP",
                "grace_days": 60,
                "max_places": 1,
                "max_pets": 1,
                "is_public": False,
                "is_active": True,
                "description": "",
                "metadata": {},
            },
        },
        {
            "slug": "business-basic",
            "defaults": {
                "name": "Business Basic",
                "audience": "business",
                "billing_interval": "monthly",
                "price_amount": 9990,
                "currency": "CLP",
                "grace_days": 0,
                "max_places": 3,
                "max_pets": 1,
                "is_public": True,
                "is_active": True,
                "description": "",
                "metadata": {},
            },
        },
    ]

    for plan in plans:
        MembershipPlan.objects.update_or_create(
            slug=plan["slug"],
            defaults=plan["defaults"],
        )


def unseed_base_membership_plans(apps, schema_editor):
    MembershipPlan = apps.get_model("memberships", "MembershipPlan")
    MembershipPlan.objects.filter(
        slug__in=["pet-owner-free", "business-trial", "business-basic"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_base_membership_plans, unseed_base_membership_plans),
    ]
