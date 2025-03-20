from rest_framework import serializers
from .models import Order, OrderImage, OrderAudio

class OrderImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderImage
        fields = ['id', 'image']

class OrderAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAudio
        fields = ['id', 'audio']

class OrderSerializer(serializers.ModelSerializer):
    images = OrderImageSerializer(many=True)
    audios = OrderAudioSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

class OrderCreateSerializer(serializers.ModelSerializer):
    # material_ids = serializers.ListField(child=serializers.IntegerField())
    class Meta:
        model = Order
        fields = '__all__'