from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie
from .serializers import MovieSerializer
from django.conf import settings
import requests
import re
from movies.utils.imgbb import upload_tmdb_image_to_imgbb
from django.core.management import call_command
import os

TMDB_API_KEY = settings.TMDB_API_KEY


HF_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {
    "Authorization": f"Bearer {settings.HF_API_TOKEN}",
    "Accept": "application/json"
}


def fetch_tmdb_movies_data(titles):
    results = []
    for title in titles:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        res = requests.get(url)
        if res.status_code == 200:
            items = res.json().get("results")
            if items:
                movie = items[0]
                # Build TMDB poster URL
                tmdb_poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None

                # Upload to ImgBB
                imgbb_url = None
                if tmdb_poster_url:
                    try:
                        imgbb_url = upload_tmdb_image_to_imgbb(tmdb_poster_url)
                    except Exception as e:
                        print(f"Failed to upload to ImgBB: {e}")
                        imgbb_url = tmdb_poster_url  # fallback to TMDB poster

                results.append({
                    "title": movie["title"],
                    "overview": movie["overview"],
                    "release_date": movie["release_date"],
                    "poster": imgbb_url,
                    "rating": movie["vote_average"]
                })
    return results

def extract_titles(text):
    raw_titles = re.findall(r'"([^"]+)"', text)
    unique = list(dict.fromkeys(raw_titles))
    return [t for t in unique if len(t.strip()) > 2]



def generate_from_hf(prompt):
    payload = {
        "inputs": f"<|user|>\n{prompt}\n<|assistant|>",
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=60)
        data = response.json()
        text = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
        return text.split("<|assistant|>")[-1].strip()
    except Exception as e:
        return f"Error: {str(e)}"

class MovieListAPIView(APIView):
    def get(self, request):
        queryset = Movie.objects.all()

        # Filter by year
        year = request.GET.get('year')
        if year:
            queryset = queryset.filter(release_year=year)

        # Filter by is_latest
        if request.GET.get('is_latest') == 'true':
            queryset = queryset.filter(is_latest=True)

        # Filter by is_top_rated
        if request.GET.get('is_top_rated') == 'true':
            queryset = queryset.filter(is_top_rated=True)

        # Filter by genre
        genre = request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genres__name__icontains=genre)

        # Filter by actor name
        actor = request.GET.get('actor')
        if actor:
            queryset = queryset.filter(actors__icontains=actor)

        # Search by title
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        serializer = MovieSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AskHuggingFaceAIView(APIView):
    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Question is required"}, status=400)

        HF_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        headers = {
            "Authorization": f"Bearer {settings.HF_API_TOKEN}",
            "Accept": "application/json"
        }
        # payload = {
        #     "inputs": f"<|user|>\n{question}\n<|assistant|>",
        #     "parameters": {
        #         "max_new_tokens": 150,
        #         "temperature": 0.7
        #     }
        # }

        payload = {
            "inputs": f"<|system|>You are a helpful movie assistant. Always wrap movie titles in double quotes.\n<|user|>\n{question}\n<|assistant|>",
            "parameters": {
                "max_new_tokens": 150,
                "temperature": 0.7
            }
        }

        try:
            response = requests.post(HF_URL, headers=headers, json=payload, timeout=60)

            # Handle non-200 responses
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text
                return Response({
                    "error": f"Hugging Face API error {response.status_code}",
                    "details": error_detail
                }, status=500)

            # Try to decode the response
            try:
                data = response.json()
            except Exception:
                return Response({"error": "Invalid JSON response from Hugging Face"}, status=500)

            if isinstance(data, list) and "generated_text" in data[0]:
                generated = data[0]["generated_text"]

                # Remove special tokens
                cleaned = generated.replace("<|user|>", "").replace("<|assistant|>", "").strip()

                # Remove the echoed question (first line)
                lines = cleaned.split("\n")
                if lines and lines[0].strip().lower() == question.strip().lower():
                    lines = lines[1:]  # skip the echoed question
                final_answer = "\n".join(lines).strip()
                movie_titles = extract_titles(final_answer)
                movie_data = fetch_tmdb_movies_data(movie_titles)

                return Response({"answer": final_answer,
                                 "movie_data": movie_data})

            else:
                return Response({"error": "Unexpected response format", "details": data}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"error": "Request failed", "details": str(e)}, status=500)


class MovieSummaryAPIView(APIView):
    def post(self, request):
        title = request.data.get("title")
        if not title:
            return Response({"error": "Movie title is required"}, status=400)

        prompt = f"Summarize the movie '{title}' in 20-22 sentences for a movie fan."
        result = generate_from_hf(prompt)

        return Response({"summary": result})



class MovieReviewsAPIView(APIView):
    def post(self, request):
        title = request.data.get("title")
        if not title:
            return Response({"error": "Movie title is required"}, status=400)

        prompt = f"Write 5 short, realistic user reviews for the movie '{title}'."
        result = generate_from_hf(prompt)

        return Response({"reviews": result})




class RunMovieImportView(APIView):
    def post(self, request):
        secret = request.data.get("secret")

        if secret != os.getenv("ADMIN_TRIGGER_SECRET"):
            return Response({"error": "Unauthorized"}, status=401)

        try:
            call_command("import_tmdb_movies")  # your custom command
            return Response({"message": "Movies imported successfully."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)