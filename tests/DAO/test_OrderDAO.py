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

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Réinitialise la base de test avant la session."""
    from utils.reset_database import ResetDatabase

    ResetDatabase(test=True).lancer()


@pytest.fixture
def db():
    """Connexion unique à la base de test."""
    return DBConnector(test=True)


@pytest.fixture
def dao(db):
    """DAO commandes utilisant la même connexion que les produits."""
    return OrderDAO(db)


@pytest.fixture
def productdao(db):
    """DAO produits utilisant la même connexion que les commandes."""
    return ProductDAO(db)


def create_test_address(address="15 Rue du Test", city="Rennes", postal_code="35000"):
    """Insère une adresse de test dans la base et la renvoie."""
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
    """Crée un driver de test en utilisant DriverDAO et retourne son ID."""
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


# TESTS


def test_create_order_ok(dao):
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


def test_create_order_invalid_customer(dao):
    addr = create_test_address()
    order = Order(
        id_customer=123456,  # inexistant
        id_driver=999,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="Cash",
    )
    order_id = dao.create_order(order)
    assert order_id is None


def test_add_product_ok(dao, productdao):
    """Vérifie que l'ajout de produit fonctionne et décrémente le stock"""
    # Création produit de test
    product = Product(
        name="Produit Test Add",
        price=5.0,
        production_cost=2.0,
        product_type="drink",
        description="Pour test add_product",
        stock=10,
    )
    productdao.create_product(product)

    # Création adresse et commande
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
    assert order_id is not None

    # Ajouter produit
    added = dao.add_product(order_id, product_id=product.id_product, quantity=3)
    assert added is True

    # Vérifier que le stock a diminué
    raw = productdao.db_connector.sql_query(
        "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
    )
    assert raw["stock"] == 7  # 10 - 3


def test_add_product_invalid_order(dao, productdao):
    """Vérifie que l'ajout échoue pour un order inexistant"""
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

    # Vérifier que le stock n'a pas été décrémenté
    raw = productdao.db_connector.sql_query(
        "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
    )
    assert raw["stock"] == 5


def test_remove_product_ok(dao, productdao):
    """Vérifie que la suppression d'un produit fonctionne et remet le stock"""
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

    # Vérifier que le stock est revenu
    raw = productdao.db_connector.sql_query(
        "SELECT stock FROM product WHERE id_product = %s", [product.id_product], "one"
    )
    assert raw["stock"] == 5


def test_remove_product_invalid(dao):
    """Vérifie que la suppression échoue pour un produit ou order inexistant"""
    removed = dao.remove_product(order_id=123456, product_id=999)
    assert removed is False


def test_get_order_products_ok(dao):
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


def test_get_order_products_invalid(dao):
    products = dao.get_order_products(order_id=999999)
    assert products == []


def test_cancel_order_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=998,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=7.0,
        payment_method="Card",
    )
    order_id = dao.create_order(order)
    cancelled = dao.cancel_order(order_id)
    assert cancelled is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].status == "Cancelled"


def test_cancel_order_invalid(dao):
    cancelled = dao.cancel_order(987654)
    assert cancelled is False


def test_mark_as_delivered_ok(dao):
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


def test_mark_as_delivered_invalid(dao):
    delivered = dao.mark_as_delivered(999999)
    assert delivered is False


def test_mark_as_ready_ok(dao):
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
    marked = dao.mark_as_ready(order_id)
    assert marked is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].status == "Ready"


def test_mark_as_ready_invalid_order(dao):
    marked = dao.mark_as_ready(999999)  # ID qui n'existe pas
    assert marked is False


def test_mark_as_en_route_ok(dao):
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

    dao.mark_as_ready(order_id)

    marked = dao.mark_as_en_route(order_id)
    assert marked is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].status == "En route"


def test_mark_as_en_route_from_ready(dao):
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

    marked = dao.mark_as_en_route(order_id)
    assert marked is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].status == "En route"


def test_mark_as_en_route_invalid_order(dao):
    marked = dao.mark_as_en_route(999999)
    assert marked is False


def test_mark_as_ready_twice(dao):
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

    marked1 = dao.mark_as_ready(order_id)
    assert marked1 is True

    marked2 = dao.mark_as_ready(order_id)
    assert marked2 is True
    data = dao.get_by_id(order_id)
    assert data["order"].status == "Ready"


def test_mark_as_ready_updates_date(dao):
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

    data_before = dao.get_by_id(order_id)
    before_date = data_before["order"].date

    import time

    time.sleep(1)

    dao.mark_as_ready(order_id)

    data_after = dao.get_by_id(order_id)
    after_date = data_after["order"].date

    assert after_date >= before_date


def test_mark_multiple_status_changes(dao):
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

    ready = dao.mark_as_ready(order_id)
    assert ready is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "Ready"

    en_route = dao.mark_as_en_route(order_id)
    assert en_route is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "En route"

    delivered = dao.mark_as_delivered(order_id)
    assert delivered is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "Delivered"


def test_mark_as_ready_with_products(dao):
    addr = create_test_address()
    order = Order(
        id_customer=998,
        id_driver=999,
        id_address=addr.id_address,
        nb_items=2,
        total_amount=15.0,
        payment_method="Card",
    )
    order_id = dao.create_order(order)

    dao.add_product(order_id, product_id=997, quantity=1)
    dao.add_product(order_id, product_id=998, quantity=2)

    marked = dao.mark_as_ready(order_id)
    assert marked is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].status == "Ready"
    assert len(data["products"]) == 2


def test_mark_status_sequence(dao):
    """Test une séquence complète de statuts"""
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

    data = dao.get_by_id(order_id)
    initial_status = data["order"].status
    assert initial_status in ["Preparing", "Ready"]

    assert dao.mark_as_ready(order_id) is True
    assert dao.get_by_id(order_id)["order"].status == "Ready"

    assert dao.mark_as_en_route(order_id) is True
    assert dao.get_by_id(order_id)["order"].status == "En route"

    assert dao.mark_as_delivered(order_id) is True
    assert dao.get_by_id(order_id)["order"].status == "Delivered"


def test_get_by_id_ok(dao):
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


def test_get_by_id_invalid(dao):
    data = dao.get_by_id(999999)
    assert data is None


def test_list_all_orders(dao):
    orders = dao.list_all_orders()
    assert isinstance(orders, list)
    for entry in orders:
        assert isinstance(entry, dict)
        assert "order" in entry and "products" in entry
        assert isinstance(entry["order"], Order)


def test_list_all_orders_ready(dao):
    # Créer une adresse de test
    addr = create_test_address()

    # Créer une commande
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=2,
        total_amount=20.0,
        payment_method="Cash",
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Vérifier que la commande n'est pas dans les commandes "Ready" au départ
    ready_orders_before = dao.list_all_orders_ready()
    assert all(o["order"].id_order != order_id for o in ready_orders_before)

    # Marquer la commande comme prête
    marked = dao.mark_as_ready(order_id)
    assert marked is True

    # Récupérer les commandes prêtes
    ready_orders = dao.list_all_orders_ready()
    assert isinstance(ready_orders, list)

    # Vérifier que notre commande est dans la liste
    assert any(o["order"].id_order == order_id for o in ready_orders)

    # vérifier que le statut est bien "Ready"
    for o in ready_orders:
        if o["order"].id_order == order_id:
            assert o["order"].status == "Ready"


def test_get_assigned_orders_ok(dao):
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

    assigned = dao.get_assigned_orders(driver_id=999)
    assert isinstance(assigned, list)
    assert any(o["order"].id_order == order_id for o in assigned)


def test_get_assigned_orders_empty(dao):
    assigned = dao.get_assigned_orders(driver_id=123456)
    assert assigned == []


def test_assign_order_ok(dao):
    """Test successful assignment of an order to a driver"""
    # Create a test driver first
    driver_id = create_test_driver(user_name=f"driver1_{datetime.now().timestamp()}")
    assert driver_id is not None

    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=driver_id,  # Use valid driver ID
        id_address=addr.id_address,
        nb_items=2,
        total_amount=25.0,
        payment_method="Cash",
        status="Preparing",
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Create another driver for assignment
    new_driver_id = create_test_driver(
        user_name=f"newdriver_{datetime.now().timestamp()}",
        first_name="New",
        last_name="Driver",
    )
    assert new_driver_id is not None

    # Assign order to new driver
    assigned = dao.assign_order(new_driver_id, order_id)
    assert assigned is True

    # Verify the assignment
    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].id_driver == new_driver_id
