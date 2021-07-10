from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse


def home(request):
    context = {
        'deepfakes': 'http://faceswap.isitfake.co.in',
        'fakenews': 'http://fakenews.isitfake.co.in',
        'clickbait': 'http://clickbait.isitfake.co.in',
        'quotexaminer': 'http://quotexaminer.isitfake.co.in'
    }
    return render(request, 'www/index.html', context)
