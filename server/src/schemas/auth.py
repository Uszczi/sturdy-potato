from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas._coercions import strip_if_str


class TokenObtainPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: object) -> object:
        return strip_if_str(value)


class TokenRefresh(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh: str


class TokenPair(BaseModel):
    access: str
    refresh: str


class AccessToken(BaseModel):
    access: str
