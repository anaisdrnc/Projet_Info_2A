from datetime import datetime

import pytest
from pydantic import ValidationError

from src.Model.Order import Order


def test_order_constructor_ok():
    """Test : Checks that an Order object has been initialized correctly."""
    order = Order(
        id_order=3,
        id_customer=1,
        id_driver=2,
        id_address=1,
        date="2025-10-23 12:30:00",
        status="Preparing",
        total_amount=45.3,
        payment_method="Cash",
        nb_items=2,
    )
    assert order.id_order == 3
    assert order.id_customer == 1
    assert order.id_driver == 2
    assert order.id_address == 1
    assert order.date == datetime(2025, 10, 23, 12, 30, 0)
    assert order.status == "Preparing"
    assert order.total_amount == 45.3
    assert order.payment_method == "Cash"
    assert order.nb_items == 2


def test_order_constructor_on_incorrect_id():
    """Test : checks constructor on incorrect id."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order="three",
            id_customer=1,
            id_driver=2,
            id_address=1,
            total_amount=45.3,
            payment_method="Cash",
            nb_items=2,
            status="Preparing",
        )
    assert "id_order" in str(exc.value)


def test_order_constructor_on_incorrect_date():
    """Test : checks constructor on incorrect date"""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            date=[2025, 10, 23],
            total_amount=45.3,
            payment_method="Cash",
            nb_items=2,
            status="Preparing",
        )
    assert "date" in str(exc.value)


def test_order_constructor_on_incorrect_status():
    """Test : checks constructor in incorrect status."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            status="ok",
            total_amount=45.3,
            payment_method="Cash",
            nb_items=2,
        )
    assert "status" in str(exc.value)
    assert "literal_error" in str(exc.value)


def test_order_constructor_on_incorrect_total_amount():
    """Test : checks constructor in incorrect total amount."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            total_amount="quarante",
            payment_method="Cash",
            nb_items=2,
            status="Preparing",
        )
    assert "total_amount" in str(exc.value)


def test_order_constructor_on_negative_total_amount():
    """Test : checks constructor on negative total amount."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            total_amount=-14.67,
            payment_method="Cash",
            nb_items=2,
            status="Preparing",
        )
    assert "greater_than" in str(exc.value)


def test_order_constructor_on_incorrect_payment_method():
    """Test : checks constructor on incorrect payment method."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            total_amount=43.5,
            payment_method="change",
            nb_items=2,
            status="Preparing",
        )
    assert "payment_method" in str(exc.value)


def test_order_constructor_on_negative_nb_items():
    """Test : checks constructor on negative number of items."""
    with pytest.raises(ValidationError) as exc:
        Order(
            id_order=3,
            id_customer=1,
            id_driver=2,
            id_address=1,
            total_amount=43.5,
            payment_method="Cash",
            nb_items=-1,
            status="Preparing",
        )
    assert "greater_than_equal" in str(exc.value)
