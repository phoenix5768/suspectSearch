# Generated by Django 4.2.10 on 2024-02-22 17:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sketch", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="criminalsdata",
            name="picture",
            field=models.ImageField(blank=True, null=True, upload_to="images/"),
        ),
    ]
