import pytest
from datetime import datetime
from src.Model.Order import Order
from src.Model.Address import Address
from src.Model.Product import Product
from src.DAO.OrderDAO import OrderDAO
from src.DAO.DBConnector import DBConnector
from dotenv import load_dotenv



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


def create_test_address(postalcode=35000, city="Rennes") -> Address:
    return Address(address="12 Yvonne Jean-Haffen Street", postalcode=postalcode, city=city)


# ---------------------------
# Création d'ordre
# ---------------------------
def test_create_order_ok(dao):
    order = Order(
        id_customer=999,
        id_driver=999,
        delivery_address=create_test_address(),
        total_amount=20.0,
        payment_method="cash",
        nb_items=2,
    )
    order_id = dao.create_order(order)
    assert order_id is not None
    assert order.id == order_id

def test_create_order_invalid_address(dao):
    # Adresse invalide (postal code non autorisé)
    order = Order(
        id_customer=999,
        id_driver=998,
        delivery_address=create_test_address(postalcode=99999, city="Rennes"),
        total_amount=15.0,
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
        id_customer=998,
        id_driver=999,
        delivery_address=create_test_address(),
        total_amount=0,
        payment_method="cash",
        nb_items=0,
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    added = dao.add_product(order_id, product_id=997, quantity=2)
    assert added is True

def test_add_product_invalid(dao):
    # Ajouter un produit sur un order_id inexistant
    added = dao.add_product(999999, product_id=1, quantity=2)
    assert added is False

def test_remove_product_ok(dao):
    order = Order(
        id_customer=998,
        id_driver=998,
        delivery_address=create_test_address(),
        total_amount=0,
        payment_method="cash",
        nb_items=0,
    )
    order_id = dao.create_order(order)
    dao.add_product(order_id, product_id=999, quantity=1)

    removed = dao.remove_product(order_id, product_id=999)
    assert removed is True

def test_remove_product_invalid(dao):
    # Retirer un produit qui n'existe pas dans la commande
    removed = dao.remove_product(order_id=999999, product_id=1)
    assert removed is False

def test_cancel_order_ok(dao):
    order = Order(
        id_customer=999,
        id_driver=999,
        delivery_address=create_test_address(),
        total_amount=10,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    cancelled = dao.cancel_order(order_id)
    assert cancelled is True

def test_cancel_order_invalid(dao):
    # Cancel order inexistant
    cancelled = dao.cancel_order(999999)
    assert cancelled is False


# ---------------------------
# Récupération par ID
# ---------------------------
def test_get_by_id_ok(dao):
    order = Order(
        id_customer=999,
        id_driver=998,
        delivery_address=create_test_address(),
        total_amount=15,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    retrieved = dao.get_by_id(order_id)
    assert retrieved is not None
    assert retrieved.id == order_id
    assert isinstance(retrieved.delivery_address, Address)


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
        id_customer=998,
        id_driver=999,
        delivery_address=create_test_address(),
        total_amount=10,
        payment_method="cash",
        nb_items=1,
    )
    order_id = dao.create_order(order)
    marked = dao.mark_as_delivered(order_id)
    assert marked is True


def test_mark_as_delivered_fail(dao):
    marked = dao.mark_as_delivered(999999)
    assert marked is False

def test_list_all_orders(dao):
    orders = dao.list_all_orders()
    assert isinstance(orders, list)
    for o in orders:
        assert isinstance(o, Order)
