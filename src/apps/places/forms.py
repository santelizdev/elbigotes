import json

from django import forms
from django.utils.safestring import mark_safe

from apps.places.chile_locations import CHILE_REGIONS, get_commune_choices, get_region_choices
from apps.places.models import PublicPetOperation


class PublicPetOperationAdminForm(forms.ModelForm):
    region = forms.ChoiceField(choices=(), required=True)
    commune = forms.ChoiceField(choices=(), required=True)

    class Meta:
        model = PublicPetOperation
        fields = "__all__"
        widgets = {
            "latitude": forms.NumberInput(attrs={"readonly": "readonly"}),
            "longitude": forms.NumberInput(attrs={"readonly": "readonly"}),
            "address": forms.TextInput(
                attrs={
                    "placeholder": "Escribe la dirección y selecciona una sugerencia de Google",
                    "autocomplete": "off",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            current_region = self.data.get("region") or ""
            current_commune = self.data.get("commune") or ""
        else:
            current_region = self.initial.get("region") or getattr(self.instance, "region", "") or ""
            current_commune = self.initial.get("commune") or getattr(self.instance, "commune", "") or ""

        self.fields["region"].choices = get_region_choices()
        self.fields["commune"].choices = get_commune_choices(current_region)
        if current_commune and current_commune not in dict(self.fields["commune"].choices):
            self.fields["commune"].choices = [
                *self.fields["commune"].choices,
                (current_commune, current_commune),
            ]

        self.fields["latitude"].help_text = "Se completa automáticamente al seleccionar una dirección."
        self.fields["longitude"].help_text = "Se completa automáticamente al seleccionar una dirección."

    def clean_commune(self):
        commune = self.cleaned_data.get("commune", "")
        region = self.cleaned_data.get("region", "")
        available_communes = dict(get_commune_choices(region))

        if commune and commune not in available_communes:
            raise forms.ValidationError("La comuna seleccionada no pertenece a la región indicada.")
        return commune


def build_public_pet_operation_admin_config(*, google_maps_api_key: str, latitude, longitude) -> str:
    payload = {
        "googleMapsApiKey": google_maps_api_key,
        "regions": CHILE_REGIONS,
        "latitude": latitude,
        "longitude": longitude,
    }
    return mark_safe(json.dumps(payload))
