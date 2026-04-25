"""DRF views for the password-generation API."""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.services.password import generate_password
from core.services.strength import evaluate_strength

from .serializers import PasswordRequestSerializer
from .throttling import GenerateRateThrottle


class GeneratePasswordView(APIView):
    """POST /api/v1/generate — stateless password generation."""

    throttle_classes = [GenerateRateThrottle]  # noqa: RUF012
    http_method_names = ["post", "options"]  # noqa: RUF012

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = PasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        policy = serializer.to_policy()
        password = generate_password(policy)
        strength = evaluate_strength(policy)

        response = Response(
            {
                "password": password,
                "strength": strength.level.label,
                "entropy_bits": round(strength.entropy_bits, 2),
                "alphabet_size": strength.alphabet_size,
            },
            status=status.HTTP_200_OK,
        )
        response["Cache-Control"] = "no-store"
        response["Pragma"] = "no-cache"
        return response
