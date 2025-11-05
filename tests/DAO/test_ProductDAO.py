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

def test_create_ok():
    """Création d'un produit réussie"""
    product = Product(
        id_product = 23,
        name="Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    creation_ok = ProductDAO().add_product(product)
    assert creation_ok
    assert product.id_product is not None


def test_creer_ko():
    """Création échouée avec nom déjà existant"""
    dao = ProductDAO()

    # Insertion initiale
    product1 = Product(
        id_product = 
        name="Panini",
        price=3.00,
        production_cost=2.50,
        description="simple lunch",
        product_type="lunch",
        stock=13,
    )
    assert dao.add_product(product1)

    # Tentative de réinsertion avec le même nom
    product2 = Product(
        name="Panini",
        price=3.50,
        production_cost=2.50,
        description="duplicated",
        product_type="lunch",
        stock=5,
    )
    creation_ok = dao.add_product(product2)
    assert not creation_ok


def test_delete_ok():
    """Suppression de Product réussie"""
    product = Product(
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
