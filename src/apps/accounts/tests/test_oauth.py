from urllib.parse import parse_qs, urlparse

import pytest
from django.test import override_settings

from apps.accounts.oauth import build_google_callback_url, build_google_oauth_start_url


@pytest.mark.django_db
@override_settings(
    GOOGLE_CLIENT_ID="google-client-id",
    GOOGLE_CLIENT_SECRET="google-client-secret",
    SITE_URL="https://app.elbigotes.cl",
)
def test_google_oauth_uses_public_site_url_for_callback():
    callback_url = build_google_callback_url()

    assert callback_url == "https://app.elbigotes.cl/api/v1/accounts/oauth/google/callback/"

    start_url = build_google_oauth_start_url(next_path="/mi-cuenta")
    parsed = urlparse(start_url)
    query = parse_qs(parsed.query)

    assert query["redirect_uri"] == [callback_url]
