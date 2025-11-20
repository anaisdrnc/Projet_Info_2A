from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.DAO.ProductDAO import ProductDAO
from src.DAO.UserRepo import UserRepo
from src.Model.Address import Address
from src.Model.Driver import Driver
from src.Model.Order import Order
from src.Model.Product import Product
from src.utils.reset_database import ResetDatabase

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Reset DB before tests"""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def db():
    return DBConnector(test=True)


@pytest.fixture
def dao(db):
    return OrderDAO(db)


@pytest.fixture
def productdao(db):
    return ProductDAO(db)


def create_test_address(address="15 Rue du Test", city="Rennes", postal_code="35000"):
    """Helper: insert a test address and return Address object"""
    db = DBConnector(test=True)
    res = db.sql_query(
        """
        INSERT INTO address (address, city, postal_code)
        VALUES (%s, %s, %s)
        RETURNING id_address
        """,
        [address, city, postal_code],
        "one",
    )
    return Address(
        id_address=res["id_address"],
        address=address,
        city=city,
        postal_code=postal_code,
    )


def create_test_driver(
    user_name=None,
    first_name="Test",
    last_name="Driver",
    email=None,
    password="password",
    mean_of_transport="Bike",
):
    """Helper: create a driver in the test DB"""
    if email is None:
        email = f"driver_{datetime.now().timestamp()}@test.com"
    if user_name is None:
        user_name = f"testdriver_{datetime.now().timestamp()}"

    salt = "mock_salt_for_testing_12345"
    hashed_password = f"hashed_{password}_{salt}"

    driver = Driver(
        user_name=user_name,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=hashed_password,
        salt=salt,
        mean_of_transport=mean_of_transport,
    )

    driver_dao = DriverDAO()
    driver_dao.db_connector = DBConnector(test=True)
    driver_dao.user_repo = UserRepo(driver_dao.db_connector)

    success = driver_dao.create(driver)
    if success:
        return driver.id_driver
    return None


class TestOrderDAO:
    """Tests for OrderDAO"""

    def test_create_order_ok(self, dao):
        """Creating a new order with a valid address succeeds and returns the order ID."""
        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=0,
            total_amount=0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        assert order_id is not None
        assert isinstance(order_id, int)

    def test_create_order_invalid_customer(self, dao):
        """Creating an order with a non-existent customer ID fails."""
        addr = create_test_address()
        order = Order(
            id_customer=123456,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=1,
            total_amount=10.0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        assert order_id is None

    def test_add_product_ok(self, dao, productdao):
        """Adding a product to an order succeeds and decrements stock."""
        product = Product(
            name="Produit Test Add",
            price=5.0,
            production_cost=2.0,
            product_type="drink",
            description="Pour test add_product",
            stock=10,
        )
        productdao.create_product(product)

        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=0,
            total_amount=0,
            payment_method="Card",
        )
        order_id = dao.create_order(order)
        added = dao.add_product(order_id, product_id=product.id_product, quantity=3)
        assert added is True

        raw = productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 7

    def test_add_product_invalid_order(self, dao, productdao):
        """Adding a product fails for a non-existent order."""
        product = Product(
            name="Produit Test Invalid",
            price=5.0,
            production_cost=2.0,
            product_type="drink",
            description="Pour test add_product invalid",
            stock=5,
        )
        productdao.create_product(product)

        added = dao.add_product(order_id=999999, product_id=product.id_product, quantity=1)
        assert added is False

        raw = productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 5

    def test_remove_product_ok(self, dao, productdao):
        """Removing a product from an order succeeds and restores stock."""
        product = Product(
            name="Produit Test Remove",
            price=3.0,
            production_cost=1.0,
            product_type="drink",
            description="Pour test remove_product",
            stock=5,
        )
        productdao.create_product(product)

        addr = create_test_address()
        order = Order(
            id_customer=998,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=0,
            total_amount=0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        dao.add_product(order_id, product_id=product.id_product, quantity=2)

        removed = dao.remove_product(order_id, product_id=product.id_product, quantity=2)
        assert removed is True

        raw = productdao.db_connector.sql_query(
            "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
        )
        assert raw["stock"] == 5

    def test_remove_product_invalid(self, dao):
        """Removing a product from a non-existent order fails."""
        removed = dao.remove_product(order_id=123456, product_id=999)
        assert removed is False

    def test_get_order_products_ok(self, dao):
        """Retrieve all products associated with an existing order."""
        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=1,
            total_amount=8.0,
            payment_method="Card",
        )
        order_id = dao.create_order(order)
        dao.add_product(order_id, product_id=998, quantity=2)

        products = dao.get_order_products(order_id)
        assert isinstance(products, list)
        assert len(products) == 1
        assert products[0]["id_product"] == 998
        assert products[0]["quantity"] == 2

    def test_get_order_products_invalid(self, dao):
        """Attempt to retrieve products for a non-existent order returns empty list."""
        products = dao.get_order_products(order_id=999999)
        assert products == []

    def test_mark_as_delivered_ok(self, dao):
        """Mark an existing order as delivered successfully."""
        addr = create_test_address()
        order = Order(
            id_customer=998,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=1,
            total_amount=9.0,
            payment_method="Card",
        )
        order_id = dao.create_order(order)
        delivered = dao.mark_as_delivered(order_id)
        assert delivered is True

    def test_mark_as_delivered_invalid(self, dao):
        """Marking a non-existent order as delivered fails."""
        delivered = dao.mark_as_delivered(999999)
        assert delivered is False

    def test_mark_as_on_the_way_ok(self, dao):
        """Mark an existing order as on the way successfully."""
        addr = create_test_address()
        order = Order(
            id_customer=998,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=1,
            total_amount=9.0,
            payment_method="Card",
        )
        order_id = dao.create_order(order)
        marked = dao.mark_as_on_the_way(order_id)
        assert marked is True

        data = dao.get_by_id(order_id)
        assert data["order"].status == "On the way"

    def test_mark_as_on_the_way_invalid_order(self, dao):
        """Marking a non-existent order as on the way fails."""
        marked = dao.mark_as_on_the_way(999999)
        assert marked is False

    def test_mark_multiple_status_changes(self, dao):
        """Verify an order can go from Ready → On the way → Delivered."""
        addr = create_test_address()
        order = Order(
            id_customer=998,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=1,
            total_amount=9.0,
            payment_method="Card",
        )
        order_id = dao.create_order(order)

        # Ready → On the way
        dao.mark_as_on_the_way(order_id)
        data = dao.get_by_id(order_id)
        assert data["order"].status == "On the way"

        # On the way → Delivered
        dao.mark_as_delivered(order_id)
        data = dao.get_by_id(order_id)
        assert data["order"].status == "Delivered"

    def test_get_by_id_ok(self, dao):
        """Retrieve an existing order with address and products."""
        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=2,
            total_amount=10.0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        dao.add_product(order_id, 997, 1)
        dao.add_product(order_id, 999, 2)

        data = dao.get_by_id(order_id)
        assert data is not None
        assert "order" in data and "address" in data and "products" in data
        assert data["order"].id_order == order_id
        assert len(data["products"]) == 2

    def test_get_by_id_invalid(self, dao):
        """Retrieve a non-existent order by ID returns None."""
        data = dao.get_by_id(999999)
        assert data is None

    def test_list_all_orders(self, dao):
        """Retrieve all orders with products."""
        orders = dao.list_all_orders()
        assert isinstance(orders, list)
        for entry in orders:
            assert isinstance(entry, dict)
            assert "order" in entry and "products" in entry
            assert isinstance(entry["order"], Order)

    def test_get_assigned_orders_ok(self, dao):
        """Retrieve orders assigned to a specific driver."""
        addr = create_test_address()
        order = Order(
            id_customer=998,
            id_driver=999,
            id_address=addr.id_address,
            nb_items=2,
            total_amount=12.0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        dao.add_product(order_id, 999, 1)

        assigned = dao.get_assigned_orders(999)
        assert isinstance(assigned, list)
        assert any(o["order"].id_order == order_id for o in assigned)

    def test_get_assigned_orders_empty(self, dao):
        """No orders returned for a driver with no assigned orders."""
        assigned = dao.get_assigned_orders(123456)
        assert assigned == []

    def test_assign_order_ok(self, dao):
        """Successfully assign an existing order to a new driver."""
        driver_id = create_test_driver(user_name=f"driver1_{datetime.now().timestamp()}")
        assert driver_id is not None

        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=driver_id,
            id_address=addr.id_address,
            nb_items=2,
            total_amount=25.0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        new_driver_id = create_test_driver(
            user_name=f"newdriver_{datetime.now().timestamp()}",
            first_name="New",
            last_name="Driver",
        )
        assigned = dao.assign_order(new_driver_id, order_id)
        assert assigned is True
        data = dao.get_by_id(order_id)
        assert data["order"].id_driver == new_driver_id

    def test_list_all_orders_ready(self, dao):
        """Only orders marked as 'Ready' are returned."""
        addr = create_test_address()
        order = Order(
            id_customer=999,
            id_driver=None,
            id_address=addr.id_address,
            nb_items=2,
            total_amount=20.0,
            payment_method="Cash",
        )
        order_id = dao.create_order(order)
        ready_orders = dao.list_all_orders_ready()
        found = any(entry["order"].id_order == order_id for entry in ready_orders)
        assert found
        for entry in ready_orders:
            assert isinstance(entry, dict)
            assert "order" in entry and "address" in entry and "products" in entry
            assert isinstance(entry["order"], Order)
