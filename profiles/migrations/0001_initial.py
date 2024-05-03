# Generated by Django 5.0.4 on 2024-05-03 22:42

import address.models
import django.db.models.deletion
import profiles.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0003_auto_20200830_1851'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('registration_number', models.CharField(max_length=225)),
                ('specialization', models.CharField(blank=True, max_length=225, null=True)),
                ('city', models.CharField(max_length=50)),
                ('image', models.ImageField(null=True, upload_to=profiles.models.image_upload_location)),
                ('company_address', address.models.AddressField(on_delete=django.db.models.deletion.CASCADE, to='address.address')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='contractor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state_province', models.CharField(blank=True, max_length=50, null=True)),
                ('address', address.models.AddressField(on_delete=django.db.models.deletion.CASCADE, to='address.address')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
