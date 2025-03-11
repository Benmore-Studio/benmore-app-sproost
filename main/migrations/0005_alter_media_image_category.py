from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_merge_20250228_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='image_category',
            field=models.CharField(blank=True, choices=[('before', 'Before'), ('after', 'After')], default='before', max_length=10, null=True),
        ),
    ]
