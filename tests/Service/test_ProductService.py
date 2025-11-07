import pytest
from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Service.ProductService import ProductService
from src.Model.Product import Product
from utils.reset_database import ResetDatabase

@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database avant chaque test"""
    ResetDatabase(test=True).lancer()

@pytest.fixture
def dao():
    """DAO pour tests"""
    return ProductDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """Service basé sur le DAO"""
    return ProductService(productdao=dao)


def test_create_ok(service):
    product = service.create(
        name="Test Burger",
        price=3.0,
        production_cost=2.0,
        product_type="lunch",
        description="Simple Burger",
        stock=10,
    )
    assert product is not None
    assert isinstance(product, Product)
    assert product.id_product is not None


def test_create_ko(service, monkeypatch):
    # On force la création à échouer
    monkeypatch.setattr(service.productdao, "create_product", lambda p: False)
    product = service.create(
        name="Test Panini KO",
        price=3.0,
        production_cost=2.0,
        product_type="lunch",
        description="Simple panini KO",
        stock=10,
    )
    assert product is None


def test_delete_ok(service):
    # Créer un produit pour le supprimer
    product = service.create(
        name="Test Delete",
        price=2.5,
        production_cost=1.5,
        product_type="lunch",
        description="Produit à supprimer",
        stock=5,
    )
    result = service.delete(product.id_product)
    assert result is True


def test_delete_ko(service):
    # Supprimer un id qui n'existe pas
    result = service.delete(999999)
    assert result is False


def test_get_list_products_names(service):
    # Ajouter des produits spécifiques
    products = [
        Product(name="Café", price=2.5, production_cost=1.0, product_type="drink", description="Café chaud", stock=10),
        Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert", description="Croissant frais", stock=5),
    ]
    for p in products:
        service.productdao.create_product(p)

    names = service.get_list_products_names()
    for p in products:
        assert p.name in names


def test_get_list_products_descriptions(service):
    products_to_add = [
        Product(name="Café", price=2.5, production_cost=1.0, product_type="drink", description="Café chaud", stock=10),
        Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert", description="Croissant frais",
        stock=5),
    ]

    for p in products_to_add:
        service.productdao.create_product(p)

    result = service.get_list_products_descriptions()
    result_list = [[r["name"], r["description"]] if isinstance(r, dict) else r for r in result]

    for p in products_to_add:
        assert [p.name, p.description] in result_list

