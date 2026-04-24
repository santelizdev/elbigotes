from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("places", "0010_refine_public_pet_operations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="registration_url",
        ),
        migrations.RemoveField(
            model_name="publicpetoperation",
            name="source_url",
        ),
    ]
