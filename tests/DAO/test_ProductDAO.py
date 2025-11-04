import os
from unittest.mock import patch

import pytest

from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.reset_database import ResetDatabase


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    with patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_delete_ok():
    """Suppression de Product réussie"""

    # GIVEN
    product = Product(
        id_product=999,
        name="Test Panini",
        price=3.00,
        production_cost=2.00,
        description="Simple panini for test",
        type="lunch",
        stock=10,
    )

    # WHEN
    suppression_ok = ProductDAO().supprimer(product)

    # THEN
    assert suppression_ok


def test_delete_ko():
    """Suppression de Product échoué unknown id"""

    # GIVEN
    product = Product(
        id_product=99956666,
        name="Test Panini",
        price=3.00,
        production_cost=2.00,
        description="Simple panini for test",
        type="lunch",
        stock=10,
    )

    # WHEN
    suppression_ok = ProductDAO().supprimer(product)

    # THEN
    assert not suppression_ok


def test_create_ok():
    """Création d'un produit réussie"""

    # GIVEN
    product = Product(
        name="Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        type="lunch",
        stock=15,
    )

    # WHEN
    creation_ok = ProductDAO().insert(product)

    # THEN
    assert creation_ok
    assert product.id_product


def test_creer_ko():
    """Création de Product échouée (name echoue)"""

    # GIVEN
    product = Product(
        id=34, name="Panini", type="lunch", price=3.00, production_cost=2.50, description="simple lunch", stock=13
    )

    # WHEN
    creation_ok = ProductDAO().creer(product)

    # THEN
    assert not creation_ok
