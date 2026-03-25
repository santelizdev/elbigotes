from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150, unique=True)),
                ("slug", models.SlugField(max_length=220, unique=True)),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("manual", "Manual"),
                            ("partner", "Partner"),
                            ("scraper", "Scraper"),
                            ("api", "API"),
                        ],
                        default="manual",
                        max_length=24,
                    ),
                ),
                ("domain", models.CharField(blank=True, max_length=255)),
                ("reliability_score", models.DecimalField(decimal_places=2, default=0.5, max_digits=3)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Source",
                "verbose_name_plural": "Sources",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="SourceSyncRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("succeeded", "Succeeded"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=24,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("items_seen", models.PositiveIntegerField(default=0)),
                ("items_created", models.PositiveIntegerField(default=0)),
                ("items_updated", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("stats", models.JSONField(blank=True, default=dict)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="sync_runs",
                        to="ingestion.source",
                    ),
                ),
            ],
            options={
                "verbose_name": "Source sync run",
                "verbose_name_plural": "Source sync runs",
                "ordering": ["-created_at"],
            },
        ),
    ]

