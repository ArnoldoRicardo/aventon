from django.urls import path, include

from .views import list_circles

urlpatterns = [
    path('circles/', list_circles)
]