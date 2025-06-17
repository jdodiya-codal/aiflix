
from django.contrib import admin
from .models import Movie, Genre

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'rating', 'is_featured')
    search_fields = ('title', 'actors')

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre, GenreAdmin)
