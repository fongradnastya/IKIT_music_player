# Generated by Django 4.1.2 on 2022-11-12 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0006_remove_playlist_length_composition_order_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]