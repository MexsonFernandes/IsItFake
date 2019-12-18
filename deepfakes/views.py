import tempfile
from django.shortcuts import render
import os
from django.conf import settings
import urllib.request
from pytube import YouTube
import requests


def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def download_video_from_url(link, destination):
    name = "sample"
    if 'youtube' in link:
        name = YouTube(link).streams.first().download(destination)
    elif link.split('/')[len(link.split('/')) - 1].__contains__('.'):
        urllib.request.urlretrieve(link, destination)
    else:
        r = requests.get(link, stream=True)
        with open(destination, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
    return name


def home(request):
    context = {}
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
            extension = filename.split('.')[1]
            destination = "/".join([target, filename])
            if os.path.exists(destination):
                new_path = tempfile.mkstemp()[1].split('/')[2]
                destination = destination.replace(filename, new_path + '.' + extension)
            print("Accept incoming file:", filename)
            handle_uploaded_file(upload, destination)
            print("Saved to:", destination)
            context = {
                'video': 'static/faceswap/upload/' + filename,
                'msg': 'output',
                'result': 'To be uploaded'
            }
        else:
            print("url")
            url = request.POST.get("url", "")
            target = os.path.join(settings.STATICFILES_DIRS[0], 'faceswap/upload')
            # destination = target + tempfile.mkstemp()[1].split('/')[2]
            name = download_video_from_url(url, target)
            print(name)
            print(url)
            print(target)
            context = {
                'video': 'static/faceswap/upload' + name.replace(target, ''),
                'msg': 'output',
                'result': 'To be uploaded'
            }
    return render(request, 'deepfakes/index.html', context)
