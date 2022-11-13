from django.contrib import admin

from .models import *


class CompositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'cover', 'is_played', 'is_liked',
                    'order')
    list_display_links = ('id', 'name', 'author')
    search_fields = ('name', 'author')


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cover', 'description', 'is_default')


class PlaylistsCompositionsAdmin(admin.ModelAdmin):
    list_display = ('playlist', 'composition', 'order')


admin.site.register(Composition, CompositionAdmin)
admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlaylistsCompositions, PlaylistsCompositionsAdmin)
