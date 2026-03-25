from decimal import Decimal
from django.db.models import Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import (
    UserProfile,
    CartItem,
    BookDetail,
    Author,
    Wishlist,
    WishlistBook, 
    CreditCard,
    BookRating,
    BookComment
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
    CreditCardSerializer,
    AuthorSerializer,
    BookCommentSerializer,
    BookReviewSummarySerializer
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

    # Check if new username already exists
    new_username = request.data.get('username')
    if new_username and new_username != username:
        if UserProfile.objects.filter(username=new_username).exists():
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

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
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    items = CartItem.objects.filter(user_id=user_id)
    serializer = CartItemSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_from_cart(request):
    user_id = request.data.get('user_id')
    book_id = request.data.get('book_id')

    if not user_id or not book_id:
        return Response({'error': 'user_id and book_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    deleted, _ = CartItem.objects.filter(user_id=user_id, book_id=book_id).delete()
    if deleted == 0:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_204_NO_CONTENT)


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

@api_view(['POST'])
def create_author(request):
    serializer = AuthorSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def retrieve_author_by_id(request, author_id):
    try:
        author = Author.objects.get(id=author_id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)
    except Author.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# -----------------------------
# Wishlist Management (Last Updated: 3-23-2026)
# -----------------------------

# Functionality for creating a wishlist given User ID and Name
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

# Functionality for adding a book to a wishlist given a Book ID and Wishlist ID
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

# Functionality for removing book from wishlist and adding it to cart given a Wishlist ID and Book ID
@api_view(['DELETE'])
def move_book_from_wishlist_to_cart(request):
    book_id = request.data.get('book_id')
    wishlist_id = request.data.get('wishlist_id')

    if not book_id or not wishlist_id:
        return Response(
            {"error": "book_id and wishlist_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return Response(
            {"error": "Wishlist not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        book = BookDetail.objects.get(id=book_id)
    except BookDetail.DoesNotExist:
        return Response(
            {"error": "Book not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        wishlist_book = WishlistBook.objects.get(wishlist=wishlist, book=book)
    except WishlistBook.DoesNotExist:
        return Response(
            {"error": "This book is not in the specified wishlist."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Remove from wishlist
    wishlist_book.delete()

    # Add to cart using the wishlist owner's user id
    existing_cart_item = CartItem.objects.filter(
        user_id=wishlist.user.id,
        book_id=book.id
    ).first()

    if existing_cart_item:
        existing_cart_item.quantity += 1
        existing_cart_item.save()
    else:
        CartItem.objects.create(
            user_id=wishlist.user.id,
            book_id=book.id,
            price=book.price,
            quantity=1
        )

    return Response(
        {"message": "Book removed from wishlist and added to cart successfully."},
        status=status.HTTP_200_OK
    )

# Functionality for listing all books in a wishlist given a Wishlist ID
@api_view(['GET'])
def list_books_in_wishlist(request, wishlist_id):
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
    except Wishlist.DoesNotExist:
        return Response(
            {"error": "Wishlist not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    wishlist_books = WishlistBook.objects.filter(wishlist=wishlist)

    books = []
    for wishlist_book in wishlist_books:
        book = wishlist_book.book
        books.append({
    	    "book_id": book.id,
    	    "isbn": book.isbn,
    	    "name": book.name,
    	    "author": book.author,
    	    "price": str(book.price),
    	    "genre": book.genre,
    	    "publisher": book.publisher,
    	    "year_published": book.year_published
	})

    return Response(books, status=status.HTTP_200_OK)

# -----------------------------
# Book Browsing & Sorting
# -----------------------------

# Retrieve List of Books by Genre
@api_view(['GET'])
def books_by_genre(request):
    genre = request.GET.get('genre')
    if not genre:
        return Response({"error": "Genre parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Case-insensitive search for genre
    books = BookDetail.objects.filter(genre__iexact=genre)
    serializer = BookBrowseSerializer(books, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Top 10 by copies_sold
@api_view(['GET'])
def top_sellers(request):
    books = BookDetail.objects.order_by('-copies_sold')[:10]
    serializer = BookBrowseSerializer(books, many=True)
    return Response(serializer.data)


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

    books = BookDetail.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).filter(avg_rating__gte=rating)

    serializer = BookBrowseSerializer(books, many=True)
    return Response(serializer.data)


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
        discount_percent = Decimal(discount_percent)
    except:
        return Response(
            {"error": "Discount must be a number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    books = BookDetail.objects.filter(publisher=publisher)

    if not books.exists():
        return Response(
            {"error": "No books found for that publisher."},
            status=status.HTTP_404_NOT_FOUND
        )

    discount = discount_percent / Decimal(100)

    for book in books:
        book.price = book.price * (Decimal(1) - discount)
        book.save()

    return Response(
        {"message": "Discount applied successfully."},
        status=status.HTTP_200_OK
    )

# -----------------------------
# Book Rating & Commenting
# -----------------------------

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

