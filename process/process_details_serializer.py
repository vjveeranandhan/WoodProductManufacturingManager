from rest_framework import serializers
from process.models import ProcessDetails
from .models import ProcessMaterials, ProcessDetailsImage

class ProcessDetailsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessDetailsImage
        fields = ['id', 'image']

class ProcessDetailsSerializer(serializers.ModelSerializer):
    images = ProcessDetailsImageSerializer(many=True)
    class Meta:
        model = ProcessDetails
        fields = '__all__'  # Include all fields

class ProcessMaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessMaterials
        fields = '__all__'
