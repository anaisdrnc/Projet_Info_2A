import pytest
from pprint import pprint
from src.Service.OrderService import OrderService
from src.DAO.OrderDAO import OrderDAO
from src.DAO.DBConnector import DBConnector

ADDRESS_ID = 999

@pytest.fixture(autouse=True)
def reset_db():
    """Reset la base de test avant chaque test"""
    from utils.reset_database import ResetDatabase
    ResetDatabase(test=True).lancer()

@pytest.fixture
def orderdao():
    """DAO Order connecté à la DB test"""
    return OrderDAO(DBConnector(test=True))

@pytest.fixture
def service(orderdao):
    """Service Order basé sur le DAO"""
    return OrderService(orderdao)

def test_create_order_ok(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    assert order_data is not None
    assert order_data['order'].id_customer == 999
    assert order_data['order'].total_amount == 0.0

def test_add_product_to_order_ok(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    result = service.add_product_to_order(order.id_order, 999, 2)
    assert result is True

def test_remove_product(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    service.add_product_to_order(order.id_order, 999, 2)
    result = service.remove(order.id_order, 999, 1)
    assert result is True

def test_cancel_order(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    service.add_product_to_order(order.id_order, 999, 2)
    result = service.cancel_order(order.id_order)
    assert result is True

def test_mark_as_ready_and_delivered(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    assert service.mark_as_ready(order.id_order) is True
    assert service.mark_as_delivered(order.id_order) is True

def test_get_order_products(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    service.add_product_to_order(order.id_order, 999, 2)
    products = service.get_order_products(order.id_order)
    assert any(p['id_product'] == 999 for p in products)

def test_get_by_id(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    fetched_order = service.get_by_id(order.id_order)
    assert fetched_order['order'].id_order == order.id_order

def test_list_all_orders(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    orders = service.list_all_orders()
    assert any(o['order'].id_order == order.id_order for o in orders)

def test_list_all_orders_ready(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    service.mark_as_ready(order.id_order)

    orders_ready = service.list_all_orders_ready()
    pprint(orders_ready)

    assert any(o['order'].id_order == order.id_order for o in orders_ready)


def test_assign_and_get_assigned_orders(service):
    order_data = service.create(999, ADDRESS_ID, 0, 0.0, "Cash")
    order = order_data['order']
    assert service.assign_order(999, order.id_order) is True
    assigned_orders = service.get_assigned_orders(999)
    assert any(o['order'].id_order == order.id_order for o in assigned_orders)
