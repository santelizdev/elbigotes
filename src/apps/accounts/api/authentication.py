from rest_framework import authentication, exceptions

from apps.accounts.models import User
from apps.accounts.tokens import read_access_token


class SignedTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        try:
            keyword, token = header.split(" ", 1)
        except ValueError:
            raise exceptions.AuthenticationFailed("Header de autorización inválido.")

        if keyword != self.keyword or not token:
            return None

        try:
            payload = read_access_token(token)
        except Exception as exc:  # noqa: BLE001
            raise exceptions.AuthenticationFailed("Token inválido o expirado.") from exc

        try:
            user = User.objects.get(pk=payload["user_id"], is_active=True)
        except User.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("La cuenta asociada al token no existe.") from exc

        return user, token
