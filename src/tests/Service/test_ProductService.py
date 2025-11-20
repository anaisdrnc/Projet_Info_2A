import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from src.Service.ProductService import ProductService
from src.utils.reset_database import ResetDatabase


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database before each test."""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """Product DAO for tests."""
    return ProductDAO(DBConnector(test=True))


@pytest.fixture
def service(dao):
    """ProductService based on the DAO."""
    return ProductService(productdao=dao)


class TestProductService:
    """Tests for ProductService."""

    def test_create_ok(self, service):
        """Test: Successfully create a new product."""
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

    def test_create_ko(self, service, monkeypatch):
        """Test: Product creation fails (returns None)."""
        monkeypatch.setattr(service.productdao, "create_product", lambda p: None)
        product = service.create(
            name="Test Panini KO",
            price=3.0,
            production_cost=2.0,
            product_type="lunch",
            description="Simple panini KO",
            stock=10,
        )
        assert product is None

    def test_delete_ok(self, service):
        """Test: Successfully delete an existing product."""
        product = service.create(
            name="Test Delete",
            price=2.5,
            production_cost=1.5,
            product_type="lunch",
            description="Product to delete",
            stock=5,
        )
        result = service.delete(product.id_product)
        assert result is True

    def test_delete_ko(self, service):
        """Test: Deleting a non-existent product returns False."""
        result = service.delete(999999)
        assert result is False

    def test_get_list_products_names(self, service):
        """Test: Retrieve the list of product names."""
        products = [
            Product(name="Coffee", price=2.5, production_cost=1.0, product_type="drink",
            description="Hot coffee", stock=10),
            Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert",
            description="Fresh croissant", stock=5),
        ]
        for p in products:
            service.productdao.create_product(p)

        names_id = service.get_list_products_names()
        names_only = [n[0] for n in names_id]
        for p in products:
            assert p.name in names_only

    def test_get_list_products_descriptions(self, service):
        """Test: Retrieve the list of product names with descriptions."""
        products_to_add = [
            Product(name="Coffee", price=2.5, production_cost=1.0, product_type="drink",
            description="Hot coffee", stock=10),
            Product(name="Croissant", price=1.5, production_cost=0.5, product_type="dessert",
            description="Fresh croissant", stock=5),
        ]
        for p in products_to_add:
            service.productdao.create_product(p)

        result = service.get_list_products_descriptions()
        result_list = [[r["name"], r["description"]] if isinstance(r, dict) else r for r in result]

        for p in products_to_add:
            assert [p.name, p.description] in result_list

    def test_get_available_products(self, service):
        """Test: Retrieve only products with stock > 0."""
        products = [
            Product(name="Available 1", price=2.0, production_cost=1.0, product_type="drink",
            description="Available", stock=5),
            Product(name="Unavailable", price=3.0, production_cost=1.5, product_type="lunch",
            description="Stock 0", stock=0),
        ]
        for p in products:
            service.productdao.create_product(p)

        available = service.get_available_products()
        names = [p["name"] for p in available]
        assert "Available 1" in names
        assert "Unavailable" not in names

    def test_decrement_stock_ok(self, service):
        """Test: Successfully decrement product stock."""
        product = service.create(
            name="Stock OK",
            price=2.0,
            production_cost=1.0,
            product_type="dessert",
            description="Test decrement",
            stock=10,
        )
        result = service.decrement_stock(product.id_product, quantity=3)
        assert result is True

        raw = service.productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 7

    def test_decrement_stock_ko(self, service):
        """Test: Decrementing stock fails when quantity exceeds available stock."""
        product = service.create(
            name="Stock KO",
            price=2.0,
            production_cost=1.0,
            product_type="dessert",
            description="Test decrement KO",
            stock=1,
        )
        result = service.decrement_stock(product.id_product, quantity=5)
        assert result is False

        raw = service.productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 1

    def test_increment_stock(self, service):
        """Test: Successfully increment product stock."""
        product = service.create(
            name="Increment Test",
            price=2.0,
            production_cost=1.0,
            product_type="dessert",
            description="Test increment",
            stock=5,
        )
        result = service.increment_stock(product.id_product, quantity=4)
        assert result is True

        raw = service.productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 9
