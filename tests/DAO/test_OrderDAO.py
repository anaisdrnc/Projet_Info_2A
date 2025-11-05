import pytest
from datetime import datetime
from src.Model.Order import Order
from src.DAO.OrderDAO import OrderDAO
from src.DAO.DBConnector import DBConnector
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialiser la base de test"""
    from utils.reset_database import ResetDatabase
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO configuré pour le schéma test"""
    order_dao = OrderDAO(test=True)
    order_dao.db_connector = DBConnector(test=True)
    return order_dao


def create_test_address():
    """Crée une adresse temporaire dans la base"""
    db = DBConnector(test=True)
    res = db.sql_query(
        "INSERT INTO address (address, city, postal_code) VALUES (%s, %s, %s) RETURNING id_address",
        ["10 Rue du Test", "Rennes", "35000"],
        "one",
    )
    return res["id_address"]


# -------------------------
# TESTS DE BASE
# -------------------------

def test_create_order_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=1,
        id_driver=1,
        id_address=id_address,
        nb_items=2,
        total_amount=25.5,
        payment_method="cash",
    )
    order_id = dao.create_order(order)
    assert order_id is not None
    retrieved = dao.get_by_id(order_id)
    assert retrieved is not None
    assert retrieved.id_order == order_id


def test_add_product_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=2,
        id_driver=2,
        id_address=id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="cash",
    )
    order_id = dao.create_order(order)
    assert order_id is not None
    added = dao.add_product(order_id, product_id=1, quantity=2)
    assert added is True


def test_add_product_invalid_order(dao):
    added = dao.add_product(order_id=999999, product_id=1, quantity=1)
    assert added is False


def test_remove_product_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=3,
        id_driver=3,
        id_address=id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="cash",
    )
    order_id = dao.create_order(order)
    dao.add_product(order_id, product_id=1, quantity=1)
    removed = dao.remove_product(order_id, product_id=1)
    assert removed is True


def test_remove_product_invalid(dao):
    removed = dao.remove_product(order_id=999999, product_id=1)
    assert removed is False


def test_cancel_order_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=4,
        id_driver=4,
        id_address=id_address,
        nb_items=1,
        total_amount=20.0,
        payment_method="card",
    )
    order_id = dao.create_order(order)
    cancelled = dao.cancel_order(order_id)
    assert cancelled is True


def test_cancel_order_invalid(dao):
    cancelled = dao.cancel_order(999999)
    assert cancelled is False


def test_get_by_id_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=5,
        id_driver=5,
        id_address=id_address,
        nb_items=1,
        total_amount=9.99,
        payment_method="cash",
    )
    order_id = dao.create_order(order)
    retrieved = dao.get_by_id(order_id)
    assert retrieved is not None
    assert retrieved.id_order == order_id
    assert isinstance(retrieved.total_amount, float)


def test_get_by_id_invalid(dao):
    retrieved = dao.get_by_id(999999)
    assert retrieved is None


def test_mark_as_delivered_ok(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=6,
        id_driver=6,
        id_address=id_address,
        nb_items=2,
        total_amount=18.5,
        payment_method="card",
    )
    order_id = dao.create_order(order)
    marked = dao.mark_as_delivered(order_id)
    assert marked is True
    retrieved = dao.get_by_id(order_id)
    assert retrieved.status == "Delivered"


def test_mark_as_delivered_invalid(dao):
    marked = dao.mark_as_delivered(999999)
    assert marked is False


def test_list_all_orders(dao):
    orders = dao.list_all_orders()
    assert isinstance(orders, list)
    if orders:
        assert isinstance(orders[0], Order)


def test_list_orders_by_customer(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=99,
        id_driver=1,
        id_address=id_address,
        nb_items=3,
        total_amount=42.0,
        payment_method="cash",
    )
    dao.create_order(order)
    orders = dao.list_orders_by_customer(99)
    assert isinstance(orders, list)
    assert all(o.id_customer == 99 for o in orders)


def test_list_orders_by_driver(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=10,
        id_driver=88,
        id_address=id_address,
        nb_items=1,
        total_amount=12.5,
        payment_method="cash",
    )
    dao.create_order(order)
    orders = dao.list_orders_by_driver(88)
    assert isinstance(orders, list)
    assert all(o.id_driver == 88 for o in orders)


def test_list_delivered_orders(dao):
    id_address = create_test_address()
    order = Order(
        id_customer=12,
        id_driver=12,
        id_address=id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="card",
    )
    order_id = dao.create_order(order)
    dao.mark_as_delivered(order_id)
    delivered = dao.list_delivered_orders()
    assert isinstance(delivered, list)
    if delivered:
        assert all(o.status == "Delivered" for o in delivered)
