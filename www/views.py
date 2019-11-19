from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse


def home(request):
    context = {
        'deepfakes': 'http://deepfakes.isitfake.co.in',
        'fakenews': 'http://fakenews.isitfake.co.in',
        'clickbait': 'http://clickbait.isitfake.co.in',
        'quotexaminer': 'http://quotexaminer.isitfake.co.in'
    }
    if settings.DEBUG:
        context = {
            'deepfakes': 'http://deepfakes.localhost:8000',
            'fakenews': 'http://fakenews.localhost:8000',
            'clickbait': 'http://clickbait.localhost:8000',
            'quotexaminer': 'http://quotexaminer.localhost:8000'
        }
    return render(request, 'www/index.html', context)
