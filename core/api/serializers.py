"""DRF serializer translating JSON payload into a PasswordPolicy."""

from __future__ import annotations

from typing import Any

from rest_framework import serializers

from core.services.password import MAX_LENGTH, MIN_LENGTH, PasswordPolicy, PolicyError


class PasswordRequestSerializer(serializers.Serializer[dict[str, Any]]):
    length = serializers.IntegerField(min_value=MIN_LENGTH, max_value=MAX_LENGTH)
    uppercase = serializers.BooleanField(default=True)
    lowercase = serializers.BooleanField(default=True)
    numbers = serializers.BooleanField(default=True)
    symbols = serializers.BooleanField(default=True)
    exclude_ambiguous = serializers.BooleanField(default=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        try:
            PasswordPolicy(**attrs)
        except PolicyError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return attrs

    def to_policy(self) -> PasswordPolicy:
        assert self.validated_data is not None
        return PasswordPolicy(**self.validated_data)
