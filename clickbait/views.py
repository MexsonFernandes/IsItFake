import io
import numpy as np
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from google.cloud import vision
from keras.models import load_model
from keras_preprocessing.sequence import pad_sequences
from keras_preprocessing.text import Tokenizer

template = 'clickbait/index.html'
model = load_model(settings.MEDIA_URL + 'clickbait/host.h5')
MAX_VOCAB_SIZE = 20000
MAX_SEQUENCE_LENGTH = 100


def check_clickbaitness(text):
    input_text = np.array([text])
    tokenizer_predict = Tokenizer(num_words=MAX_VOCAB_SIZE)
    tokenizer_predict.fit_on_texts(input_text)
    sequences = tokenizer_predict.texts_to_sequences(input_text)
    data_predict = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    return model.predict(data_predict)[0][0]


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
            score = check_clickbaitness(text)
            context['score'] = '%.5f' % score
            context['output'] = 'Text is ' + ('clickbait' if score >= 0.5 else 'not a clickbait')
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
            score = check_clickbaitness(fetched)
            context['score'] = '%.5f' % score
            context['output'] = 'Image content is ' + ('clickbait' if score >= 0.5 else 'not a clickbait')
        except Exception as e:
            print(str(e))
            context['error'] = str(e)
    return render(request, template, context)


def graph(request):
    input_text = request.GET.get('text', '')
    return render(request, 'clickbait/graph.html', {'input': input_text})
