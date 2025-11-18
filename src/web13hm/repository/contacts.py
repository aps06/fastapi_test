from typing import List

from fastapi import HTTPException, status

from sqlalchemy import or_
from sqlalchemy.orm import Session

from datetime import date, timedelta

from src.web13hm.database.models import Contacts, User
from src.web13hm.shemas import ContactModel, ResponseContactModel


async def get_Contacts(
    skip: int, limit: int, user: User, db: Session
) -> List[ResponseContactModel]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[ResponseContactModel]
    """
    contacts = (
        db.query(Contacts)
        .filter(Contacts.user_id == user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return contacts


async def get_Contacts_by(
    Contacts_data: int | str, user: User, db: Session
) -> List[ResponseContactModel]:
    """
    Retrieves a contacts with the specified ID, NAME, EMAIL for a specific user.

    :param Contacts_data: The ID, NAME, EMAIL of the contacts to retrieve.
    :type Contacts_data: str
    :param user: The user to retrieve the contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException:  if contact does not exist.
    :return: The contacts with the specified ID, NAME, EMAIL.
    :rtype: List[ResponseContactModel]
    """
    conditions = [
        Contacts.name == Contacts_data,
        Contacts.last_name == Contacts_data,
        Contacts.email == Contacts_data,
    ]

    if Contacts_data.isdigit():
        conditions.append(Contacts.id == int(Contacts_data))

    contacts = (
        db.query(Contacts).filter(or_(*conditions), Contacts.user_id == user.id).all()
    )

    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contacts


async def birthday_by_7_day(
    skip: int,
    limit: int,
    db: Session,
    current_user: User,
) -> List[ResponseContactModel]:
    """
    Retrieves a list of contacts with birthday by 7 day for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param current_user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[ResponseContactModel]
    """
    date_by_7_day = date.today() + timedelta(days=7)
    print("today-{date.today()}, 7 {date_by_7_day}")
    contacts = (
        db.query(Contacts)
        .filter(Contacts.birthday <= date_by_7_day, Contacts.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return contacts


async def create_contact(body: ContactModel, db: Session, current_user: User):
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param current_user: The user to create the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contacts
    """
    new_contact = Contacts(
        name=body.name,
        last_name=body.last_name,
        email=body.email,
        number=body.number,
        birthday=body.birthday,
        user_id=current_user.id,
        extra_data=body.extra_data,
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


async def delete_contact(
    contact_id: int,
    db: Session,
    current_user: User,
):
    """
    Delete a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException:  if contact does not exist.
    :return: The delete contact, or raise exception if it does not exist.
    :rtype: Dict[str, bool]
    """
    contact = (
        db.query(Contacts)
        .filter(Contacts.id == contact_id, Contacts.user_id == current_user.id)
        .first()
    )
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"ok": True}


async def update_contact(
    contact_id: int, body: ContactModel, db: Session, current_user: User
):
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param current_user: The user to update the contact for.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :raises HTTPException:  if contact does not exist.
    :return: The updated contact, or raise exception if it does not exist.
    :rtype: Contacts
    """
    contacts_db = (
        db.query(Contacts)
        .filter(Contacts.id == contact_id, Contacts.user_id == current_user.id)
        .first()
    )
    if not contacts_db:
        raise HTTPException(status_code=404, detail="Contact not found")
    contacts_db.name = body.name
    contacts_db.last_name = body.last_name
    contacts_db.email = body.email
    contacts_db.number = body.number
    contacts_db.birthday = body.birthday
    contacts_db.extra_data = body.extra_data
    db.commit()
    db.refresh(contacts_db)
    return contacts_db
