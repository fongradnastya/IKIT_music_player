from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='home'),
    path('playlist/<int:playlist_id>', show_playlist, name='playlist'),
    path('tracks', tracks, name="tracks"),
    path('new_playlist/', create_playlist, name='new'),
    path('tracks/<int:track_id>', play_track, name="play"),
    path('/<int:playlist_id>', start_playlist, name="start")
]


