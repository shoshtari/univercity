import datetime
from typing import Optional, cast

import jwt


class JWTHandler:
    def __init__(
        self, encrypt_key: str, decrypt_key: str, algorithm: str, ttl: int
    ) -> None:
        self.encrypt_key = encrypt_key
        self.decrypt_key = decrypt_key
        self.algorithm = algorithm
        self.ttl = ttl

    def create_token(self, user_id: int, ttl: Optional[int] = None) -> str:
        if ttl is None:
            ttl = self.ttl
        iat = int(datetime.datetime.now().timestamp())
        return jwt.encode(
            {"user_id": user_id, "iat": iat, "exp": iat + ttl},
            key=self.encrypt_key,
            algorithm=self.algorithm,
        )

    def parse_token(self, token: str) -> int:
        payload = jwt.decode(token, key=self.decrypt_key, algorithms=[self.algorithm])
        if not isinstance(payload.get("user_id"), int):
            raise jwt.InvalidTokenError("Invalid user_id in token")
        return cast(int, payload["user_id"])
