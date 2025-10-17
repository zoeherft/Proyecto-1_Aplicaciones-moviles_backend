import json
from django.db.models import *
from django.db import transaction
from datetime import datetime, date
from django.shortcuts import get_object_or_404
from app_movil_escolar_api.serializers import UserSerializer
from app_movil_escolar_api.serializers import *
from app_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group

def _build_user_payload(data):
    return {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email"),
    }


def _upper_or_none(value):
    if not value:
        return None
    return str(value).upper()


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = value.strip()
        value = value.replace("/", "-")
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
    return None


def _require_fields(data, required):
    missing = [field for field in required if not data.get(field)]
    if missing:
        raise ValueError("Missing required fields: " + ", ".join(missing))


class AdminAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        user = request.user
        #TODO: Regresar perfil del usuario
        return Response({})

class AdminView(generics.CreateAPIView):
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Serializamos los datos del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=_build_user_payload(request.data))
        
        try:
            _require_fields(request.data, ["first_name", "last_name", "email", "password"])
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_valid():
            #Grab user data
            role = request.data.get('rol') or 'admin'
            first_name = user.validated_data['first_name']
            last_name = user.validated_data['last_name']
            email = user.validated_data['email']
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
            # Cifrar la contrasena
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data["clave_admin"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            edad= request.data["edad"],
                                            ocupacion= request.data["ocupacion"])
            admin.save()

            return Response({"admin_created_id": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)


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

        role = request.data.get('rol') or 'alumno'
        first_name = user_serializer.validated_data['first_name']
        last_name = user_serializer.validated_data['last_name']
        email = user_serializer.validated_data['email']
        password = request.data['password']

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return Response({"message": "Username "+email+", is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=1
        )

        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role)
        group.user_set.add(user)
        user.save()

        fecha_nacimiento = _parse_date(request.data.get("fecha_nacimiento"))
        if request.data.get("fecha_nacimiento") and not fecha_nacimiento:
            return Response({"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({"message": "Username "+new_email+", is already taken"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."}, status=status.HTTP_400_BAD_REQUEST)
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


class MaestrosView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.select_related("user").all()
        serializer = MaestrosSerializer(maestros, many=True)
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

        role = request.data.get('rol') or 'maestro'
        first_name = user_serializer.validated_data['first_name']
        last_name = user_serializer.validated_data['last_name']
        email = user_serializer.validated_data['email']
        password = request.data['password']

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return Response({"message": "Username "+email+", is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=1
        )

        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role)
        group.user_set.add(user)
        user.save()

        materias = request.data.get("materias_json", [])
        if isinstance(materias, str):
            try:
                materias = json.loads(materias)
            except json.JSONDecodeError:
                materias = []

        fecha_nacimiento = _parse_date(request.data.get("fecha_nacimiento"))
        if request.data.get("fecha_nacimiento") and not fecha_nacimiento:
            return Response({"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."}, status=status.HTTP_400_BAD_REQUEST)

        maestro = Maestros.objects.create(
            user=user,
            telefono=request.data.get("telefono"),
            id_trabajador=request.data.get("id_trabajador"),
            fecha_nacimiento=fecha_nacimiento,
            rfc=_upper_or_none(request.data.get("rfc")),
            cubiculo=request.data.get("cubiculo"),
            area_investigacion=request.data.get("area_investigacion"),
            materias_json=materias,
        )

        return Response({"maestro_created_id": maestro.id}, status=status.HTTP_201_CREATED)


class MaestroDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def _get_object(self, pk):
        return get_object_or_404(Maestros.objects.select_related("user"), pk=pk)

    def get(self, request, pk, *args, **kwargs):
        maestro = self._get_object(pk)
        serializer = MaestrosSerializer(maestro)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        maestro = self._get_object(pk)
        user = maestro.user

        payload = _build_user_payload(request.data)
        new_email = payload.get("email")
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                return Response({"message": "Username "+new_email+", is already taken"}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."}, status=status.HTTP_400_BAD_REQUEST)
            maestro.fecha_nacimiento = fecha_nacimiento

        if "telefono" in request.data:
            maestro.telefono = request.data.get("telefono") or None
        if "id_trabajador" in request.data:
            maestro.id_trabajador = request.data.get("id_trabajador") or None
        if "rfc" in request.data:
            maestro.rfc = _upper_or_none(request.data.get("rfc"))
        if "cubiculo" in request.data:
            maestro.cubiculo = request.data.get("cubiculo") or None
        if "area_investigacion" in request.data:
            maestro.area_investigacion = request.data.get("area_investigacion") or None
        if "materias_json" in request.data:
            materias = request.data.get("materias_json")
            if isinstance(materias, str):
                try:
                    materias = json.loads(materias)
                except json.JSONDecodeError:
                    return Response({"message": "Formato invalido para materias_json."}, status=status.HTTP_400_BAD_REQUEST)
            if materias is None or materias == "":
                materias = []
            maestro.materias_json = materias

        maestro.save()
        serializer = MaestrosSerializer(maestro)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        maestro = self._get_object(pk)
        user = maestro.user
        maestro.delete()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
