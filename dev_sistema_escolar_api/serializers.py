from django.contrib.auth.models import User
from rest_framework import serializers
from dev_sistema_escolar_api.models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'

class EstudianteSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Estudiantes
        fields = '__all__'

class MaestroSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Maestros
        fields = '__all__'