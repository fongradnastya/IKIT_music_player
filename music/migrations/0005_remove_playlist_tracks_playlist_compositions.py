# Generated by Django 4.1.2 on 2022-11-08 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_remove_playlist_head_playlist_tracks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playlist',
            name='tracks',
        ),
        migrations.AddField(
            model_name='playlist',
            name='compositions',
            field=models.ManyToManyField(blank=True, null=True, to='music.composition'),
        ),
    ]
