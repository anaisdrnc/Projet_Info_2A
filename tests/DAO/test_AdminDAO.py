import os

import pytest
from dotenv import load_dotenv

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Admin import Admin
from utils.reset_database import ResetDatabase
from utils.securite import hash_password

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    admin_dao = AdminDAO()
    admin_dao.db_connector = DBConnector(test=True)
    return admin_dao


def test_create_admin_ok(dao):
    admin = Admin(
        user_name="testadmin",
        password=hash_password("secret", "testadmin"),
        first_name="Admin",
        last_name="Test",
        email="testadmin@test.com",
    )
    created = dao.add_admin(admin)
    assert created
    assert admin.id > 0


if __name__ == "__main__":
    pytest.main([__file__])
