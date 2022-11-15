from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from .models import *
from .forms import *


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
    tracks_array = create_tr_array(compositions)
    playlists = Playlist.objects.all()
    context = {
        "tracks_array": tracks_array,
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
    tracks_array = create_tr_array(compositions)
    track = Composition.objects.get(id=track_id)
    playlists = Playlist.objects.all()
    context = {
        "tracks_array": tracks_array,
        "compositions": compositions,
        "playlists": playlists,
        "played": track
    }
    return render(request, "music/tracks.html", context)


def show_playlist(request, playlist_id):
    """
    Отображает плейлист и его треки
    :param request:
    :param playlist_id:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    fix_order(playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'connect': None
    }
    return render(request, "music/playlist.html", context)


def count_track_number(playlist, track_number):
    size = playlist.compositions.count()
    if track_number > size:
        track_number = 1
    elif track_number < 1:
        track_number = size
    return track_number


def count_order(playlist, order):
    size = PlaylistsCompositions.objects.filter(playlist=playlist).count()
    if order > size:
        order = 1
    elif order < 1:
        order = size
    return order


def create_tr_array(compositions):
    size = Composition.objects.count()
    columns = size // 3
    if size % 3 > 0:
        columns += 1
    tracks_array = []
    for column in range(columns):
        tracks_array.append(compositions[column * 3:(column + 1) * 3])
    return tracks_array


def create_array(playlist, compositions):
    size = playlist.compositions.count()
    columns = size // 4
    if size % 4 > 0:
        columns += 1
    tracks_array = []
    for column in range(columns):
        tracks_array.append(compositions[column * 4:(column + 1) * 4])
    return tracks_array


def play_all(request, playlist_id, order):
    """
    Проигрывание треков из плейлиста
    :param request:
    :param playlist_id:
    :param track_number:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    order = count_order(playlist, order)
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    connect = PlaylistsCompositions.objects.get(order=order, playlist=playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'connect': connect
    }
    return render(request, "music/playlist.html", context)


def create_playlist(request):
    """
    Создание нового плейлиста
    :param request:
    :return:
    """
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AddPostForm()
    return render(request, "music/form.html", {"form": form})


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def new_track(request, playlist_id, track_number):
    """
    Проигрывание трека из списка
    :param request:
    :param playlist_id:
    :param track_number:
    :return:
    """
    playlists = Playlist.objects.all()
    playlist = Playlist.objects.get(id=playlist_id)
    track_number = count_track_number(playlist, track_number)
    composition = Composition.objects.get(order=track_number)
    context = {
        'playlists': playlists,
        "playlist": playlist,
        "composition": composition,
        "track_number": track_number
    }
    return render(request, "music/index.html", context)


def fix_order(playlist):
    previous = 0
    for connect in PlaylistsCompositions.objects.filter(playlist=playlist):
        order = connect.order
        if order - previous != 1:
            connect.order = previous + 1
            connect.save()
        previous = order


def delete_track(request, playlist_id, track_id):
    """
    Удаление трека из плейлиста
    :param request:
    :param playlist_id:
    :param track_id:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    connection = PlaylistsCompositions.objects.get(id=track_id)
    connection.delete()
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    fix_order(playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)


def delete_playlist(request, deleted_id):
    """
    Удаление плейлиста
    :param request:
    :param deleted_id:
    :return:
    """
    playlists = Playlist.objects.all()
    deleted = Playlist.objects.get(id=deleted_id)
    deleted.delete()
    context = {
        'playlists': playlists,
        "playlist": None,
        "composition": None
    }
    return render(request, "music/index.html", context)


def choose_playlist(request, track_id):
    """
    Выбрать плейлист для добавления
    :param request:
    :param track_id:
    :return:
    """
    playlists = Playlist.objects.all()
    track = Composition.objects.get(id=track_id)
    context = {
        'playlists': playlists,
        "track": track,
    }
    return render(request, "music/choose.html", context)


def add_track(request, track_id, playlist_id):
    """
    Добавление трека в плейлист
    :param request:
    :param track_id:
    :param playlist_id:
    :return:
    """
    playlist = Playlist.objects.get(id=playlist_id)
    track = Composition.objects.get(id=track_id)
    if not PlaylistsCompositions.objects.filter(
            playlist=playlist, composition=track).exists():
        PlaylistsCompositions.objects.create(playlist=playlist,
                                             composition=track, order=1)
    else:
        order = PlaylistsCompositions.objects.filter(playlist=playlist).count()
        PlaylistsCompositions.objects.create(playlist=playlist,
                                             composition=track, order=order+1)
    fix_order(playlist)
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)


def sort(request):
    film_pks_order = request.POST.getlist('item')
    print(film_pks_order)
    return HttpResponse("")
