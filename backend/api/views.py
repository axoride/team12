from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class CreateBookView(APIView):
    def post(self, request):
        serializer = BookSerializer(data=request.data) #creates an instance of BookSerializer into JSON
        if serializer.is_valid(): #if valid save
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) #else return error
    

class RetrieveBookView(APIView):
    def get(self, request, isbn):
        try:
            book = Book.objects.get(isbn=isbn)  #find the book
            serializer = BookSerializer(book)  #convert to JSON
            return Response(serializer.data)  #return it
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class ListBooksView(APIView):
    def get(self, request):
        books = Book.objects.all()  #get all books
        serializer = BookSerializer(books, many=True) 
        return Response(serializer.data)