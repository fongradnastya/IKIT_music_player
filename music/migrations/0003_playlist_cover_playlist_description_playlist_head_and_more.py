# Generated by Django 4.1.2 on 2022-11-07 09:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_linkedlistitem_playlist_alter_composition_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='cover',
            field=models.ImageField(null=True, upload_to='photos/%Y/%m/%d/'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='description',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='playlist',
            name='head',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='music.linkedlistitem'),
        ),
        migrations.AddField(
            model_name='playlist',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playlist',
            name='length',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playlist',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
