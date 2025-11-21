from unittest.mock import MagicMock

import pytest

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Customer import Customer
from src.Service.CustomerService import CustomerService
from src.utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for testing"""
    return CustomerDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service based on the DAO"""
    return CustomerService(customerdao=dao)


class TestCustomerService:
    """Tests for CustomerService"""

    def test_create_customer_ok(self, service):
        """Test: Successfully create a new customer"""
        customer = service.create_customer(
            username="johnDoe",
            password="Password123",
            firstname="John",
            lastname="Doe",
            email="john.doe@email.com",
        )

        assert customer is not None
        assert isinstance(customer, Customer)
        assert customer.id_customer is not None
        assert customer.user_name == "johnDoe"
        assert customer.email == "john.doe@email.com"
        assert customer.password != "Password123"
        assert customer.salt is not None

    def test_create_customer_weak_password(self, service):
        """Test: Creating a customer with a weak password should raise Exception"""
        with pytest.raises(ValueError):
            service.create_customer(
                username="weak",
                password="123",
                firstname="AA",
                lastname="BB",
                email="weak@example.com",
            )

    def test_get_by_id_ok(self, service):
        """Test: Retrieve an existing customer by ID"""
        customer = service.create_customer(
            username="johnDoe",
            password="Password123",
            firstname="John",
            lastname="Doe",
            email="john@example.com",
        )

        retrieved = service.get_by_id(customer.id_customer)
        assert retrieved is not None
        assert isinstance(retrieved, Customer)
        assert retrieved.id_customer == customer.id_customer
        assert retrieved.user_name == "johnDoe"
        assert retrieved.email == "john@example.com"

    def test_get_by_id_ko(self, service):
        """Test: Retrieving a non-existent customer returns None"""
        service.customerdao.get_by_id = MagicMock(side_effect=Exception("DB error"))
        result = service.get_by_id(999)
        assert result is None

    def test_update_customer_ok(self, service):
        """Test: Successfully update a customer's data"""
        customer = service.create_customer(
            username="johnDoe",
            password="Password123",
            firstname="John",
            lastname="Doe",
            email="john@example.com",
        )

        customer.email = "new@example.com"
        result = service.update_customer(customer)
        assert result is True

        updated = service.get_by_id(customer.id_customer)
        assert updated.email == "new@example.com"

    def test_update_customer_ko(self, service):
        """Test: Updating a customer fails → should return False"""
        customer = Customer(
            id_customer=1,
            user_name="johnDoe",
            password="abc",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            salt="xyz",
        )
        service.customerdao.update_customer = MagicMock(side_effect=Exception("DB error"))
        result = service.update_customer(customer)
        assert result is False
