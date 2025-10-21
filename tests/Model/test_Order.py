from datetime import date

import pytest
from pydantic import ValidationError

from src.Model.Address import Address
from src.Model.Order import Order


def test_product_constructor_ok():
    """Constructor test"""
    Order1 = Order(
        id=3,
        date="2025-10-23",
        status="waiting",
        delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
        total_amount=45.3,
        transport_method="car",
        payment_method="cash",
    )
    assert Order1.id == 3
    assert Order1.date == date(2025, 10, 23)
    assert Order1.status == "waiting"
    assert Order1.delivery_address == Address(address="4 rue de Dinan", postalcode=35000, city="Rennes")
    assert Order1.total_amount == 45.3
    assert Order1.transport_method == "car"
    assert Order1.payment_method == "cash"


def test_order_constructor_on_incorrect_id():
    """Test : id must be an integer"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id="three",
            date="2025-10-23",
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount=45.3,
            transport_method="car",
            payment_method="cash",
        )
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)


def test_order_constructor_on_incorrect_date():
    """Test : date must be a date"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date=[2025, 10, 23],
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount=45.3,
            transport_method="car",
            payment_method="cash",
        )
    assert "date" in str(exception_info.value)
    assert "Input should be a valid date" in str(exception_info.value)
    assert "date_type" in str(exception_info.value)


def test_order_constructor_on_incorrect_status():
    """Test : Status must be one of the allowed literals ('delivered' or 'waiting')"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date="2025-10-23",
            status="ok",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount=45.3,
            transport_method="car",
            payment_method="cash",
        )
    assert "status" in str(exception_info.value)
    assert "Input should be 'delivered' or 'waiting'" in str(exception_info.value)
    assert "literal_error" in str(exception_info.value)


def test_order_constructor_on_incorrect_delivery_address():
    """Test : delivery address must be an address"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date="2025-10-23",
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city=12345),
            total_amount=45.3,
            transport_method="car",
            payment_method="cash",
        )
    assert "Address" in str(exception_info.value)
    assert "city" in str(exception_info.value)
    assert "Input should be a valid string" in str(exception_info.value)


def test_order_constructor_on_incorrect_total_amount():
    """Test : total amount must be a float"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date="2025-10-23",
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount="quarante",
            transport_method="car",
            payment_method="cash",
        )
    assert "total_amount" in str(exception_info.value) and "Input should be a valid number" in str(exception_info.value)


def test_order_constructor_on_incorrect_transport_method():
    """Test : transport method must be one of the allowed literals ('car' or 'bicycle')"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date="2025-10-23",
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount=43.5,
            transport_method="voiture",
            payment_method="cash",
        )
    assert "transport_method" in str(exception_info.value)
    assert "Input should be 'bicycle' or 'car'" in str(exception_info.value)
    assert "literal_error" in str(exception_info.value)


def test_order_constructor_on_incorrect_payment_method():
    """Test : payment method must be one of the allowed literals ('cash' or 'card')"""
    with pytest.raises(ValidationError) as exception_info:
        Order(
            id=3,
            date="2025-10-23",
            status="waiting",
            delivery_address=Address(address="4 rue de Dinan", postalcode=35000, city="Rennes"),
            total_amount=43.5,
            transport_method="car",
            payment_method="change",
        )
    assert "payment_method" in str(exception_info.value)
    assert "Input should be 'card' or 'cash'" in str(exception_info.value)
    assert "literal_error" in str(exception_info.value)
