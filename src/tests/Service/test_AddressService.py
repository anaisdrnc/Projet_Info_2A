import pytest

from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Address import Address
from src.Service.AddressService import AddressService
from src.utils.reset_database import ResetDatabase


# Réinitialisation de la base avant chaque test
@pytest.fixture(autouse=True)
def reset_db():
    ResetDatabase(test=True).lancer()


# DAO pour les tests
@pytest.fixture
def dao():
    return AddressDAO(DBConnector(test=True))


# Service basé sur le DAO
@pytest.fixture
def service(dao):
    return AddressService(addressdao=dao)


# --- Tests ---


def test_validate_address_ok(service):
    addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Rennes")
    assert service.validate_address(addr) is True


def test_validate_address_wrong_city(service):
    addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=35000, city="Bruz")
    assert service.validate_address(addr) is False


def test_validate_address_wrong_postalcode(service):
    addr = Address(address="12 Yvonne Jean-Haffen Street", postal_code=99999, city="Rennes")
    assert service.validate_address(addr) is False


def test_add_address(service):
    new_addr = service.add_address(address="24 Rue de la Paix", city="Rennes", postal_code=35000)

    # Vérifications
    assert isinstance(new_addr, Address)
    assert new_addr.address == "24 Rue de la Paix"
    assert new_addr.city == "Rennes"
    assert new_addr.postal_code == 35000
