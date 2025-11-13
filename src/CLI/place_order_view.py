from InquirerPy import inquirer

from src.CLI.menu_customer import MenuView

from src.Service.OrderService import OrderService
from src.Service.ProductService import ProductService
from src.Service.AddressService import AddressService
from src.CLI.view_abstract import VueAbstraite
from src.CLI.session import Session
from src.DAO.ProductDAO import ProductDAO
from src.DAO.OrderDAO import OrderDAO
from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector


class PlaceOrderView(VueAbstraite):
    def choisir_menu(self):
        """Place an order"""
        productdao = ProductDAO(DBConnector())
        orderdao = OrderDAO(DBConnector())
        product_service = ProductService(productdao)
        order_service = OrderService(orderdao)
        addressdao = AddressDAO(DBConnector())
        address_service = AddressService(addressdao)

        # get id_user for creating order
        id_customer = Session().get_id_user()

        # get the list of products, the quantities and the price of the order
        list_choosen_products_names = []
        quantities = []
        total_amount = 0

        raw_list_products = product_service.get_available_products()
        list_products = []
        prices = {}
        for product in raw_list_products:
            name = product["name"]
            list_products.append(name)
            price = product["price"]
            prices[name] = float(price)

        product = inquirer.select(
            message="Choose a product : ",
            choices=list_products,
        ).execute()
        quantity = inquirer.number(
            message="Quantity :",
            min_allowed=0,
            max_allowed=10,
        ).execute()
        list_choosen_products_names.append(product)
        quantities.append(quantity)
        total_amount += prices[product] * int(quantity)

        choice = inquirer.select(
            message="choose : ",
            choices=["add a product to the order", "finish the order"],
        ).execute()

        nb_iterations = 0

        while choice == "add a product to the order" and nb_iterations < 50:
            list_products_proposed = {
                product
                for product in list_products
                if product not in list_choosen_products_names
            }
            product = inquirer.select(
                message="Choose a product : ",
                choices=list_products_proposed,
            ).execute()
            quantity = inquirer.number(message="Quantity :").execute()
            list_choosen_products_names.append(product)
            quantities.append(quantity)
            total_amount += prices[product] * quantity

            choice = inquirer.select(
                message="choose : ",
                choices=["add a product to the order", "finish the order"],
            ).execute()
            nb_iterations += 1

        if nb_iterations == 50:
            print("You exceed the maximal number of products ordered")

        nb_items = len(quantities)

        # get the address where the order is to be delivered
        address = inquirer.text(
            message="Enter your address (ex : 51 rue Blaise Pascal) :"
        ).execute()
        city = inquirer.text(message="Enter your city (ex: Bruz):").execute()
        postal_code = inquirer.text(
            message="Enter your postal code (ex: 35 170) :"
        ).execute()
        address_order = address_service.add_address(
            address=address, city=city, postal_code=postal_code
        )
        if address_order == None:
            return MenuView(f"Your address is incorrect. Please try again.")
        else:
            id_address = address_order.id_address

        # payment method
        payment_method = inquirer.select(
            message="Select a payment method :", choices=["Cash", "Card"]
        ).execute()

        # creating the order
        order = order_service.create(
            id_customer=id_customer,
            id_address=id_address,
            nb_items=nb_items,
            total_amount=total_amount,
            payment_method=payment_method,
        )

        id_order = order.id_order

        # putting choosen products into the order
        for i in range(nb_items):
            product = list_choosen_products_names[i]
            quantity = quantities[i]
            id_product = product_service.get_id_by_name(product)
            added = order_service.add_product_to_order(
                order_id=id_order, product_id=id_product, quantity=int(quantity)
            )

        message = "Order validated"
        return MenuView(message=message)
