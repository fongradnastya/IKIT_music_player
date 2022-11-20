from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('playlist/<int:playlist_id>', show_playlist, name='playlist'),
    path('tracks', tracks, name="tracks"),
    path('new_playlist/', create_playlist, name='new'),
    path('tracks/<int:track_id>', play_track, name="play"),
    path('<int:playlist_id>/track/<int:track_order>', new_track, name="next"),
    path('playlist/<int:playlist_id>/track/<int:order>', play_all,
         name="play_all"),
    path("playlist/<int:playlist_id>/-track/<int:track_id>", delete_track,
         name="delete"),
    path('-playlists/<int:deleted_id>', delete_playlist, name="delete_pl"),
    path('add_track/<int:track_id>', choose_playlist, name="choose"),
    path('add_track/<int:track_id>/playlist/<int:playlist_id>', add_track,
         name="add"),
    path("sort/", sort, name="sort"),
    path("favorite/<int:track_id>", remove_from_favorite, name="remove")
]

