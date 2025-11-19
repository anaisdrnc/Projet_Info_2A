import pytest

from Model.Address import Address
from Model.Customer import Customer


def test_create_customer_with_address():
    """Test : Checks that an Customer object has been initialized correctly."""
    addr = Address(address="12 Maple Street", postal_code=35000, city="Rennes")
    cust = Customer(
        id=1,
        user_name="testuser",
        password="secret",
        first_name="Alice",
        last_name="Martin",
        email="alice@test.com",
        salt="j",
        address=addr,
    )

    assert cust.id == 1
    assert cust.user_name == "testuser"
    assert cust.address.city == "Rennes"
    assert isinstance(cust.address, Address)


def test_create_customer_without_address():
    """Test : checks constructor without address."""
    cust = Customer(
        id=2,
        user_name="bobuser",
        password="secret",
        first_name="Bob",
        last_name="Durand",
        email="bob@test.com",
        salt="k",
        address=None,
    )

    assert cust.address is None
    assert cust.first_name == "Bob"


def test_invalid_address_type():
    """Test : checks constructor with a wrong type of address."""
    with pytest.raises(ValueError):
        Customer(
            id=3,
            username="erroruser",
            password="pass",
            firstname="Charlie",
            lastname="Dupont",
            email="charlie@test.com",
            salt="m",
            address="This should not be a string",
        )
