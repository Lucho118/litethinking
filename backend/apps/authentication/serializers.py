from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict:
        user = authenticate(
            request=self.context.get("request"),
            email=data["email"],
            password=data["password"],
        )
        if user is None:
            raise serializers.ValidationError(
                "Email o contraseña incorrectos.",
                code="invalid_credentials",
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Esta cuenta está desactivada.",
                code="user_inactive",
            )
        data["user"] = user
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirmar = serializers.CharField(write_only=True)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value

    def validate(self, data: dict) -> dict:
        if data["password"] != data["password_confirmar"]:
            raise serializers.ValidationError(
                {"password_confirmar": "Las contraseñas no coinciden."}
            )
        # Ejecuta TODOS los validadores registrados en AUTH_PASSWORD_VALIDATORS
        try:
            validate_password(data["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return data

    def save(self, **kwargs):
        email = self.validated_data["email"]
        # username = email: evita crear un modelo de usuario custom
        return User.objects.create_user(
            username=email,
            email=email,
            password=self.validated_data["password"],
        )
