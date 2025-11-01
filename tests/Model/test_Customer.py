import pytest

from src.Model.Address import Address
from src.Model.Customer import Customer


def test_create_customer_with_address():
    """Test normal : création d’un Customer avec adresse complète"""
    addr = Address(address="12 Maple Street", postalcode=35000, city="Rennes")
    cust = Customer(
        id=1,
        username="testuser",
        password="secret",
        firstname="Alice",
        lastname="Martin",
        email="alice@test.com",
        address=addr
    )

    assert cust.id == 1
    assert cust.username == "testuser"
    assert cust.address.city == "Rennes"
    assert isinstance(cust.address, Address)


def test_create_customer_without_address():
    """Test : création d’un Customer sans adresse"""
    cust = Customer(
        id=2,
        username="bobuser",
        password="secret",
        firstname="Bob",
        lastname="Durand",
        email="bob@test.com",
        address=None
    )

    assert cust.address is None
    assert cust.firstname == "Bob"


def test_invalid_address_type():
    """Test : on donne une mauvaise valeur pour address"""
    with pytest.raises(ValueError):
        Customer(
            id=3,
            username="erroruser",
            password="pass",
            firstname="Charlie",
            lastname="Dupont",
            email="charlie@test.com",
            address="This should not be a string"
        )
