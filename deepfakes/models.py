from django.db import models
from django.utils import timezone

class UserInputModel(models.Model):
    added_on = models.DateTimeField(default=timezone.now)
    video = models.CharField(max_length=200)
    url = models.URLField()
    output = models.CharField(max_length=100)
    score = models.FloatField()