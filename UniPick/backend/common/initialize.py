"""
This code will initialize dependencies
"""

from dataclasses import dataclass

import db
from common.configs import Settings
from utils.jwt_wrapper import JWTHandler


@dataclass
class DependenciesOutDTO:
    user_repository: db.UserRepository
    course_repository: db.CourseRepository
    user_course_repository: db.UserCourseRepository
    jwt_handler: JWTHandler


def init_dependency(settings: Settings) -> DependenciesOutDTO:
    db_engine = db.create_engine(settings.DATABASE_URL)
    db.migrate(db_engine)
    user_repository = db.UserRepository(db_engine, bcrypt_rounds=settings.BCRYPT_ROUNDS)
    course_repository = db.CourseRepository(db_engine)
    user_course_repository = db.UserCourseRepository(db_engine)
    jwt_handler = JWTHandler(
        encrypt_key=settings.JWT.ENCRYPT_KEY,
        decrypt_key=settings.JWT.DECRYPT_KEY,
        algorithm=settings.JWT.ALGORITHM,
        ttl=settings.JWT.TTL,
    )

    return DependenciesOutDTO(
        user_repository=user_repository,
        course_repository=course_repository,
        user_course_repository=user_course_repository,
        jwt_handler=jwt_handler,
    )
