# Generated by Django 5.0.4 on 2025-03-19 19:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0007_roommembership'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroom',
            name='members',
        ),
    ]
