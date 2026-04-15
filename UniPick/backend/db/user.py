import datetime
from typing import cast

import bcrypt
import structlog
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Table,
    insert,
    select,
)

import common.configs as configs
from common.errors import InvalidUserPasswordError, UserNotFoundError
from db.engine import METADATA, get_engine

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

    @staticmethod
    def migrate() -> None:
        user.create(get_engine(), checkfirst=True)
        logger.info("user table migration done")

    @classmethod
    def create(cls, username: str, password: str) -> int:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=configs.BCRYPT_ROUNDS),
        ).decode("utf-8")

        stmt = (
            insert(user)
            .values(username=username, password=hashed_password)
            .returning(user.c.id)
        )

        with get_engine().begin() as conn:
            result = conn.execute(stmt)
            user_id: int = result.scalar_one()

        logger.info("user created", username=username, user_id=user_id)
        return user_id

    @classmethod
    def check_password(cls, username: str, password: str) -> int:
        stmt = select(user.c.password, user.c.id).where(user.c.username == username)

        with get_engine().connect() as conn:
            result = conn.execute(stmt).fetchone()

        stored_hash = DEFAULT_HASH
        if result is not None:
            stored_hash = result.password.encode("utf-8")

        is_correct = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        if not is_correct or result is None:
            raise InvalidUserPasswordError

        return cast(int, result.id)

    @classmethod
    def get_username_by_id(cls, user_id: int) -> str:
        stmt = select(user.c.username).where(user.c.id == user_id)

        with get_engine().connect() as conn:
            result = conn.execute(stmt).fetchone()

        if result is None:
            raise UserNotFoundError

        return cast(str, result.username)
