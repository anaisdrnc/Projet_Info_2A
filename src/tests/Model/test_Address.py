import pytest
from pydantic_core import ValidationError

from src.Model.Address import Address


def test_address_constructor_ok():
    """Test : Checks that an Address object has been initialized correctly."""
    Address1 = Address(address="51 rue Blaise Pascal", postal_code=35170, city="Bruz")
    assert Address1.address == "51 rue Blaise Pascal"
    assert Address1.postal_code == 35170
    assert Address1.city == "Bruz"


def test_address_constructor_on_incorrect_address():
    """Test : Checks constructor on incorrect address."""
    with pytest.raises(ValidationError) as exception_info:
        Address(address=51, postal_code=35170, city="Bruz")
    assert "address" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_address_constructor_on_incorrect_postalcode():
    """Test : Checks constructor on incorrect postal code."""
    with pytest.raises(ValidationError) as exception_info:
        Address(address="51 rue Blaise Pascal", postal_code="Trente cinq", city="Bruz")
    assert "postal_code" in str(exception_info.value) and "Input should be a valid integer" in str(exception_info.value)


def test_address_constructor_on_incorrect_city():
    """Test : Checks constructor on incorrect city name."""
    with pytest.raises(ValidationError) as exception_info:
        Address(address="51 rue Blaise Pascal", postal_code=35170, city=True)
    assert "city" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)
