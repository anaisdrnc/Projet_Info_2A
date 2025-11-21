from unittest.mock import MagicMock, patch

import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.UserService import UserService
from src.utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database before each test."""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def repo():
    """UserRepo fixture for tests."""
    return UserRepo(DBConnector(test=True))


@pytest.fixture
def service(repo):
    """UserService fixture based on the repo."""
    return UserService(user_repo=repo)


class TestUserService:
    """Tests for UserService."""

    def test_create_user_ok(self, service):
        """Test: Successfully create a new user."""
        user_id = service.create_user(
            username="TestUser",
            password="StrongPass1",
            firstname="Alice",
            lastname="Durand",
            email="alice3@test.com",
        )
        assert isinstance(user_id, int)
        assert user_id > 0

        user = service.get_user(user_id)
        assert user is not None
        assert user.user_name == "TestUser"
        assert user.first_name == "Alice"
        assert user.last_name == "Durand"
        assert user.email == "alice3@test.com"
        assert user.password != "StrongPass1"
        assert len(user.salt) > 0

    def test_create_user_weak_password(self, service):
        """Test: Creating a user with a weak password raises Exception."""
        with pytest.raises(ValueError):
            service.create_user(
                username="Weak",
                password="123",
                firstname="Bob",
                lastname="Martin",
                email="bob@test.com",
            )

    def test_get_user(self, service):
        """Test: Retrieve an existing user by ID."""
        created = service.create_user(
            username="TestUser",
            password="StrongPass1",
            firstname="Alice",
            lastname="Durand",
            email="alice2@test.com",
        )
        user = service.get_user(created)
        assert user is not None
        assert isinstance(user, User)
        assert user.user_name == "TestUser"

    def test_is_username_taken(self, service):
        """Test: Check whether a username is already taken."""
        service.create_user("UserX", "StrongPass1", "A", "B", "a@b.com")
        assert service.is_username_taken("UserX") is True
        assert service.is_username_taken("UnknownUser") is False

    @patch("src.Service.UserService.validate_username_password", return_value=True)
    def test_change_password_ok(self, mock_validate):
        """Test: Successfully change a user's password."""
        service = UserService(user_repo=MagicMock())
        service.user_repo.get_by_username = MagicMock(
            return_value=User(
                id=1,
                user_name="john",
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                password="OLDHASH",
                salt="SALT",
            )
        )
        service.user_repo.update_user = MagicMock(return_value=True)

        result = service.change_password("john", "old", "newPassword123")

        assert result is True
        mock_validate.assert_called_once_with(username="john", password="old", user_repo=service.user_repo)
        service.user_repo.update_user.assert_called_once()

    @patch("src.Service.UserService.validate_username_password", return_value=False)
    def test_change_password_wrong_password(self, mock_validate):
        """Test: Attempt to change password with incorrect old password returns False."""
        service = UserService(user_repo=MagicMock())
        service.user_repo.get_by_username = MagicMock()

        result = service.change_password("john", "wrongOld", "new123")

        assert result is False
        mock_validate.assert_called_once_with(username="john", password="wrongOld", user_repo=service.user_repo)

    def test_change_password_update_exception(self):
        """Test: Changing password raises exception if update fails."""
        service = UserService(user_repo=MagicMock())
        user_mock = User(
            id=1,
            user_name="john",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            password="OLDHASH",
            salt="SALT",
        )
        service.user_repo.get_by_username = MagicMock(return_value=user_mock)

        with patch("src.Service.UserService.validate_username_password", return_value=True):
            service.user_repo.update_user = MagicMock(side_effect=Exception("DB error"))
            with pytest.raises(Exception) as excinfo:
                service.change_password("john", "old123", "newPassword123")
            assert str(excinfo.value) == "DB error"
