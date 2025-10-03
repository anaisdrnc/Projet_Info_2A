import pytest
from Product import Product
from pydantic_core import ValidationError


def test_product_constructor_ok():
    Product1 = Product(
        id=3, name="Italian Panini", selling_price=3.0, purchase_price=2.5, product_type="lunch", stock_quantity=3
    )
    assert Product1.id == 3
    assert Product1.name == "Italian Panini"
    assert Product1.selling_price == 3.0
    assert Product1.purchase_price == 2.5
    assert Product1.type == "lunch"
    assert Product1.stock_quantity == 3


def test_product_constructor_on_incorrect_id():
    """Test : id must be a integer"""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id="three",
            name="Italian Panini",
            selling_price=3.0,
            purchase_price=2.5,
            product_type="lunch",
            stock_quantity=3,
        )
    assert "id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)


def test_product_constructor_on_incorrect_name():
    """Test : name must be a string"""
    with pytest.raises(ValidationError) as exception_info:
        Product(id=3, name=343, selling_price=3.0, purchase_price=2.5, product_type="lunch", stock_quantity=3)
    assert "name" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_product_constructor_on_selling_price():
    """Test : selling price must be a float"""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id=3,
            name="Italian Panini",
            selling_price="four",
            purchase_price=2.5,
            product_type="lunch",
            stock_quantity=3,
        )
    assert "selling_price" in str(exception_info.value) and "Input should be a valid number" in str(
        exception_info.value
    )


def test_product_constructor_on_purchase_price():
    """Test : purchase price must be a float"""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id=3, name="Italian Panini", selling_price=4, purchase_price="two", product_type="lunch", stock_quantity=3
        )
    assert "purchase_price" in str(exception_info.value) and "Input should be a valid number" in str(
        exception_info.value
    )


def test_product_constructor_on_product_type():
    """Test : type must be a string"""
    with pytest.raises(ValidationError) as exception_info:
        Product(id=3, name="Italian Panini", selling_price=4, purchase_price=2.5, product_type=123, stock_quantity=3)
    assert "selling_price" in str(exception_info.value) and "Input should be a valid number" in str(
        exception_info.value
    )
