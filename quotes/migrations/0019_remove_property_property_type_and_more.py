# Generated by Django 5.0.2 on 2025-01-13 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0018_remove_quoterequest_quote_for_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='property_type',
        ),
        migrations.AddField(
            model_name='quoterequest',
            name='property_type',
            field=models.CharField(choices=[('interior', 'Interior'), ('exterior', 'Exterior')], default='interior', max_length=50),
            preserve_default=False,
        ),
    ]