import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

from src.web13hm.database.models import User
from src.web13hm.shemas import UserModel
from src.web13hm.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUserRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.db = MagicMock(spec=Session)

    async def test_get_user_by_email_found(self):
        user = User(id=1, email="test@example.com")
        self.db.query().filter().first.return_value = user

        result = await get_user_by_email("test@example.com", self.db)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.db.query().filter().first.return_value = None

        result = await get_user_by_email("none@example.com", self.db)
        self.assertIsNone(result)

    @patch("src.web13hm.repository.users.Gravatar")
    async def test_create_user(self, mock_gravatar):
        mock_gravatar.return_value.get_image.return_value = "http://avatar"

        body = UserModel(username="test@example.com", password="pass12345")

        new_user = User(
            id=1, email=body.username, password=body.password, avatar="http://avatar"
        )
        self.db.add.return_value = None
        self.db.commit.return_value = None
        self.db.refresh.return_value = None

        with patch("src.web13hm.repository.users.User", return_value=new_user):
            result = await create_user(body, self.db)

        self.assertEqual(result.email, body.username)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, "http://avatar")

    async def test_update_token(self):
        user = User(id=1, refresh_token=None)

        await update_token(user=user, token="NEW_TOKEN", db=self.db)

        self.assertEqual(user.refresh_token, "NEW_TOKEN")
        self.db.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(id=1, email="test@example.com", confirmed=False)
        self.db.query().filter().first.return_value = user

        await confirmed_email("test@example.com", self.db)

        self.assertTrue(user.confirmed)
        self.db.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(id=1, email="test@example.com", avatar=None)
        self.db.query().filter().first.return_value = user

        result = await update_avatar("test@example.com", "http://newavatar", self.db)

        self.assertEqual(result.avatar, "http://newavatar")
        self.db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
