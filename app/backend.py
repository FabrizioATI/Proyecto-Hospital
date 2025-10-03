# accounts/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from .models import Entidad

class EntidadBackend(ModelBackend):
    """
    Autentica usando Entidad.dni + Entidad.contrase�a.
    Crea/actualiza un User 'sombra' con username=dni para integrarse con el ecosistema Django.
    """
    def authenticate(self, request, dni=None, password=None, **kwargs):
        if not dni or not password:
            return None
        try:
            entidad = Entidad.objects.get(dni=dni)
        except Entidad.DoesNotExist:
            return None

        raw_or_hashed = entidad.contrasena or ""

        # 1) Si contrase�a ya est� hasheada (pbkdf2_sha256/argon2/etc.)
        is_ok = check_password(password, raw_or_hashed)

        # 2) Si no est� hasheada (texto plano), valida directo:
        if not is_ok and raw_or_hashed and "$" not in raw_or_hashed:
            is_ok = (password == raw_or_hashed)

        if not is_ok:
            return None

        # Sincroniza/crea el User �sombra�
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=entidad.dni)
            # Llena nombres b�sicos (opcional)
            user.first_name = entidad.nombre or ""
            user.last_name = f"{entidad.apellidoPaterno or ''} {entidad.apellidoMaterno or ''}".strip()
            user.email = entidad.correo or ""
            user.is_active = True

            # Si en Entidad la contrase�a est� en texto plano, guarda el hash en User
            if "$" not in raw_or_hashed:
                user.set_password(password)
            else:
                # Si ya estaba hasheada en Entidad, reflejarla en User
                user.password = raw_or_hashed
            user.save()

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
