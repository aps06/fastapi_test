from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date, datetime


class ContactModel(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    number: str
    birthday: date
    extra_data: str | None = None


class ResponseContactModel(BaseModel):
    id: int
    name: str
    last_name: str
    email: EmailStr
    number: str
    birthday: date
    extra_data: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    username: EmailStr
    password: str


class UserDb(BaseModel):
    id: int
    email: str
    created_at: datetime
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
