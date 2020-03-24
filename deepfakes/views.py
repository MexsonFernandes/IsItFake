import math
import tempfile
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse
import urllib.request
from pytube import YouTube
import requests
import cv2
from keras.preprocessing import image
import numpy as np
import tensorflow as tf
import os
import glob
from wsgiref.util import FileWrapper
import mimetypes
from django.utils.encoding import smart_str
from deepfakes.models import UserInputModel


global classifier
classifier = tf.keras.models.load_model(settings.MEDIA_URL + 'faceswap/' + 'MODEL.h5')


# predict input image images
def predict_image(image_path, classifier):
    test_image = image.load_img(image_path, target_size=(128, 128))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = classifier.predict(test_image)
    return result[0][0]


def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def download_video_from_url(link, destination):
    name = "sample"
    if 'youtube' in link:
        yt = YouTube(link)
        name = yt.streams.filter(res="144p").first().download(destination)
    elif link.split('/')[len(link.split('/')) - 1].__contains__('.'):
        urllib.request.urlretrieve(link, destination)
    else:
        r = requests.get(link, stream=True)
        with open(destination, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return name


def download(request, file_name):
    print(file_name)
    file_path = settings.MEDIA_URL + 'faceswap/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    print(response)
    return response


def create_frames_for_slots(path):
    # count frame
    video = cv2.VideoCapture(path)
    count = 0
    frame_rate = video.get(5)
    print(video.isOpened())
    property_id = int(cv2.CAP_PROP_FRAME_COUNT)
    count = int(cv2.VideoCapture.get(video, property_id))
    # create frames
    frame_path = path.replace(".mp4", "") + "/"
    os.mkdir(frame_path)
    while video.isOpened():
        frame_id = int(video.get(1))
        ret, frame = video.read()
        if frame_id == 1 or frame_id == count -1 or frame_id == int(count / 2):
            filename = frame_path + str(frame_id) + ".jpg"
            print(frame_id)
            cv2.imwrite(filename, frame)
        if frame is None:
            break
    return frame_path


def home(request):
    context = {}
    try:
        if request.method == 'POST':
            if len(request.POST.get("url", "")) == 0:
                print('file uploaded')
                # target = os.path.join(APP_ROOT, 'images/')
                target = os.path.join(settings.STATICFILES_DIRS[0], 'faceswap/upload')
                print(target)
                if not os.path.exists(target):
                    os.mkdir(target)
                else:
                    print("Couldn't create upload directory: {}".format(target))
                upload = request.FILES["file"]
                print(upload)
                print("{} is the file name".format(upload.name))
                filename = upload.name
                extension = filename[filename.rfind('.') + 1: ]
                destination = "/".join([target, filename])
                if os.path.exists(destination):
                    new_path = tempfile.mkstemp()[1].split('/')[2]
                    destination = destination.replace(filename, new_path + '.' + extension)
                    print(extension)
                    print(destination)
                print("Accept incoming file:", filename)
                handle_uploaded_file(upload, destination)
                print("Saved to:", destination)
                path = glob.glob(create_frames_for_slots(destination) + '*.jpg')
                global classifier
                average_score = sum([predict_image(img, classifier) for img in path]) / len(path)
                print(average_score)
                context = {
                    'video': 'static/faceswap/upload/' + filename,
                    'msg': 'output',
                    'result': 'real' if average_score < 50 else 'fake',
                    'score': "%.2f" % (float(average_score)*100)
                }
                obj = UserInputModel(
                    video = 'static/faceswap/upload/' + filename,
                    output = context['result'],
                    score = context['score'],
                    url = ''
                )
                obj.save()
            else:
                print("url")
                url = request.POST.get("url", "")
                target = os.path.join(settings.STATICFILES_DIRS[0], 'faceswap/upload')
                # destination = target + tempfile.mkstemp()[1].split('/')[2]
                destination = download_video_from_url(url, target)
                print(url)
                print(target)
                path = glob.glob(create_frames_for_slots(destination) + '*.jpg')
                global classifier
                average_score = sum([predict_image(img, classifier) for img in path]) / len(path)
                print(average_score)
                context = {
                    'video': 'static/faceswap/upload' + destination.replace(target, ''),
                    'msg': 'output',
                    'result': 'real' if average_score < 50 else 'fake',
                    'score': "%.2f" % (float(average_score)*100)
                }
                obj = UserInputModel(
                    video = 'static/faceswap/upload' + destination.replace(target, ''),
                    output = context['result'],
                    score = context['score'],
                    url = url
                )
                obj.save()
    except Exception as e:
        context = {
            "error": str(e)
        }
    return render(request, 'deepfakes/index.html', context)
