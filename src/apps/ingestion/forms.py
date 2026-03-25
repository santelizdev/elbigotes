from django import forms


class ImportPetPlacesAdminForm(forms.Form):
    csv_file = forms.FileField(
        label="Archivo CSV",
        help_text=(
            "Formato UTF-8 con columnas: country, region, commune, category, name, "
            "address, latitude, longitude, phone, email, website, source, notes."
        ),
    )
    dataset_name = forms.CharField(
        label="Nombre del lote",
        required=False,
        help_text="Opcional. Si lo dejas vacío, se usará el nombre del archivo.",
    )
    default_source = forms.CharField(
        label="Source por defecto",
        required=False,
        initial="manual_seed",
        help_text="Se usa solo cuando una fila venga sin valor en la columna source.",
    )
    update_existing = forms.BooleanField(
        label="Actualizar duplicados razonables",
        required=False,
        help_text=(
            "Si se marca, la importación actualizará lugares existentes con el "
            "mismo name + commune + category."
        ),
    )
    dry_run = forms.BooleanField(
        label="Solo validar",
        required=False,
        help_text=(
            "Ejecuta la importación y luego revierte la transacción para revisar "
            "el resumen sin persistir cambios."
        ),
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.lower().endswith(".csv"):
            raise forms.ValidationError("Debes subir un archivo .csv.")
        return csv_file
