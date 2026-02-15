from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your Profile POST endpoint
    path('api/profile/', views.create_profile),
]
