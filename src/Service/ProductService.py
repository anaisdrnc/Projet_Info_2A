from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Model.Product import Product
from utils.log_decorator import log


class ProductService:
    """Classe contenant les méthodes de services des produits"""

    def __init__(self, productdao):
        self.productdao = productdao

    @log
    def create(self, name, price, production_cost, product_type, description, stock) -> Product:
        """Création d'un joueur à partir de ses attributs"""
        productdao = self.productdao

        new_product = Product(
            name=name,
            price=price,
            production_cost=production_cost,
            product_type=product_type,
            description=description,
            stock=stock,
        )

        return new_product if productdao.create_product(new_product) else None

    @log
    def delete(self, product) -> bool:
        """Supprimer un produit"""
        productdao = self.productdao
        return productdao.deleting_product(product)

    @log
    def get_list_products_names(self):
        """Get the list of the names of all products available"""
        productdao = self.productdao
        list_complete = productdao.get_all_products()
        list_names = []
        for product in list_complete:
            name = product.name
            list_names.append(name)
        return list_names

    @log
    def get_list_products_descriptions(self):
        """Get the list of the names and descriptions of all products available"""
        productdao = self.productdao
        list_complete = productdao.get_all_products()
        list_desc = []
        for product in list_complete:
            name = product.name
            description = product.description
            list_desc.append([name, description])
        return list_desc
