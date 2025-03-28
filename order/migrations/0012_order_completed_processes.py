# Generated by Django 5.1.4 on 2025-01-08 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0011_alter_order_carpenter_id_alter_order_main_manager_id_and_more"),
        ("process", "0011_processmaterials"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="completed_processes",
            field=models.ManyToManyField(
                blank=True, related_name="process", to="process.process"
            ),
        ),
    ]
