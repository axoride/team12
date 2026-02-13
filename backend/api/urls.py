#give access to our endpoint to people
from django.urls import path
from .views import CreateBookView, RetrieveBookView, ListBooksView

urlpatterns = [
    path('books/', CreateBookView.as_view(), name='create-book'),
    path('books/all/', ListBooksView.as_view(), name='list_books'),
    path('books/<str:isbn>/', RetrieveBookView.as_view(), name='retrieve-book'),
    
]