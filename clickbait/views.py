import io
import pickle
import numpy as np
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from google.cloud import vision
from keras.models import load_model
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer
from django.http import JsonResponse, HttpResponse
import traceback
import pandas as pd
from django.utils.encoding import smart_str
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
ps = PorterStemmer()
from django.views.decorators.csrf import csrf_exempt
from numpy.core._multiarray_umath import ndarray
from django.http import JsonResponse
from clickbait.models import UserInputModel
from wsgiref.util import FileWrapper
import mimetypes
import os


template = 'clickbait/index.html'
model_cnn = load_model(settings.MEDIA_URL + 'clickbait/host.h5')
MAX_VOCAB_SIZE = 20000
MAX_SEQUENCE_LENGTH = 100
# load model
model = pickle.load(open(settings.MEDIA_URL + 'clickbait/linearSVC.sav', 'rb'))
# load vec
tfidf = pickle.load(open(settings.MEDIA_URL + 'clickbait/vec_result.pkl', "rb" ) )


def check_clickbaitness_cnn_lstm(text):
    input_text = np.array([text])
    tokenizer_predict = Tokenizer(num_words=MAX_VOCAB_SIZE)
    tokenizer_predict.fit_on_texts(input_text)
    sequences = tokenizer_predict.texts_to_sequences(input_text)
    data_predict = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    return model_cnn.predict(data_predict)[0][0]


def check_clickbaitness(text):
    content = np.array([str(text)])
    predict_vec = tfidf.transform(content)
    return model.predict(predict_vec)[0], model.predict_proba(predict_vec)[0]


def text_detection(path):
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    for text in texts:
        txt = text.description
        return txt


def class_str(words, keywords):
    for i in words:
        if i in keywords:
            return True
    return False


def check_class_map(text):
    words = text.split(' ')
    words = [i.upper() for i in words]

    def check_mapping(words):
        # p1 hypothesis
        p1_hypo_keywords = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/hypo.csv', header=None, index_col=None)[0])
        if class_str(words, p1_hypo_keywords):
            return 'hypothesis'

        # p2 shocking
        p2_shocking_keywords = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/shock.csv', header=None, index_col=None)[0])
        print(p2_shocking_keywords)
        if class_str(words, p2_shocking_keywords):
            return 'shocking'

        # p3 reaction
        p3_reaction_keywords = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/react.csv', header=None, index_col=None)[0])
        if class_str(words, p3_reaction_keywords):
            return 'reaction'

        # p4 questionable
        p4_question_keywords = ['WHICH', 'AM', 'WHAT', 'HOW', 'WHEN', 'ARE', 'WAS', 'WERE', 'MAY', 'MIGHT', 'CAN',
                                'COULD', 'WILL', 'SHALL', 'WOULD', 'SHOULD', 'HAS', 'HAVE', 'HAD', 'DID']
        if class_str(words, p4_question_keywords):
            return 'questionable'

            # p5 reasoning
        p5_reasoning_keywords = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/reason.csv', header=None, index_col=None)[0])
        if class_str(words, p5_reasoning_keywords):
            return 'reasoning'

        # p6 forward referencing
        p6_forward_ref = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/forward.csv', header=None, index_col=None)[0])
        if class_str(words, p6_forward_ref):
            return 'forwardreferencing'

        # p7 revealing
        p7_revealing = list(pd.read_csv(settings.MEDIA_URL + 'clickbait/reveal.csv', header=None, index_col=None)[0])
        if class_str(words, p7_revealing):
            return 'revealing'

        # p8 number
        for i in words:
            if i.isnumeric():
                return 'number'

        # p9 rest
        return 'miscellaneous'

    mapping = check_mapping(words)
    return mapping


@csrf_exempt
def api_text(request):
    if 'text-input' in request.POST:
        try:
            print(request.POST)
            text = request.POST.get('text-input', '')
            cluster = check_class_map(text)
            context = {
                'msg': 'output',
                'input': text,
                'cluster': cluster
            }
            pred, score = check_clickbaitness(text)
            context['score'] = '%.5f' % score[0] if pred == 0 else '%.5f' % score[1]
            context['output'] = 'Text is ' + ('clickbait' if pred == 0 else 'not a clickbait')
            return JsonResponse({'result': True, "output": context})
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
            return JsonResponse({'result': False})


@csrf_exempt
def home(request):
    context = {
    }
    if 'text-input' in request.POST:
        try:
            print(request.POST)
            text = request.POST.get('text-input', '')
            cluster = check_class_map(text)
            context = {
                'msg': 'output',
                'input': text,
                'cluster': cluster
            }
            pred, score = check_clickbaitness(text)
            context['score'] = '%.5f' % score[0] if pred == 0 else '%.5f' % score[1]
            context['output'] = 'Text is ' + ('clickbait' if pred == 0 else 'not a clickbait')
            obj = UserInputModel(
                image='',
                cluster=cluster,
                output=context['output'],
                text=text,
                pred=pred,
                score=context['score'])
            obj.save()
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
    elif 'file' in request.FILES.keys():
        try:
            uploaded_file = request.FILES['file']
            file_obj = FileSystemStorage()
            upload_path = '/clickbait/upload/' + uploaded_file.name
            path = file_obj.save(settings.STATICFILES_DIRS[0] + upload_path , uploaded_file)
            fetched = text_detection(path)
            print(fetched)
            cluster = check_class_map(fetched)
            context = {
                'msg': 'output',
                'image': True,
                'image_path': upload_path,
                'fetched_output': fetched,
                'cluster': cluster
            }
            pred, score = check_clickbaitness(fetched)
            context['score'] = '%.5f' % score[0] if pred == 0 else '%.5f' % score[1]
            context['output'] = 'Image content is ' + ('clickbait' if pred == 0 else 'not a clickbait')
            obj = UserInputModel(
                image=request.FILES['file'],
                cluster=cluster,
                output=context['output'],
                text=fetched,
                pred=pred,
                score=context['score'])
            obj.save()
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            context['error'] = str(e)
    
    return render(request, template, context)


def graph(request):
    input_text = request.GET.get('text', '')
    cluster = request.GET.get('cluster', '')
    return render(request, 'clickbait/graph.html', {'input': input_text, 'cluster': cluster})


def download(request, name):
    file_name = name
    file_path = settings.MEDIA_URL + 'clickbait/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    print(response)
    return response
