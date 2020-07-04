from rest_framework import serializers


class FakeNewsSerializer(serializers.Serializer):
    news = serializers.CharField(max_length=5000, default='')
    url = serializers.URLField(default='')
    api_key = serializers.CharField(max_length=300)
