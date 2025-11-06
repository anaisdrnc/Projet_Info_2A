from tabulate import tabulate

from src.DAO.ProductDAO import ProductDAO

# from utils.securite import hash_password
from src.Model.Product import Product
from utils.log_decorator import log


class ProductService:
    """Classe contenant les méthodes de services des produits"""

    @log
    def create(self, name, price, production_cost, product_type, description, stock) -> Product:
        """Création d'un joueur à partir de ses attributs"""

        new_product = Product(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        return new_product if ProductDAO().create_product(new_product) else None

    @log
    def delete(self, product) -> bool:
        """Supprimer un produit"""
        return ProductDAO().deleting_product(product)
