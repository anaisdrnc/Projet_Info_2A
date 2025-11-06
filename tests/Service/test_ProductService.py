from unittest.mock import patch

from src.Model.Product import Product
from src.Service.ProductService import ProductService


def test_creer_ok():
    name = "Panini Mozarella"
    price = 3.5
    production_cost = 2.5
    product_type = "lunch"
    description = "Panini with mozzarella and tomato"
    stock = 4

    with patch("src.Service.ProductService.ProductDAO.create_product", return_value=True) as mock_create:
        with patch("src.DAO.ProductDAO.DBConnector"):
            service = ProductService()
            result = service.create(
                name=name,
                price=price,
                production_cost=production_cost,
                product_type=product_type,
                description=description,
                stock=stock,
            )

            assert result is not None
            assert isinstance(result, Product)
            mock_create.assert_called_once()


def test_creer_ko():
    name = "Panini Mozarella"
    price = 3.5
    production_cost = 2.5
    product_type = "lunch"
    description = "Panini with mozzarella and tomato"
    stock = 4

    with patch("src.Service.ProductService.ProductDAO.create_product", return_value=False) as mock_create:
        with patch("src.DAO.ProductDAO.DBConnector"):
            service = ProductService()

            result = service.create(
                name=name,
                price=price,
                production_cost=production_cost,
                product_type=product_type,
                description=description,
                stock=stock,
            )

            assert result is None
            mock_create.assert_called_once()


def test_delete_ok():
    with patch("src.Service.ProductService.ProductDAO.deleting_product", return_value=True) as mock_delete:
        with patch("src.DAO.ProductDAO.DBConnector"):
            service = ProductService()

            result = service.delete(product=1)

            assert result is True
            mock_delete.assert_called_once_with(1)


def test_delete_ko():
    with patch("src.Service.ProductService.ProductDAO.deleting_product", return_value=False) as mock_delete:
        with patch("src.DAO.ProductDAO.DBConnector"):
            service = ProductService()

            result = service.delete(product=1)

            assert result is False
            mock_delete.assert_called_once_with(1)
