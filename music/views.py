from django.http import HttpResponseNotFound
from django.shortcuts import render
from .models import *


def index(request):
    playlists = Playlist.objects.all()
    return render(request, "music/index.html", {'playlists': playlists})


def tracks(request):
    compositions = Composition.objects.all()
    return render(request, "music/tracks.html", {"compositions": compositions,
                                                 "played": None})


def show_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    compositions = playlist.compositions.all()
    return render(request, "music/playlist.html", {'playlist': playlist,
                                                   'compositions': compositions})


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


def start_playlist(request, playlist_id):
    playlists = Playlist.objects.all()
    playlist = Playlist.objects.get(id=playlist_id)
    composition = playlist.compositions.all()[0]
    context = {
        'playlists': playlists,
        "playlist": playlist,
        "composition": composition
    }
    return render(request, "music/index.html", context)
