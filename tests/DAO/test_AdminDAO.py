from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Admin import Admin
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
    admin_dao = AdminDAO(db_connector=DBConnector(test=True))
    admin_dao.user_repo = UserRepo(admin_dao.db_connector)
    return admin_dao


def unique_username(base="admin"):
    return f"{base}_{datetime.utcnow().timestamp()}"


# --- Tests ---


def test_add_admin_ok(dao):
    """Test : Verify that a new admin can be successfully added to the database."""
    username = unique_username("add_admin")
    salt = unique_username("salt")
    admin = Admin(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Test",
        last_name="Admin",
        email=f"{username}@test.com",
    )
    created = dao.add_admin(admin)
    assert created
    assert admin.id > 0
    assert admin.id_admin > 0


def test_add_admin_duplicate(dao):
    """Test :Verify that adding an administrator with a duplicate username fails."""
    username = unique_username("dup_admin")
    salt = unique_username("saltdup")
    admin1 = Admin(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Dup",
        last_name="Admin",
        email=f"{username}@test.com",
    )
    dao.add_admin(admin1)

    admin2 = Admin(
        user_name=username,
        password=hash_password("secret", salt),
        salt=salt,
        first_name="Dup",
        last_name="Admin",
        email=f"{username}@test.com",
    )
    created2 = dao.add_admin(admin2)
    assert not created2


def test_login_admin_ok(dao):
    """Test: An administrator can successfully log in with correct login details"""
    username = unique_username("login_admin")
    password = "secret"
    salt = unique_username("saltlogin")
    hashed = hash_password(password, salt)
    admin = Admin(
        user_name=username,
        password=hashed,
        salt=salt,
        first_name="Login",
        last_name="Admin",
        email=f"{username}@test.com",
    )
    dao.add_admin(admin)

    logged = dao.login(username, password)
    assert logged is not None
    assert logged.user_name == username
    assert logged.email == admin.email


def test_login_admin_wrong_password(dao):
    """Test: Administrator login fails with an incorrect password."""
    username = unique_username("login_wrong")
    password = "secret"
    salt = unique_username("saltwrong")
    hashed = hash_password(password, salt)
    admin = Admin(
        user_name=username,
        password=hashed,
        salt=salt,
        first_name="Login",
        last_name="Admin",
        email=f"{username}@test.com",
    )
    dao.add_admin(admin)

    logged = dao.login(username, "wrongpass")
    assert logged is None


def test_login_admin_nonexistent_user(dao):
    """Test: Login fails for a non-existent administrator."""
    logged = dao.login("nonexistent_admin_xyz", "anypass")
    assert logged is None


if __name__ == "__main__":
    pytest.main([__file__])
