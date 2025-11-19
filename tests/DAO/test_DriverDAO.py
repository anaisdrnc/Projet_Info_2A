from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.UserRepo import UserRepo
from src.Model.Driver import Driver
from utils.reset_database import ResetDatabase
from utils.securite import hash_password

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Reset DB before tests"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for the test schema"""
    driver_dao = DriverDAO(db_connector=DBConnector(test=True))
    driver_dao.user_repo = UserRepo(driver_dao.db_connector)
    return driver_dao


def unique_username(base="driver"):
    return f"{base}_{datetime.utcnow().timestamp()}"


# --- Tests ---


def test_create_driver_ok(dao):
    """Test : Verify that a new driver can be successfully added to the database."""
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
    """Test :Verify that adding a driver with a duplicate username fails."""
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
    """Test: Retrieve a driver by their ID successfully."""
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
    """Test: Retrieving a driver with a non-existent ID returns None."""
    retrieved = dao.get_by_id(999999)
    assert retrieved is None


def test_list_all_drivers(dao):
    """Test: Verify that all drivers are correctly listed from the database."""
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
    """Test: Successfully update a driver's information."""
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
    """Test: Updating a non-existent driver fails."""
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
    """Test: A driver can successfully log in with correct login details."""
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
    """Test: Driver login fails with an incorrect password."""
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

    logged = dao.login(username, "wrongpass")
    assert logged is None


def test_login_driver_nonexistent_user(dao):
    """Test: Login fails for a non-existent driver."""
    logged = dao.login("nonexistent_user_xyz", "anypass")
    assert logged is None


def test_delete_driver_ok(dao):
    """Test: Verify that a driver can be successfully deleted from the database."""
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
    """Test: Attempting to delete a non-existent driver returns False."""
    deleted = dao.delete(999999)
    assert not deleted


def test_get_id_driver_by_id_user(dao):
    """Test: Retrieve an existing driver's ID by their user ID."""
    username = unique_username("get_id_by_user")
    salt = unique_username("salt_driver")

    driver = Driver(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Id",
        last_name="Driver",
        email=f"{username}@test.com",
        mean_of_transport="Car",
    )

    created = dao.create(driver)
    assert created
    assert driver.id > 0
    assert driver.id_driver > 0

    retrieved_id_driver = dao.get_id_driver_by_id_user(driver.id)

    assert retrieved_id_driver == driver.id_driver


def test_get_id_driver_by_id_user_ko(dao):
    """Test: Retrieve a driver's ID by their non-existent user id."""
    retrieved = dao.get_id_driver_by_id_user(999999)
    assert retrieved is None


if __name__ == "__main__":
    pytest.main([__file__])
