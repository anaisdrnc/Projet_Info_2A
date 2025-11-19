import pytest
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Service.UserService import UserService
from src.Model.User import User
from utils.reset_database import ResetDatabase
from unittest.mock import MagicMock, patch
from src.Service.UserService import UserService
from src.Model.User import User


@pytest.fixture(autouse=True)
def reset_db():
    """Reset la base test avant chaque test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def repo():
    return UserRepo(DBConnector(test=True))


@pytest.fixture
def service(repo):
    return UserService(user_repo=repo)


def test_create_user_ok(service):
    """Création d'utilisateur correcte"""
    user_id = service.create_user(
        username="TestUser",
        password="StrongPass1",
        firstname="Alice",
        lastname="Durand",
        email="alice3@test.com",
    )

    # Vérifie que la fonction renvoie bien un int
    assert isinstance(user_id, int)
    assert user_id > 0

    # Vérifie que l'utilisateur a été correctement créé en base
    user = service.get_user(user_id)
    assert user is not None

    assert user.user_name == "TestUser"
    assert user.first_name == "Alice"
    assert user.last_name == "Durand"
    assert user.email == "alice3@test.com"

    # Le mot de passe doit être stocké hashé
    assert user.password is not None
    assert user.password != "StrongPass1"
    assert len(user.salt) > 0


def test_create_user_weak_password(service):
    """Mot de passe trop faible → doit lever une Exception."""
    with pytest.raises(Exception):
        service.create_user(
            username="Weak",
            password="123",
            firstname="Bob",
            lastname="Martin",
            email="bob@test.com",
        )


def test_get_user(service):
    """Récupération d'un utilisateur existant"""
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



def test_is_username_taken(service):
    """Test du check sur les usernames"""
    service.create_user("UserX", "StrongPass1", "A", "B", "a@b.com")

    assert service.is_username_taken("UserX") is True
    assert service.is_username_taken("UnknownUser") is False



@patch("src.Service.UserService.validate_username_password", return_value=True)
def test_change_password_ok(mock_validate):
    """
    Cas OK :
    - ancien mot de passe bon
    - update_user renvoie True
    """
    service = UserService(user_repo=MagicMock())

    # Simuler un user existant
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

    # update_user OK
    service.user_repo.update_user = MagicMock(return_value=True)

    result = service.change_password("john", "old", "new123")

    assert result is True
    mock_validate.assert_called_once_with(username="john", password="old", user_repo=service.user_repo)
    service.user_repo.update_user.assert_called_once()


@patch("src.Service.UserService.validate_username_password", return_value=False)
def test_change_password_wrong_password(mock_validate):
    """
    Cas KO :
    - ancien mot de passe incorrect → retourne False
    - rien d'autre n'est appelé
    """
    service = UserService(user_repo=MagicMock())

    # Aucun user réel n'est nécessaire ici
    service.user_repo.get_by_username = MagicMock()

    result = service.change_password("john", "wrongOld", "new123")

    assert result is False
    mock_validate.assert_called_once_with(username="john", password="wrongOld", user_repo=service.user_repo)


def test_change_password_update_exception():
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

    # Ancien mot de passe correct → on patch validate_username_password
    with patch("src.Service.UserService.validate_username_password", return_value=True):
        # update → lève une exception
        service.user_repo.update_user = MagicMock(side_effect=Exception("DB error"))

        # Vérifie que l’exception remonte
        with pytest.raises(Exception) as excinfo:
            service.change_password("john", "old123", "new123")

        assert str(excinfo.value) == "DB error"