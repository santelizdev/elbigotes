import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("places", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="place",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                blank=True,
                geography=True,
                null=True,
                srid=4326,
            ),
        ),
        migrations.AddField(
            model_name="place",
            name="last_quality_check_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="place",
            name="quality_score",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="PlaceQualityIssue",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=64)),
                (
                    "severity",
                    models.CharField(
                        choices=[("info", "Info"), ("warning", "Warning"), ("critical", "Critical")],
                        max_length=20,
                    ),
                ),
                ("message", models.CharField(max_length=255)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("is_resolved", models.BooleanField(default=False)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quality_issues",
                        to="places.place",
                    ),
                ),
            ],
            options={
                "verbose_name": "Place quality issue",
                "verbose_name_plural": "Place quality issues",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="DuplicatePlaceCandidate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reason", models.CharField(max_length=255)),
                ("similarity_score", models.DecimalField(decimal_places=2, max_digits=5)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("confirmed", "Confirmed"),
                            ("dismissed", "Dismissed"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "candidate_place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duplicate_matches",
                        to="places.place",
                    ),
                ),
                (
                    "primary_place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="duplicate_candidates",
                        to="places.place",
                    ),
                ),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_duplicate_candidates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Duplicate place candidate",
                "verbose_name_plural": "Duplicate place candidates",
                "ordering": ["-similarity_score", "-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="placequalityissue",
            constraint=models.UniqueConstraint(
                fields=("place", "code", "message", "is_resolved"),
                name="places_quality_issue_unique_open",
            ),
        ),
        migrations.AddConstraint(
            model_name="duplicateplacecandidate",
            constraint=models.UniqueConstraint(
                fields=("primary_place", "candidate_place"),
                name="places_duplicate_candidate_unique_pair",
            ),
        ),
    ]

