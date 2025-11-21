from django.db import transaction
from datetime import datetime, date

# IMPORTAMOS LOS SERIALIZERS NECESARIOS
from app_movil_escolar_api.serializers import (
    UserSerializer,
    AdminSerializer  # ← ESTE FALTABA
)

from app_movil_escolar_api.models import Administradores, User

from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

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
        admin = Administradores.objects.filter(user__is_active=1).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)


class AdminView(generics.CreateAPIView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=_build_user_payload(request.data))

        try:
            _require_fields(request.data, ["first_name", "last_name", "email", "password"])
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_valid():

            role = request.data.get('rol') or 'admin'
            first_name = user.validated_data['first_name']
            last_name = user.validated_data['last_name']
            email = user.validated_data['email']
            password = request.data['password']

            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message": "Username " + email + ", is already taken"}, 400)

            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )

            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            admin = Administradores.objects.create(
                user=user,
                clave_admin=request.data.get("clave_admin"),
                telefono=request.data.get("telefono"),
                rfc=_upper_or_none(request.data.get("rfc")),
                edad=_parse_int(request.data.get("edad")),
                ocupacion=request.data.get("ocupacion"),
            )
            admin.save()

            return Response({"admin_created_id": admin.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
