from django.db import models
from django.urls import reverse
from .linked_list import *


class Composition(models.Model):
    name = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.ImageField(upload_to="photos/%Y/%m/%d/")
    audio = models.FileField(upload_to="audio/%Y/%m/%d/")
    is_played = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)

    order = models.PositiveSmallIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.author}"

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_id': self.pk})

    class Meta:
        ordering = ['name', 'author']


class Playlist(models.Model):
    name = models.CharField(max_length=255, null=True)
    cover = models.ImageField(upload_to="photos/%Y/%m/%d/",
                              default="photos/2022/11/07/cover.png")
    description = models.CharField(max_length=500, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    compositions = models.ManyToManyField(Composition,
                                          through='PlaylistsCompositions')

    def __str__(self):
        return f"{self.name}"


class PlaylistsCompositions(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']


"""class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=250)
    password = models.CharField(max_length=100)"""
