import pytest
from dotenv import load_dotenv

from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Address import Address
from utils.reset_database import ResetDatabase

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Reset DB before tests"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    address_dao = AddressDAO(db_connector=DBConnector(test=True))
    address_dao.db_connector = DBConnector(test=True)
    return address_dao


# --- Tests ---


def test_add_address_ok(dao):
    """Test : Verify that a new address can be successfully added to the database."""
    address = Address(address="14 Rue du Chapitre", postal_code=35000, city="Rennes")

    result = dao.add_address(address)

    assert result
    assert result.id_address > 0


def test_add_address_ko_invalid_postal_db(dao):
    """Test : Verify that a new address can be unsuccessfully added to the database with a wrong postalcode."""
    address = Address(address="Rue test", postal_code=9999999, city="Rennes")

    result = dao.add_address(address)

    assert result is None
    assert address.id_address is None
