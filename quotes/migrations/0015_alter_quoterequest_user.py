# Generated by Django 5.0.2 on 2025-01-10 17:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_rename_city_contractorprofile_address_and_more'),
        ('quotes', '0014_alter_quoterequest_contractors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quoterequest',
            name='user',
            field=models.ForeignKey(help_text='the user who created the quote', on_delete=django.db.models.deletion.CASCADE, related_name='quote_requests', to='profiles.userprofile'),
        ),
    ]