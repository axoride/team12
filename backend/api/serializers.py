from rest_framework import serializers
from .models import UserProfile, CartItem, BookDetail, Wishlist, WishlistBook

# -------------------
# Profile Management
# -------------------
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

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

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
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
