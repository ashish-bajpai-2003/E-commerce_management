# Generated by Django 5.1.6 on 2025-04-28 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facebook', '0012_remove_myproduct_cname'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategory',
            name='subcategory_image',
            field=models.ImageField(blank=True, null=True, upload_to='subcategory_image/'),
        ),
    ]
