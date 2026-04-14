from django.db import migrations


def update_default_membership_rules(apps, schema_editor):
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
                "description": "Cuenta gratuita para tutores de mascotas.",
                "metadata": {"lifecycle": "pet_owner_free"},
            },
        },
        {
            "slug": "business-trial",
            "defaults": {
                "name": "Business Trial 30 Dias",
                "audience": "business",
                "billing_interval": "monthly",
                "price_amount": 0,
                "currency": "CLP",
                "grace_days": 30,
                "max_places": 1,
                "max_pets": 1,
                "is_public": False,
                "is_active": True,
                "description": "Trial comercial de 30 dias para negocios facturables.",
                "metadata": {"lifecycle": "business_trial", "trial_days": 30},
            },
        },
        {
            "slug": "business-free-lifetime",
            "defaults": {
                "name": "Business Free Lifetime",
                "audience": "business",
                "billing_interval": "one_time",
                "price_amount": 0,
                "currency": "CLP",
                "grace_days": 0,
                "max_places": 1,
                "max_pets": 1,
                "is_public": False,
                "is_active": True,
                "description": "Plan gratuito permanente para categorias no facturables.",
                "metadata": {"lifecycle": "business_free_lifetime"},
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
                "description": "Plan comercial base para negocios.",
                "metadata": {"lifecycle": "business_paid"},
            },
        },
    ]

    for plan in plans:
        MembershipPlan.objects.update_or_create(
            slug=plan["slug"],
            defaults=plan["defaults"],
        )


def revert_default_membership_rules(apps, schema_editor):
    MembershipPlan = apps.get_model("memberships", "MembershipPlan")
    MembershipPlan.objects.filter(slug="business-free-lifetime").delete()
    MembershipPlan.objects.filter(slug="business-trial").update(
        name="Business Trial",
        grace_days=60,
        description="",
        metadata={},
    )
    MembershipPlan.objects.filter(slug="pet-owner-free").update(
        description="",
        metadata={},
    )
    MembershipPlan.objects.filter(slug="business-basic").update(
        description="",
        metadata={},
    )


class Migration(migrations.Migration):

    dependencies = [
        ("memberships", "0002_seed_base_membership_plans"),
    ]

    operations = [
        migrations.RunPython(update_default_membership_rules, revert_default_membership_rules),
    ]
