from django.urls import path
from .views import MovieListAPIView, AskHuggingFaceAIView, MovieReviewsAPIView, MovieSummaryAPIView, AskOpenRouterDynamicModelView, RunMovieImportView

urlpatterns = [
    path('movies/', MovieListAPIView.as_view(), name='movie-list'),
    path('ask-hugging-face-ai/', AskHuggingFaceAIView.as_view()),
    path('movie-summary/', MovieSummaryAPIView.as_view(), name='movie-summary'),
    path('movie-reviews/', MovieReviewsAPIView.as_view(), name='movie-reviews'),
    path('api/import-movies/', RunMovieImportView.as_view(), name='run-movie-import'),
    path("ask-ai/", AskOpenRouterDynamicModelView.as_view(), name="ask-ai"),
]
