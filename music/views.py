from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect

from users.models import User
from .functions import *
from .forms import *


def index(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    playlists = Playlist.objects.all()
    context = {
        'playlists': playlists,
        "playlist": None,
        "connection": None,
        "username": user.username,
    }
    return render(request, "music/index.html", context)


def tracks(request):
    compositions = Composition.objects.all()
    add_to_favorite()
    counter = 1
    for composition in compositions:
        composition.order = counter
        composition.save()
        counter += 1
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
    compositions = Composition.objects.all()
    size = Composition.objects.count()
    if track_id < 1:
        track_id = size
    elif track_id > size:
        track_id = 1
    tracks_array = create_tr_array(compositions)
    track = Composition.objects.get(order=track_id)
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
    add_to_favorite()
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
    fix_order(playlist)
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


def new_track(request, playlist_id, track_order):
    """
    Проигрывание трека из списка
    :param request:
    :param playlist_id:
    :param track_number:
    :return:
    """
    playlists = Playlist.objects.all()
    playlist = Playlist.objects.get(id=playlist_id)
    track_order = count_order(playlist, track_order)
    if not PlaylistsCompositions.objects.filter(playlist=playlist):
        connection = None
    else:
        connection = PlaylistsCompositions.objects.get(order=track_order,
                                                       playlist=playlist)
    context = {
        'playlists': playlists,
        "playlist": playlist,
        "connection": connection,
    }
    return render(request, "music/index.html", context)


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
    add_to_favorite()
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
    add_to_favorite()
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None
    }
    return render(request, "music/playlist.html", context)


def sort(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    track_pks_order = request.POST.getlist('item')
    print(track_pks_order)
    for idx, track_pk in enumerate(track_pks_order, start=1):
        composition = Composition.objects.get(pk=track_pk)
        connect = PlaylistsCompositions.objects.get(composition=composition,
                                                    playlist=playlist)
        connect.order = idx
        connect.save()
    add_to_favorite()
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    return render(request, "music/playlist.html", compositions)


def remove_from_favorite(request, track_id):
    playlist = Playlist.objects.get(id=5)
    connections = PlaylistsCompositions.objects.filter(playlist=playlist)
    print(track_id)
    for connection in connections:
        if connection.composition.pk == track_id:
            connection.delete()
            compositions = PlaylistsCompositions.objects.filter(
                playlist=playlist)
            tracks_array = create_array(playlist, compositions)
            fix_order(playlist)
            add_to_favorite()
            context = {
                'playlist': playlist,
                'compositions': compositions,
                'tracks': tracks_array,
                'composition': None
            }
            return render(request, "music/playlist.html", context)
