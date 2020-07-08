import io
import mimetypes
import os
import re

from django.conf import settings
from django.core.files import File
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from flask import send_file
from nltk import ne_chunk, pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from google.cloud import vision
from googleapiclient.discovery import build
from django.views.decorators.csrf import csrf_exempt
from wsgiref.util import FileWrapper
from quotexaminer.models import UserInputModel


def words(text):
    return re.findall(r'\w+', text.lower())


def entities(txt):
    return ne_chunk(pos_tag(word_tokenize(txt)))


def download(request, file_name):
    print(file_name)
    file_path = settings.MEDIA_URL + 'quotexaminer/' + file_name
    file_wrapper = FileWrapper(open(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)
    print(response)
    return response


def verify_quote(result):
    service = build("customsearch", "v1",
                    developerKey="AIzaSyAaJ8-PEOVH4AiNEZ2KcS24h48tPIkrmdY")
    status = "CANNOT VERIFY IMAGE!!!"
    print(result)
    a1 = 'is'
    a2 = result
    a3 = 'a misquote?'

    result = ' '.join([a1, a2, a3])
    print(result)
    res = service.cse().list(
        q=result,
        cx='004620519245503932279:5cjutc5z-oa',
        lr='lang_en',
    ).execute()

    i = 0
    dd = 0
    qq = 0
    while i < 15:
        try:
            link = res["items"][i].get("formattedUrl")
            qq = 1
            print(link)
            if (link.find("fake-quote") > -1 or link.find("fake_quote") > -1
                    or link.find("misquoted") > -1
                    or link.find("misquote") > -1
                    or link.find("misattributed") > -1
                    or link.find("misquotation") > -1):
                status = "MISQUOTED IMAGE!!!"
                return status
            else:
                domain = link.split('/')[0]
                if domain.startswith("https"):
                    domain = link.split('//')[-1].split('/')[0]

                ll = words(open(settings.STATIC_ROOT + '/quotexaminer/site.txt', 'r', encoding='utf-8').read())
                for hh in range(0, len(ll)):
                    if (ll[hh] == domain.replace('www.', '').replace
                        ('.com', '').replace('en.', '').
                            replace('.org', '')):
                        dd = dd + 1
                print(domain)

        except IndexError as e:
            print(e)
        i = i + 1
    if qq == 1:
        if dd == 0:
            status = "QUOTE NOT VERIFIED!!!"
        else:
            status = "QUOTE VERIFIED!!!"
    return status


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
        break


def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def home(request):
    try:
        if request.method == 'POST':
            # target = os.path.join(APP_ROOT, 'images/')
            target = os.path.join(settings.STATICFILES_DIRS[0], 'quotexaminer/upload')
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

            result = text_detection(destination)
            print(result, "\n\n")
            result = result.replace('"', '')

            number_of_sentences = sent_tokenize(result)
            if len(number_of_sentences) > 1:
                result1 = '\n'.join(number_of_sentences[0:len(number_of_sentences) - 1])
            else:
                result1 = result
            import language_check
            tool = language_check.LanguageTool('en-US')
            result1 = language_check.correct(result1, tool.check(result1))
            st = verify_quote(result1)
            # status = "L"
            nn = len(result1)
            s = str(entities(result))
            if s.find('(PERSON', nn) > 0:
                start = s.find('(PERSON', nn) + 8
                end = s.find(')', start)
                r = str(s[start:end])
                r = r.replace('/NNP', '')\
                    .replace('/NN', '')
            else:
                r = "Unknown"
            result = result.replace(r, '')
            res = result1#language_check.correct(result, tool.check(result))
            context = {
                'image_name': 'quotexaminer/upload/' + filename,
                'q': res,
                'a': r,
                'v': st
            }
            obj = UserInputModel(image=request.FILES["file"],
                            quote=res,
                            author=r,
                            output=st)
            obj.save()
            return render(request, "quotexaminer/disp.html", context=context)
        else:
            return render(request, 'quotexaminer/disp.html')
    except Exception as e:
        print(str(e))
        return render(request, 'quotexaminer/index.html')
