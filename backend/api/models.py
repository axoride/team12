from django.db import models

class CartItem(models.Model):
    user_id = models.IntegerField()
    book_id = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"user {self.user_id} book {self.book_id}"
