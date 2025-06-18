import base64
import requests
from django.core.management.base import BaseCommand
from movies.models import Movie, Genre
import os

TMDB_API_KEY = '22c8aea5e941ff42bc5aa70532467e07'
TMDB_API_URL = 'https://api.themoviedb.org/3/movie/popular'
POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500'

def upload_tmdb_image_to_imgbb(tmdb_image_url):
    api_key = os.getenv("IMGBB_API_KEY")
    response = requests.get(tmdb_image_url)
    if response.status_code != 200:
        return None
    image_data = response.content
    encoded = base64.b64encode(image_data).decode("utf-8")
    upload = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            'key': api_key,
            'image': encoded
        }
    )
    try:
        return upload.json()["data"]["url"]
    except:
        return None

class Command(BaseCommand):
    help = 'Import movies from TMDB API'

    def get_tmdb_genres(self):
        response = requests.get(
            f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
        )
        genre_data = response.json()["genres"]
        return {genre["id"]: genre["name"] for genre in genre_data}

    def handle(self, *args, **kwargs):
        imported_movies = []
        page = 1
        total_imported = 0
        genre_map = self.get_tmdb_genres()

        while total_imported < 500:
            url = f'{TMDB_API_URL}?api_key={TMDB_API_KEY}&language=en-US&page={page}'
            response = requests.get(url)
            data = response.json()

            for tmdb_movie in data['results']:
                title = tmdb_movie['title']
                description = tmdb_movie.get('overview', '')
                release_year = int(tmdb_movie.get('release_date', '2000-01-01')[:4])
                rating = tmdb_movie.get('vote_average', 0)
                poster_path = tmdb_movie.get('poster_path', '')
                poster_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else None
                is_top_rated = rating >= 7.0

                # Upload to ImgBB (optional)
                imgbb_url = upload_tmdb_image_to_imgbb(poster_url) if poster_url else None

                # Genres
                genre_ids = tmdb_movie.get("genre_ids", [])
                genre_objs = []
                for genre_id in genre_ids:
                    genre_name = genre_map.get(genre_id, "Unknown")
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    genre_objs.append(genre)

                # Actors
                credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_movie['id']}/credits?api_key={TMDB_API_KEY}"
                credits_res = requests.get(credits_url)
                actors = "Unknown"
                if credits_res.status_code == 200:
                    credits_data = credits_res.json()
                    cast = credits_data.get("cast", [])
                    top_actors = [actor["name"] for actor in cast[:3]]
                    actors = ", ".join(top_actors)

                # Trailer
                trailer_url = None
                videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_movie['id']}/videos?api_key={TMDB_API_KEY}"
                videos_res = requests.get(videos_url)
                if videos_res.status_code == 200:
                    videos = videos_res.json().get("results", [])
                    for video in videos:
                        if video["site"] == "YouTube" and video["type"] == "Trailer":
                            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                            break

                # Save movie
                movie = Movie.objects.create(
                    title=title,
                    description=description,
                    release_year=release_year,
                    rating=rating,
                    poster=imgbb_url,       # ImgBB hosted
                    poster_url=poster_url,  # TMDB direct
                    actors=actors,
                    language="English",
                    award_count=0,
                    is_featured=False,
                    is_top_rated=is_top_rated,
                    trailer_url=trailer_url,
                )
                movie.genres.set(genre_objs)
                movie.save()
                imported_movies.append(movie)
                self.stdout.write(self.style.SUCCESS(f'Imported: {title}'))
                total_imported += 1
                if total_imported >= 500:
                    break

            page += 1

        # Mark latest 20
        latest_20 = sorted(imported_movies, key=lambda m: m.release_year or 0, reverse=True)[:20]
        for m in latest_20:
            m.is_latest = True
            m.save()

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Imported {total_imported} movies from TMDB.'))
