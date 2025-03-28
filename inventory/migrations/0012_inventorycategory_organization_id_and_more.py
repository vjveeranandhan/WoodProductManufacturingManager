# Generated by Django 5.1.4 on 2025-03-17 16:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_material_mrp_in_gst'),
        ('organization', '0002_organization_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorycategory',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
        migrations.AddField(
            model_name='material',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
    ]
