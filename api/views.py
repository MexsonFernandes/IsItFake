from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fakenews.views import headline_text, predict
from clickbait.views import check_clickbaitness


@csrf_exempt
def check_url(request):
    if request.method == 'POST':
        print(request.POST)
        url = request.POST.get('url', 'sample')
        print(url)
        url, headline, text = headline_text(url)
        pred, score = check_clickbaitness(text)
        return JsonResponse({
            "result": True,
            "clickbait": {
                "score": '%.5f' % score[0] if pred == 0 else '%.5f' % score[1],
                "predict": 'Text is ' + ('clickbait' if pred == 0 else 'not a clickbait')
            },
            "article": {
                "predict": 'fake' if predict(text) == 1 else 'real'
            }
        })
    else:
        return JsonResponse({
            "result": False,
            "response": "GET not supported"
        })
