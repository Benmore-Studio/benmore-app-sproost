# Generated by Django 5.0.4 on 2025-02-19 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0004_rename_returned_budget_quoterequest_proposed_returned_budget_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='has_quotes',
            field=models.BooleanField(default=False),
        ),
    ]
