from .models import *


"""def add_to_favorite():
    playlist = Playlist.objects.get(id=5)
    connects = PlaylistsCompositions.objects.filter(playlist=playlist)
    for connect in PlaylistsCompositions.objects.all():
        composition = connect.composition
        if connect in connects:
            composition.is_liked = True
        else:
            composition.is_liked = False
        composition.save()"""


def count_order(playlist, order):
    size = PlaylistsCompositions.objects.filter(playlist=playlist).count()
    if order > size:
        order = 1
    elif order < 1:
        order = size
    return order


def fix_order(playlist):
    previous = 0
    for connect in PlaylistsCompositions.objects.filter(playlist=playlist):
        order = connect.order
        if order - previous != 1:
            connect.order = previous + 1
            connect.save()
        previous = order


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
