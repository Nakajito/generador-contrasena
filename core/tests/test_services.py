"""TDD unit tests for the password generation service (pure logic)."""

from __future__ import annotations

import math
import re
import string
from collections import Counter

import pytest

from core.services.password import (
    AMBIGUOUS_CHARS,
    MAX_LENGTH,
    MIN_LENGTH,
    PasswordPolicy,
    PolicyError,
    generate_password,
)


class TestPasswordPolicy:
    def test_defaults_produce_all_classes_enabled(self) -> None:
        policy = PasswordPolicy()
        assert policy.length == 16
        assert policy.uppercase is True
        assert policy.lowercase is True
        assert policy.numbers is True
        assert policy.symbols is True
        assert policy.exclude_ambiguous is False

    def test_rejects_length_below_minimum(self) -> None:
        with pytest.raises(PolicyError, match="length"):
            PasswordPolicy(length=MIN_LENGTH - 1)

    def test_rejects_length_above_maximum(self) -> None:
        with pytest.raises(PolicyError, match="length"):
            PasswordPolicy(length=MAX_LENGTH + 1)

    def test_rejects_no_character_classes(self) -> None:
        with pytest.raises(PolicyError, match="at least one"):
            PasswordPolicy(
                uppercase=False,
                lowercase=False,
                numbers=False,
                symbols=False,
            )


class TestGeneratePassword:
    def test_returns_string_of_requested_length(self) -> None:
        policy = PasswordPolicy(length=24)
        pw = generate_password(policy)
        assert isinstance(pw, str)
        assert len(pw) == 24

    def test_respects_boundary_lengths(self) -> None:
        for n in (MIN_LENGTH, 16, MAX_LENGTH):
            assert len(generate_password(PasswordPolicy(length=n))) == n

    def test_contains_at_least_one_of_each_enabled_class(self) -> None:
        policy = PasswordPolicy(length=32)
        pw = generate_password(policy)
        assert any(c.isupper() for c in pw)
        assert any(c.islower() for c in pw)
        assert any(c.isdigit() for c in pw)
        assert re.search(r"[^A-Za-z0-9]", pw) is not None

    def test_only_lowercase_when_others_disabled(self) -> None:
        policy = PasswordPolicy(length=20, uppercase=False, numbers=False, symbols=False)
        pw = generate_password(policy)
        assert pw.islower()
        assert all(c in string.ascii_lowercase for c in pw)

    def test_only_digits_when_others_disabled(self) -> None:
        policy = PasswordPolicy(length=20, uppercase=False, lowercase=False, symbols=False)
        pw = generate_password(policy)
        assert pw.isdigit()

    def test_exclude_ambiguous_removes_ambiguous_characters(self) -> None:
        policy = PasswordPolicy(length=MAX_LENGTH, exclude_ambiguous=True)
        for _ in range(50):
            pw = generate_password(policy)
            assert not any(c in AMBIGUOUS_CHARS for c in pw)

    def test_short_length_with_many_classes_still_includes_each(self) -> None:
        # Minimum length must be enough to satisfy all 4 guaranteed chars.
        policy = PasswordPolicy(length=MIN_LENGTH)
        pw = generate_password(policy)
        assert any(c.isupper() for c in pw)
        assert any(c.islower() for c in pw)
        assert any(c.isdigit() for c in pw)
        assert any(not c.isalnum() for c in pw)

    def test_produces_distinct_outputs(self) -> None:
        policy = PasswordPolicy(length=32)
        sample = {generate_password(policy) for _ in range(200)}
        # Collision probability for 32-char alphabet is negligible.
        assert len(sample) == 200

    def test_distribution_is_uniform_enough(self) -> None:
        """Chi-square goodness-of-fit — loose sanity check, not cryptographic proof."""
        policy = PasswordPolicy(length=64, symbols=False)  # fixed 62-char alphabet
        counter: Counter[str] = Counter()
        for _ in range(400):
            counter.update(generate_password(policy))
        total = sum(counter.values())
        alphabet = string.ascii_letters + string.digits
        expected = total / len(alphabet)
        chi2 = sum(((counter.get(ch, 0) - expected) ** 2) / expected for ch in alphabet)
        # df = 61; critical value at p=0.001 is ~106. Use 150 to avoid flakes.
        assert chi2 < 150, f"chi2={chi2:.2f} suggests biased distribution"

    def test_uses_secrets_systemrandom(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Must pull randomness from SystemRandom, never from the insecure Random."""
        import secrets

        calls: list[str] = []
        real_choice = secrets.SystemRandom.choice

        def tracking_choice(self, seq):  # type: ignore[no-untyped-def]
            calls.append("choice")
            return real_choice(self, seq)

        monkeypatch.setattr(secrets.SystemRandom, "choice", tracking_choice)
        generate_password(PasswordPolicy(length=16))
        assert calls, "generator must delegate to secrets.SystemRandom.choice"

    def test_entropy_contains_no_leaked_placeholder(self) -> None:
        policy = PasswordPolicy(length=32)
        pw = generate_password(policy)
        # Sanity: output never contains control chars or whitespace.
        assert all(c.isprintable() and not c.isspace() for c in pw)


class TestPasswordPolicyMinimumLength:
    def test_min_length_matches_character_class_count(self) -> None:
        """MIN_LENGTH must be >= number of character classes to satisfy guarantees."""
        assert MIN_LENGTH >= 4
        assert int(MIN_LENGTH) == MIN_LENGTH
        assert math.isfinite(MIN_LENGTH)
