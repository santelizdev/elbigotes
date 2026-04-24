from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0009_public_pet_operations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="category",
        ),
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="place",
        ),
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="price_label",
        ),
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="quota",
        ),
        migrations.AddField(
            model_name="publicpetoperation",
            name="creator_name",
            field=models.CharField(default="Organizador no informado", max_length=160),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="publicpetoperation",
            name="creator_type",
            field=models.CharField(
                choices=[("public", "Public"), ("private", "Private")],
                default="public",
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="publicpetoperation",
            name="image",
            field=models.ImageField(blank=True, upload_to="places/public-operations/%Y/%m/"),
        ),
        migrations.AlterField(
            model_name="publicpetoperation",
            name="region",
            field=models.CharField(max_length=120),
        ),
    ]
