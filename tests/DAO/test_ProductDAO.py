import logging
import os
from unittest.mock import patch

import pytest

from src.DAO.ProductDAO import ProductDAO
from src.Model.Driver import Product
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
