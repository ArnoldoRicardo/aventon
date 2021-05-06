from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import circles as circles_views


router = DefaultRouter()
router.register(r'circles', circles_views.CircleViewSet, basename='circle')

urlpatterns = [
    path('', include(router.urls))
]
