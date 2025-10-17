import json

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group

from app_movil_escolar_api.serializers import UserSerializer, MaestrosSerializer
from app_movil_escolar_api.models import User, Maestros

from app_movil_escolar_api.views.users import (
    _build_user_payload,
    _upper_or_none,
    _parse_date,
    _require_fields,
)


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

        role = request.data.get("rol") or "maestro"
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

        materias = request.data.get("materias_json", [])
        if isinstance(materias, str):
            try:
                materias = json.loads(materias)
            except json.JSONDecodeError:
                materias = []

        fecha_nacimiento = _parse_date(request.data.get("fecha_nacimiento"))
        if request.data.get("fecha_nacimiento") and not fecha_nacimiento:
            return Response(
                {"message": "Fecha de nacimiento invalida. Usa formatos YYYY-MM-DD, DD-MM-YYYY o MM-DD-YYYY."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
