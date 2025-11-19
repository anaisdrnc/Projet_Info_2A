from unittest.mock import MagicMock

import pytest

from DAO.AdminDAO import AdminDAO
from DAO.DBConnector import DBConnector
from Model.Admin import Admin
from Model.User import User
from Service.AdminService import AdminService
from utils.reset_database import ResetDatabase
from utils.securite import hash_password


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database avant chaque test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO pour tests"""
    return AdminDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service basé sur le DAO"""
    return AdminService(admindao=dao)


def test_create_ok(service):
    # Act
    admin = service.create_admin(
        username="JulDjrdn",
        password="Caraibe35",
        first_name="Julie",
        last_name="Dujardin",
        email="julie.dujardin@gmail.com",
    )

    # Assert
    assert admin is not None
    assert isinstance(admin, Admin) or isinstance(admin, User)
    assert admin.id_admin is not None  # id généré
    assert admin.user_name == "JulDjrdn"
    assert admin.email == "julie.dujardin@gmail.com"

    # Vérifie que le mot de passe a bien été hashé et qu’il y a un salt
    assert admin.password != "Caraibe35"
    assert admin.salt is not None


def test_create_admin_weak_password(service):
    """
    Test KO : le mot de passe est trop faible -> doit lever une Exception.
    """
    with pytest.raises(Exception) as excinfo:
        service.create_admin(
            username="WeakAdmin",
            password="123",  # trop court
            first_name="Jean",
            last_name="Dupont",
            email="jean.dupont@example.com",
        )

    assert "password" in str(excinfo.value).lower()
    assert "8" in str(excinfo.value)  # pour vérifier le message d'erreur


def test_get_by_username_ok(service, dao):
    """
    Test OK : le DAO retourne un Admin valide.
    """
    # Arrange : on crée un admin dans la base
    service.create_admin(
        username="JulDjrdn",
        password="Caraibe35",
        first_name="Julie",
        last_name="Dujardin",
        email="julie.dujardin@gmail.com",
    )

    # Act : on tente de le récupérer
    admin = service.get_by_username("JulDjrdn")

    # Assert
    assert admin is not None
    assert isinstance(admin, Admin)
    assert admin.user_name == "JulDjrdn"
    assert admin.email == "julie.dujardin@gmail.com"


def test_get_by_username_ko(service):
    """
    Test KO : le DAO lève une exception, le service doit retourner None.
    """
    # Arrange : on force une exception dans le DAO
    service.admindao.get_by_username = MagicMock(side_effect=Exception("DB error"))

    # Act
    result = service.get_by_username("inexistant")

    # Assert
    assert result is None

def test_get_by_id_ok(service):
    """
    Test OK : récupération d'un admin par son id_admin.
    """
    created = service.create_admin(
        username="TestAdmin",
        password="StrongPass1",
        first_name="Alice",
        last_name="Durand",
        email="aliced@example.com",
    )

    admin = service.get_by_id(created.id_admin)

    assert admin is not None
    assert isinstance(admin, Admin)
    assert admin.id_admin == created.id_admin
    assert admin.user_name == "TestAdmin"


def test_get_by_id_ko(service):
    """
    Test KO : le DAO lève une erreur → le service doit retourner None.
    """
    service.admindao.get_by_id = MagicMock(side_effect=Exception("DB error"))

    result = service.get_by_id(999)

    assert result is None


def test_verify_password_ok(service):
    """
    Test OK : verify_password retourne True quand le mot de passe est correct.
    """
    pwd = "StrongPass1"
    salt = "selDeTest"
    hashed = hash_password(pwd, salt)

    assert service.verify_password(pwd, hashed, salt) is True


def test_verify_password_ko(service):
    """
    Test KO : verify_password retourne False quand le mot de passe est incorrect.
    """
    pwd = "StrongPass1"
    salt = "selDeTest"
    hashed = hash_password(pwd, salt)

    assert service.verify_password("WrongPassword", hashed, salt) is False
