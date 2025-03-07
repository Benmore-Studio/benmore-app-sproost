# Generated by Django 5.0.4 on 2025-01-28 10:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_rename_invited_home_owners_agentprofile_agent_invited_home_owners_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='home_owner_associated_contarctors',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='home_owner_invited_agents',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='home_owner_associated_contarctors',
            field=models.ManyToManyField(related_name='associated_contarctors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='home_owner_invited_agents',
            field=models.ManyToManyField(related_name='invited_agents', to=settings.AUTH_USER_MODEL),
        ),
    ]
