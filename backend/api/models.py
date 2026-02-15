from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    genre = models.CharField(max_length=100)
    rating = models.FloatField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    copies_sold = models.IntegerField()

    def __str__(self):
        return self.title


