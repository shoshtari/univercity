import datetime

import bcrypt
import structlog
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    insert,
    select,
)

from db.engine import ENGINE

logger = structlog.getLogger()

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(255), nullable=False, unique=True),
    Column("password", String(255), nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.now),
    Column(
        "updated_at",
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    ),
)


class UserRepository:

    @staticmethod
    def migrate() -> None:
        metadata.create_all(ENGINE)
        logger.info("user table migration done")

    @classmethod
    def create(cls, username: str, password: str) -> int:
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=16),
        ).decode("utf-8")

        stmt = (
            insert(user)
            .values(username=username, password=hashed_password)
            .returning(user.c.id)
        )

        with ENGINE.begin() as conn:
            result = conn.execute(stmt)
            user_id: int = result.scalar_one()

        logger.info("user created", username=username, user_id=user_id)
        return user_id

    @classmethod
    def check_password(cls, username: str, password: str) -> tuple[bool, int]:
        stmt = select(user.c.password, user.c.id).where(user.c.username == username)

        with ENGINE.connect() as conn:
            result = conn.execute(stmt).fetchone()

        if result is None:
            return False, 0

        stored_hash: bytes = result.password.encode("utf-8")
        is_correct = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        return is_correct, result.id
