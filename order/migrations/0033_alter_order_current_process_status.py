# Generated by Django 5.1.4 on 2025-03-28 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0032_order_organization_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='current_process_status',
            field=models.CharField(choices=[('initiated', 'Initiated'), ('requested', 'Requested'), ('on_going', 'On going'), ('paused', 'Paused'), ('verification', 'Verification'), ('completed', 'Completed'), ('over_due', 'Over due')], default='initiated', help_text='Status of current process', max_length=20),
        ),
    ]
