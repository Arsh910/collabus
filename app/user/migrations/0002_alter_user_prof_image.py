# Generated by Django 3.2.25 on 2025-06-11 06:34

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="prof_image",
            field=models.ImageField(
                blank=True, null=True, upload_to=user.models.user_image_file_path
            ),
        ),
    ]
