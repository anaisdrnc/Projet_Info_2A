import pytest

from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Address import Address
from src.Service.AddressService import AddressService
from src.utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for testing"""
    return AddressDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service based on the DAO"""
    return AddressService(addressdao=dao)


class TestAddressService:
    """Tests for AddressService"""

    def test_validate_address_ok(self, service):
        """Test: Valid address should pass validation"""
        addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Rennes")
        assert service.validate_address(addr) is True

    def test_validate_address_wrong_city(self, service):
        """Test: Address with wrong city should fail validation"""
        addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Bruz")
        assert service.validate_address(addr) is False

    def test_validate_address_wrong_postalcode(self, service):
        """Test: Address with wrong postal code should fail validation"""
        addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=99999, city="Rennes")
        assert service.validate_address(addr) is False

    def test_add_address(self, service):
        """Test: Adding a new address should return an Address object"""
        new_addr = service.add_address(address="24 Rue de la Paix", city="Rennes", postal_code=35000)
        assert isinstance(new_addr, Address)
        assert new_addr.address == "24 Rue de la Paix"
        assert new_addr.city == "Rennes"
        assert new_addr.postal_code == 35000
