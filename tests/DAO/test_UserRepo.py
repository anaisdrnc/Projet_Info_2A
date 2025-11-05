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


def test_add_user_ok(dao):
    user = User(username = "user_test", firstname = "User", lastname = "Test", password = "1234password", "user.test@gmail.com")
    created = dao.add_user(user)
    assert created != False 
    assert created > 0

def test_add_user_ko(dao):
    "test if the user already exist"
    user = User(username = "user_test", firstname = "User", lastname = "Test", password = "1234password", "user.test@gmail.com")
    created = dao.add_user(user)
    assert created != False
    #create a second type
    created2 = dao.add_user(user)
    assert created2 == False

