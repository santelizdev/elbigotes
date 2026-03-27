from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework import serializers

from apps.accounts.models import (
    BusinessKind,
    BusinessProfile,
    PetOwnerProfile,
    PetProfile,
    User,
)
from apps.accounts.services import (
    create_business_branch,
    register_business_account,
    register_pet_owner_account,
    update_business_account,
)
from apps.accounts.tokens import create_access_token
from apps.lost_pets.api.serializers import LostPetReportListSerializer
from apps.lost_pets.models import LostPetReport
from apps.memberships.models import MembershipAssignment
from apps.places.models import Place
from apps.taxonomy.models import Category


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "email_verified", "first_name", "last_name", "role")


class MembershipAssignmentSummarySerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    plan_slug = serializers.CharField(source="plan.slug", read_only=True)
    audience = serializers.CharField(source="plan.audience", read_only=True)

    class Meta:
        model = MembershipAssignment
        fields = (
            "id",
            "plan_name",
            "plan_slug",
            "audience",
            "status",
            "starts_at",
            "ends_at",
            "renews_at",
        )


class BusinessProfileSerializer(serializers.ModelSerializer):
    place_slug = serializers.CharField(source="place.slug", read_only=True)
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = BusinessProfile
        fields = (
            "place_slug",
            "business_name",
            "business_kind",
            "phone",
            "commune",
            "region",
            "website",
            "marketing_opt_in",
            "notes",
            "memberships",
        )

    def get_memberships(self, obj):
        assignments = MembershipAssignment.objects.for_owner(obj)
        return MembershipAssignmentSummarySerializer(assignments, many=True).data


class PetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfile
        fields = ("id", "name", "species", "breed", "sex", "birth_date", "notes", "is_active")


class PetOwnerProfileSerializer(serializers.ModelSerializer):
    pets = PetProfileSerializer(many=True, read_only=True)
    memberships = serializers.SerializerMethodField()

    class Meta:
        model = PetOwnerProfile
        fields = (
            "phone",
            "address_line",
            "commune",
            "region",
            "marketing_opt_in",
            "pets",
            "memberships",
        )

    def get_memberships(self, obj):
        assignments = MembershipAssignment.objects.for_owner(obj)
        return MembershipAssignmentSummarySerializer(assignments, many=True).data


class BusinessOwnedPlaceSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    is_primary = serializers.SerializerMethodField()

    class Meta:
        model = Place
        fields = (
            "name",
            "slug",
            "status",
            "formatted_address",
            "commune",
            "region",
            "website",
            "latitude",
            "longitude",
            "is_primary",
            "created_at",
            "updated_at",
        )

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

    def get_is_primary(self, obj):
        profile = self.context.get("profile")
        return bool(profile and profile.place_id == obj.id)


class BusinessRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    business_name = serializers.CharField(max_length=160)
    business_kind = serializers.ChoiceField(choices=BusinessKind.choices)
    phone = serializers.CharField(max_length=40)
    commune = serializers.CharField(max_length=120)
    region = serializers.CharField(max_length=120, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    place_label = serializers.CharField(max_length=255)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    marketing_opt_in = serializers.BooleanField(required=False, default=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return value

    def validate(self, attrs):
        if not (-90 <= attrs["latitude"] <= 90) or not (-180 <= attrs["longitude"] <= 180):
            raise serializers.ValidationError("La ubicación seleccionada no es válida.")

        category_slug = {
            "veterinary": "veterinarias",
            "daycare": "guarderias",
            "emergency": "emergencias-veterinarias",
            "shelter": "refugios-albergues",
            "park": "parques-pet-friendly",
        }[attrs["business_kind"]]
        if not Category.objects.filter(slug=category_slug).exists():
            raise serializers.ValidationError(
                "La taxonomía pública todavía no está lista para este tipo de negocio."
            )

        duplicate_profile = (
            BusinessProfile.objects.filter(
                business_name__iexact=attrs["business_name"],
                commune__iexact=attrs["commune"],
                business_kind=attrs["business_kind"],
            )
            .order_by("id")
            .first()
        )
        if duplicate_profile:
            raise serializers.ValidationError(
                "Ya existe un registro comercial con el mismo nombre, comuna y tipo de cuenta."
            )
        return attrs

    def create(self, validated_data):
        user, profile = register_business_account(
            {
                "password": validated_data["password"],
                "user": {
                    "email": validated_data["email"],
                    "first_name": validated_data["first_name"],
                    "last_name": validated_data.get("last_name", ""),
                },
                "profile": {
                    "business_name": validated_data["business_name"],
                    "business_kind": validated_data["business_kind"],
                    "phone": validated_data["phone"],
                    "commune": validated_data["commune"],
                    "region": validated_data.get("region") or "Región Metropolitana",
                    "website": validated_data.get("website", ""),
                    "place_label": validated_data["place_label"],
                    "latitude": validated_data["latitude"],
                    "longitude": validated_data["longitude"],
                    "marketing_opt_in": validated_data.get("marketing_opt_in", True),
                    "notes": validated_data.get("notes", ""),
                },
            }
        )
        return {"user": user, "profile": profile}

    def to_representation(self, instance):
        return {
            "user": UserSummarySerializer(instance["user"]).data,
            "profile": BusinessProfileSerializer(instance["profile"]).data,
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        user = authenticate(request=request, username=attrs["email"], password=attrs["password"])
        if user is None:
            raise serializers.ValidationError("Email o password inválidos.")
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta no está activa.")
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        return {
            "token": create_access_token(user),
            "user": user,
        }

    def to_representation(self, instance):
        return {
            "token": instance["token"],
            "user": UserSummarySerializer(instance["user"]).data,
        }


class InitialPetRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    species = serializers.ChoiceField(choices=PetProfile._meta.get_field("species").choices)
    breed = serializers.CharField(max_length=120, required=False, allow_blank=True)
    sex = serializers.ChoiceField(choices=PetProfile._meta.get_field("sex").choices, required=False)
    birth_date = serializers.DateField(required=False, allow_null=True)


class PetOwnerRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=40)
    address_line = serializers.CharField(max_length=255, required=False, allow_blank=True)
    commune = serializers.CharField(max_length=120, required=False, allow_blank=True)
    region = serializers.CharField(max_length=120, required=False, allow_blank=True)
    marketing_opt_in = serializers.BooleanField(required=False, default=True)
    pet = InitialPetRegistrationSerializer()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este email.")
        return value

    def create(self, validated_data):
        user, profile, pet = register_pet_owner_account(
            {
                "password": validated_data["password"],
                "user": {
                    "email": validated_data["email"],
                    "first_name": validated_data["first_name"],
                    "last_name": validated_data.get("last_name", ""),
                },
                "profile": {
                    "phone": validated_data["phone"],
                    "address_line": validated_data.get("address_line", ""),
                    "commune": validated_data.get("commune", ""),
                    "region": validated_data.get("region") or "Región Metropolitana",
                    "marketing_opt_in": validated_data.get("marketing_opt_in", True),
                },
                "pet": {
                    "name": validated_data["pet"]["name"],
                    "species": validated_data["pet"]["species"],
                    "breed": validated_data["pet"].get("breed", ""),
                    "sex": validated_data["pet"].get("sex", "unknown"),
                    "birth_date": validated_data["pet"].get("birth_date"),
                    "notes": "",
                },
            }
        )
        return {"user": user, "profile": profile, "pet": pet}

    def to_representation(self, instance):
        return {
            "user": UserSummarySerializer(instance["user"]).data,
            "profile": PetOwnerProfileSerializer(instance["profile"]).data,
            "initial_pet": PetProfileSerializer(instance["pet"]).data,
        }


class BusinessWorkspaceSerializer(serializers.Serializer):
    user = UserSummarySerializer()
    profile = BusinessProfileSerializer()
    places = serializers.SerializerMethodField()

    def get_places(self, obj):
        profile = obj["profile"]
        places = profile.owned_places.order_by("-created_at", "name")
        return BusinessOwnedPlaceSerializer(
            places,
            many=True,
            context={"profile": profile},
        ).data


class PetOwnerWorkspaceSerializer(serializers.Serializer):
    user = UserSummarySerializer()
    profile = PetOwnerProfileSerializer()
    reports = serializers.SerializerMethodField()

    def get_reports(self, obj):
        profile = obj["profile"]
        reports = (
            LostPetReport.objects.filter(
                Q(pet_profile__owner=profile) | Q(metadata__pet_owner_profile_id=profile.id)
            )
            .distinct()
            .order_by("-last_seen_at", "-created_at")
        )
        return LostPetReportListSerializer(reports, many=True, context=self.context).data


class BusinessWorkspaceUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    business_name = serializers.CharField(max_length=160)
    phone = serializers.CharField(max_length=40)
    commune = serializers.CharField(max_length=120)
    region = serializers.CharField(max_length=120)
    website = serializers.URLField(required=False, allow_blank=True)
    marketing_opt_in = serializers.BooleanField(required=False, default=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def update(self, instance, validated_data):
        user, profile = update_business_account(
            instance,
            {
                "user": {
                    "first_name": validated_data["first_name"],
                    "last_name": validated_data.get("last_name", ""),
                },
                "profile": {
                    "business_name": validated_data["business_name"],
                    "phone": validated_data["phone"],
                    "commune": validated_data["commune"],
                    "region": validated_data["region"],
                    "website": validated_data.get("website", ""),
                    "marketing_opt_in": validated_data.get("marketing_opt_in", True),
                    "notes": validated_data.get("notes", ""),
                },
            },
        )
        return {"user": user, "profile": profile}

    def to_representation(self, instance):
        return BusinessWorkspaceSerializer(instance).data


class BusinessBranchCreateSerializer(serializers.Serializer):
    branch_name = serializers.CharField(max_length=160)
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    commune = serializers.CharField(max_length=120)
    region = serializers.CharField(max_length=120)
    website = serializers.URLField(required=False, allow_blank=True)
    place_label = serializers.CharField(max_length=255)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if not (-90 <= attrs["latitude"] <= 90) or not (-180 <= attrs["longitude"] <= 180):
            raise serializers.ValidationError("La ubicación seleccionada no es válida.")
        return attrs

    def create(self, validated_data):
        profile = self.context["profile"]
        return create_business_branch(profile, validated_data)

    def to_representation(self, instance):
        profile = instance.owner_business_profile
        return BusinessOwnedPlaceSerializer(instance, context={"profile": profile}).data


class RegistrationCatalogSerializer(serializers.Serializer):
    business_kinds = serializers.ListField(child=serializers.DictField())


def build_registration_catalog():
    return {
        "business_kinds": [
            {
                "value": value,
                "label": label,
            }
            for value, label in BusinessKind.choices
        ],
    }
