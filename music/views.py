import math

from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import *


def index(request):
    playlists = Playlist.objects.all()
    context = {
        'playlists': playlists,
        "playlist": None,
        "composition": None
    }
    return render(request, "music/index.html", context)


def tracks(request):
    compositions = Composition.objects.all()
    return render(request, "music/tracks.html", {"compositions": compositions,
                                                 "played": None})


def show_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    compositions = playlist.compositions.all()
    size = playlist.compositions.count()
    columns = size // 4
    if size % 4 > 0:
        columns += 1
    tracks_array = []
    for column in range(columns):
        tracks_array.append(compositions[column*4:(column+1)*4])
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)


def create_playlist(request):
    return render(request, "music/form.html")


def play_track(request, track_id):
    if track_id < 1:
        track_id = 12
    elif track_id > 12:
        track_id = 1
    compositions = Composition.objects.all()
    track = Composition.objects.get(id=track_id)
    return render(request, "music/tracks.html", {"compositions": compositions,
                                                 "played": track})


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def new_track(request, playlist_id, track_number):
    playlists = Playlist.objects.all()
    playlist = Playlist.objects.get(id=playlist_id)
    size = playlist.compositions.count()
    if track_number >= size:
        track_number = 1
    elif track_number < 0:
        track_number = size - 1
    composition = playlist.compositions.all()[track_number]
    context = {
        'playlists': playlists,
        "playlist": playlist,
        "composition": composition,
        "size": size,
        "track_number": track_number
    }
    return render(request, "music/index.html", context)