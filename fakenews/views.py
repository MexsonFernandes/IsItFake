import numpy as np
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from newspaper import Article
import pickle
from django.conf import settings
import traceback
from fakenews.models import UserInputModel
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer, BrowsableAPIRenderer
from rest_framework import generics
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
from fakenews.serializers import FakeNewsSerializer
from rest_framework_api_key.models import APIKey
# from rest_framework_api.key.permissions import HasAPIKey
from wsgiref.util import FileWrapper
import mimetypes
import os
from django.utils.encoding import smart_str


def headline_text(url='', summary=False):
    '''
    Returns headline text of news..
    Just makes call to the newspaper class.
    '''
    article = Article(url)
    # Download the article and parse it.
    article.download()
    article.parse()
    # authors = article.authors
    headline = article.title
    text = article.text
    if summary:
        article.nlp()
        summary = article.summary
        return url, headline, text, summary
    return url, headline, text


model = pickle.load(open(settings.MEDIA_URL + 'fakenews/model.sav', 'rb'))
vec = pickle.load(open(settings.MEDIA_URL + 'fakenews/vec_fnd.pkl', 'rb'))


def predict(text):
    pred = vec.transform(np.array([text]))
    out = model.predict(pred)
    return out[0]


# @csrf_exempt
def home(request):
    context = {
        'msg': ''
    }
    if request.POST:
        try:
            print(request.POST)
            out = 0
            context = {
                'msg': 'output',
                'input': '',
                'out': out
            }
            if len(request.POST.get('text-input', '')) > 0:
                text = request.POST.get('text-input', '')
                if len(text) < 30:
                    context['msg'] = 'error'
                    context['error'] = 'Text length should be more than 30 characters'
                    return render(request, 'fakenews/index.html', context)
                out = predict(text)
                context['out'] = 'fake' if out == 1 else 'real'
                context['input'] = text
                obj = UserInputModel(
                    news=text,
                    output=context['out'],
                    url=''
                )
                obj.save()
            else:
                url = request.POST.get('url')
                _, head, content = headline_text(url)
                print(content)
                out = predict(content)
                context['out'] = 'fake' if out == 1 else 'real'
                context['input'] = content
                obj = UserInputModel(
                    news=content,
                    output=context['out'],
                    url=url
                )
                obj.save()
        except Exception as e:
            print(str(e))
            context['msg'] = 'error'
            print(traceback.print_exc())
            if 'text-input' in request.POST:
                context['error'] = 'Error in parsing data'
                if len(request.POST.get('text-input', '')) < 30:
                    context['error'] = 'Text length should be more than 30 characters'
            else:
                context['error'] = 'Link is incorrect'
    return render(request, 'fakenews/index.html', context)


class FakeNewsViews(generics.CreateAPIView):
    """
    A view that returns a templated API representation of fakenews service
    """
    serializer_class = FakeNewsSerializer

    def get(self, request, format=None):
        context = {'status': True, 'message': 'GET request'}
        if format == None:
            return Response(context, template_name='fakenews/index.html')
        else:
            return Response(context)

    def post(self, request, *args, **kwargs):
        context = {'status': True,}
        context['data'] = request.data
        # HasAPIKey.
        print('df')
        return (Response(context) if format == None else Response(context, template_name='fakenews/index.html'))




def download(request, name):
    file_name = name
    file_path = settings.MEDIA_URL + 'fakenews/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    print(response)
    return response
