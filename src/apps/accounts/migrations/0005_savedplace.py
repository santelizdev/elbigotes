from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("places", "0007_place_opening_hours"),
        ("accounts", "0004_remove_businessprofile_grace_expires_at_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SavedPlace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_by_users",
                        to="places.place",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saved_places",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Saved place",
                "verbose_name_plural": "Saved places",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="savedplace",
            constraint=models.UniqueConstraint(
                fields=("user", "place"),
                name="accounts_saved_place_unique_user_place",
            ),
        ),
    ]
