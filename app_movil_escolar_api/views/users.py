from django.db import transaction
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from app_movil_escolar_api.serializers import UserSerializer
from app_movil_escolar_api.models import *

class UserMe(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "groups": list(user.groups.values_list("name", flat=True)),
        }
        return Response(data, status=status.HTTP_200_OK)
