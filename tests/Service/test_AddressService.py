import pytest
from src.Model.Address import Address
from src.Service.AddressService import validate_address


def test_validate_address_ok():
    addr = Address(
        address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Rennes"
    )
    assert validate_address(addr) is True


def test_validate_address_wrong_city():
    addr = Address(
        address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Bruz"
    )
    assert validate_address(addr) is False


def test_validate_address_wrong_postalcode():
    addr = Address(
        address="12 Yvonne Jean-Haffen Street", postal_code=99999, city="Rennes"
    )
    assert validate_address(addr) is False
