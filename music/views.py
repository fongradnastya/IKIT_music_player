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
    playlists = Playlist.objects.all()
    context = {
        "compositions": compositions,
        "playlists": playlists,
        "played": None
    }
    return render(request, "music/tracks.html", context)


def play_track(request, track_id):
    if track_id < 1:
        track_id = 12
    elif track_id > 12:
        track_id = 1
    compositions = Composition.objects.all()
    track = Composition.objects.get(id=track_id)
    playlists = Playlist.objects.all()
    context = {
        "compositions": compositions,
        "playlists": playlists,
        "played": track
    }
    return render(request, "music/tracks.html", context)


def show_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    compositions = playlist.compositions.all()
    tracks_array = create_array(playlist, compositions)
    set_order(compositions)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)


def set_order(compositions):
    counter = 1
    for composition in Composition.objects.all():
        if composition in compositions:
            composition.order = counter
            counter += 1
        else:
            composition.order = 0
        composition.save()


def count_track_number(playlist, track_number):
    size = playlist.compositions.count()
    if track_number > size:
        track_number = 1
    elif track_number < 1:
        track_number = size
    return track_number


def create_array(playlist, compositions):
    size = playlist.compositions.count()
    columns = size // 4
    if size % 4 > 0:
        columns += 1
    tracks_array = []
    for column in range(columns):
        tracks_array.append(compositions[column * 4:(column + 1) * 4])
    return tracks_array


def play_all(request, playlist_id, track_number):
    playlist = Playlist.objects.get(id=playlist_id)
    compositions = playlist.compositions.all()
    tracks_array = create_array(playlist, compositions)
    track_number = count_track_number(playlist, track_number)
    composition = Composition.objects.get(order=track_number)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': composition
    }
    return render(request, "music/playlist.html", context)


def create_playlist(request):
    return render(request, "music/form.html")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def new_track(request, playlist_id, track_number):
    playlists = Playlist.objects.all()
    playlist = Playlist.objects.get(id=playlist_id)
    track_number = count_track_number(playlist, track_number)
    composition = playlist.compositions.all()[track_number]
    context = {
        'playlists': playlists,
        "playlist": playlist,
        "composition": composition,
        "track_number": track_number
    }
    return render(request, "music/index.html", context)


def delete_track(request, playlist_id, track_id):
    playlist = Playlist.objects.get(id=playlist_id)
    track = Composition.objects.get(id=track_id)
    track.delete()
    compositions = playlist.compositions.all()
    set_order(compositions)
    tracks_array = create_array(playlist, compositions)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)
