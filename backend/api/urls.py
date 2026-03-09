#give access to our endpoint to people
from django.urls import path
from .views import CreateBookView, RetrieveBookByISBNView

urlpatterns = [
    path('books/', CreateBookView.as_view(), name='create-book'),
    path('books/<str:isbn>/', RetrieveBookByISBNView.as_view(), name='retrieve-book'),
    
]