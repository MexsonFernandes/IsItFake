import numpy as np
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from newspaper import Article
import pickle
from django.conf import settings
import traceback


def home(request):
    return render(request, 'fakenews/index.html')


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


@csrf_exempt
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
                out = predict(text)
                context['out'] = 'fake' if out == 1 else 'real'
                context['input'] = text
            else:
                url = request.POST.get('url')
                _, head, content = headline_text(url)
                print(content)
                out = predict(content)
                context['out'] = 'fake' if out == 1 else 'real'
                context['input'] = content

        except Exception as e:
            print(str(e))
            context['msg'] = 'error'
            print(traceback.print_exc())
            if 'text-input' in request.POST:
                context['error'] = 'Error in parsing data'
            else:
                context['error'] = 'Link is incorrect'
    return render(request, 'fakenews/index.html', context)

