# Generated by Django 5.0.4 on 2025-01-28 09:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_rename_city_contractorprofile_address_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='agentprofile',
            name='invited_home_owners',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='invited_home_owners', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='invited_agents',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='invited_agents', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
