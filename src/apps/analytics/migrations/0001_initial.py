import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("places", "0006_place_verification_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category_slug", models.CharField(blank=True, max_length=120)),
                ("search_term", models.CharField(blank=True, max_length=160)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("commune", models.CharField(blank=True, max_length=120)),
                ("has_user_location", models.BooleanField(default=False)),
                ("user_latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("user_longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("radius_km", models.PositiveIntegerField(blank=True, null=True)),
                ("verified_only", models.BooleanField(default=False)),
                ("result_count", models.PositiveIntegerField(default=0)),
                ("is_registered", models.BooleanField(default=False)),
                ("device_type", models.CharField(choices=[("phone", "Phone"), ("pc", "PC"), ("tablet", "Tablet"), ("unknown", "Unknown")], default="unknown", max_length=20)),
                ("path", models.CharField(blank=True, max_length=255)),
                ("user_agent", models.TextField(blank=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="search_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Search event",
                "verbose_name_plural": "Search events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PlaceViewEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category_slug", models.CharField(blank=True, max_length=120)),
                ("region", models.CharField(blank=True, max_length=120)),
                ("commune", models.CharField(blank=True, max_length=120)),
                ("verification_status", models.CharField(blank=True, max_length=40)),
                ("is_registered", models.BooleanField(default=False)),
                ("device_type", models.CharField(choices=[("phone", "Phone"), ("pc", "PC"), ("tablet", "Tablet"), ("unknown", "Unknown")], default="unknown", max_length=20)),
                ("path", models.CharField(blank=True, max_length=255)),
                ("user_agent", models.TextField(blank=True)),
                ("place", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="view_events", to="places.place")),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="place_view_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Place view event",
                "verbose_name_plural": "Place view events",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="searchevent",
            index=models.Index(fields=["created_at"], name="analytics_s_created_6aaae7_idx"),
        ),
        migrations.AddIndex(
            model_name="searchevent",
            index=models.Index(fields=["category_slug"], name="analytics_s_categor_cfd2ab_idx"),
        ),
        migrations.AddIndex(
            model_name="searchevent",
            index=models.Index(fields=["device_type"], name="analytics_s_device__e964da_idx"),
        ),
        migrations.AddIndex(
            model_name="searchevent",
            index=models.Index(fields=["is_registered"], name="analytics_s_is_regi_117eef_idx"),
        ),
        migrations.AddIndex(
            model_name="placeviewevent",
            index=models.Index(fields=["created_at"], name="analytics_p_created_f61f3e_idx"),
        ),
        migrations.AddIndex(
            model_name="placeviewevent",
            index=models.Index(fields=["place"], name="analytics_p_place_i_0e1236_idx"),
        ),
        migrations.AddIndex(
            model_name="placeviewevent",
            index=models.Index(fields=["device_type"], name="analytics_p_device__a09959_idx"),
        ),
        migrations.AddIndex(
            model_name="placeviewevent",
            index=models.Index(fields=["is_registered"], name="analytics_p_is_regi_52af55_idx"),
        ),
    ]
