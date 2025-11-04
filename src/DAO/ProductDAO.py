import logging

from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from src.DAO.DBConnector import DBConnector
from src.Model.Product import Product
from utils.log_decorator import log
from utils.singleton import Singleton


class ProductDAO:
    """Class providing access to products in the database"""

    def __init__(self):
        """Initialize a new DriverDAO instance with a database connector."""
        self.db_connector = DBConnector()

    @log
    def deleting_product(self, product) -> bool:
        """Deleting a product from the database

        Parameters
        ----------
        product: Product
            product to be deleted from the database

        Returns
        -------
            True if the product has been successfully deleted
        """

        res = None
        try:
            res = self.db_connector.sql_query(
                "DELETE FROM product WHERE id_product = %(id_product)s",
                {"id_product": product.id},
                "one",
            )
        except Exception as e:
            logging.info(e)
            raise

        return res > 0

    @log
    def add_product(self, product) -> bool:
        """Adding a product to the database

        Parameters
        ----------
        product : Product

        Returns
        -------
        created : bool
            True if the creation is a success
        """
        res = None
        try:
            res = self.db_connector.sql_query(
                """
                INSERT INTO product (id_product, name, price,production_cost, description, type, stock)
                VALUES (%(id_product)s, %(name)s, %(price)s, %(production_cost)s, %(description)s, %(type)s, %(stock)s)
                RETURNING id_product;
                """,
                {
                    "id_product": product.id,
                    "name": product.name,
                    "price": product.price,
                    "production_cost": product.production_cost,
                    "description": product.description,
                    "type": product.type,
                    "stock": product.stock,
                },
                "one",
            )
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            product.id = res["id_product"]
            created = True

        return created
