import os
from unittest.mock import patch

import pytest

from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()

@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    product_dao = DriverDAO()
    product_dao.db_connector = DBConnector(test=True)
    return product_dao

def test_create_ok():
    """Successful product creation"""
    product = Product(
        id_product = 23,
        name=" Test Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    creation_ok = ProductDAO().add_product(product)
    assert creation_ok
    assert product.id_product is not None


def test_delete_ok():
    """Suppression de Product réussie"""
    product = Product(
        id_product = 40, 
        name="Test Panini OK",
        price=3.00,
        production_cost=2.00,
        description="Simple panini for test",
        product_type="lunch",
        stock=10,
    )
    dao = ProductDAO()
    assert dao.add_product(product)

    suppression_ok = dao.deleting_product(product)
    assert suppression_ok

