from rest_framework import serializers
from .models import PresentationData

class TextSerializer(serializers.Serializer):
    text = serializers.CharField()

class PresentationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentationData
        fields = '__all__'