# Generated by Django 5.0.4 on 2025-03-11 08:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_remove_message_receiver_message_receiver'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='read_by',
            field=models.ManyToManyField(blank=True, help_text=' Track who has read it', related_name='messages_read', to=settings.AUTH_USER_MODEL),
        ),
    ]
