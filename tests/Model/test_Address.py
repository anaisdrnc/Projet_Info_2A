import pytest
from pydantic_core import ValidationError

from src.Model.Address import Address


def test_address_constructor_ok():
    Address1 = Address(address="51 rue Blaise Pascal", postal_code=35170, city="Bruz")
    assert Address1.address == "51 rue Blaise Pascal"
    assert Address1.postal_code == 35170
    assert Address1.city == "Bruz"


def test_address_constructor_throws_on_incorrect_address():
    with pytest.raises(ValidationError) as exception_info:
        Address(address=51, postal_code=35170, city="Bruz")
    assert "address" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_address_constructor_throws_on_incorrect_postalcode():
    with pytest.raises(ValidationError) as exception_info:
        Address(address="51 rue Blaise Pascal", postal_code="Trente cinq", city="Bruz")
    assert "postal_code" in str(exception_info.value) and "Input should be a valid integer" in str(exception_info.value)


def test_address_constructor_throws_on_incorrect_city():
    with pytest.raises(ValidationError) as exception_info:
        Address(address="51 rue Blaise Pascal", postal_code=35170, city=True)
    assert "city" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)
