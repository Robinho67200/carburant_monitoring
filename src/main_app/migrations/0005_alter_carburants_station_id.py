# Generated by Django 5.1.7 on 2025-03-25 09:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0004_alter_carburants_dat_maj"),
    ]

    operations = [
        migrations.AlterField(
            model_name="carburants",
            name="station_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="main_app.stations"
            ),
        ),
    ]
