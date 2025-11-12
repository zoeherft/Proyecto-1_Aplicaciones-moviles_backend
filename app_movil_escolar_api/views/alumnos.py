<<<<<<< HEAD
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group

from app_movil_escolar_api.serializers import UserSerializer, AlumnosSerializer
from app_movil_escolar_api.models import User, Alumnos

from app_movil_escolar_api.views.users import (
    _build_user_payload,
    _upper_or_none,
    _parse_int,
    _parse_date,
    _require_fields,
)


class AlumnosView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.select_related("user").all()
        serializer = AlumnosSerializer(alumnos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_serializer = UserSerializer(data=_build_user_payload(request.data))

        try:
            _require_fields(request.data, ["first_name", "last_name", "email", "password"])
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        role = request.data.get("rol") or "alumno"
        first_name = user_serializer.validated_data["first_name"]
        last_name = user_serializer.validated_data["last_name"]
        email = user_serializer.validated_data["email"]
        password = request.data["password"]

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return Response({"message": "Username " + email + ", is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=1,
        )

        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role)
        group.user_set.add(user)
        user.save()

        fecha_nacimiento = _parse_date(request.data.get("fecha_nacimiento"))
        if request.data.get("fecha_nacimiento") and not fecha_nacimiento:
            return Response(
                {"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        alumno = Alumnos.objects.create(
            user=user,
            matricula=request.data.get("matricula"),
            telefono=request.data.get("telefono"),
            fecha_nacimiento=fecha_nacimiento,
            curp=_upper_or_none(request.data.get("curp")),
            rfc=_upper_or_none(request.data.get("rfc")),
            edad=_parse_int(request.data.get("edad")),
            ocupacion=request.data.get("ocupacion"),
        )

        return Response({"alumno_created_id": alumno.id}, status=status.HTTP_201_CREATED)


class AlumnoDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def _get_object(self, pk):
        return get_object_or_404(Alumnos.objects.select_related("user"), pk=pk)

    def get(self, request, pk, *args, **kwargs):
        alumno = self._get_object(pk)
        serializer = AlumnosSerializer(alumno)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        alumno = self._get_object(pk)
        user = alumno.user

        payload = _build_user_payload(request.data)
        new_email = payload.get("email")
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                return Response({"message": "Username " + new_email + ", is already taken"}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email
            user.username = new_email
        if payload.get("first_name"):
            user.first_name = payload["first_name"]
        if payload.get("last_name"):
            user.last_name = payload["last_name"]

        password = request.data.get("password")
        if password:
            user.set_password(password)
        user.save()

        fecha_valor = request.data.get("fecha_nacimiento")
        if fecha_valor is not None:
            fecha_nacimiento = _parse_date(fecha_valor)
            if fecha_valor and not fecha_nacimiento:
                return Response(
                    {"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            alumno.fecha_nacimiento = fecha_nacimiento

        if "matricula" in request.data:
            alumno.matricula = request.data.get("matricula") or None
        if "telefono" in request.data:
            alumno.telefono = request.data.get("telefono") or None
        if "curp" in request.data:
            alumno.curp = _upper_or_none(request.data.get("curp"))
        if "rfc" in request.data:
            alumno.rfc = _upper_or_none(request.data.get("rfc"))
        if "edad" in request.data:
            alumno.edad = _parse_int(request.data.get("edad"))
        if "ocupacion" in request.data:
            alumno.ocupacion = request.data.get("ocupacion") or None

        alumno.save()
        serializer = AlumnosSerializer(alumno)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        alumno = self._get_object(pk)
        user = alumno.user
        alumno.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
=======
from django.db.models import *
from django.db import transaction
from app_movil_escolar_api.serializers import UserSerializer
from app_movil_escolar_api.serializers import *
from app_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group

#Esta funcion regresa todos los alumnos registrados 
class AlumnosAll(generics.CreateAPIView):
    #Aquí se valida la autenticación del usuario
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Create a profile for the user
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID= ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
>>>>>>> upstream/master
