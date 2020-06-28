from django.db import models
from django.utils import timezone


class UserInputModel(models.Model):
    added_on = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to="clickbait/upload")
    cluster = models.CharField(max_length=50)
    output = models.CharField(max_length=50)
    text = models.CharField(max_length=1000)
    pred = models.IntegerField(default=-1)
    score = models.FloatField(default=-1.0)
