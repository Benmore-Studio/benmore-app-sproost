# Generated by Django 5.0.4 on 2025-02-28 08:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_chatroom_chatroominvitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatroominvitation',
            name='room',
        ),
        migrations.DeleteModel(
            name='ChatRoom',
        ),
        migrations.DeleteModel(
            name='ChatRoomInvitation',
        ),
    ]
