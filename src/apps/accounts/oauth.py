import json
import logging
import secrets
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings

from apps.accounts.models import PetOwnerProfile, User, UserRole
from apps.accounts.tokens import create_oauth_state, read_oauth_state
from apps.memberships.services import assign_default_pet_owner_membership

logger = logging.getLogger(__name__)

GOOGLE_OAUTH_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_OAUTH_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleOAuthConfigurationError(RuntimeError):
    pass


class GoogleOAuthExchangeError(RuntimeError):
    pass


def google_oauth_is_configured() -> bool:
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET and settings.SITE_URL)


def build_google_callback_url(site_url: str | None = None) -> str:
    base_url = (site_url or settings.SITE_URL).rstrip("/")
    return f"{base_url}/api/v1/accounts/oauth/google/callback/"


def build_google_oauth_start_url(next_path: str = "/ingresar", site_url: str | None = None) -> str:
    if not google_oauth_is_configured():
        raise GoogleOAuthConfigurationError("Google OAuth is not configured.")

    query = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": build_google_callback_url(site_url),
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "prompt": "select_account",
            "state": create_oauth_state("google", next_path=next_path),
        }
    )
    return f"{GOOGLE_OAUTH_AUTHORIZE_URL}?{query}"


def _post_json(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str, access_token: str) -> dict:
    request = Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def exchange_google_code_for_profile(
    *,
    code: str,
    state_token: str,
    site_url: str | None = None,
) -> tuple[dict, dict]:
    if not google_oauth_is_configured():
        raise GoogleOAuthConfigurationError("Google OAuth is not configured.")

    state = read_oauth_state(state_token)
    if state.get("provider") != "google":
        raise GoogleOAuthExchangeError("OAuth state is invalid.")

    token_payload = _post_json(
        GOOGLE_OAUTH_TOKEN_URL,
        {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": build_google_callback_url(site_url),
            "grant_type": "authorization_code",
        },
    )
    access_token = token_payload.get("access_token")
    if not access_token:
        raise GoogleOAuthExchangeError("Google did not return an access token.")

    profile = _get_json(GOOGLE_OAUTH_USERINFO_URL, access_token)
    if not profile.get("email"):
        raise GoogleOAuthExchangeError("Google did not return a usable email.")

    return state, profile


def get_or_create_user_from_google_profile(profile: dict) -> User:
    email = str(profile.get("email", "")).strip().lower()
    if not email:
        raise GoogleOAuthExchangeError("Google profile is missing email.")

    user = User.objects.filter(email__iexact=email).first()
    if user:
        if not user.is_active:
            raise GoogleOAuthExchangeError("This account is inactive.")
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified", "updated_at"])
        return user

    user = User.objects.create_user(
        email=email,
        password=secrets.token_urlsafe(32),
        role=UserRole.PET_OWNER,
        first_name=str(profile.get("given_name") or profile.get("name") or "").strip(),
        last_name=str(profile.get("family_name") or "").strip(),
        email_verified=True,
    )
    # Google ya verificó el correo. Dejamos el perfil del tutor listo para completar luego.
    user.set_unusable_password()
    user.save(update_fields=["password", "updated_at"])

    profile_record = PetOwnerProfile.objects.create(
        user=user,
        phone="",
        address_line="",
        commune="",
        region="Región Metropolitana",
        marketing_opt_in=True,
    )
    assign_default_pet_owner_membership(profile_record)
    logger.info("Created pet owner account from Google OAuth for %s", user.email)
    return user
