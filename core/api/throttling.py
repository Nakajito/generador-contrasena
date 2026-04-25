"""Scoped throttle for the generate endpoint."""

from rest_framework.settings import api_settings
from rest_framework.throttling import AnonRateThrottle


class GenerateRateThrottle(AnonRateThrottle):
    scope = "generate"

    def get_rate(self) -> str:
        # Re-read on every request so override_settings takes effect in tests
        # (DRF caches THROTTLE_RATES at class-definition time).
        rate = api_settings.DEFAULT_THROTTLE_RATES[self.scope]
        return str(rate)
