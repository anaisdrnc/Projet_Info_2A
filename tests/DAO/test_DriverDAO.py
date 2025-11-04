import os
import pytest
from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_create_driver_ok():
    """Successfully create a driver"""

    # GIVEN
    driver = Driver(
        username="testdriver",
        password=hash_password("secret", "testdriver"),
        firstname="Test",
        lastname="Driver",
        email="testdriver@test.com",
        transport_mean="Car"
    )


    # WHEN
    created = DriverDAO().create(driver)

    # THEN
    assert created
    assert driver.id > 0


def test_create_driver_ko():
    """Fail to create a driver with invalid data"""

    # GIVEN
    driver = Driver(
        username="testdriver",
        password=hash_password("secret", "testdriver"),
        firstname="Test",
        lastname="Driver",
        email="testdriver@test.com",
        transport_mean="Car"
    )

    # WHEN
    created = DriverDAO().create(driver)

    # THEN
    assert not created


def test_get_by_id_ok():
    """Retrieve an existing driver by ID"""

    # GIVEN
    driver = Driver(
        username="testdriver",
        password=hash_password("secret", "testdriver"),
        firstname="Test",
        lastname="Driver",
        email="testdriver@test.com",
        transport_mean="Car"
    )
    DriverDAO().create(driver)
    driver_id = driver.id

    # WHEN
    retrieved = DriverDAO().get_by_id(driver_id)

    # THEN
    assert retrieved is not None
    assert retrieved.username == driver.username


def test_get_by_id_ko():
    """Return None for non-existent driver ID"""

    # GIVEN
    driver_id = 999999

    # WHEN
    retrieved = DriverDAO().get_by_id(driver_id)

    # THEN
    assert retrieved is None


def test_list_all_drivers():
    """Retrieve a list of all drivers"""

    # GIVEN
    driver1 = Driver(
        username="list_driver1",
        password=hash_password("secret1", "list_driver1"),
        firstname="List",
        lastname="Driver1",
        email="list1@test.com",
        transport_mean="Car"
    )
    driver2 = Driver(
        username="list_driver2",
        password=hash_password("secret2", "list_driver2"),
        firstname="List",
        lastname="Driver2",
        email="list2@test.com",
        transport_mean="Car"
    )
    DriverDAO().create(driver1)
    DriverDAO().create(driver2)

    # WHEN
    all_drivers = DriverDAO().list_all()

    # THEN
    assert isinstance(all_drivers, list)
    assert len(all_drivers) >= 2
    usernames = [d.username for d in all_drivers]
    assert driver1.username in usernames
    assert driver2.username in usernames


def test_update_driver_ok():
    """Successfully update a driver"""

    # GIVEN
    driver = Driver(
        username="update_driver",
        password=hash_password("secret", "update_driver"),
        firstname="Update",
        lastname="Driver",
        email="update@test.com",
        transport_mean="Car"
    )
    DriverDAO().create(driver)

    driver.transport_mean = "Bike"

    # WHEN
    updated = DriverDAO().update(driver)
    updated_driver = DriverDAO().get_by_id(driver.id)

    # THEN
    assert updated
    assert updated_driver.transport_mean == "Bike"


def test_update_driver_ko():
    """Fail to update a non-existent driver"""

    # GIVEN
    driver = Driver(
        username="nonexist",
        password=hash_password("secret", "nonexist"),
        firstname="No",
        lastname="Exist",
        email="noexist@test.com",
        transport_mean="Car"
    )

    # WHEN
    updated = DriverDAO().update(driver)

    # THEN
    assert not updated


def test_login_driver_ok():
    """Successfully login a driver"""

    # GIVEN
    username = "login_driver"
    password = "secret"
    driver = Driver(
        username=username,
        password=hash_password(password, username),
        firstname="Login",
        lastname="Driver",
        email="login@test.com",
        transport_mean="Car"
    )
    DriverDAO().create(driver)

    # WHEN
    logged_in = DriverDAO().login(username, hash_password(password, username))

    # THEN
    assert logged_in is not None
    assert logged_in.username == username


def test_login_driver_ko():
    """Fail login with wrong credentials"""

    # GIVEN
    username = "wronguser"
    password = "wrongpass"

    # WHEN
    logged_in = DriverDAO().login(username, hash_password(password, username))

    # THEN
    assert logged_in is None


def test_delete_driver_ok():
    """Successfully delete a driver"""

    # GIVEN
    driver = Driver(
        username="delete_driver",
        password=hash_password("secret", "delete_driver"),
        firstname="Delete",
        lastname="Driver",
        email="delete@test.com",
        transport_mean="Car"
    )
    DriverDAO().create(driver)

    # WHEN
    deleted = DriverDAO().delete(driver.id)
    driver_after = DriverDAO().get_by_id(driver.id)

    # THEN
    assert deleted
    assert driver_after is None


def test_delete_driver_ko():
    """Fail to delete a non-existent driver"""

    # GIVEN
    driver_id = 999999

    # WHEN
    deleted = DriverDAO().delete(driver_id)

    # THEN
    assert not deleted


if __name__ == "__main__":
    pytest.main([__file__])
