from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .serializers import UserProfileSerializer


# -----------------------------
# Create User (POST)
# Endpoint: /api/users/
# -----------------------------
@api_view(['POST'])
def create_user(request):
    serializer = UserProfileSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------
# Retrieve User by Username (GET)
# Endpoint: /api/users/<username>/
# ------------------------------------
@api_view(['GET'])
def get_user(request, username):
    try:
        user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        return Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)