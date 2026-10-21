class InputError(ValueError):
    """Geçersiz girdi. CLI bunu {"error": ...} JSON'una çevirir (çıkış kodu 2)."""


class UnsupportedFamily(InputError):
    """Bilinmeyen test ailesi (çıkış kodu 3)."""
