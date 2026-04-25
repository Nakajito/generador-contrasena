"""Secure password generator service (pure domain logic)."""

from __future__ import annotations

import secrets
import string
from dataclasses import dataclass

MIN_LENGTH: int = 8
MAX_LENGTH: int = 128

UPPERCASE: str = string.ascii_uppercase
LOWERCASE: str = string.ascii_lowercase
DIGITS: str = string.digits
SYMBOLS: str = "!@#$%^&*()-_=+[]{};:,.<>?/~"

# Characters that look alike in common fonts.
AMBIGUOUS_CHARS: frozenset[str] = frozenset("Il1O0o`'\"B8S5Z2")


class PolicyError(ValueError):
    """Raised when a PasswordPolicy cannot be satisfied."""


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    length: int = 16
    uppercase: bool = True
    lowercase: bool = True
    numbers: bool = True
    symbols: bool = True
    exclude_ambiguous: bool = False

    def __post_init__(self) -> None:
        if not MIN_LENGTH <= self.length <= MAX_LENGTH:
            raise PolicyError(
                f"length must be between {MIN_LENGTH} and {MAX_LENGTH}, got {self.length}"
            )
        if not any((self.uppercase, self.lowercase, self.numbers, self.symbols)):
            raise PolicyError("at least one character class must be enabled")

    def pools(self) -> list[str]:
        """Return active character pools after ambiguous filtering."""
        mapping = (
            (self.uppercase, UPPERCASE),
            (self.lowercase, LOWERCASE),
            (self.numbers, DIGITS),
            (self.symbols, SYMBOLS),
        )
        pools = [chars for enabled, chars in mapping if enabled]
        if self.exclude_ambiguous:
            pools = ["".join(c for c in pool if c not in AMBIGUOUS_CHARS) for pool in pools]
            if any(not pool for pool in pools):
                raise PolicyError("ambiguous-char exclusion emptied a required character class")
        return pools


def generate_password(policy: PasswordPolicy) -> str:
    """Generate a cryptographically secure password satisfying ``policy``.

    Uses ``secrets.SystemRandom`` for all random choices.
    """
    rng = secrets.SystemRandom()
    pools = policy.pools()

    # Guarantee at least one char from every enabled pool.
    chars: list[str] = [rng.choice(pool) for pool in pools]

    combined = "".join(pools)
    remaining = policy.length - len(chars)
    chars.extend(rng.choice(combined) for _ in range(remaining))

    # Durstenfeld shuffle with SystemRandom so position of guaranteed chars is random.
    for i in range(len(chars) - 1, 0, -1):
        j = rng.randrange(i + 1)
        chars[i], chars[j] = chars[j], chars[i]

    return "".join(chars)
