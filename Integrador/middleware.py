from django.shortcuts import redirect
from django.urls import reverse

ALLOWED_PATHS = (
    # rutas públicas (ajusta a tus paths reales)
    '/login/', '/register/', '/logout/',
)

# Prefijos permitidos (estáticos/media/admin si lo usas)
ALLOWED_PREFIXES = (
    '/static/', '/media/', '/admin/',
)

class SessionLoginRequiredMiddleware:
    """
    Exige que exista request.session['entidad_id'] para acceder al sitio.
    Deja pasar solo las rutas públicas definidas arriba.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # deja pasar prefijos (static, media, admin)
        if any(path.startswith(p) for p in ALLOWED_PREFIXES):
            return self.get_response(request)

        # deja pasar rutas explícitas
        if path in ALLOWED_PATHS:
            return self.get_response(request)

        # si no hay sesión => redirige a login
        if not request.session.get('entidad_id'):
            # si quieres llevar al usuario a donde iba, guarda next
            login_url = reverse('login')
            return redirect(f"{login_url}?next={path}")

        return self.get_response(request)
