#translates into json
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book #model getting serialized
        fields = ['isbn', 'name' , 'description', 'price', 'author', 'genre', 'publisher', 'year_published', 'copies_sold'] #which fields can also do all() for every one but listing gives more control