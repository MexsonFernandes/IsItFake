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
from numpy.core._multiarray_umath import ndarray

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
    content = np.array([text])
    predict_vec = tfidf.transform(content)
    return model.predict(predict_vec)[0], model.predict_proba(predict_vec)[0][0]


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
            pred, score = check_clickbaitness(text)
            context['score'] = '%.5f' % score
            context['output'] = 'Text is ' + ('clickbait' if pred == 1 else 'not a clickbait')
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
            pred, score = check_clickbaitness(fetched)
            context['score'] = '%.5f' % score
            context['output'] = 'Image content is ' + ('clickbait' if pred == 1 else 'not a clickbait')
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
    return render(request, template, context)


def graph(request):
    input_text = request.GET.get('text', '')
    return render(request, 'clickbait/graph.html', {'input': input_text})
