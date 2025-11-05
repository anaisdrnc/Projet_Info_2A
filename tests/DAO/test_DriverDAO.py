import os
import pytest
from dotenv import load_dotenv
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from datetime import datetime
from src.DAO.DBConnector import DBConnector

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    driver_dao = DriverDAO()
    driver_dao.db_connector = DBConnector(test=True)
    return driver_dao


def unique_username(base="driver"):
    """Générer un username unique pour éviter les collisions entre tests"""
    return f"{base}_{datetime.utcnow().timestamp()}"


def test_create_driver_ok(dao):
    username = unique_username("testdriver")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Test",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    created = dao.create(driver)
    assert created
    assert driver.id > 0


def test_create_driver_ko(dao):
    username = unique_username("dupdriver")
    driver1 = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Dup",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver1)

    driver2 = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Dup",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    created = dao.create(driver2)
    assert not created


def test_get_by_id_ok(dao):
    username = unique_username("get_driver")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Get",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)
    retrieved = dao.get_by_id(driver.id)
    assert retrieved is not None
    assert retrieved.user_name == driver.user_name


def test_get_by_id_ko(dao):
    retrieved = dao.get_by_id(999999)
    assert retrieved is None


def test_list_all_drivers(dao):
    username1 = unique_username("list_driver1")
    username2 = unique_username("list_driver2")
    driver1 = Driver(
        user_name=username1,
        password=hash_password("secret1", username1),
        first_name="List",
        last_name="Driver1",
        email=f"{username1}@test.com",
        mean_of_transport="Car",
    )
    driver2 = Driver(
        user_name=username2,
        password=hash_password("secret2", username2),
        first_name="List",
        last_name="Driver2",
        email=f"{username2}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver1)
    dao.create(driver2)

    all_drivers = dao.list_all()
    usernames = [d.user_name for d in all_drivers]
    assert username1 in usernames
    assert username2 in usernames


def test_update_driver_ok(dao):
    username = unique_username("update_driver")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Update",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    driver.mean_of_transport = "Bike"
    updated = dao.update(driver)
    updated_driver = dao.get_by_id(driver.id)
    assert updated
    assert updated_driver.mean_of_transport == "Bike"


def test_update_driver_ko(dao):
    driver = Driver(
        user_name="nonexist",
        password=hash_password("secret", "nonexist"),
        first_name="No",
        last_name="Exist",
        email="noexist@test.com",
        mean_of_transport="Car",
        id=999999,
    )
    updated = dao.update(driver)
    assert not updated


def test_login_driver_ok(dao):
    username = unique_username("login_driver")
    password = "secret"
    driver = Driver(
        user_name=username,
        password=hash_password(password, username),
        first_name="Login",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    logged_in = dao.login(username, hash_password(password, username))
    assert logged_in is not None
    assert logged_in.user_name == username


def test_login_driver_ko(dao):
    logged_in = dao.login("wronguser", hash_password("wrongpass", "wronguser"))
    assert logged_in is None


def test_delete_driver_ok(dao):
    username = unique_username("delete_driver")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", username),
        first_name="Delete",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    deleted = dao.delete(driver.id)
    driver_after = dao.get_by_id(driver.id)
    assert deleted
    assert driver_after is None


def test_delete_driver_ko(dao):
    deleted = dao.delete(999999)
    assert not deleted


if __name__ == "__main__":
    pytest.main([__file__])
