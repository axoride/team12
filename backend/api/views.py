from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book
from .serializers import BookSerializer

# Retrieve List of Books by Genre
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

# Retrieve List of Top Sellers (Top 10 books that have sold the most copied)
@api_view(['GET'])
def top_sellers(request):
    books = Book.objects.order_by('-copies_sold')[:10]
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

# Retrieve List of Books for a particular rating and higher
@api_view(['GET'])
def books_by_rating(request):

    rating = request.GET.get('rating')

    if rating is None:
        return Response(
            {"error": "Rating parameter is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rating = float(rating)
    except ValueError:
        return Response(
            {"error": "Rating must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if rating < 0 or rating > 5:
        return Response(
            {"error": "Rating must be between 0 and 5."},
            status=status.HTTP_400_BAD_REQUEST
        )

    books = Book.objects.filter(rating__gte=rating)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

# Discount books by publisher
@api_view(['PATCH'])
def discount_books_by_publisher(request):

    publisher = request.data.get('publisher')
    discount_percent = request.data.get('discount_percent')

    if not publisher or discount_percent is None:
        return Response(
            {"error": "Publisher and discount_percent are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        discount_percent = float(discount_percent)
    except ValueError:
        return Response(
            {"error": "Discount percent must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    books = Book.objects.filter(publisher=publisher)

    if not books.exists():
        return Response(
            {"error": "No books found for that publisher."},
            status=status.HTTP_404_NOT_FOUND
        )

    for book in books:
        book.price = book.price * (1 - discount_percent / 100)
        book.save()

    return Response(
        {"message": "Discount applied successfully."},
        status=status.HTTP_200_OK
    )

