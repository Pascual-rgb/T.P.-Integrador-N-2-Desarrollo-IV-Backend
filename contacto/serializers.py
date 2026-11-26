from rest_framework import serializers
from .models import Mensaje


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = ['id', 'nombre', 'correo', 'mensaje', 'creado', 'leido']
        read_only_fields = ['id', 'creado']

    def validate_nombre(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('El nombre es demasiado corto.')
        return value.strip()

    def validate_mensaje(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('El mensaje debe tener al menos 10 caracteres.')
        return value.strip()

    def create(self, validated_data):
        validated_data['leido'] = False
        return super().create(validated_data)