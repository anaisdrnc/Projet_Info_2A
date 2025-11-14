from unittest.mock import MagicMock, patch

import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.UserService import UserService
from utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database avant chaque test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO pour tests"""
    return UserRepo(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service basé sur le DAO"""
    return UserService(user_repo=dao)
