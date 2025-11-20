from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer
from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_password

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Reset DB before tests"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for the test schema"""
    customer_dao = CustomerDAO()
    customer_dao.db_connector = DBConnector(test=True)
    customer_dao.user_repo = UserRepo(customer_dao.db_connector)
    return customer_dao


def unique_username(base="customer"):
    """Generate a unique username for testing."""
    return f"{base}_{datetime.utcnow().timestamp()}"


class TestCustomerDAO:
    """Tests for CustomerDAO"""

    def test_add_customer_ok(self, dao):
        """Test: Verify that a new customer can be successfully added to the database."""
        username = unique_username("add_ok")
        salt = unique_username("salt")
        customer = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Test",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        added = dao.add_customer(customer)
        assert added
        assert customer.id > 0

    def test_add_customer_duplicate(self, dao):
        """Test: Verify that adding a customer with a duplicate username fails."""
        username = unique_username("dup_customer")
        salt = unique_username("saltdup")
        customer1 = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Dup",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        dao.add_customer(customer1)

        customer2 = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Dup",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        added2 = dao.add_customer(customer2)
        assert not added2

    def test_get_by_id_ok(self, dao):
        """Test: Retrieve a customer by their ID successfully."""
        username = unique_username("get_customer")
        salt = unique_username("saltget")
        customer = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Get",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        dao.add_customer(customer)
        retrieved = dao.get_by_id(customer.id_customer)
        assert retrieved is not None
        assert retrieved.user_name == username

    def test_get_by_id_ko(self, dao):
        """Test: Retrieving a customer with a non-existent ID returns None."""
        retrieved = dao.get_by_id(999999)
        assert retrieved is None

    def test_update_customer_ok(self, dao):
        """Test: Successfully update a customer's information."""
        username = unique_username("update_customer")
        salt = unique_username("saltupdate")
        customer = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Original",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        dao.add_customer(customer)

        customer.first_name = "Updated"
        customer.last_name = "CustomerUpdated"
        customer.email = f"updated_{username}@test.com"

        updated = dao.update_customer(customer)
        assert updated

        retrieved = dao.get_by_id(customer.id_customer)
        assert retrieved.first_name == "Updated"
        assert retrieved.last_name == "CustomerUpdated"
        assert retrieved.email == f"updated_{username}@test.com"

    def test_update_customer_ko(self, dao):
        """Test: Updating a non-existent customer fails."""
        fake_customer = Customer(
            id=999999,
            user_name="nonexist",
            password=hash_password("secret", "nonexist"),
            salt="nonexist",
            first_name="No",
            last_name="Exist",
            email="noexist@test.com",
        )
        updated = dao.update_customer(fake_customer)
        assert not updated

    def test_delete_customer_ok(self, dao):
        """Test: Successfully delete an existing customer."""
        username = unique_username("delete_ok")
        salt = unique_username("saltdel")
        customer = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Delete",
            last_name="Customer",
            email=f"{username}@test.com",
        )
        dao.add_customer(customer)
        deleted = dao.delete_customer(customer.id_customer)
        assert deleted
        assert dao.get_by_id(customer.id_customer) is None

    def test_delete_customer_ko(self, dao):
        """Test: Attempting to delete a non-existent customer returns False."""
        deleted = dao.delete_customer(999999)
        assert not deleted

    def test_get_id_customer_by_id_user(self, dao):
        """Test: Retrieve an existing customer's ID by their user ID."""
        username = unique_username("get_id_customer")
        salt = unique_username("salt_customer")

        customer = Customer(
            user_name=username,
            password=hash_password("secret", salt),
            salt=salt,
            first_name="Id",
            last_name="Customer",
            email=f"{username}@test.com",
        )

        created = dao.add_customer(customer)
        assert created is not None
        assert customer.id > 0
        assert customer.id_customer > 0

        retrieved_id_customer = dao.get_id_customer_by_id_user(customer.id)
        assert retrieved_id_customer == customer.id_customer

    def test_get_id_customer_by_id_user_not_found(self, dao):
        """Test: Retrieve a customer's ID by their non-existent user ID."""
        retrieved = dao.get_id_customer_by_id_user(999999)
        assert retrieved is None
