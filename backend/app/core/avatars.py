AVATAR_KEYS: tuple[str, ...] = tuple(f"avatar_{index:02d}" for index in range(1, 13))
DEFAULT_AVATAR_KEY = AVATAR_KEYS[0]


def validate_avatar_key(avatar_key: str) -> str:
    if avatar_key not in AVATAR_KEYS:
        raise ValueError("Unsupported avatar")
    return avatar_key
