# Generated by Django 5.0.1 on 2024-02-08 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0005_alter_enterprise_enterprise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category',
            field=models.CharField(help_text='category', max_length=100),
        ),
    ]