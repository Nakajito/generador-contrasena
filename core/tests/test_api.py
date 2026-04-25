"""Integration tests for the /api/v1/generate endpoint."""

from __future__ import annotations

from typing import Any

import pytest
from rest_framework.test import APIClient

from core.services.password import MAX_LENGTH, MIN_LENGTH

URL = "/api/v1/generate"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


def _payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "length": 20,
        "uppercase": True,
        "lowercase": True,
        "numbers": True,
        "symbols": True,
        "exclude_ambiguous": False,
    }
    base.update(overrides)
    return base


@pytest.mark.django_db
class TestGeneratePasswordEndpoint:
    def test_valid_payload_returns_password_and_metadata(self, client: APIClient) -> None:
        response = client.post(URL, data=_payload(), format="json")
        assert response.status_code == 200
        body = response.json()
        assert set(body) >= {"password", "strength", "entropy_bits", "alphabet_size"}
        assert isinstance(body["password"], str)
        assert len(body["password"]) == 20
        assert body["strength"] in {"weak", "fair", "strong", "excellent"}
        assert body["entropy_bits"] > 0

    def test_no_character_classes_returns_400(self, client: APIClient) -> None:
        payload = _payload(uppercase=False, lowercase=False, numbers=False, symbols=False)
        response = client.post(URL, data=payload, format="json")
        assert response.status_code == 400
        assert "non_field_errors" in response.json() or "detail" in response.json()

    def test_length_below_minimum_returns_400(self, client: APIClient) -> None:
        response = client.post(URL, data=_payload(length=MIN_LENGTH - 1), format="json")
        assert response.status_code == 400

    def test_length_above_maximum_returns_400(self, client: APIClient) -> None:
        response = client.post(URL, data=_payload(length=MAX_LENGTH + 1), format="json")
        assert response.status_code == 400

    def test_malformed_json_returns_400(self, client: APIClient) -> None:
        response = client.post(URL, data="not-json", content_type="application/json")
        assert response.status_code == 400

    def test_get_method_not_allowed(self, client: APIClient) -> None:
        response = client.get(URL)
        assert response.status_code == 405

    def test_response_has_no_store_cache_header(self, client: APIClient) -> None:
        response = client.post(URL, data=_payload(), format="json")
        assert "no-store" in response.headers.get("Cache-Control", "")

    def test_exclude_ambiguous_is_honored(self, client: APIClient) -> None:
        from core.services.password import AMBIGUOUS_CHARS

        response = client.post(URL, data=_payload(length=64, exclude_ambiguous=True), format="json")
        assert response.status_code == 200
        pw = response.json()["password"]
        assert not any(c in AMBIGUOUS_CHARS for c in pw)


@pytest.mark.django_db
class TestThrottling:
    """Rate-limit is disabled in the test settings by default.
    Re-enable via override_settings to ensure the 429 path works.
    """

    def test_hits_throttle_after_limit(self) -> None:
        from django.core.cache import cache
        from django.test import override_settings

        overrides = {
            "DEFAULT_THROTTLE_CLASSES": [
                "rest_framework.throttling.AnonRateThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {"anon": "3/min", "generate": "3/min"},
            "DEFAULT_AUTHENTICATION_CLASSES": [],
            "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
            "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
            "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
            "UNAUTHENTICATED_USER": None,
        }

        cache.clear()
        with override_settings(REST_FRAMEWORK=overrides):
            client = APIClient()
            payload = _payload(length=12)
            statuses = [client.post(URL, data=payload, format="json").status_code for _ in range(5)]
        assert 429 in statuses, f"expected 429 among {statuses}"
