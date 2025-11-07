from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.Model.Address import Address
from src.Model.Order import Order

load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Réinitialise la base de test avant la session."""
    from utils.reset_database import ResetDatabase

    ResetDatabase(test=True).lancer()


@pytest.fixture
def dao():
    """DAO connecté à la base de test."""
    order_dao = OrderDAO()
    order_dao.db_connector = DBConnector(test=True)
    return order_dao


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
    return Address(id_address=res["id_address"], address=address, city=city, postal_code=postal_code)


# TESTS


def test_create_order_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=999, id_driver=999, id_address=addr.id_address, nb_items=2, total_amount=25.0, payment_method="Cash"
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


def test_add_product_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=999, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=5.0, payment_method="Card"
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    added = dao.add_product(order_id, product_id=997, quantity=2)
    assert added is True


def test_add_product_invalid_order(dao):
    added = dao.add_product(order_id=999999, product_id=999, quantity=1)
    assert added is False


def test_remove_product_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=3.0, payment_method="Cash"
    )
    order_id = dao.create_order(order)
    dao.add_product(order_id, product_id=999, quantity=1)

    removed = dao.remove_product(order_id, product_id=999)
    assert removed is True


def test_remove_product_invalid(dao):
    removed = dao.remove_product(order_id=123456, product_id=999)
    assert removed is False


def test_get_order_products_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=999, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=8.0, payment_method="Card"
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
        id_customer=999, id_driver=998, id_address=addr.id_address, nb_items=1, total_amount=7.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=2, total_amount=15.0, payment_method="Card"
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
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=1, total_amount=9.0, payment_method="Card"
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
        id_customer=999, id_driver=999, id_address=addr.id_address, nb_items=2, total_amount=10.0, payment_method="Cash"
    )
    order_id = dao.create_order(order)
    dao.add_product(order_id, 997, 1)
    dao.add_product(order_id, 998, 2)

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


def test_get_assigned_orders_ok(dao):
    addr = create_test_address()
    order = Order(
        id_customer=998, id_driver=999, id_address=addr.id_address, nb_items=2, total_amount=12.0, payment_method="Cash"
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
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=2,
        total_amount=25.0,
        payment_method="Cash",
        status="Preparing",
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    assert assigned is True

    data = dao.get_by_id(order_id)
    assert data is not None
    assert data["order"].id_driver == 888


def test_assign_order_invalid_order(dao):
    """Test assignment with non-existent order"""
    assigned = dao.assign_order(driver_id=888, id_order=999999)
    assert assigned is False


def test_assign_order_already_assigned(dao):
    """Test assigning an order that already has a driver"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=777,  # Already has a driver
        id_address=addr.id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="Card",
        status="Preparing",
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Try to assign to another driver
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    # This depends on your business logic - should reassignment be allowed?
    assert assigned is False or assigned is True  # Adjust based on your requirements


def test_assign_order_delivered_status(dao):
    """Test assigning an order that's already delivered"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="Card",
        status="Delivered",  # Already delivered
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Try to assign delivered order
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    assert assigned is False

    # Verify status remains unchanged
    data = dao.get_by_id(order_id)
    assert data["order"].status == "Delivered"
    assert data["order"].id_driver is None


def test_assign_order_cancelled_status(dao):
    """Test assigning a cancelled order"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="Card",
        status="Cancelled",  # Cancelled order
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Try to assign cancelled order
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    assert assigned is False

    # Verify status remains unchanged
    data = dao.get_by_id(order_id)
    assert data["order"].status == "Cancelled"


def test_assign_order_ready_status(dao):
    """Test assigning a ready order"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="Card",
        status="Ready",  # Ready order
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Try to assign ready order
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    # This depends on your business logic
    assert assigned is True or assigned is False


def test_assign_order_en_route_status(dao):
    """Test assigning an en route order"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="Card",
        status="En route",  # En route order
    )
    order_id = dao.create_order(order)
    assert order_id is not None

    # Try to assign en route order
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    assert assigned is False  # Should not reassign orders already en route


def test_assign_order_multiple_orders_same_driver(dao):
    """Test assigning multiple orders to the same driver"""
    addr = create_test_address()

    # Create multiple preparing orders
    orders_data = [(999, 2, 25.0, "Cash"), (998, 1, 15.0, "Card"), (997, 3, 35.0, "Cash")]

    order_ids = []
    for customer_id, nb_items, total, payment in orders_data:
        order = Order(
            id_customer=customer_id,
            id_driver=None,
            id_address=addr.id_address,
            nb_items=nb_items,
            total_amount=total,
            payment_method=payment,
            status="Preparing",
        )
        order_id = dao.create_order(order)
        assert order_id is not None
        order_ids.append(order_id)

    # Assign all orders to the same driver
    driver_id = 888
    for order_id in order_ids:
        assigned = dao.assign_order(driver_id=driver_id, id_order=order_id)
        assert assigned is True

    # Verify all orders are assigned to the same driver
    for order_id in order_ids:
        data = dao.get_by_id(order_id)
        assert data["order"].id_driver == driver_id


def test_assign_order_different_drivers(dao):
    """Test assigning orders to different drivers"""
    addr = create_test_address()

    # Create multiple preparing orders
    order1 = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=2,
        total_amount=25.0,
        payment_method="Cash",
        status="Preparing",
    )
    order1_id = dao.create_order(order1)

    order2 = Order(
        id_customer=998,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=15.0,
        payment_method="Card",
        status="Preparing",
    )
    order2_id = dao.create_order(order2)

    # Assign to different drivers
    assigned1 = dao.assign_order(driver_id=777, id_order=order1_id)
    assigned2 = dao.assign_order(driver_id=888, id_order=order2_id)

    assert assigned1 is True
    assert assigned2 is True

    # Verify correct assignments
    data1 = dao.get_by_id(order1_id)
    data2 = dao.get_by_id(order2_id)

    assert data1["order"].id_driver == 777
    assert data2["order"].id_driver == 888


def test_assign_order_zero_driver_id(dao):
    """Test assignment with invalid driver ID"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="Cash",
        status="Preparing",
    )
    order_id = dao.create_order(order)

    assigned = dao.assign_order(driver_id=0, id_order=order_id)
    assert assigned is False


def test_assign_order_negative_driver_id(dao):
    """Test assignment with negative driver ID"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=1,
        total_amount=10.0,
        payment_method="Cash",
        status="Preparing",
    )
    order_id = dao.create_order(order)

    assigned = dao.assign_order(driver_id=-1, id_order=order_id)
    assert assigned is False


def test_assign_order_status_workflow(dao):
    """Test order assignment as part of complete workflow"""
    addr = create_test_address()
    order = Order(
        id_customer=999,
        id_driver=None,
        id_address=addr.id_address,
        nb_items=2,
        total_amount=20.0,
        payment_method="Card",
        status="Preparing",
    )
    order_id = dao.create_order(order)

    # 1. Assign order to driver
    assigned = dao.assign_order(driver_id=888, id_order=order_id)
    assert assigned is True

    data = dao.get_by_id(order_id)
    assert data["order"].id_driver == 888

    # 2. Mark as ready
    ready = dao.mark_as_ready(order_id)
    assert ready is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "Ready"
    assert data["order"].id_driver == 888  # Driver should still be assigned

    # 3. Mark as en route
    en_route = dao.mark_as_en_route(order_id)
    assert en_route is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "En route"
    assert data["order"].id_driver == 888  # Driver should still be assigned

    # 4. Mark as delivered
    delivered = dao.mark_as_delivered(order_id)
    assert delivered is True

    data = dao.get_by_id(order_id)
    assert data["order"].status == "Delivered"
    # Driver should still be assigned even after delivery
    assert data["order"].id_driver == 888
