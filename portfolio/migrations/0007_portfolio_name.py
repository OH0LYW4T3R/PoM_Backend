# Generated by Django 5.0.1 on 2024-02-08 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_alter_category_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
