from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.UserRepo import UserRepo

load_dotenv()

# --- Fixtures ---


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Reset DB before tests"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    driver_dao = DriverDAO()
    driver_dao.db_connector = DBConnector(test=True)
    driver_dao.user_repo = UserRepo(driver_dao.db_connector)
    return driver_dao


# --- Utilitaire ---


def unique_username(base="driver"):
    return f"{base}_{datetime.utcnow().timestamp()}"


# --- Tests ---


def test_create_driver_ok(dao):
    username = unique_username("create_ok")
    salt = unique_username("salt")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Test",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    created = dao.create(driver)
    assert created
    assert driver.id > 0
    assert driver.id_driver > 0


def test_create_driver_duplicate(dao):
    username = unique_username("dup_driver")
    salt = unique_username("saltdup")
    driver1 = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Dup",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver1)

    driver2 = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Dup",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    created2 = dao.create(driver2)
    assert not created2


def test_get_by_id_ok(dao):
    username = unique_username("get_driver")
    salt = unique_username("saltget")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Get",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)
    retrieved = dao.get_by_id(driver.id_driver)
    assert retrieved is not None
    assert retrieved.user_name == username


def test_get_by_id_ko(dao):
    retrieved = dao.get_by_id(999999)
    assert retrieved is None


def test_list_all_drivers(dao):
    username1 = unique_username("list1")
    username2 = unique_username("list2")
    salt1 = unique_username("salt1")
    salt2 = unique_username("salt2")
    driver1 = Driver(
        user_name=username1,
        password=hash_password("p1", salt1),
        salt=salt1,
        first_name="List",
        last_name="Driver1",
        email=f"{username1}@test.com",
        mean_of_transport="Car",
    )
    driver2 = Driver(
        user_name=username2,
        password=hash_password("p2", salt2),
        salt=salt2,
        first_name="List",
        last_name="Driver2",
        email=f"{username2}@test.com",
        mean_of_transport="Bike",
    )
    dao.create(driver1)
    dao.create(driver2)

    all_drivers = dao.list_all()
    usernames = [d.user_name for d in all_drivers]
    assert username1 in usernames
    assert username2 in usernames


def test_update_driver_ok(dao):
    username = unique_username("update_driver")
    salt = unique_username("saltupdate")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Update",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    driver.mean_of_transport = "Bike"
    updated = dao.update(driver)
    assert updated
    updated_driver = dao.get_by_id(driver.id_driver)
    assert updated_driver.mean_of_transport == "Bike"


def test_update_driver_ko(dao):
    driver = Driver(
        id=999999,
        user_name="nonexist",
        password=hash_password("secret", "nonexist"),
        salt="nonexist",
        first_name="No",
        last_name="Exist",
        email="noexist@test.com",
        mean_of_transport="Car",
    )
    updated = dao.update(driver)
    assert not updated


def test_login_driver_ok(dao):
    username = unique_username("login_ok")
    password = "secret"
    salt = unique_username("saltlogin")
    hashed = hash_password(password, salt)

    driver = Driver(
        user_name=username,
        password=hashed,
        salt=salt,
        first_name="Login",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    logged = dao.login(username, password)
    assert logged is not None
    assert logged.user_name == username
    assert logged.email == driver.email


def test_login_driver_wrong_password(dao):
    username = unique_username("login_wrong")
    password = "secret"
    salt = unique_username("saltwrong")
    hashed = hash_password(password, salt)

    driver = Driver(
        user_name=username,
        password=hashed,
        salt=salt,
        first_name="Login",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)

    # Mauvais mot de passe en clair
    logged = dao.login(username, "wrongpass")
    assert logged is None


def test_login_driver_nonexistent_user(dao):
    logged = dao.login("nonexistent_user_xyz", "anypass")
    assert logged is None


def test_delete_driver_ok(dao):
    username = unique_username("delete_ok")
    salt = unique_username("saltdel")
    driver = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Delete",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )
    dao.create(driver)
    deleted = dao.delete(driver.id_driver)
    assert deleted
    assert dao.get_by_id(driver.id_driver) is None


def test_delete_driver_ko(dao):
    deleted = dao.delete(999999)
    assert not deleted


if __name__ == "__main__":
    pytest.main([__file__])
