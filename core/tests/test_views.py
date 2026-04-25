"""Smoke tests for non-API views."""

from __future__ import annotations

import pytest
from django.test import Client


@pytest.mark.django_db
def test_home_returns_200(client: Client) -> None:
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_healthz_returns_ok(client: Client) -> None:
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
