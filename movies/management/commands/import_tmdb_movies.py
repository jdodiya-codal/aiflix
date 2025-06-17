import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from movies.models import Movie, Genre

TMDB_API_KEY = '22c8aea5e941ff42bc5aa70532467e07'
TMDB_API_URL = 'https://api.themoviedb.org/3/movie/popular'

POSTER_BASE_URL = 'https://image.tmdb.org/t/p/w500'


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
                imported_movies = []
                title = tmdb_movie['title']
                description = tmdb_movie.get('overview', '')
                release_year = int(tmdb_movie.get('release_date', '2000-01-01')[:4])
                rating = tmdb_movie.get('vote_average', 0)
                poster_path = tmdb_movie.get('poster_path', '')
                is_top_rated = rating >= 7.0

                # Download poster image
                poster_file = None
                if poster_path:
                    image_url = POSTER_BASE_URL + poster_path
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        poster_file = ContentFile(img_response.content, name=poster_path.strip('/'))

                # Placeholder genres (since TMDB IDs are numeric)
                genre_objs = []
                # genre_names = ["Top Rated"]  # You can map actual genre IDs to names if needed

                genre_ids = tmdb_movie.get("genre_ids", [])
                genre_names = [genre_map.get(genre_id, "Unknown") for genre_id in genre_ids]

                for genre_name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    genre_objs.append(genre)

                # Get actor names (limit to first 3)
                credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_movie['id']}/credits?api_key={TMDB_API_KEY}"
                credits_res = requests.get(credits_url)
                actors = "Unknown"

                if credits_res.status_code == 200:
                    credits_data = credits_res.json()
                    cast = credits_data.get("cast", [])
                    top_actors = [actor["name"] for actor in cast[:3]]
                    actors = ", ".join(top_actors)

                trailer_url = None
                videos_url = f"https://api.themoviedb.org/3/movie/{tmdb_movie['id']}/videos?api_key={TMDB_API_KEY}"
                videos_res = requests.get(videos_url)

                if videos_res.status_code == 200:
                    videos = videos_res.json().get("results", [])
                    for video in videos:
                        if video["site"] == "YouTube" and video["type"] == "Trailer":
                            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                            break

                # Create the movie
                movie = Movie.objects.create(
                    title=title,
                    description=description,
                    release_year=release_year,
                    rating=rating,
                    poster=poster_file,
                    actors=actors,
                    language="English",
                    award_count=0,
                    is_featured=False,
                    is_top_rated=is_top_rated,
                    trailer_url=trailer_url,
                )
                imported_movies.append(movie)
                movie.genres.set(genre_objs)
                movie.save()

                self.stdout.write(self.style.SUCCESS(f'Imported: {title}'))
                total_imported += 1

                if total_imported >= 100:
                    break

            page += 1

        latest_20 = sorted(imported_movies, key=lambda m: m.release_year or 0, reverse=True)[:20]
        for m in latest_20:
            m.is_latest = True
            m.save()

        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Imported {total_imported} movies from TMDB.'))
