"""
API schemas for auth apis
"""

from pydantic import BaseModel, Field


class UserSignupIn(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserSignupOut(BaseModel):
    id: int
    username: str


class UserLoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserLoginOut(BaseModel):
    access_token: str
    ttl: int


class GetMeOut(BaseModel):
    id: int
    username: str
