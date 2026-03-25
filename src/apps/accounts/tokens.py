from django.core import signing

from apps.accounts.models import User

TOKEN_SALT = "accounts.api.token"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 14


def create_access_token(user: User) -> str:
    return signing.dumps({"user_id": user.pk, "role": user.role}, salt=TOKEN_SALT)


def read_access_token(token: str) -> dict:
    return signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)
