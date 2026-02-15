from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

@api_view(['GET'])
def books_by_genre(request):
    genre = request.GET.get('genre')

    if not genre:
        return Response(
            {"error": "Genre parameter is required."},
            status=400
        )

    books = Book.objects.filter(genre__iexact=genre)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)
