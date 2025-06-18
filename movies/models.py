from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_genres = models.JSONField(default=list)
    liked_actors = models.JSONField(default=list)
    liked_movies = models.ManyToManyField("Movie", blank=True)
    watch_history = models.ManyToManyField("Movie", related_name="watched_by", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Genre(models.Model):
    name = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='genre_thumbnails/', blank=True, null=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    poster = models.URLField(null=True, blank=True)
    poster_url = models.URLField(null=True, blank=True)
    trailer_url = models.URLField(blank=True, null=True)
    release_year = models.IntegerField()
    genres = models.ManyToManyField(Genre)
    actors = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    rating = models.FloatField()
    award_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_latest = models.BooleanField(default=False)
    is_top_rated = models.BooleanField(default=False)
    trailer_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

