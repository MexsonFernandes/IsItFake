from django.db import models
from django.utils import timezone


class UserInputModel(models.Model):
    added_on = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="quotexaminer/upload")
    quote = models.CharField(max_length=500)
    author = models.CharField(max_length=100)
    output = models.CharField(max_length=50)
