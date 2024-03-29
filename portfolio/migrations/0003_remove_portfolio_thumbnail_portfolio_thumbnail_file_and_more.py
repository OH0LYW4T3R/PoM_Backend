# Generated by Django 5.0.1 on 2024-02-03 21:53

import portfolio.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_alter_portfolio_thumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='portfolio',
            name='thumbnail_file',
            field=models.ImageField(blank=True, null=True, upload_to=portfolio.models.upload_to_portfolio_thumbnail),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='thumbnail_url',
            field=models.CharField(blank=True, max_length=10000),
        ),
    ]
