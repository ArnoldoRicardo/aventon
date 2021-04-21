from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models.circles import Circle
from .serializers import CircleSerializer, CreateCircleSerializer


@api_view(['GET', 'POST'])
def list_circles(request):
    """List circles."""

    if request.method == 'GET':
        circles = Circle.objects.filter(is_public=True)
        serializer = CircleSerializer(circles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        """Create circle"""
        serializer = CreateCircleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        circle = serializer.save()

        return Response(CircleSerializer(circle).data)