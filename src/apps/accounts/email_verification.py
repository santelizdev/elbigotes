import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

from apps.accounts.models import User
from apps.accounts.tokens import create_email_verification_token, read_email_verification_token

logger = logging.getLogger(__name__)

BREVO_SEND_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"


def email_verification_is_configured() -> bool:
    return bool(settings.BREVO_API_KEY and settings.BREVO_SENDER_EMAIL and settings.SITE_URL)


def build_email_verification_url(user: User) -> str:
    token = create_email_verification_token(user)
    return f"{settings.SITE_URL}/api/v1/accounts/verify-email/?token={token}"


def send_verification_email(user: User) -> bool:
    if settings.TESTING:
        return False

    if not email_verification_is_configured():
        logger.info("Skipping verification email for %s because Brevo is not configured.", user.email)
        return False

    verification_url = build_email_verification_url(user)
    payload = {
        "sender": {
            "email": settings.BREVO_SENDER_EMAIL,
            "name": settings.BREVO_SENDER_NAME,
        },
        "to": [{"email": user.email, "name": user.get_full_name() or user.email}],
        "subject": "Confirma tu cuenta en ElBigotes",
        "htmlContent": (
            "<p>Hola,</p>"
            "<p>Gracias por registrarte en ElBigotes.</p>"
            f"<p>Confirma tu cuenta haciendo clic aquí: <a href=\"{verification_url}\">Confirmar cuenta</a></p>"
            "<p>Si no solicitaste este registro, puedes ignorar este mensaje.</p>"
        ),
        "textContent": (
            "Hola.\n\n"
            "Gracias por registrarte en ElBigotes.\n"
            f"Confirma tu cuenta aquí: {verification_url}\n\n"
            "Si no solicitaste este registro, ignora este mensaje."
        ),
    }
    if settings.BREVO_REPLY_TO:
        payload["replyTo"] = {"email": settings.BREVO_REPLY_TO, "name": settings.BREVO_SENDER_NAME}

    request = Request(
        BREVO_SEND_EMAIL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=15) as response:
            response.read()
        logger.info("Sent verification email to %s", user.email)
        return True
    except (HTTPError, URLError, TimeoutError) as exc:
        logger.exception("Failed to send Brevo verification email to %s: %s", user.email, exc)
        return False


def verify_email_token(token: str) -> User:
    payload = read_email_verification_token(token)
    user = User.objects.get(pk=payload["user_id"], email=payload["email"])
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=["email_verified", "updated_at"])
    return user
