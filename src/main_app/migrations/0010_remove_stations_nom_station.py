# Generated by Django 5.1.7 on 2025-04-07 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0009_evolutionofnationalfuelprices_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stations",
            name="nom_station",
        ),
    ]
