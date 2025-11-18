from typing import Union
from sqlalchemy.orm import Session
from libgravatar import Gravatar
from src.web13hm.database.models import User
from src.web13hm.shemas import UserModel


async def get_user_by_email(email, db):
    """
    Retrieves a user with the specified EMAIL.

    :param email: The EMAIL of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The User with the specified EMAIL or None if it does not exist.
    :rtype: User | None
    """
    user: User = db.query(User).filter(User.email == email).first()

    return user


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user.

    :param body: The data for the user to create.
    :type user: UserModel
    :param db: The database session.
    :type db: Session
    :return: The new user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.username)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    try:
        new_user = User(email=body.username, password=body.password, avatar=avatar)
    except Exception as e:
        print(e)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: Union[str, None], db: Session) -> None:
    """
    Update user token.

    :param user: current user
    :type user: User
    :param token: The new token.
    :type token: Union[str, None]
    :param db: The database session.
    :type db: Session
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the user's email.

    :param email: The email of the user to confirm.
    :type email: str
    :param db: The database session.
    :type db: Session
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the user's avatar.

    :param email: The email of the user whose avatar should be updated.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: The updated user instance.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
