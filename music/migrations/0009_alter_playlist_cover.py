# Generated by Django 4.1.2 on 2022-11-12 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_alter_playlist_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='cover',
            field=models.ImageField(default='photos/2022/11/07/cover.png', upload_to='photos/%Y/%m/%d/'),
        ),
    ]