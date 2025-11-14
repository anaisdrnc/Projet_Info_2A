import pytest
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Service.UserService import UserService
from src.Model.User import User
from utils.reset_database import ResetDatabase


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


def test_get_all_users_without_password(service):
    """get_all_users: les mots de passe doivent être retirés"""

    # Création de deux utilisateurs
    service.create_user("User1", "StrongPass1", "A", "B", "a@b.com")
    service.create_user("User2", "StrongPass1", "C", "D", "c@d.com")

    users = service.get_all_users(include_password=False)

    # Vérifie que les utilisateurs sont bien des objets User et que password est None
    for user in users:
        # certains utilisateurs peuvent déjà exister dans la base (ex: admin)
        assert hasattr(user, "user_name")
        assert user.password is None



def test_get_all_users_with_password(service):
    """get_all_users(include_password=True) doit fournir les passwords hashés"""
    service.create_user("User1", "StrongPass1", "A", "B", "a@b.com")

    users = service.get_all_users(include_password=True)

    assert len(users) == 1
    assert users[0].password not in [None, "StrongPass1"]  # hash non vide


def test_is_username_taken(service):
    """Test du check sur les usernames"""
    service.create_user("UserX", "StrongPass1", "A", "B", "a@b.com")

    assert service.is_username_taken("UserX") is True
    assert service.is_username_taken("UnknownUser") is False
