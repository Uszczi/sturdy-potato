from pydantic import BaseModel, ConfigDict


class TokenObtainPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class TokenRefresh(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh: str


class TokenPair(BaseModel):
    access: str
    refresh: str


class AccessToken(BaseModel):
    access: str
