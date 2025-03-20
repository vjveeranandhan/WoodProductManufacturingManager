from rest_framework import serializers
from .models import Material, MaterialImages

class MaterialImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialImages
        fields = ['id', 'image']

class MaterialSerializer(serializers.ModelSerializer):
    material_images = MaterialImagesSerializer(many=True)
    class Meta:
        model = Material
        fields = '__all__'

class CreateMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'