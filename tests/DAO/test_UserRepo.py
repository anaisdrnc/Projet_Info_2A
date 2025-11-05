from typing import TYPE_CHECKING, Literal, Optional, Union

from src.DAO.UserRepo import UserRepo

if TYPE_CHECKING:
    from src.Model.User import User
import os
import pytest
from dotenv import load_dotenv
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.DBConnector import DBConnector

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    user_dao = UserRepo()
    user_dao.db_connector = DBConnector(test=True)
    return user_dao

def unique_username(base="admin"):
    """Générer un username unique pour éviter les collisions entre tests"""
    return f"{base}_{datetime.utcnow().timestamp()}"


def test_add_user_ok(dao):
    username = unique_username('user_test')
    user = User(user_name = username , first_name = "User", last_name = "Test", password = "1234password", email = "user.test@gmail.com")
    created = dao.add_user(user)
    assert created != None
    assert created > 0

def test_add_user_ko(dao):
    "test if the user already exist"
    username = unique_username('user_test')
    user = User(user_name = username , first_name = "User", last_name = "Test", password = "1234password", email = "user.test@gmail.com")
    created = dao.add_user(user)
    assert created != None
    #create a second type
    created2 = dao.add_user(user)
    assert created2 == None

def test_get_by_id(dao):
    username = unique_username('user_test')
    user = User(user_name = username , first_name = "User", last_name = "Test", password = "1234password", email ="user.test@gmail.com")
    created = UserRepo.add_user(user)
    assert created != None
    user2 = UserRepo.get_by_id(created)
    assert user2 is not None
    assert user2.user_name == username
    assert user2.first_name == "User"
    assert user2.last_name == "Test"

def test_get_by_username(dao):
    username = unique_username('user_test')
    user = User(user_name = username , first_name = "User", last_name = "Test", password = "1234password", email ="user.test@gmail.com")
    created = UserRepo.add_user(user)
    assert created != None
    user2 = UserRepo.get_by_username(username)
    assert user2 is not None
    assert user2.user_name == username
    assert user2.first_name == "User"
    assert user2.last_name == "Test"



