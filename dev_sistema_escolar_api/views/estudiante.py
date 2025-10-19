from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from dev_sistema_escolar_api.serializers import UserSerializer
from dev_sistema_escolar_api.models import Estudiantes

class EstudianteView(generics.CreateAPIView):
    """
    Registrar nuevo Estudiante + crear usuario auth y asignar rol (Group).
    """
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_ser = UserSerializer(data=request.data)

        if not user_ser.is_valid():
            return Response(user_ser.errors, status=status.HTTP_400_BAD_REQUEST)

        role = request.data.get('rol')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')

        # Valida si existe el usuario por email
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return Response({"message": f"Username {email}, is already taken"}, status=400)

        # Crea usuario base
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=1,
        )
        user.set_password(password)
        user.save()

        # Asignar rol por Group
        group, _ = Group.objects.get_or_create(name=role)
        group.user_set.add(user)

        # Datos específicos de Estudiante
        estudiante = Estudiantes.objects.create(
            user=user,
            matricula=request.data.get("matricula"),
            fecha_nacimiento=request.data.get("fecha_nacimiento"),
            curp=request.data.get("curp", "").upper(),
            rfc=request.data.get("rfc", "").upper(),
            edad=request.data.get("edad"),
            telefono=request.data.get("telefono"),
            ocupacion=request.data.get("ocupacion"),
        )
        estudiante.save()

        return Response({"estudiante_created_id": estudiante.id}, status=201)
