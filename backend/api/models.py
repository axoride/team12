from django.db import models
from django.template.defaultfilters import yesno


class Book(models.Model):
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