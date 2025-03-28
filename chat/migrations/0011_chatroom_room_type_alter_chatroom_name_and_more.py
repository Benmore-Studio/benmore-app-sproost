# Generated by Django 5.0.4 on 2025-03-26 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_message_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='room_type',
            field=models.CharField(choices=[('group', 'Group'), ('private', 'Private'), ('broadcast', 'Broadcast')], default='private', max_length=20),
        ),
        migrations.AlterField(
            model_name='chatroom',
            name='name',
            field=models.CharField(db_index=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
