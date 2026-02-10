from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.username
