from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

template = 'clickbait/index.html'

def home(request):
    context = {
    }
    if 'text-input' in request.POST:
        print(request.POST)
        text = request.POST.get('text-input', '')
        context = {
            'msg': 'output',
            'input': text
        }
        context['score'] = '58%'
        context['output'] = "Clickbait"
        return render(request, template, context)
    elif 'file' in request.POST:
        print('files')
        context = {
            'msg': 'output'
        }
        return render(request, template, context)
    return render(request, template, context)
