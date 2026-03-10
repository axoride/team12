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

# -------------------
# Book Browsing & Sorting
# -------------------

class BookBrowseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetail
        fields = '__all__'