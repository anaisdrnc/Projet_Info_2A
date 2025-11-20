import pytest

from src.Model.Address import Address
from src.Model.Customer import Customer


class TestCustomer:
    """Tests for the Customer model"""

    def test_create_customer_with_address(self):
        """Test: Customer object initialized correctly with an address."""
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
        assert cust.address.address == "12 Maple Street"
        assert cust.address.postal_code == 35000
        assert cust.address.city == "Rennes"

    def test_create_customer_without_address(self):
        """Test: Customer object initialized correctly without an address."""
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

    def test_invalid_address_type(self):
        """Test: Customer constructor raises error with wrong address type."""
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
