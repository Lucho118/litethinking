from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Autentica usuarios por email en lugar de username.
    Se registra en AUTHENTICATION_BACKENDS en settings/base.py.
    Como username == email en nuestros usuarios, el admin de Django
    también funciona con este backend.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Acepta 'email' como kwarg explícito (desde LoginSerializer)
        # o 'username' como fallback (desde admin de Django)
        email = kwargs.get("email") or username
        if not email:
            return None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Ejecuta el hash de contraseña de todas formas para evitar
            # timing attacks que permitan enumerar usuarios.
            User().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
