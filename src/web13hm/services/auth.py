from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status
from sqlalchemy.orm import Session
from src.web13hm.database.models import User
from src.web13hm.database.db import get_db
from src.web13hm.conf.config import settings

security = HTTPBearer()


class Auth:
    pwd_context = CryptContext(
        schemes=["bcrypt"], bcrypt__ident="2b", deprecated="auto"
    )

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Compares a plain password with a hashed password to check if they match.

        :param plain_password: The plain text password.
        :type plain_password: str
        :param hashed_password: The hashed password.
        :type hashed_password: str
        :return: True if the passwords match, False otherwise.
        :rtype: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hash for a plain password using the bcrypt algorithm.

        :param password: The plain text password.
        :type password: str
        :return: The hashed password.
        :rtype: str
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a JWT access token with a specified expiration time (in seconds).

        :param data: The data to include in the token.
        :type data: dict
        :param expires_delta: The duration (in seconds) for which the token is valid.
        :type expires_delta: Optional[float]
        :return: The encoded access token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Generates a JWT refresh token with a specified expiration time (in seconds).

        :param data: The data to include in the token.
        :type data: dict
        :param expires_delta: The duration (in seconds) for which the token is valid.
        :type expires_delta: Optional[float]
        :return: The encoded refresh token.
        :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_refresh_token

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db),
    ):
        """
        Returns the current user associated with the provided JWT token.

        :param token: The JWT token for which to retrieve the user.
        :type token: str
        :param db: The database session to use.
        :type db: sqlalchemy.orm.Session
        :return: The user associated with the provided token.
        :rtype: dict
        :raises HTTPException: If the token is invalid, the scope is incorrect, or the user cannot be found.
        """
        token = credentials.credentials

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            if payload.get("scope") != "access_token":
                raise credentials_exception
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user: User = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict):
        """
        Generates a JWT email verification token.

        :param data: The data to include in the token.
        :type data: dict
        :return: The encoded email verification token.
        :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
        token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return token

    async def get_email_from_token(self, refresh_token: str):
        """
        Decodes the provided JWT email verification token and returns the associated email.

        :param token: The token to decode.
        :type token: str
        :return: The email associated with the token.
        :rtype: str
        :raises HTTPException: If the token is invalid.
        """
        try:
            payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )


auth_service = Auth()
