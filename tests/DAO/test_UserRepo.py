from typing import TYPE_CHECKING, Literal, Optional, Union

from src.DAO.UserRepo import UserRepo


from src.Model.User import User
import os
import pytest
from dotenv import load_dotenv
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from datetime import datetime
from src.DAO.DBConnector import DBConnector
from src.Service.PasswordService import create_salt

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    user_dao = UserRepo(db_connector=DBConnector(test=True))
    user_dao.db_connector = DBConnector(test=True)
    return user_dao


def unique_username(base="admin"):
    """Générer un username unique pour éviter les collisions entre tests"""
    return f"{base}_{datetime.utcnow().timestamp()}"


def test_add_user_ok(dao):
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


def test_add_user_ko(dao):
    "test if the user already exist"
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
    assert created != None
    # create a second type
    created2 = dao.add_user(user)
    assert created2 == None


def test_get_by_id_ok(dao):
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
    assert created != None
    user2 = dao.get_by_id(created)
    assert user2 is not None
    assert user2.user_name == username
    assert user2.first_name == "User"
    assert user2.last_name == "Test"


def test_get_by_id_ko(dao):
    retrieved = dao.get_by_id(10000)
    assert retrieved == None


def test_get_by_username_ok(dao):
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
    assert created != None
    user2 = dao.get_by_username(username)
    assert user2 is not None
    assert user2.user_name == username
    assert user2.first_name == "User"
    assert user2.last_name == "Test"


def test_delete_user_ok(dao):
    "test if we can delete user with their id"
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
    assert created != None
    retrieved = dao.delete_user(created)
    assert retrieved
    retrieved = dao.get_by_id(created)
    assert retrieved == None


"""def test_get_all_users_ok(dao):
    username1 = unique_username('list_username1')
    username2 = unique_username('list_username2')
    user1 = User(user_name = username1, last_name = "Test1", first_name = "User1", password = '123password', email = "user1.test@gmail.com")
    user2 = User(user_name = username2, last_name = "Test2", first_name = "User2", password = "234password", email = "user2.test@gmail.com")
    id1 = dao.add_user(user1)
    id2 = dao.add_user(user2)
    list_users = dao.get_all_users()
    assert user1 in list_users
    assert user2 in list_users"""
