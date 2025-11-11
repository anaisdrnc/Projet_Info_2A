from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite
from src.DAO.ProductDAO import ProductDAO
from src.DAO.DBConnector import DBConnector
from src.Service.ProductService import ProductService


class ProductView(VueAbstraite):
    """View that shows :
    - the list of products available with description
    """

    def choisir_menu(self):
        productdao = ProductDAO(DBConnector(test = False))
        productservice = ProductService(productdao)

        raw_list_products = productservice.get_list_products_descriptions()
        list_products = []
        for product in raw_list_products:
            name = product["name"]
            description = product["description"]
            list_products.append([name, description])

        from src.CLI.menu_customer import MenuView

        products_str = f"Liste des produits disponibles : \n\n"
        for product in list_products:
            products_str += str(product[0]) + f"description :" + str(product[1]) + f"\n"
        return MenuView(products_str)
