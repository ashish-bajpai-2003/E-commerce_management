# Generated by Django 5.1.6 on 2025-05-01 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0019_myorder_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='myproduct',
            name='stock',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
