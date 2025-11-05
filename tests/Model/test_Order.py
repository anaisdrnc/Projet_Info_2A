from datetime import datetime

import pytest
from pydantic import ValidationError

from src.Model.Address import Address
from src.Model.Order import Order


def test_order_constructor_ok():
    """Constructor test"""
    order = Order(
        id=3,
        id_customer=1,
        id_driver=2,
        delivery_address=Address(
            address="4 rue de Dinan", postalcode=35000, city="Rennes"
        ),
        date="2025-10-23 12:30:00",
        status="waiting",
        total_amount=45.3,
        payment_method="cash",
        nb_items=2,
        products=[{"id_product": 1, "quantity": 2}],
    )
    assert order.id == 3
    assert order.id_customer == 1
    assert order.id_driver == 2
    assert order.delivery_address == Address(
        address="4 rue de Dinan", postalcode=35000, city="Rennes"
    )
    assert order.date == datetime(2025, 10, 23, 12, 30, 0)
    assert order.status == "waiting"
    assert order.total_amount == 45.3
    assert order.payment_method == "cash"
    assert order.nb_items == 2
    assert order.products == [{"id_product": 1, "quantity": 2}]


def test_order_constructor_on_incorrect_id():
    """Test : id must be an integer"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id="three",
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount=45.3,
            payment_method="cash",
            nb_items=2,
        )
    assert "id" in str(exc.value)


def test_order_constructor_on_incorrect_date():
    """Test : date must be a datetime"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            date=[2025, 10, 23],
            total_amount=45.3,
            payment_method="cash",
            nb_items=2,
        )
    assert "date" in str(exc.value)


def test_order_constructor_on_incorrect_status():
    """Test : Status must be one of the allowed literals ('delivered' or 'waiting')"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            status="ok",
            total_amount=45.3,
            payment_method="cash",
            nb_items=2,
        )
    assert "status" in str(exc.value)
    assert "literal_error" in str(exc.value)


def test_order_constructor_on_incorrect_delivery_address():
    """Test : delivery address must be valid"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city=12345
            ),
            total_amount=45.3,
            payment_method="cash",
            nb_items=2,
        )
    assert "city" in str(exc.value)


def test_order_constructor_on_incorrect_total_amount():
    """Test : total amount must be a float"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount="quarante",
            payment_method="cash",
            nb_items=2,
        )
    assert "total_amount" in str(exc.value)


def test_order_constructor_on_negative_total_amount():
    """Test : total_amount must be strictly greater than 0."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount=-14.67,
            payment_method="cash",
            nb_items=2,
        )
    assert "greater_than" in str(exc.value)


def test_order_constructor_on_total_amount_equal_to_zero():
    """Test : total_amount must be strictly greater than 0."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount=0.00,
            payment_method="cash",
            nb_items=2,
        )
    assert "greater_than" in str(exc.value)


def test_order_constructor_on_incorrect_payment_method():
    """Test : payment method must be one of the allowed literals ('cash' or 'card')"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount=43.5,
            payment_method="change",
            nb_items=2,
        )
    assert "payment_method" in str(exc.value)


def test_order_constructor_on_negative_nb_items():
    """Test : nb_items must be >= 0"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id=3,
            id_customer=1,
            id_driver=2,
            delivery_address=Address(
                address="4 rue de Dinan", postalcode=35000, city="Rennes"
            ),
            total_amount=43.5,
            payment_method="cash",
            nb_items=-1,
        )
    assert "greater_than_equal" in str(exc.value)
