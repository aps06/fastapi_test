import unittest
from unittest.mock import MagicMock
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from datetime import date
from src.web13hm.database.models import User, Contacts
from src.web13hm.shemas import ContactModel
from src.web13hm.repository.contacts import (
    get_Contacts,
    get_Contacts_by,
    create_contact,
    delete_contact,
    update_contact,
    birthday_by_7_day,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_Contacts(self):
        contacts = [Contacts(), Contacts(), Contacts()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_Contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_found(self):
        contacts = Contacts()
        self.session.query().filter().all.return_value = contacts
        result = await get_Contacts_by(Contacts_data='1', user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_not_found(self):
        self.session.query().filter().all.return_value = []
        with self.assertRaises(HTTPException) as context:
            await get_Contacts_by(
                Contacts_data='999',
                user=self.user,
                db=self.session,
            )
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Not found")

    async def test_create_contact(self):
        body = ContactModel(name='test_name',
                            last_name='test_last_name',
                            email='test3mail@gmail.com',
                            number='test_number',
                            birthday=date.today(),
                            extra_data='test_extra_data')
        result = await create_contact(body=body, current_user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.number, body.number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.extra_data, body.extra_data)
        self.assertTrue(hasattr(result, "id"))

    async def test_delete_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, current_user=self.user, db=self.session)
        self.assertEqual(result, {'ok': True})

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as context:
            await delete_contact(
                contact_id=67,
                current_user=self.user,
                db=self.session,
            )
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Contact not found")

    async def test_update_contact_found(self):
        body = ContactModel(
            name="test_name2",
            last_name="test_last_name",
            email="test3mail@gmail.com",
            number="test_number",
            birthday=date.today(),
            extra_data="test_extra_data",
        )
        contact = ContactModel(
            name="test_name",
            last_name="test_last_name",
            email="test3mail@gmail.com",
            number="test_number",
            birthday=date.today(),
            extra_data="test_extra_data",
        )
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(
            contact_id=1, body=body, current_user=self.user, db=self.session
        )
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        body = ContactModel(
            name="test_name2",
            last_name="test_last_name",
            email="test3mail@gmail.com",
            number="test_number",
            birthday=date.today(),
            extra_data="test_extra_data")
        with self.assertRaises(HTTPException) as context:
            await update_contact(
            contact_id=99, body=body, current_user=self.user, db=self.session
        )
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Contact not found")


if __name__ == "__main__":
    unittest.main()
