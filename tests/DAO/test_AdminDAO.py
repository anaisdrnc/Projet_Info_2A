import os
import pytest
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.AdminDAO import AdminDAO
from src.Model.Admin import Admin


import pytest
from utils.reset_database import ResetDatabase
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

def test_create_admin_ok():
    admin = Admin(
        user_name="testadmin",
        password=hash_password("secret", "testadmin"),
        first_name="Admin",
        last_name="Test",
        email="testadmin@test.com"
    )
    created = AdminDAO().add_admin(admin)
    assert created
    assert admin.id > 0