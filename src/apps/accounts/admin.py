from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import BusinessProfile, PetOwnerProfile, PetProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "email_verified", "role", "is_staff", "is_active")
    list_filter = ("role", "email_verified", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "role", "email_verified")}),
        (
            "Permisos",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Fechas importantes",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
    )
    readonly_fields = ("created_at", "updated_at", "date_joined", "last_login")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "is_staff", "is_superuser"),
            },
        ),
    )


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "business_kind",
        "membership_status",
        "place",
        "commune",
        "region",
        "grace_expires_at",
    )
    list_filter = ("business_kind", "membership_status", "region", "marketing_opt_in")
    search_fields = ("business_name", "user__email", "phone", "commune")
    autocomplete_fields = ("user", "place")


class PetProfileInline(admin.TabularInline):
    model = PetProfile
    extra = 0
    fields = ("name", "species", "breed", "sex", "birth_date", "is_active")


@admin.register(PetOwnerProfile)
class PetOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "address_line", "commune", "region", "marketing_opt_in")
    list_filter = ("region", "marketing_opt_in")
    search_fields = ("user__email", "user__first_name", "user__last_name", "phone")
    autocomplete_fields = ("user",)
    inlines = [PetProfileInline]


@admin.register(PetProfile)
class PetProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "species", "owner", "birth_date", "is_active")
    list_filter = ("species", "sex", "is_active")
    search_fields = ("name", "owner__user__email", "breed")
    autocomplete_fields = ("owner",)
