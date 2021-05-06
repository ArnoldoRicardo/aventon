"""Cirucles views."""

from rest_framework import viewsets
from aventon.circles.models import Circle
from aventon.circles.serializers import CircleModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set."""
    
    queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer
