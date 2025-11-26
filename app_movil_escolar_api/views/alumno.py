from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from app_movil_escolar_api.serializers import UserSerializer , AlumnoSerializer
from app_movil_escolar_api.models import Alumnos
from django.shortcuts import get_object_or_404 as get_objetct_or_404

class AlumnosAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active=1).order_by('id')
        serializer = AlumnoSerializer(alumnos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AlumnoView(generics.CreateAPIView):

    
    '''
    Obtener un Alumno por ID
    '''
    def get(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        print(request)
        alumno = get_objetct_or_404(Alumnos, id=request.GET.get("id"))
        alumno = AlumnoSerializer(alumno, many=False).data
        return Response(alumno, status=status.HTTP_200_OK)

    """
    Registrar nuevo Alumno + crear usuario auth y asignar rol (Group).
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

        # Datos específicos de Alumno
        Alumno = Alumnos.objects.create(
            user=user,
            matricula=request.data.get("matricula"),
            fecha_nacimiento=request.data.get("fecha_nacimiento"),
            curp=request.data.get("curp", "").upper(),
            rfc=request.data.get("rfc", "").upper(),
            edad=request.data.get("edad"),
            telefono=request.data.get("telefono"),
            ocupacion=request.data.get("ocupacion"),
        )
        Alumno.save()

        return Response({"Alumno_created_id": Alumno.id}, status=201)
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        # Verificamos que el usuario este autenticado
        permissions_classes = (permissions.IsAuthenticated,)
        alumno = get_objetct_or_404(Alumnos, id=request.data["id"])
        alumno.id_trabajador = request.data["matricula"]
        alumno.telefono = request.data["telefono"]
        alumno.rfc = request.data["rfc"].upper()
        alumno.edad = request.data["edad"]
        alumno.save()
        # Actualizamos también los datos del usuario asociado
        user = alumno.user
        user.first_name = request.data["first_name"]
        user.last_name = request.data["last_name"]
        user.save()

        return Response({"message": "alumno updated successfully", "alumno":AlumnoSerializer(alumno).data}, status=200)
    
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_objetct_or_404(Alumnos, id=request.GET.get('id'))
        try:
            alumno.user.delete()
            return Response({"details":"Alumno eliminado"}, 200)
        except Exception as e:
            return Response({"details":"Error al eliminar"}, 400)
