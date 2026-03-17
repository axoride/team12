from django.db import models

# ====================
# Profile Management  (Updated: 3-17-2026)
# ====================

class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username


# ====================
# Shopping Cart
# ====================

class CartItem(models.Model):
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"user {self.user_id} book {self.book_id}"


# ====================
# Book Details
# ====================

class BookDetail(models.Model):
    isbn = models.CharField(max_length=17, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    year_published = models.IntegerField()
    copies_sold = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# ====================
# Wishlist Management (Updated: 3-10-2026)
# ====================

class Wishlist(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_id", "name"], name="unique_wishlist_name_per_user")
        ]

    def __str__(self):
        return f"User {self.user_id} - {self.name}"


class WishlistBook(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(BookDetail, on_delete=models.CASCADE)  # now points to BookDetail

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["wishlist", "book"], name="unique_book_per_wishlist")
        ]

    def __str__(self):
        return f"{self.book.name} in {self.wishlist.name}"


# ====================
# Book Rating & Commenting  (Added: 3-15-2026)
# ====================
class BookRating(models.Model):
    book = models.ForeignKey(BookDetail, on_delete=models.CASCADE, related_name='ratings', to_field='isbn')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField()  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['book', 'user'], name='unique_rating_per_user_per_book')
        ]

    def __str__(self):
        return f"Rating {self.rating}/5 for {self.book.isbn} by {self.user.username}"


class BookComment(models.Model):
    book = models.ForeignKey(BookDetail, on_delete=models.CASCADE, related_name='comments', to_field='isbn')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.book.isbn} by {self.user.username}"
