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
    WishlistBook, 
    CreditCard
)
from .serializers import (
    UserProfileSerializer,
    CartItemSerializer,
    BookDetailSerializer,
    WishlistCreateSerializer,
    AddBookToWishlistSerializer,
    WishlistBookSerializer,
    BookBrowseSerializer,
    UpdateUserSerializer,
    CreditCardSerializer
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


@api_view(['PATCH'])
def update_user(request, username):
    try:
        user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check if email is in the request body and reject it
    if 'email' in request.data:
        return Response({"error": "Email cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UpdateUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_credit_card(request):
    """
    Create a credit card linked to an existing user.
    Requires: username, card_number, expiration_date, cvv
    """
    serializer = CreditCardSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Credit card added successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
@api_view(['GET'])
def books_by_genre(request):
    genre = request.GET.get('genre')
    if not genre:
        return Response({"error": "Genre parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Case-insensitive search for genre
    books = BookDetail.objects.filter(genre__iexact=genre)
    serializer = BookBrowseSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def top_sellers(request):
    # Top 10 by copies_sold
    books = BookDetail.objects.order_by('-copies_sold')[:10]
    serializer = BookBrowseSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

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


# Story 8 — GET all comments for a book
@api_view(['GET'])
def get_book_comments(request, isbn):
    try:
        book = BookDetail.objects.get(isbn=isbn)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    comments = BookComment.objects.filter(book=book).values(
        'id',
        'user__username',
        'comment',
        'created_at'
    )

    return Response({
        "book_isbn": isbn,
        "book_name": book.name,
        "comments": list(comments)
    }, status=status.HTTP_200_OK)


# Story 9 — GET average rating for a book
@api_view(['GET'])
def get_average_rating(request, isbn):
    try:
        book = BookDetail.objects.get(isbn=isbn)
    except BookDetail.DoesNotExist:
        return Response({"error": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    result = BookRating.objects.filter(book=book).aggregate(avg=Avg('rating'))
    avg = result['avg']

    return Response({
        "book_isbn": isbn,
        "book_name": book.name,
        "average_rating": round(float(avg), 2) if avg is not None else None,
        "message": "No ratings yet." if avg is None else "Average rating calculated successfully."
    }, status=status.HTTP_200_OK)
