from rest_framework import serializers
from .models import InventoryCategory

class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = '__all__'  # Includes all fields from the model
