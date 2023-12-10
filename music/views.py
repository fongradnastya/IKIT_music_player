from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseForbidden
from django.shortcuts import render, redirect

from users.models import User
from .functions import *
from .forms import *
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_default_playlist(sender, instance, created, **kwargs):
    if created:
        Playlist.objects.create(owner=instance, name='Favorite',
                                is_default=True)


def index(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    playlists = Playlist.objects.all().filter(owner=user)
    context = {
        'playlists': playlists,
        "playlist": None,
        "connection": None,
        "username": user.username,
    }
    return render(request, "music/index.html", context)


def tracks(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    compositions = Composition.objects.all()
    counter = 1
    for composition in compositions:
        composition.order = counter
        composition.save()
        counter += 1
    tracks_array = create_tr_array(compositions)
    playlists = Playlist.objects.all().filter(owner=user)
    context = {
        "tracks_array": tracks_array,
        "compositions": compositions,
        "playlists": playlists,
        "played": None,
        'username': user.username,
    }
    return render(request, "music/tracks.html", context)


def play_track(request, track_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    compositions = Composition.objects.all()
    size = Composition.objects.count()
    if track_id < 1:
        track_id = size
    elif track_id > size:
        track_id = 1
    tracks_array = create_tr_array(compositions)
    track = Composition.objects.get(order=track_id)
    playlists = Playlist.objects.all().filter(owner=user)
    context = {
        "tracks_array": tracks_array,
        "compositions": compositions,
        "playlists": playlists,
        "played": track,
        'username': user.username,
    }
    return render(request, "music/tracks.html", context)


def show_playlist(request, playlist_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(id=playlist_id)
    if playlist.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to see this playlist.")
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    fix_order(playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'connect': None,
        'username': user.username,
    }
    return render(request, "music/playlist.html", context)

def show_favorite(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])

    # Get the "Favorite" playlist for the current user
    playlist = Playlist.objects.get(owner=user, name='Favorite')
    return redirect(f"playlist/{playlist.id}")


def play_all(request, playlist_id, order):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(id=playlist_id)
    if playlist.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to see this playlist.")
    order = count_order(playlist, order)
    fix_order(playlist)
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    connect = PlaylistsCompositions.objects.get(order=order, playlist=playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'connect': connect,
        'username': user.username,
    }
    return render(request, "music/playlist.html", context)


def create_playlist(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.owner = user
            playlist.save()
            return redirect('home')
    else:
        form = AddPostForm()
    context = {
        "form": form,
        'username': user.username,
    }
    return render(request, "music/form.html", context)


def new_track(request, playlist_id, track_order):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlists = Playlist.objects.all().filter(owner=user)
    playlist = Playlist.objects.get(id=playlist_id)
    if playlist.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to add tracks to this playlist.")
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
        'username': user.username,
    }
    return render(request, "music/index.html", context)


def delete_track(request, playlist_id, track_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(id=playlist_id)
    if playlist.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to delete tracks from this playlist.")
    connection = PlaylistsCompositions.objects.get(id=track_id)
    connection.delete()
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    tracks_array = create_array(playlist, compositions)
    fix_order(playlist)
    context = {
        'playlist': playlist,
        'compositions': compositions,
        'tracks': tracks_array,
        'composition': None,
        'username': user.username,
    }
    return render(request, "music/playlist.html", context)


def delete_playlist(request, deleted_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlists = Playlist.objects.all().filter(owner=user)
    deleted = Playlist.objects.get(id=deleted_id)
    if deleted.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to delete this playlist.")
    deleted.delete()
    context = {
        'playlists': playlists,
        "playlist": None,
        "composition": None,
        'username': user.username,
    }
    return render(request, "music/index.html", context)


def choose_playlist(request, track_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlists = Playlist.objects.all().filter(owner=user)
    track = Composition.objects.get(id=track_id)
    context = {
        'playlists': playlists,
        "track": track,
        'username': user.username,
    }
    return render(request, "music/choose.html", context)


def add_track(request, track_id, playlist_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(id=playlist_id)
    if playlist.owner != user:
        return HttpResponseForbidden(
            "You do not have permission to add tracks to this playlist.")
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
        'composition': None,
        'username': user.username,
    }
    return render(request, "music/playlist.html", context)

def like_playlist(request, track_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(owner=user, name="Favorite")
    return redirect(f"/add_track/{track_id}/playlist/{playlist.id}")


def sort(request, playlist_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(id=playlist_id)
    track_pks_order = request.POST.getlist('item')
    print(track_pks_order)
    for idx, track_pk in enumerate(track_pks_order, start=1):
        composition = Composition.objects.get(pk=track_pk)
        connect = PlaylistsCompositions.objects.get(composition=composition,
                                                    playlist=playlist)
        connect.order = idx
        connect.save()
    compositions = PlaylistsCompositions.objects.filter(playlist=playlist)
    context = {
        "compositions": compositions,
        'username': user.username,
    }
    return render(request, "music/playlist.html", context)


def remove_from_favorite(request, track_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(id=request.session['user_id'])
    playlist = Playlist.objects.get(owner=user, name='Favorite')
    connections = PlaylistsCompositions.objects.filter(playlist=playlist)
    for connection in connections:
        if connection.composition.pk == track_id:
            connection.delete()
            compositions = PlaylistsCompositions.objects.filter(
                playlist=playlist)
            tracks_array = create_array(playlist, compositions)
            fix_order(playlist)
            context = {
                'playlist': playlist,
                'compositions': compositions,
                'tracks': tracks_array,
                'composition': None,
                'username': user.username,
            }
            return render(request, "music/playlist.html", context)
