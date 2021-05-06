"""Circles serializers."""

from rest_framework import serializers
from aventon.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """Circle model serializer."""

    class Meta:
        """Meta class."""

        model = Circle
        fields = '_all'
