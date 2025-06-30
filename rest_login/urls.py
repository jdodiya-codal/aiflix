# rest_login/urls.py

from django.urls import path
from .views import register, EmailTokenObtainPairView, dashboard

urlpatterns = [
    path('register/', register, name='register'),
    path('token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('dashboard/', dashboard, name='dashboard'),
]
