from django.conf import settings
from django_hosts import patterns, host


host_patterns = patterns(
    '',
    host(r'www', 'www.urls', name='www'),
    host(r'admin', settings.ROOT_URLCONF, name='admin'),
    host(r'clickbait', 'clickbait.urls', name='clickbait'),
    host(r'fakenews', 'fakenews.urls', name='fakenews'),
    host(r'faceswap', 'deepfakes.urls', name='faceswap'),
    host(r'quotexaminer', 'quotexaminer.urls', name='quotexaminer')
)
