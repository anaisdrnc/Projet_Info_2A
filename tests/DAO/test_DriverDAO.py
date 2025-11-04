import os
import pytest
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver


import pytest
from utils.reset_database import ResetDatabase
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

def test_create_driver_ok():
    driver = Driver(
        user_name="testdriver",
        password=hash_password("secret", "testdriver"),
        first_name="Test",
        last_name="Driver",
        email="testdriver@test.com",
        mean_of_transport="Car"
    )
    created = DriverDAO().create(driver)
    assert created
    assert driver.id > 0


def test_create_driver_ko():
    driver = Driver(
        user_name="testdriver",
        password=hash_password("secret", "testdriver"),
        first_name="Test",
        last_name="Driver",
        email="testdriver@test.com",
        mean_of_transport="Car"
    )
    created = DriverDAO().create(driver)
    assert not created


def test_get_by_id_ok():
    driver = Driver(
        user_name="get_driver",
        password=hash_password("secret", "get_driver"),
        first_name="Get",
        last_name="Driver",
        email="get@test.com",
        mean_of_transport="Car"
    )
    DriverDAO().create(driver)
    retrieved = DriverDAO().get_by_id(driver.id)
    assert retrieved is not None
    assert retrieved.user_name == driver.user_name


def test_get_by_id_ko():
    retrieved = DriverDAO().get_by_id(999999)
    assert retrieved is None


def test_list_all_drivers():
    driver1 = Driver(
        user_name="list_driver1",
        password=hash_password("secret1", "list_driver1"),
        first_name="List",
        last_name="Driver1",
        email="list1@test.com",
        mean_of_transport="Car"
    )
    driver2 = Driver(
        user_name="list_driver2",
        password=hash_password("secret2", "list_driver2"),
        first_name="List",
        last_name="Driver2",
        email="list2@test.com",
        mean_of_transport="Car"
    )
    DriverDAO().create(driver1)
    DriverDAO().create(driver2)
    all_drivers = DriverDAO().list_all()
    usernames = [d.user_name for d in all_drivers]
    assert driver1.user_name in usernames
    assert driver2.user_name in usernames


def test_update_driver_ok():
    driver = Driver(
        user_name="update_driver",
        password=hash_password("secret", "update_driver"),
        first_name="Update",
        last_name="Driver",
        email="update@test.com",
        mean_of_transport="Car"
    )
    DriverDAO().create(driver)
    driver.mean_of_transport = "Bike"
    updated = DriverDAO().update(driver)
    updated_driver = DriverDAO().get_by_id(driver.id)
    assert updated
    assert updated_driver.mean_of_transport == "Bike"


def test_update_driver_ko():
    driver = Driver(
        user_name="nonexist",
        password=hash_password("secret", "nonexist"),
        first_name="No",
        last_name="Exist",
        email="noexist@test.com",
        mean_of_transport="Car"
    )
    updated = DriverDAO().update(driver)
    assert not updated


def test_login_driver_ok():
    username = "login_driver"
    password = "secret"
    driver = Driver(
        user_name=username,
        password=hash_password(password, username),
        first_name="Login",
        last_name="Driver",
        email="login@test.com",
        mean_of_transport="Car"
    )
    DriverDAO().create(driver)
    logged_in = DriverDAO().login(username, hash_password(password, username))
    assert logged_in is not None
    assert logged_in.user_name == username


def test_login_driver_ko():
    logged_in = DriverDAO().login("wronguser", hash_password("wrongpass", "wronguser"))
    assert logged_in is None


def test_delete_driver_ok():
    driver = Driver(
        user_name="delete_driver",
        password=hash_password("secret", "delete_driver"),
        first_name="Delete",
        last_name="Driver",
        email="delete@test.com",
        mean_of_transport="Car"
    )
    DriverDAO().create(driver)
    deleted = DriverDAO().delete(driver.id)
    driver_after = DriverDAO().get_by_id(driver.id)
    assert deleted
    assert driver_after is None


def test_delete_driver_ko():
    deleted = DriverDAO().delete(999999)
    assert not deleted


if __name__ == "__main__":
    pytest.main([__file__])
