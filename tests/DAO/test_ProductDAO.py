import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.reset_database import ResetDatabase

load_dotenv()


# @pytest.fixture(autouse=True)
# def setup_test_environment():
# """Reset the test database before each test function"""
# ResetDatabase(test=True).lancer()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialize the test database environment"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configured for the test schema"""
    product_dao = ProductDAO(db_connector=DBConnector(test=True))
    product_dao.db_connector = DBConnector(test=True)
    return product_dao


# --- Tests ---


def test_create_ok(dao):
    """Test: Successfully create a new product in the database"""
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
    """Test: DAO should reject creation of a duplicate product"""

    product1 = Product(
        name="Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    assert dao.create_product(product1)

    product_duplicate = Product(
        name="Galette Saucisse",
        price=2.50,
        production_cost=2.00,
        description="simple galette saucisse",
        product_type="lunch",
        stock=15,
    )

    creation_ok = dao.create_product(product_duplicate)
    assert not creation_ok


def test_delete_ok(dao):
    """Test: Successfully delete a product from the database"""
    product = Product(
        name="Test Croque Monsieur",
        price=3.00,
        production_cost=2.00,
        description="Simple panini for test",
        product_type="lunch",
        stock=10,
    )

    assert dao.create_product(product)
    assert product.id_product is not None

    res = dao.db_connector.sql_query(
        "SELECT * FROM product WHERE id_product = %(id_product)s;",
        {"id_product": product.id_product},
        return_type="one",
    )
    assert res is not None

    suppression_ok = dao.deleting_product(product.id_product)
    assert suppression_ok

    res = dao.db_connector.sql_query(
        "SELECT * FROM product WHERE id_product = %(id_product)s;",
        {"id_product": product.id_product},
        return_type="one",
    )
    assert res is None


def test_delete_ko(dao):
    """Test: Deleting a non-existent product should fail"""
    non_existent_id = 99999
    delete_ok = dao.deleting_product(non_existent_id)

    assert not delete_ok


def test_get_all_products(dao):
    """Test: Retrieve all products from the database"""
    p1 = Product(
        name="Prod1",
        price=1.0,
        production_cost=0.5,
        description="desc1",
        product_type="drink",
        stock=5,
    )
    p2 = Product(
        name="Prod2",
        price=2.0,
        production_cost=1.0,
        description="desc2",
        product_type="dessert",
        stock=3,
    )
    dao.create_product(p1)
    dao.create_product(p2)

    all_products = dao.get_all_products()
    assert len(all_products) >= 2
    names = [p.name for p in all_products]
    assert "Prod1" in names
    assert "Prod2" in names


def test_get_all_product_names(dao):
    """Test: Verify that all product names are retrieved correctly"""
    products = [
        Product(
            name="Café",
            price=2.5,
            production_cost=1.0,
            product_type="drink",
            description="Café chaud",
            stock=10,
        ),
        Product(
            name="Croissant",
            price=1.5,
            production_cost=0.5,
            product_type="dessert",
            description="Croissant frais",
            stock=5,
        ),
    ]
    for p in products:
        dao.create_product(p)

    names = dao.get_all_product_names()
    for p in products:
        assert p.name in names


def test_get_all_product_names_descriptions(dao):
    """Test: Verify that all product names and descriptions are retrieved correctly"""
    products_to_add = [
        Product(
            name="Café",
            price=2.5,
            production_cost=1.0,
            product_type="drink",
            description="Café chaud",
            stock=10,
        ),
        Product(
            name="Croissant",
            price=1.5,
            production_cost=0.5,
            product_type="dessert",
            description="Croissant frais",
            stock=5,
        ),
    ]

    for p in products_to_add:
        dao.create_product(p)

    result = dao.get_all_product_names_descriptions()

    result_list = [[r["name"], r["description"]] for r in result]

    for p in products_to_add:
        assert [p.name, p.description] in result_list


def test_decrement_stock(dao):
    """Test: Verify that stock decreases correctly and prevents decrement if insufficient"""
    product = Product(
        name="decrement",
        price=5.0,
        production_cost=2.0,
        product_type="drink",
        description="Produit pour test decrement",
        stock=5,
    )
    dao.create_product(product)

    success = dao.decrement_stock(product.id_product, 3)
    assert success

    updated = [p for p in dao.get_all_products() if p.id_product == product.id_product][0]
    assert updated.stock == 2

    success = dao.decrement_stock(product.id_product, 3)
    assert not success


def test_increment_stock(dao):
    """Test: Verify that stock increases correctly when incrementing"""
    product = Product(
        name="increment",
        price=5.0,
        production_cost=2.0,
        product_type="drink",
        description="Produit pour test increment",
        stock=2,
    )
    dao.create_product(product)

    success = dao.increment_stock(product.id_product, 5)
    assert success

    updated = [p for p in dao.get_all_products() if p.id_product == product.id_product][0]
    assert updated.stock == 7


def test_get_available_products(dao):
    """Test: Only products with stock greater than 0 are returned."""
    product1 = Product(
        name="Disponible",
        price=2.0,
        production_cost=1.0,
        product_type="drink",
        description="Stock > 0",
        stock=3,
    )
    product2 = Product(
        name="Indisponible",
        price=2.0,
        production_cost=1.0,
        product_type="lunch",
        description="Stock = 0",
        stock=0,
    )
    dao.create_product(product1)
    dao.create_product(product2)

    available = dao.get_available_products()
    names = [p["name"] for p in available]
    assert "Disponible" in names
    assert "Indisponible" not in names


def test_get_id_by_productname(dao):
    """Test: Retrieve the product ID by its name"""
    product = Product(
        name="test_id",
        price=5.0,
        production_cost=2.0,
        product_type="drink",
        description="Produit pour test id",
        stock=2,
    )
    dao.create_product(product)
    id_product = dao.get_id_by_productname("test_id")
    assert id_product == product.id_product
