import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.Service.OrderService import OrderService
from src.utils.reset_database import ResetDatabase

ADDRESS_ID = 999


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the test database before each test."""
    ResetDatabase(test=True).lancer()


@pytest.fixture
def orderdao():
    """Order DAO connected to the test database."""
    return OrderDAO(DBConnector(test=True))


@pytest.fixture
def service(orderdao):
    """OrderService based on the DAO."""
    return OrderService(orderdao)


class TestOrderService:
    """Tests for OrderService."""

    def test_create_order_ok(self, service):
        """Test: Successfully create a new order"""
        order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        assert order_data is not None
        assert order_data.id_customer == 999
        assert order_data.total_amount == 0.0

    def test_add_product_to_order_ok(self, service):
        """Test: Add a product to an existing order"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        result = service.add_product_to_order(order.id_order, 999, 2)
        assert result is True

    def test_remove_product(self, service):
        """Test: Remove a product from an existing order"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        service.add_product_to_order(order.id_order, 999, 2)
        result = service.remove(order.id_order, 999, 1)
        assert result is True

    def test_mark_as_on_the_way_and_delivered(self, service):
        """Test: Mark an order as 'On the way' and then as 'Delivered'"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        assert service.mark_as_on_the_way(order.id_order) is True
        assert service.mark_as_delivered(order.id_order) is True

    def test_get_order_products(self, service):
        """Test: Retrieve all products for a given order"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        service.add_product_to_order(order.id_order, 999, 2)
        products = service.get_order_products(order.id_order)
        assert any(p["id_product"] == 999 for p in products)

    def test_get_by_id(self, service):
        """Test: Retrieve an order by its ID"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        fetched_order = service.get_by_id(order.id_order)
        assert fetched_order.id_order == order.id_order

    def test_list_all_orders(self, service):
        """Test: List all orders"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        orders = service.list_all_orders()
        assert any(o["id_order"] == order.id_order for o in orders)

    def test_list_all_orders_ready(self, service):
        """Test: List all orders with status 'Ready'"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        orders_ready = service.list_all_orders_ready()
        assert any(o["order"].id_order == order.id_order for o in orders_ready)

    def test_assign_and_get_assigned_orders(self, service):
        """Test: Assign an order to a driver and retrieve assigned orders"""
        order = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
        driver_id = 999
        assert service.assign_order(driver_id, order.id_order) is True
        assigned_orders = service.get_assigned_orders(driver_id)
        assert any(o["order"].id_order == order.id_order for o in assigned_orders)
