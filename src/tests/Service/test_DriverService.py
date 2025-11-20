import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from src.Service.DriverService import DriverService
from src.utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database before each test."""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """Driver DAO for testing."""
    return DriverDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service based on the DAO."""
    return DriverService(driverdao=dao)


class TestDriverService:
    """Tests for DriverService"""

    def test_create_ok(self, service):
        """Test: Successfully create a new driver"""
        driver = service.create_driver(
            username="DriverTest",
            password="SecurePass123",
            firstname="John",
            lastname="Doe",
            email="john.doe@test.com",
            mean_of_transport="Car",
        )

        assert driver is not None
        assert isinstance(driver, Driver)
        assert driver.id_driver is not None
        assert driver.user_name == "DriverTest"
        assert driver.email == "john.doe@test.com"
        assert driver.password != "SecurePass123"
        assert driver.salt is not None

    def test_create_driver_weak_password(self, service):
        """Test: Creating a driver with a weak password should raise Exception"""
        with pytest.raises(Exception) as excinfo:
            service.create_driver(
                username="WeakDriver",
                password="123",  # too short
                firstname="Tim",
                lastname="Short",
                email="tim.short@test.com",
                mean_of_transport="Bike",
            )

        assert "password" in str(excinfo.value).lower()
        assert "8" in str(excinfo.value).lower()

    def test_get_by_username_ok(self, service):
        """Test: Retrieve an existing driver by username"""
        service.create_driver(
            username="DriverUser",
            password="MyPassword99",
            firstname="Alice",
            lastname="Moran",
            email="alice2@test.com",
            mean_of_transport="Car",
        )

        driver = service.get_by_username("DriverUser")
        assert driver is not None
        assert isinstance(driver, Driver)
        assert driver.user_name == "DriverUser"
        assert driver.email == "alice2@test.com"

    def test_login_ok(self, service):
        """Test: Successfully log in with correct credentials"""
        service.create_driver(
            username="LoginDriver",
            password="StrongPass88",
            firstname="Laura",
            lastname="Sky",
            email="laura@test.com",
            mean_of_transport="Car",
        )

        logged = service.login("LoginDriver", "StrongPass88")
        assert logged is not None
        assert isinstance(logged, Driver)
        assert logged.user_name == "LoginDriver"

    def test_login_wrong_password(self, service):
        """Test: Login fails with incorrect password"""
        service.create_driver(
            username="WrongPassDriver",
            password="CorrectPass123",
            firstname="Mark",
            lastname="Stone",
            email="mark@test.com",
            mean_of_transport="Bike",
        )

        logged = service.login("WrongPassDriver", "badpass")
        assert logged is None

    def test_update_driver_ok(self, service):
        """Test: Successfully update a driver's transport method"""
        driver = service.create_driver(
            username="UpdateDriver",
            password="SafePassword777",
            firstname="Paul",
            lastname="Rex",
            email="paul@test.com",
            mean_of_transport="Car",
        )

        driver.mean_of_transport = "Bike"
        updated = service.update_driver(driver.user_name, "Bike")
        assert updated is True

        refreshed = service.get_by_username("UpdateDriver")
        assert refreshed.mean_of_transport == "Bike"

    def test_delete_driver_ok(self, service):
        """Test: Successfully delete an existing driver"""
        driver = service.create_driver(
            username="DeleteDriver",
            password="RemovePass55",
            firstname="Lola",
            lastname="Briggs",
            email="lola@test.com",
            mean_of_transport="Bike",
        )

        deleted = service.delete_driver(driver.id_driver)
        assert deleted is True
        assert service.get_by_username("DeleteDriver") is None
