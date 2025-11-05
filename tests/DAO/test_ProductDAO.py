import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.reset_database import ResetDatabase

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    product_dao = ProductDAO()
    product_dao.db_connector = DBConnector(test=True)
    return product_dao


def test_create_ok():
    """Successful product creation"""
    product = Product(
        id_product=23,
        name="Test Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    creation_ok = ProductDAO().create_product(product)
    assert creation_ok
    assert product.id_product is not None


def test_create_ko(dao):
    """DAO should reject adding a duplicate product"""

    # Premier produit
    product1 = Product(
        name="Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    # Création → succès
    assert dao.create_product(product1), "Le premier produit doit être créé"

    # Doublon
    product_duplicate = Product(
        name="Galette Saucisse",  # même nom pour provoquer le doublon
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    # Création échoue → False attendu
    creation_ok = dao.create_product(product_duplicate)
    assert not creation_ok, "La création d'un doublon doit échouer"


def test_delete_ok(dao):
    product = Product(
        name="Test Croque Monsieur",
        price=3.00,
        production_cost=2.00,
        description="Simple panini for test",
        product_type="lunch",
        stock=10,
    )

    # Création
    assert dao.create_product(product)
    assert product.id_product is not None, "Le produit doit avoir un ID généré"

    # Vérification existence
    res = dao.db_connector.sql_query(
        "SELECT * FROM product WHERE id_product = %(id_product)s;",
        {"id_product": product.id_product},
        return_type="one",
    )
    assert res is not None, "Le produit doit exister dans la DB avant suppression"

    # Suppression
    suppression_ok = dao.deleting_product(product.id_product)
    assert suppression_ok, "La suppression doit réussir"

    # Vérification post-suppression
    res = dao.db_connector.sql_query(
        "SELECT * FROM product WHERE id_product = %(id_product)s;",
        {"id_product": product.id_product},
        return_type="one",
    )
    assert res is None, "Le produit ne doit plus exister dans la DB"
