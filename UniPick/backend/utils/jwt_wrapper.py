from typing import Optional

import jwt

import common.configs as configs


def create_token(user_id: int, ttl: Optional[int] = None) -> str:
    if ttl is None:
        ttl = configs.JWT_TTL
    return jwt.encode(
        {"user_id": user_id, "ttl": configs.JWT_TTL},
        key=configs.JWT_ENCRYPT_KEY,
        algorithm=configs.JWT_ALGORITHM,
    )


def parse_token(token: str) -> int:
    raise NotImplementedError
