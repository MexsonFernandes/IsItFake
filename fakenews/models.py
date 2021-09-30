from django.db import models
from django.utils import timezone


class UserInputModel(models.Model):
    added_on = models.DateTimeField(default=timezone.now)
    news = models.CharField(max_length=5000)
    url = models.URLField()
    output = models.CharField(max_length=50)
