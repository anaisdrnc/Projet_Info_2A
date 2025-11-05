import os
import pytest
from utils.reset_database import ResetDatabase
from utils.securite import hash_password
from src.DAO.CustomerDAO import CustomerDAO
from src.Model.Customer import Customer
from src.DAO.DBConnector import DBConnector
import pytest
from utils.reset_database import ResetDatabase
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    customer_dao = CustomerDAO(db_connector = DBConnector(test=True))
    customer_dao.db_connector = DBConnector(test=True)
    return customer_dao

def test_create_customer_ok(dao):
    customer = Customer(
        user_name="testcustomer",
        password=hash_password("secret", "testcustomer"),
        first_name="Customer",
        last_name="Test",
        email="testcustomer@test.com"
    )
    created = dao.add_customer(customer)
    assert created
    assert customer.id > 0

if __name__ == "__main__":
    pytest.main([__file__])