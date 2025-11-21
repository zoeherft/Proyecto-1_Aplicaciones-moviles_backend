import json
from datetime import datetime, time

from django.contrib.auth.models import Group
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from app_movil_escolar_api.models import Maestros, User
from app_movil_escolar_api.serializers import MaestroSerializer, UserSerializer
from app_movil_escolar_api.views.users import (
    _build_user_payload,
    _parse_date,
    _parse_int,
    _require_fields,
    _upper_or_none,
)


def _parse_datetime(value):
    """Normaliza fecha_nacimiento a datetime consciente de zona horaria."""
    date_value = _parse_date(value)
    if not date_value:
        return None
    naive_dt = datetime.combine(date_value, time.min)
    return timezone.make_aware(naive_dt, timezone.get_default_timezone())


class MaestrosAll(generics.CreateAPIView):
    # Obtener todos los maestros (requiere token)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestroSerializer(maestros, many=True).data
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    maestro["materias_json"] = []
        return Response(lista, 200)


class MaestrosView(generics.CreateAPIView):
    # Registrar nuevo usuario maestro
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
        email = user_serializer.validated_data["email"]
        password = request.data["password"]

        if User.objects.filter(email=email).exists():
            return Response({"message": "Username " + email + ", is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=email,
            email=email,
            first_name=user_serializer.validated_data["first_name"],
            last_name=user_serializer.validated_data["last_name"],
            is_active=1,
        )
        user.set_password(password)
        user.save()

        group, _ = Group.objects.get_or_create(name=role)
        group.user_set.add(user)

        materias = request.data.get("materias_json", [])
        if isinstance(materias, str):
            try:
                materias = json.loads(materias)
            except json.JSONDecodeError:
                materias = []
        if materias is None or materias == "":
            materias = []

        fecha_nacimiento = _parse_datetime(request.data.get("fecha_nacimiento"))

        maestro = Maestros.objects.create(
            user=user,
            id_trabajador=request.data.get("id_trabajador"),
            fecha_nacimiento=fecha_nacimiento,
            telefono=request.data.get("telefono"),
            rfc=_upper_or_none(request.data.get("rfc")),
            cubiculo=request.data.get("cubiculo"),
            area_investigacion=request.data.get("area_investigacion"),
            materias_json=json.dumps(materias),
        )

        return Response({"maestro_created_id": maestro.id}, status=status.HTTP_201_CREATED)
