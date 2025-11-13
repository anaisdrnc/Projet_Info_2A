from unittest.mock import MagicMock, patch

import pytest

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Admin import Admin
from src.Service.AdminService import AdminService
from utils.reset_database import ResetDatabase


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
        firstname="Julie",
        lastname="Dujardin",
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
            firstname="Jean",
            lastname="Dupont",
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
        firstname="Julie",
        lastname="Dujardin",
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
