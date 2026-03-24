from rest_framework import serializers
from .models import UserProfile, CartItem, BookDetail, Wishlist, WishlistBook, CreditCard, Author

# -------------------
# Profile Management
# -------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class UpdateUserSerializer(serializers.ModelSerializer):
    """
    Used for PATCH update — excludes email so it cannot be changed.
    All fields are optional since it's a partial update.
    """
    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'name', 'address', 'city', 'state', 'zip']
        # email is intentionally excluded here

class CreditCardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)  # used to look up user, not stored directly

    class Meta:
        model = CreditCard
        fields = ['id', 'username', 'card_number', 'expiration_date', 'cvv']

    def validate_card_number(self, value):
        # Make sure card number is exactly 16 digits
        if not value.isdigit() or len(value) != 16:
            raise serializers.ValidationError("Card number must be exactly 16 digits.")
        return value

    def validate_cvv(self, value):
        # CVV should be 3 or 4 digits
        if not value.isdigit() or len(value) not in [3, 4]:
            raise serializers.ValidationError("CVV must be 3 or 4 digits.")
        return value

    def validate_expiration_date(self, value):
        # Basic format check MM/YY
        if len(value) != 5 or value[2] != '/':
            raise serializers.ValidationError("Expiration date must be in MM/YY format.")
        return value

    def create(self, validated_data):
        # Pop username, look up the user, then create the card
        username = validated_data.pop('username')
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError({"username": "User not found."})
        return CreditCard.objects.create(user=user, **validated_data)


# -------------------
# Wishlist Management
# -------------------

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'name', 'created_at']


class WishlistBookSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=BookDetail.objects.all())

    class Meta:
        model = WishlistBook
        fields = ['id', 'wishlist', 'book']


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['user', 'name']


class AddBookToWishlistSerializer(serializers.Serializer):
    wishlist_id = serializers.IntegerField()
    book_id = serializers.IntegerField()

# -------------------
# Shopping Cart
# -------------------

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

# -------------------
# Book Details
# -------------------

class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetail  # model getting serialized
        fields = ['isbn', 'name', 'description', 'price', 'author', 'genre', 'publisher', 'year_published', 'copies_sold']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'
# -------------------
# Book Browsing & Sorting
# -------------------

class BookBrowseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetail
        fields = '__all__'

# -------------------
# Book Rating & Commenting
# -------------------
from .models import BookRating, BookComment


class BookRatingSerializer(serializers.ModelSerializer):
    book_isbn = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = BookRating
        fields = ['id', 'book_isbn', 'user_id', 'username', 'book_name', 'rating', 'created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        book = BookDetail.objects.get(isbn=validated_data.pop('book_isbn'))
        user = UserProfile.objects.get(id=validated_data.pop('user_id'))
        return BookRating.objects.create(book=book, user=user, **validated_data)


class BookCommentSerializer(serializers.ModelSerializer):
    book_isbn = serializers.CharField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    book_name = serializers.CharField(source='book.name', read_only=True)

    class Meta:
        model = BookComment
        fields = ['id', 'book_isbn', 'user_id', 'username', 'book_name', 'comment', 'created_at']

    def create(self, validated_data):
        book = BookDetail.objects.get(isbn=validated_data.pop('book_isbn'))
        user = UserProfile.objects.get(id=validated_data.pop('user_id'))
        return BookComment.objects.create(book=book, user=user, **validated_data)


class BookReviewSummarySerializer(serializers.Serializer):
    book_isbn = serializers.CharField()
    average_rating = serializers.FloatField(allow_null=True)
    ratings = BookRatingSerializer(many=True)
    comments = BookCommentSerializer(many=True)
