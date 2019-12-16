from django.shortcuts import render
import os
from django.conf import settings


def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def home(request):
    context = {}
    print(request.POST)
    if not dict(request.POST).__contains__("file"):
        print("sirbhss")
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
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        handle_uploaded_file(upload, destination)
        print("Save it to:", destination)
        context = {
            'image_name': 'faceswap/upload/' + filename,
        }
    else:
        print("url")
        url = request.POST.get("url", "")
        print(url)
    return render(request, 'deepfakes/index.html', context)
