from django.shortcuts import render
from django.http import HttpResponse
import os
import io
from google.cloud import vision
from django.core.files.storage import FileSystemStorage
from django.conf import settings

template = 'clickbait/index.html'


def text_detection(path):
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    for text in texts:
        txt = text.description
        return txt


def home(request):
    context = {
    }
    if 'text-input' in request.POST:
        try:
            print(request.POST)
            text = request.POST.get('text-input', '')
            context = {
                'msg': 'output',
                'input': text
            }
            context['score'] = '58%'
            context['output'] = "Clickbait"
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
    elif 'file' in request.FILES.keys():
        try:
            uploaded_file = request.FILES['file']
            file_obj = FileSystemStorage()
            path = file_obj.save(settings.STATICFILES_DIRS[0] + '/clickbait/upload/' + uploaded_file.name, uploaded_file)
            fetched = text_detection(path)
            print(fetched)
            context = {
                'msg': 'output',
                'image': True,
                'fetched_output': fetched
            }
            context['score'] = '58%'
            context['output'] = "Clickbait"
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
    return render(request, template, context)
