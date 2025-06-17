from django.urls import path
from .views import MovieListAPIView, AskAIView, AskHuggingFaceAIView, MovieReviewsAPIView, MovieSummaryAPIView

urlpatterns = [
    path('movies/', MovieListAPIView.as_view(), name='movie-list'),
    path('ask-ai/', AskAIView.as_view()),
    path('ask-hugging-face-ai/', AskHuggingFaceAIView.as_view()),
    path('movie-summary/', MovieSummaryAPIView.as_view(), name='movie-summary'),
    path('movie-reviews/', MovieReviewsAPIView.as_view(), name='movie-reviews'),
]
