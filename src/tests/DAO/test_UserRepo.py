from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import create_salt
from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_password

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for the test schema"""
    user_dao = UserRepo(db_connector=DBConnector(test=True))
    user_dao.db_connector = DBConnector(test=True)
    return user_dao


def unique_username(base="user"):
    """Generate a unique username to avoid collisions between tests."""
    return f"{base}_{datetime.utcnow().timestamp()}"


class TestUserRepo:
    """Tests for the UserRepo DAO"""

    def test_add_user_ok(self, dao):
        """Successfully add a new user to the database"""
        username = unique_username("user_test")
        salt = create_salt()
        user = User(
            user_name=username,
            first_name="User",
            last_name="Test",
            password=hash_password("1234password", salt),
            email="user.test1@gmail.com",
            salt=salt,
        )
        created = dao.add_user(user)
        assert created is not None
        assert created > 0

    def test_add_user_ko(self, dao):
        """Adding a user that already exists should fail"""
        username = unique_username("user_test")
        salt = create_salt()
        user = User(
            user_name=username,
            first_name="User",
            last_name="Test",
            password="1234password",
            email="user.test2@gmail.com",
            salt=salt,
        )
        created = dao.add_user(user)
        assert created is not None
        created2 = dao.add_user(user)
        assert created2 is None

    def test_get_by_id_ok(self, dao):
        """Retrieve an existing user by their ID"""
        username = unique_username("user_test")
        salt = create_salt()
        user = User(
            user_name=username,
            first_name="User",
            last_name="Test",
            password="1234password",
            email="user.test3@gmail.com",
            salt=salt,
        )
        created = dao.add_user(user=user)
        assert created is not None
        user2 = dao.get_by_id(created)
        assert user2 is not None
        assert user2.user_name == username
        assert user2.first_name == "User"
        assert user2.last_name == "Test"

    def test_get_by_id_ko(self, dao):
        """Attempt to retrieve a non-existent user by ID should return None"""
        retrieved = dao.get_by_id(10000)
        assert retrieved is None

    def test_get_by_username_ok(self, dao):
        """Retrieve an existing user by their username successfully"""
        username = unique_username("user_test")
        salt = create_salt()
        user = User(
            user_name=username,
            first_name="User",
            last_name="Test",
            password="1234password",
            email="user.test4@gmail.com",
            salt=salt,
        )
        created = dao.add_user(user)
        assert created is not None
        user2 = dao.get_by_username(username)
        assert user2 is not None
        assert user2.user_name == username
        assert user2.first_name == "User"
        assert user2.last_name == "Test"

    def test_delete_user_ok(self, dao):
        """Successfully delete a user by their ID"""
        username = unique_username("user_test")
        salt = create_salt()
        user = User(
            user_name=username,
            first_name="User",
            last_name="Test",
            password="1234password",
            email="user.test5@gmail.com",
            salt=salt,
        )
        created = dao.add_user(user)
        assert created is not None
        deleted = dao.delete_user(created)
        assert deleted
        retrieved = dao.get_by_id(created)
        assert retrieved is None
