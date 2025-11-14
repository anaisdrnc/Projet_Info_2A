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


def test_create_ok(service):
    # Act
    user = service.create_user(
        username="Martin",
        password="Caraibe35",
        firstname="Martin",
        lastname="Legendre",
        email="martin.legendre@gmail.com",
    )

    # Assert
    assert user is not None
    assert isinstance(user, User)
    assert user.id_user is not None  # id généré
    assert user.user_name == "Martin"
    assert user.email == "martin.legendre@gmail.com"

    # Vérifie que le mot de passe a bien été hashé et qu’il y a un salt
    assert user.password != "Caraibe35"
    assert user.salt is not None