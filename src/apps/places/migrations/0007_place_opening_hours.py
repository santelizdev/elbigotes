from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0006_place_verification_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="place",
            name="opening_hours_raw",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Horario crudo de la fuente externa, sin normalizar.",
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="opening_hours_normalized",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Horario estructurado normalizado para cálculos internos.",
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="timezone_name",
            field=models.CharField(
                default="America/Santiago",
                help_text="Zona horaria IANA usada para cálculos de apertura.",
                max_length=64,
            ),
        ),
    ]