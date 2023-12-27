from django.urls import path
from .views import download_instagram

urlpatterns = [
    path('', download_instagram),
]