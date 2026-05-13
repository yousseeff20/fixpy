"""i18n sub-package — language string lookup."""

from __future__ import annotations

from .ar import STRINGS as AR_STRINGS
from .en import STRINGS as EN_STRINGS

_CATALOGUES: dict[str, dict[str, str]] = {
    "en": EN_STRINGS,
    "ar": AR_STRINGS,
}


def get_strings(lang: str = "en") -> dict[str, str]:
    """Return the string catalogue for *lang*, falling back to English."""
    return _CATALOGUES.get(lang, EN_STRINGS)


__all__ = ["get_strings"]
