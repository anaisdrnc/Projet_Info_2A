import logging

from dao.db_connection import DBConnection

# from src.Model.Product import Product
from utils.log_decorator import log
from utils.singleton import Singleton


class ProductDAO(metaclass=Singleton):
    """Class providing access to products in the database"""

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

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Delete a product
                    cursor.execute(
                        "DELETE FROM product           WHERE id_product=%(id_product)s      ",
                        {"id_product": product.id_product},
                    )
                    res = cursor.rowcount
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
            False otherwise
        """

        res = None

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO product(name, price, production_cost, description, type, stock) VALUES        "
                        "(%(name)s, %(price)s, %(production_cost)s, %(description)s, %(type)s, %(stock)s)             "
                        "  RETURNING id_product;                                                ",
                        {
                            "name": product.name,
                            "price": product.price,
                            "production_cost": product.production_cost,
                            "description": product.description,
                            "type": product.type,
                            "stock": product.stock,
                        },
                    )
                    res = cursor.fetchone()
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            product.id_product = res["id_product"]
            created = True

        return created
