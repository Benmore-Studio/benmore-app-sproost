# Generated by Django 5.0.4 on 2025-03-10 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0003_property'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='is_first_property',
            field=models.BooleanField(default=False, help_text="Indicates if this is the property owner's first property."),
        ),
    ]
