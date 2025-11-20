import pytest
from pydantic_core import ValidationError

from src.Model.Address import Address


class TestAddress:
    """Tests for Address model"""

    def test_constructor_ok(self):
        """Test: Checks that an Address object has been initialized correctly."""
        address = Address(address="51 rue Blaise Pascal", postal_code=35170, city="Bruz")
        assert address.address == "51 rue Blaise Pascal"
        assert address.postal_code == 35170
        assert address.city == "Bruz"

    def test_constructor_on_incorrect_address(self):
        """Test: Checks constructor on incorrect address."""
        with pytest.raises(ValidationError) as exception_info:
            Address(address=51, postal_code=35170, city="Bruz")
        assert "address" in str(exception_info.value)
        assert "Input should be a valid string" in str(exception_info.value)

    def test_constructor_on_incorrect_postalcode(self):
        """Test: Checks constructor on incorrect postal code."""
        with pytest.raises(ValidationError) as exception_info:
            Address(address="51 rue Blaise Pascal", postal_code="Trente cinq", city="Bruz")
        assert "postal_code" in str(exception_info.value)
        assert "Input should be a valid integer" in str(exception_info.value)

    def test_constructor_on_incorrect_city(self):
        """Test: Checks constructor on incorrect city name."""
        with pytest.raises(ValidationError) as exception_info:
            Address(address="51 rue Blaise Pascal", postal_code=35170, city=True)
        assert "city" in str(exception_info.value)
        assert "Input should be a valid string" in str(exception_info.value)
