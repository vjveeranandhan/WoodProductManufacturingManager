# Generated by Django 5.1.4 on 2025-03-16 14:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('user_manager', '0006_alter_customuser_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
    ]
