from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404 as get_objetct_or_404

from app_movil_escolar_api.serializers import UserSerializer, AdminSerializer
from app_movil_escolar_api.models import Administradores

class AdminsAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        admins = Administradores.objects.filter(user__is_active=1).order_by('id')
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminView(generics.CreateAPIView):
    
    '''
    Obtener un Administrador por ID
    '''
    def get(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        print(request)
        admins = get_objetct_or_404(Administradores, id=request.GET.get("id"))
        admin = AdminSerializer(admins, many=False).data
        return Response(admin, status=status.HTTP_200_OK)

    """
    Registrar nuevo Administrador + crear usuario auth y asignar rol (Group).
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

        # Datos específicos de Administrador
        admin = Administradores.objects.create(
            user=user,
            clave_admin=request.data.get("clave_admin"),
            telefono=request.data.get("telefono"),
            rfc=request.data.get("rfc", "").upper(),
            edad=request.data.get("edad"),
            ocupacion=request.data.get("ocupacion"),
        )
        admin.save()

        return Response({"admin_created_id": admin.id}, status=201)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verificamos que el usuario este autenticado
        permissions_classes = (permissions.IsAuthenticated,)
        admin = get_objetct_or_404(Administradores, id=request.data["id"])
        admin.clave_admin = request.data["clave_admin"]
        admin.telefono = request.data["telefono"]
        admin.rfc = request.data["rfc"].upper()
        admin.edad = request.data["edad"]
        admin.ocupacion = request.data["ocupacion"]
        admin.save()
        # Actualizamos también los datos del usuario asociado
        user = admin.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        return Response({"message": "Administrador updated successfully", "admin":AdminSerializer(admin).data}, status=200)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        admin = get_objetct_or_404(Administradores, id=request.GET.get('id'))
        try:
            admin.user.delete()
            return Response({"details":"Administrador eliminado"}, 200)
        except Exception as e:
            return Response({"details":"Administrador eliminado"}, 400)

    

    
