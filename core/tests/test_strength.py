"""TDD tests for password strength / entropy calculation."""

from __future__ import annotations

import math

import pytest

from core.services.password import (
    AMBIGUOUS_CHARS,
    DIGITS,
    LOWERCASE,
    SYMBOLS,
    UPPERCASE,
    PasswordPolicy,
)
from core.services.strength import StrengthLevel, entropy_bits, evaluate_strength


class TestEntropyBits:
    def test_zero_length_is_zero_entropy(self) -> None:
        assert entropy_bits(length=0, alphabet_size=62) == 0.0

    def test_zero_alphabet_is_zero_entropy(self) -> None:
        assert entropy_bits(length=16, alphabet_size=0) == 0.0

    def test_matches_formula(self) -> None:
        assert entropy_bits(length=20, alphabet_size=94) == pytest.approx(
            20 * math.log2(94), rel=1e-9
        )

    def test_longer_is_stronger(self) -> None:
        assert entropy_bits(32, 62) > entropy_bits(16, 62)

    def test_bigger_alphabet_is_stronger(self) -> None:
        assert entropy_bits(16, 94) > entropy_bits(16, 26)


class TestEvaluateStrength:
    @pytest.mark.parametrize(
        ("policy", "expected_min_level"),
        [
            (PasswordPolicy(length=8, symbols=False, numbers=False), StrengthLevel.WEAK),
            (PasswordPolicy(length=12), StrengthLevel.FAIR),
            (PasswordPolicy(length=16), StrengthLevel.STRONG),
            (PasswordPolicy(length=32), StrengthLevel.EXCELLENT),
        ],
    )
    def test_level_scales_with_length(
        self, policy: PasswordPolicy, expected_min_level: StrengthLevel
    ) -> None:
        result = evaluate_strength(policy)
        assert result.level.value >= expected_min_level.value

    def test_returns_entropy_bits_and_alphabet_size(self) -> None:
        policy = PasswordPolicy(length=16)
        result = evaluate_strength(policy)
        assert result.entropy_bits > 0
        assert result.alphabet_size == len(UPPERCASE + LOWERCASE + DIGITS + SYMBOLS)

    def test_alphabet_shrinks_with_exclude_ambiguous(self) -> None:
        full = evaluate_strength(PasswordPolicy(length=16))
        filtered = evaluate_strength(PasswordPolicy(length=16, exclude_ambiguous=True))
        assert filtered.alphabet_size < full.alphabet_size
        ambiguous_count = sum(
            1 for c in (UPPERCASE + LOWERCASE + DIGITS + SYMBOLS) if c in AMBIGUOUS_CHARS
        )
        assert full.alphabet_size - filtered.alphabet_size == ambiguous_count

    def test_single_class_has_smaller_alphabet(self) -> None:
        only_digits = evaluate_strength(
            PasswordPolicy(length=16, uppercase=False, lowercase=False, symbols=False)
        )
        assert only_digits.alphabet_size == len(DIGITS)
