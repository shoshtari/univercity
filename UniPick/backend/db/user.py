import datetime
from typing import cast

import bcrypt
import structlog
from sqlalchemy import (
    Column,
    DateTime,
    Engine,
    Integer,
    String,
    Table,
    insert,
    select,
)

from common.errors import InvalidUserPasswordError, UserNotFoundError
from db.engine import METADATA

logger = structlog.getLogger()

# in order to use for avoiding side channel time attack on check password
DEFAULT_HASH = b"$2b$12$ZkuEY3P4fsEsDmRXbN1LI.zmh0A/Avu6WCHDnCRldr.K3GR6o270O"

user = Table(
    "user",
    METADATA,
    Column("id", Integer, primary_key=True),
    Column("username", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column(
        "created_at",
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
    ),
    Column(
        "updated_at",
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
    ),
)


class UserRepository:

    def __init__(self, engine: Engine, bcrypt_rounds: int) -> None:
        self.engine = engine
        self.bcrypt_rounds = bcrypt_rounds

    def create(self, username: str, password: str) -> int:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=self.bcrypt_rounds),
        ).decode("utf-8")

        stmt = (
            insert(user)
            .values(username=username, password=hashed_password)
            .returning(user.c.id)
        )

        with self.engine.begin() as conn:
            result = conn.execute(stmt)
            user_id: int = result.scalar_one()

        logger.info("user created", username=username, user_id=user_id)
        return user_id

    def check_password(self, username: str, password: str) -> int:
        stmt = select(user.c.password, user.c.id).where(user.c.username == username)

        with self.engine.connect() as conn:
            result = conn.execute(stmt).fetchone()

        stored_hash = DEFAULT_HASH
        if result is not None:
            stored_hash = result.password.encode("utf-8")

        is_correct = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        if not is_correct or result is None:
            raise InvalidUserPasswordError

        return cast(int, result.id)

    def get_username_by_id(self, user_id: int) -> str:
        stmt = select(user.c.username).where(user.c.id == user_id)

        with self.engine.connect() as conn:
            result = conn.execute(stmt).fetchone()

        if result is None:
            raise UserNotFoundError

        return cast(str, result.username)
