# Generated by Django 5.0.2 on 2024-10-04 11:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignedaccount',
            name='assigned_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_properties_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='assignedaccount',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_properties_to', to=settings.AUTH_USER_MODEL),
        ),
    ]