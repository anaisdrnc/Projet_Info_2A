import pytest
from unittest.mock import MagicMock

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.src.Model.Customer import Customer
from src.Service.CustomerService import CustomerService
from src.utils.reset_database import ResetDatabase
from src.utils.securite import hash_password


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database avant chaque test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO pour tests"""
    return CustomerDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service basé sur le DAO"""
    return CustomerService(customerdao=dao)


def test_create_customer_ok(service):
    """Test OK : création d’un customer"""
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

    # Vérifie hachage + salt
    assert customer.password != "Password123"
    assert customer.salt is not None


def test_create_customer_weak_password(service):
    """Mot de passe trop faible → Exception attendue"""
    with pytest.raises(Exception):
        service.create_customer(
            username="weak",
            password="123",
            firstname="AA",
            lastname="BB",
            email="weak@example.com",
        )

def test_get_by_id_ok(service):
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


def test_get_by_id_ko(service):
    service.customerdao.get_by_id = MagicMock(side_effect=Exception("DB error"))

    result = service.get_by_id(999)

    assert result is None


def test_update_customer_ok(service):
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

    # Relecture depuis la BDD
    updated = service.get_by_id(customer.id_customer)

    assert updated.email == "new@example.com"



def test_update_customer_ko(service):
    """KO : le DAO lève une exception → le service doit retourner False"""
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


