from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import LoginSerializer, RegisterSerializer

# Re-exporta la vista de refresco de simplejwt sin modificaciones
RefreshTokenView = TokenRefreshView


def _tokens_para(user) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class LoginView(APIView):
    """
    POST /api/auth/login/
    Body: { "email": "...", "password": "..." }
    Devuelve: access token (60 min), refresh token (7 días) + info del usuario.
    """

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = LoginSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        return Response(
            {
                **_tokens_para(user),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "grupos": list(user.groups.values_list("name", flat=True)),
                },
            }
        )


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Crea un usuario con rol EXTERNO únicamente.
    El registro público no puede auto-asignarse Administrador.
    """

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        try:
            user.groups.add(Group.objects.get(name="Externo"))
        except Group.DoesNotExist:
            # Si las migraciones no se han corrido aún, continuar sin grupo
            pass

        return Response(
            {
                **_tokens_para(user),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "nombre": user.first_name,
                    "apellido": user.last_name,
                    "grupos": ["Externo"],
                },
            },
            status=status.HTTP_201_CREATED,
        )
