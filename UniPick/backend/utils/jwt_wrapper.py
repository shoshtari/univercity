import datetime
from typing import Optional, cast

import jwt

import common.configs as configs


def create_token(user_id: int, ttl: Optional[int] = None) -> str:
    if ttl is None:
        ttl = configs.JWT_TTL
    iat = int(datetime.datetime.now().timestamp())
    return jwt.encode(
        {"user_id": user_id, "iat": iat, "exp": configs.JWT_TTL + iat},
        key=configs.JWT_ENCRYPT_KEY,
        algorithm=configs.JWT_ALGORITHM,
    )


def parse_token(token: str) -> int:
    payload = jwt.decode(
        token, key=configs.JWT_DECRYPT_KEY, algorithms=configs.JWT_ALGORITHM
    )
    return cast(int, payload["user_id"])
