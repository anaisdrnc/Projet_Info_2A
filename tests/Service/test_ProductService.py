from unittest.mock import patch

import pytest

from src.Model.Product import Product
from src.Service.ProductService import ProductService


def test_creer_ok():
    name = "Panini Mozarella"
    price = 3.5
    production_cost = 2.5
    product_type = "lunch"
    description = "Panini with mozzarella and tomato"
    stock = 4

    # Patch la méthode create_product et DBConnector pour éviter la DB réelle
    with patch("src.Service.ProductService.ProductDAO.create_product", return_value=True):
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


def test_creer_ko():
    """Création de produit échouée via ProductService"""

    # GIVEN
    name = "Panini Mozarella"
    price = 3.5
    production_cost = 2.5
    product_type = "lunch"
    description = "Panini with mozzarella and tomato"
    stock = 4

    # PATCH : on simule que create_product échoue et DBConnector pour éviter la vraie DB
    with patch("src.Service.ProductService.ProductDAO.create_product", return_value=False):
        with patch("src.DAO.ProductDAO.DBConnector"):
            service = ProductService()

            # WHEN
            result = service.create(
                name=name,
                price=price,
                production_cost=production_cost,
                product_type=product_type,
                description=description,
                stock=stock,
            )

            # THEN
            # La création a échoué → retourne None
            assert result is None


def test_delete_ok():
    """Suppression réussie d'un produit"""

    with patch("src.Service.ProductService.ProductDAO.deleting_product", return_value=True):
        with patch("src.DAO.ProductDAO.DBConnector"):  # éviter la vraie DB
            service = ProductService()

            result = service.delete(product=1)  # 1 = id ou objet selon ton usage

            assert result is True
