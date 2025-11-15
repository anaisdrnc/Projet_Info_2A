from InquirerPy import inquirer

from src.CLI.customer.menu_customer import MenuView
from src.CLI.session import Session
from src.CLI.view_abstract import VueAbstraite
from src.DAO.AddressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.DAO.ProductDAO import ProductDAO
from src.Service.AddressService import AddressService
from src.Service.OrderService import OrderService
from src.Service.ProductService import ProductService

class OrdersHistory(VueAbstraite):
    def choisir_menu(self):
        orderdao = OrderDAO(DBConnector(test = False))
        order_service = OrderService(orderdao)

        id_customer = Session().id_role

        raw_list_orders = order_service.get_all_orders_by_id_customer(id_customer=id_customer)
        dates_orders = []
        for raw_order in raw_list_orders:
            order = raw_order["order"]
            date = order.date
            if date not in dates_orders:
                dates_orders.append(date)

        choosen_date = inquirer.select(
            message= "I want my order history of which date:",
            choices= dates_orders
        ).execute()

        message = "Orders history for {choosen_date}: \n\n"

        for raw_order in raw_list_orders:
            order = raw_order['order']
            if order.date == choosen_date:
                message += "Order #{order.id_order}: \n"
                address = raw_order['address']
                for raw_product in raw_order['products']:
                    product_name = raw_product['name']
                    quantity = raw_product['quantity']
                    message += product_name + "quantity : " + str(quantity) +  "\n"
                message += "address : " + address.address + " " + address.city + " " + str(address.postal_code) + "\n"
                message += "status : " + order.status + "\n"
                message += "total price : " + str(order.total_amount) + '\n\n'

        return MenuView(message)


