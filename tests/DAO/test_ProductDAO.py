# import os
# from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.reset_database import ResetDatabase

load_dotenv()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Reset the test database before each test function"""
    ResetDatabase(test=True).lancer()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    product_dao = ProductDAO(db_connector=DBConnector(test=True))
    product_dao.db_connector = DBConnector(test=True)
    return product_dao


def test_create_ok(dao):
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

    creation_ok = dao.create_product(product)
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


def test_delete_ko(dao):
    non_existent_id = 99999
    delete_ok = dao.deleting_product(non_existent_id)

    assert not delete_ok

def test_get_all_products(dao):
    # Ajouter deux produits
    p1 = Product(name="Prod1", price=1.0, production_cost=0.5, description="desc1", product_type="drink", stock=5)
    p2 = Product(name="Prod2", price=2.0, production_cost=1.0, description="desc2", product_type="dessert", stock=3)
    dao.create_product(p1)
    dao.create_product(p2)

    all_products = dao.get_all_products()
    assert len(all_products) >= 2
    names = [p.name for p in all_products]
    assert "Prod1" in names
    assert "Prod2" in names

def test_get_all_product_names(dao):
    """Vérifie que les noms des produits sont récupérés correctement"""
    products = [
        Product(name="Café", price=2.5, production_cost=1.0, product_type="drink", description="Café chaud", stock=10),
        Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert", description="Croissant frais", stock=5),
    ]
    for p in products:
        dao.create_product(p)

    names = dao.get_all_product_names()
    for p in products:
        assert p.name in names

def test_get_all_product_names_descriptions(dao):
    """Vérifie que les noms et descriptions des produits sont récupérés correctement"""
    products = [
        Product(name="Café", price=2.5, production_cost=1.0, product_type="drink", description="Café chaud", stock=10),
        Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert", description="Croissant frais", stock=5),
    ]
    for p in products:
        dao.create_product(p)

    result = dao.get_all_product_names_descriptions()
    for p in products:
        assert [p.name, p.description] in result