from InquirerPy import inquirer

from src.CLI.view_abstract import VueAbstraite
from src.DAO.DBConnector import DBConnector
from src.DAO.ProductDAO import ProductDAO
from src.Service.ProductService import ProductService


class ProductView(VueAbstraite):
    """View that shows :
    - the list of products available with description
    """

    def choisir_menu(self):
        productdao = ProductDAO(DBConnector(test=False))
        productservice = ProductService(productdao)

        raw_list_products = productservice.get_available_products()
        list_products = []
        for product in raw_list_products:
            name = product["name"]
            description = product["description"]
            price = product["price"]
            list_products.append([name, description, price])

        from CLI.customer.menu_customer import MenuView

        products_str = f"List of available products : \n\n"
        for product in list_products:
            products_str += (
                f" {product[0]}, ingredients : {product[1]}, price : {product[2]} \n"
            )
        return MenuView(products_str)
