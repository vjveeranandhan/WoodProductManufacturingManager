from rest_framework import serializers
from .models import CarpenterEnquire

class CarpenterEnquireSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(read_only=True)  # Returns order ID
    material_id = serializers.PrimaryKeyRelatedField(read_only=True)  # Returns material ID
    carpenter_id = serializers.PrimaryKeyRelatedField(read_only=True)  # Returns carpenter ID

    class Meta:
        model = CarpenterEnquire
        fields = [
            'id', 
            'order_id', 
            'material_id', 
            'material_length', 
            'material_height', 
            'material_width', 
            'status', 
            'carpenter_id', 
            'material_cost'
        ]
