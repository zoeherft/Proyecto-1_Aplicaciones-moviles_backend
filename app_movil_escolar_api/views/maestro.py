from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from app_movil_escolar_api.serializers import UserSerializer, MaestroSerializer
from app_movil_escolar_api.models import Maestros
import json
from django.shortcuts import get_object_or_404 as get_objetct_or_404

class MaestrosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by('id')
        maestros_lista = MaestroSerializer(maestros, many=True).data
        for maestro in maestros_lista:
            if isinstance(maestro,dict) and 'materias_json' in maestro:
                try:
                    maestro['materias_json'] = json.loads(maestro['materias_json'])
                except Exception:
                    maestro['materias_json'] = []
        return Response(maestros_lista, status=status.HTTP_200_OK)


class MaestroView(generics.CreateAPIView):

    
    '''
    Obtener un Maestro por ID
    '''
    def get(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        maestro = get_objetct_or_404(Maestros, id=request.GET.get("id"))
        maestro = MaestroSerializer(maestro, many=False).data
        return Response(maestro, status=status.HTTP_200_OK)

    """
    Registrar nuevo Maestro + crear usuario auth y asignar rol (Group).
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

        # Datos específicos de Maestro
        maestro = Maestros.objects.create(
            user=user,
            id_trabajador=request.data.get("id_trabajador"),
            fecha_nacimiento=request.data.get("fecha_nacimiento"),
            telefono=request.data.get("telefono"),
            rfc=request.data.get("rfc", "").upper(),
            cubiculo=request.data.get("cubiculo"),
            edad=request.data.get("edad"),
            area_investigacion=request.data.get("area_investigacion"),
            materias_json=request.data.get("materias_json"),
        )
        maestro.save()

        return Response({"maestro_created_id": maestro.id}, status=201)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verificamos que el usuario este autenticado
        permissions_classes = (permissions.IsAuthenticated,)
        maestro = get_objetct_or_404(Maestros, id=request.data["id"])
        maestro.id_trabajador = request.data["id_trabajador"]
        maestro.telefono = request.data["telefono"]
        maestro.rfc = request.data["rfc"].upper()
        maestro.edad = request.data["edad"]
        maestro.save()
        # Actualizamos también los datos del usuario asociado
        user = maestro.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        return Response({"message": "maestro updated successfully", "maestro":MaestroSerializer(maestro).data}, status=200)
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        maestro = get_objetct_or_404(Maestros, id=request.GET.get('id'))
        try:
            maestro.user.delete()
            return Response({"details":"Maestro eliminado"}, 200)
        except Exception as e:
            return Response({"details":"Error al eliminar"}, 400)
