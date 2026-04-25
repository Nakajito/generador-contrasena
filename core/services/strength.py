"""Password strength evaluation based on Shannon-style entropy."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum

from .password import PasswordPolicy


class StrengthLevel(IntEnum):
    WEAK = 1
    FAIR = 2
    STRONG = 3
    EXCELLENT = 4

    @property
    def label(self) -> str:
        return self.name.lower()


# Entropy thresholds in bits.
_WEAK_MAX = 40.0
_FAIR_MAX = 60.0
_STRONG_MAX = 80.0


@dataclass(frozen=True, slots=True)
class StrengthResult:
    level: StrengthLevel
    entropy_bits: float
    alphabet_size: int


def entropy_bits(length: int, alphabet_size: int) -> float:
    """Return ``length * log2(alphabet_size)``; 0 when either input is <= 0."""
    if length <= 0 or alphabet_size <= 0:
        return 0.0
    return float(length) * math.log2(alphabet_size)


def _classify(bits: float) -> StrengthLevel:
    if bits < _WEAK_MAX:
        return StrengthLevel.WEAK
    if bits < _FAIR_MAX:
        return StrengthLevel.FAIR
    if bits < _STRONG_MAX:
        return StrengthLevel.STRONG
    return StrengthLevel.EXCELLENT


def evaluate_strength(policy: PasswordPolicy) -> StrengthResult:
    alphabet_size = sum(len(pool) for pool in policy.pools())
    bits = entropy_bits(policy.length, alphabet_size)
    return StrengthResult(level=_classify(bits), entropy_bits=bits, alphabet_size=alphabet_size)
