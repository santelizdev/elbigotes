from django.core import signing

from apps.accounts.models import User

TOKEN_SALT = "accounts.api.token"
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 14
EMAIL_VERIFICATION_SALT = "accounts.email.verification"
EMAIL_VERIFICATION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
OAUTH_STATE_SALT = "accounts.oauth.state"
OAUTH_STATE_MAX_AGE_SECONDS = 60 * 10


def create_access_token(user: User) -> str:
    return signing.dumps({"user_id": user.pk, "role": user.role}, salt=TOKEN_SALT)


def read_access_token(token: str) -> dict:
    return signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE_SECONDS)


def create_email_verification_token(user: User) -> str:
    return signing.dumps({"user_id": user.pk, "email": user.email}, salt=EMAIL_VERIFICATION_SALT)


def read_email_verification_token(token: str) -> dict:
    return signing.loads(
        token,
        salt=EMAIL_VERIFICATION_SALT,
        max_age=EMAIL_VERIFICATION_MAX_AGE_SECONDS,
    )


def create_oauth_state(provider: str, next_path: str = "/ingresar") -> str:
    return signing.dumps({"provider": provider, "next_path": next_path}, salt=OAUTH_STATE_SALT)


def read_oauth_state(token: str) -> dict:
    return signing.loads(token, salt=OAUTH_STATE_SALT, max_age=OAUTH_STATE_MAX_AGE_SECONDS)
