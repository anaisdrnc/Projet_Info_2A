import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from src.Service.DriverService import DriverService
from utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset la base de test avant chaque test."""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO Driver pour les tests."""
    return DriverDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service basé sur le DAO."""
    return DriverService(driverdao=dao)


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def test_create_ok(service):
    # Act
    driver = service.create_driver(
        username="DriverTest",
        password="SecurePass123",
        firstname="John",
        lastname="Doe",
        email="john.doe@test.com",
        mean_of_transport="car"
    )

    # Assert
    assert driver is not None
    assert isinstance(driver, Driver)
    assert driver.id_driver is not None
    assert driver.user_name == "DriverTest"
    assert driver.email == "john.doe@test.com"

    # Le mot de passe doit être hashé
    assert driver.password != "SecurePass123"
    assert driver.salt is not None


def test_create_driver_weak_password(service):
    """
    Mot de passe trop faible → doit lever une exception.
    """
    with pytest.raises(Exception) as excinfo:
        service.create_driver(
            username="WeakDriver",
            password="123",  # trop court
            firstname="Tim",
            lastname="Short",
            email="tim.short@test.com",
            mean_of_transport="bike"
        )

    assert "password" in str(excinfo.value).lower()
    assert "8" in str(excinfo.value).lower()


# ---------------------------------------------------------------------------
# GET BY USERNAME
# ---------------------------------------------------------------------------

def test_get_by_username_ok(service):
    # Arrange
    service.create_driver(
        username="DriverUser",
        password="MyPassword99",
        firstname="Alice",
        lastname="Moran",
        email="alice@test.com",
        mean_of_transport="scooter"
    )

    # Act
    driver = service.get_by_username("DriverUser")

    # Assert
    assert driver is not None
    assert isinstance(driver, Driver)
    assert driver.user_name == "DriverUser"
    assert driver.email == "alice@test.com"


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------

def test_login_ok(service):
    # Arrange
    service.create_driver(
        username="LoginDriver",
        password="StrongPass88",
        firstname="Laura",
        lastname="Sky",
        email="laura@test.com",
        mean_of_transport="car"
    )

    # Act
    logged = service.login("LoginDriver", "StrongPass88")

    # Assert
    assert logged is not None
    assert isinstance(logged, Driver)
    assert logged.user_name == "LoginDriver"


def test_login_wrong_password(service):
    # Arrange
    service.create_driver(
        username="WrongPassDriver",
        password="CorrectPass123",
        firstname="Mark",
        lastname="Stone",
        email="mark@test.com",
        mean_of_transport="bike"
    )

    # Act
    logged = service.login("WrongPassDriver", "badpass")

    # Assert
    assert logged is None


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def test_update_driver_ok(service):
    # Arrange
    driver = service.create_driver(
        username="UpdateDriver",
        password="SafePassword777",
        firstname="Paul",
        lastname="Rex",
        email="paul@test.com",
        mean_of_transport="car"
    )

    driver.mean_of_transport = "electric scooter"

    # Act
    updated = service.update_driver(driver)

    # Assert
    assert updated is True

    refreshed = service.get_by_username("UpdateDriver")
    assert refreshed.mean_of_transport == "electric scooter"


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_delete_driver_ok(service):
    # Arrange
    driver = service.create_driver(
        username="DeleteDriver",
        password="RemovePass55",
        firstname="Lola",
        lastname="Briggs",
        email="lola@test.com",
        mean_of_transport="bike"
    )

    # Act
    deleted = service.delete_driver(driver.id_driver)

    # Assert
    assert deleted is True
    assert service.get_by_username("DeleteDriver") is None
