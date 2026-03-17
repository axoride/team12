from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import (
    UserProfile,
    CartItem,
    BookDetail,
    Wishlist,
    WishlistBook
)
from .serializers import (
    UserProfileSerializer,
    CartItemSerializer,
    BookDetailSerializer,
    WishlistCreateSerializer,
    AddBookToWishlistSerializer,
    WishlistBookSerializer,
    BookBrowseSerializer
)

# -----------------------------
# Profile Management
# -----------------------------
@api_view(['POST'])
def create_user(request):
    serializer = UserProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user(request, username):
    try:
        user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserProfileSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# -----------------------------
# Shopping Cart
# -----------------------------
@api_view(['GET'])
def get_cart_items(request):
    items = CartItem.objects.all()
    serializer = CartItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_cart(request):
    user_id = request.data.get('user_id')
    book_id = request.data.get('book_id')
    price = request.data.get('price')
    quantity = request.data.get('quantity', 1)

    if not user_id or not book_id or not price:
        return Response({'error': 'user_id, book_id, and price are required'}, status=status.HTTP_400_BAD_REQUEST)

    item = CartItem.objects.create(user_id=user_id, book_id=book_id, price=price, quantity=quantity)
    serializer = CartItemSerializer(item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_cart_subtotal(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    items = CartItem.objects.filter(user_id=user_id)
    subtotal = sum(item.price * item.quantity for item in items)

    return Response({'user_id': int(user_id), 'subtotal': subtotal})


# -----------------------------
# Book Details
# -----------------------------
@api_view(['POST'])
def create_book(request):
    serializer = BookDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def retrieve_book_by_isbn(request, isbn):
    try:
        book = BookDetail.objects.get(isbn=isbn)
        serializer = BookDetailSerializer(book)
        return Response(serializer.data)
    except BookDetail.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


# -----------------------------
# Wishlist Management
# -----------------------------
@api_view(['POST'])
def create_wishlist(request):
    serializer = WishlistCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.validated_data["user"]
    name = serializer.validated_data["name"]

    if Wishlist.objects.filter(user=user).count() >= 3:
        return Response({"error": "You can only have 3 wishlists."}, status=status.HTTP_400_BAD_REQUEST)

    if Wishlist.objects.filter(user=user, name=name).exists():
        return Response({"error": "Wishlist name already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)

    Wishlist.objects.create(user=user, name=name)
    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def add_book_to_wishlist(request):
    serializer = AddBookToWishlistSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    book_id = serializer.validated_data["book_id"]
    wishlist_id = serializer.validated_data["wishlist_id"]

    try:
        book = BookDetail.objects.get(id=book_id)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return Response({"error": "Wishlist not found."}, status=status.HTTP_404_NOT_FOUND)

    if WishlistBook.objects.filter(book=book, wishlist=wishlist).exists():
        return Response({"error": "This book is already in the wishlist."}, status=status.HTTP_409_CONFLICT)

    WishlistBook.objects.create(book=book, wishlist=wishlist)
    return Response({"message": "Book added to wishlist successfully."}, status=status.HTTP_200_OK)


# -----------------------------
# Book Browsing & Sorting
# -----------------------------
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

# -----------------------------
# Book Rating & Commenting
# -----------------------------
from django.db.models import Avg
from .models import BookRating, BookComment
from .serializers import BookRatingSerializer, BookCommentSerializer, BookReviewSummarySerializer


@api_view(['GET'])
def get_book_reviews(request, isbn):
    try:
        book = BookDetail.objects.get(isbn=isbn)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    ratings = BookRating.objects.filter(book=book)
    comments = BookComment.objects.filter(book=book)
    avg = ratings.aggregate(avg=Avg('rating'))['avg']

    data = {
        'book_isbn': isbn,
        'average_rating': round(avg, 2) if avg is not None else None,
        'ratings': ratings,
        'comments': comments,
    }
    serializer = BookReviewSummarySerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def submit_rating(request, isbn):
    try:
        BookDetail.objects.get(isbn=isbn)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['book_isbn'] = isbn
    serializer = BookRatingSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def submit_comment(request, isbn):
    try:
        BookDetail.objects.get(isbn=isbn)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['book_isbn'] = isbn
    serializer = BookCommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

