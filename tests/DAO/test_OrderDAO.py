import pytest
from datetime import datetime
from dotenv import load_dotenv
from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from src.Model.Address import Address
from src.Model.Product import Product
from src.DAO.DBConnector import DBConnector
from utils.reset_database import ResetDatabase

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    order_dao = OrderDAO()
    order_dao.db_connector = DBConnector(test=True)
    return order_dao


def create_test_address():
    return Address(address="1 Test Street", city="Testville", postalcode=12345)


def create_test_product():
    return Product(
        id_product=1,
        name="Test Product",
        price=10.0,
        production_cost=5.0,
        product_type="lunch",
        description="Test product",
        stock=100,
    )


# ---------------------------
# Création d'ordre
# ---------------------------
def test_create_order_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=20.0,
        payment_method="cash",
        nb_items=2,
    )
    order_id = dao.create_order(order)
    assert order_id is not None
    assert order.id == order_id


def test_create_order_fail_invalid_address(dao):
    # Adresse None simule une erreur
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=None,
        total_amount=10.0,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    assert order_id is None


# ---------------------------
# Ajout / suppression produit
# ---------------------------
def test_add_product_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=0,
        payment_method="cash",
        nb_items=0,
    )
    order_id = dao.create_order(order)
    product = create_test_product()
    added = dao.add_product(order_id, product.id_product, 2)
    assert added


def test_add_product_fail_invalid_order(dao):
    product = create_test_product()
    added = dao.add_product(999999, product.id_product, 1)
    assert not added


def test_remove_product_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=0,
        payment_method="cash",
        nb_items=0,
    )
    order_id = dao.create_order(order)
    product = create_test_product()
    dao.add_product(order_id, product.id_product, 2)
    removed = dao.remove_product(order_id, product.id_product)
    assert removed


def test_remove_product_fail(dao):
    removed = dao.remove_product(999999, 1)
    assert not removed


# ---------------------------
# Annulation d'ordre
# ---------------------------
def test_cancel_order_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=10,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    cancelled = dao.cancel_order(order_id)
    assert cancelled
    assert dao.get_by_id(order_id) is None


def test_cancel_order_fail(dao):
    cancelled = dao.cancel_order(999999)
    assert not cancelled


# ---------------------------
# Récupération par ID
# ---------------------------
def test_get_by_id_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=15,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    retrieved = dao.get_by_id(order_id)
    assert retrieved is not None
    assert retrieved.id == order_id


def test_get_by_id_fail(dao):
    retrieved = dao.get_by_id(999999)
    assert retrieved is None


# ---------------------------
# Liste des commandes
# ---------------------------
def test_list_all_orders(dao):
    orders = dao.list_all_orders()
    assert isinstance(orders, list)


# ---------------------------
# Marquer comme livré
# ---------------------------
def test_mark_as_delivered_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=10,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    marked = dao.mark_as_delivered(order_id)
    assert marked
    retrieved = dao.get_by_id(order_id)
    assert retrieved.status == "delivered"


def test_mark_as_delivered_fail(dao):
    marked = dao.mark_as_delivered(999999)
    assert not marked


# ---------------------------
# Commandes assignées à un driver
# ---------------------------
def test_get_assigned_orders_ok(dao):
    order = Order(
        id_customer=1,
        id_driver=1,
        delivery_address=create_test_address(),
        total_amount=10,
        payment_method="cash",
        nb_items=1,
    )
    dao.create_order(order)
    assigned_orders = dao.get_assigned_orders(driver_id=1)
    assert isinstance(assigned_orders, list)
    for o in assigned_orders:
        assert o.id_driver == 1
        assert o.status == "waiting"


def test_get_assigned_orders_none(dao):
    assigned_orders = dao.get_assigned_orders(driver_id=999999)
    assert assigned_orders == []


if __name__ == "__main__":
    pytest.main([__file__])
