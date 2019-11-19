from django.shortcuts import render


def home(request):
    return render(request, 'fakenews/index.html')
