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
import traceback
import pandas as pd
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
ps = PorterStemmer()

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
    content = np.array([str(text)])
    predict_vec = tfidf.transform(content)
    return model.predict(predict_vec)[0], model.predict_proba(predict_vec)[0]


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
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            context['error'] = str(e)
    return render(request, template, context)


def graph(request):
    input_text = request.GET.get('text', '')
    cluster = request.GET.get('cluster', '')
    return render(request, 'clickbait/graph.html', {'input': input_text, 'cluster': cluster})
