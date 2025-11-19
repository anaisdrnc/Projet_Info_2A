import pytest
from pydantic import ValidationError

from Model.Product import Product


def test_product_constructor_ok():
    """Test : Checks that an Product object has been initialized correctly."""
    Product1 = Product(
        id_product=3,
        name="Italian Panini",
        price=3.0,
        production_cost=2.5,
        product_type="lunch",
        stock=3,
        description="tomato panini",
    )
    assert Product1.id_product == 3
    assert Product1.name == "Italian Panini"
    assert Product1.price == 3.0
    assert Product1.production_cost == 2.5
    assert Product1.product_type == "lunch"
    assert Product1.stock == 3
    assert Product1.description == "tomato panini"


def test_product_constructor_on_incorrect_id():
    """Test : checks constructor on incorrect id."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product="three",
            name="Italian Panini",
            price=3.0,
            production_cost=2.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "id_product" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)


def test_product_constructor_on_incorrect_name():
    """Test : checks constructor on incorrect name."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name=343,
            price=3.0,
            production_cost=2.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "name" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)


def test_product_constructor_on_price():
    """Test : checks constructor on incorrect type of price."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price="four",
            production_cost=2.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "price" in str(exception_info.value) and "Input should be a valid number" in str(exception_info.value)


def test_product_constructor_on_zero_price():
    """Test: checks constructor on price of zero."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=0.0,
            production_cost=2.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "price" in str(exception_info.value)
    assert "greater_than" in str(exception_info.value)


def test_product_constructor_on_negative_price():
    """Test: checks constructor on negative price."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=-1.0,
            production_cost=2.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "price" in str(exception_info.value)
    assert "greater_than" in str(exception_info.value)


def test_product_constructor_on_production_cost():
    """Test : checks constructor on incorrect production cost."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=4,
            production_cost="two",
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "production_cost" in str(exception_info.value) and "Input should be a valid number" in str(
        exception_info.value
    )


def test_product_constructor_on_zero_production_cost():
    """Test: checks constructor on production cost of zero."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=3.0,
            production_cost=0.0,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "production_cost" in str(exception_info.value)
    assert "greater_than" in str(exception_info.value)


def test_product_constructor_on_negative_production_cost():
    """Test: checks constructor on negative production cost."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=3.0,
            production_cost=-0.5,
            product_type="lunch",
            stock=3,
            description="tomato panini",
        )
    assert "production_cost" in str(exception_info.value)
    assert "greater_than" in str(exception_info.value)


def test_product_constructor_on_product_type():
    """Test : checks constructor on incorrect product type."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=4,
            production_cost=2.5,
            product_type=123,
            stock=3,
            description="tomato panini",
        )
    assert "product_type" in str(exception_info.value) and "Input should be 'drink', 'lunch' or 'dessert'" in str(
        exception_info.value
    )


def test_product_constructor_on_stock_quantity():
    """Test : checks constructor on incorrect quantity."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=3.0,
            production_cost=2.5,
            product_type="lunch",
            stock="four",
            description="tomato panini",
        )
    assert "stock" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(exception_info.value)


def test_product_constructor_on_negative_stock_quantity():
    """Test: checks constructor on negative quantity."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=3.0,
            production_cost=2.5,
            product_type="lunch",
            stock=-5,
            description="tomato panini",
        )
    assert "stock" in str(exception_info.value)
    assert "greater_than_equal" in str(exception_info.value)


def test_product_constructor_on_description_fail():
    """Test: checks constructor on incorrect description."""
    with pytest.raises(ValidationError) as exception_info:
        Product(
            id_product=3,
            name="Italian Panini",
            price=3.0,
            production_cost=2.5,
            product_type="lunch",
            stock=5,
            description=4,
        )
    assert "description" in str(exception_info.value) and "Input should be a valid string" in str(exception_info.value)
