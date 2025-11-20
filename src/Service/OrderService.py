from typing import Any, Dict, List, Optional

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DriverDAO import DriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from src.Service.CustomerService import CustomerService
from src.utils.log_decorator import log


class OrderService:
    """Service class providing business logic related to orders."""

    def __init__(self, orderdao: OrderDAO):
        """Initialize OrderService with an OrderDAO.

        Parameters
        ----------
        orderdao : OrderDAO
            The DAO responsible for persisting orders and related data.
        """
        self.orderdao = orderdao

    @log
    def create(self, id_customer: int, id_address: int, nb_items: int, total_amount: float, payment_method: str
    ) -> Optional[Order]:
        """Create a new order and persist it in the database.

        Parameters
        ----------
        id_customer : int
            ID of the customer placing the order.
        id_address : int
            ID of the delivery address.
        nb_items : int
            Number of items in the order.
        total_amount : float
            Total price of the order.
        payment_method : str
            Payment method chosen by the customer.

        Returns
        -------
        Order or None
            The created Order object if successful, otherwise None.
        """
        order = Order(
            id_customer=id_customer,
            id_driver=None,
            id_address=id_address,
            nb_items=nb_items,
            total_amount=total_amount,
            payment_method=payment_method,
            status="Ready",
        )
        order.id_order = self.orderdao.create_order(order)
        if order.id_order:
            return self.get_by_id(order.id_order)
        return None

    @log
    def add_product_to_order(self, order_id: int, product_id: int, quantity: int = 1, promotion: bool = False) -> bool:
        """Add a product to an existing order and decrement stock.

        Parameters
        ----------
        order_id : int
            ID of the order.
        product_id : int
            ID of the product to add.
        quantity : int, optional
            Number of units to add (default is 1).
        promotion : bool, optional
            Whether the product is part of a promotion (default is False).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if order_id <= 0 or product_id <= 0 or quantity <= 0:
            return False
        return self.orderdao.add_product(order_id, product_id, quantity, promotion)

    @log
    def remove(self, id_order: int, id_product: int, quantity: int = 1) -> bool:
        """Remove a product from an order and restore stock.

        Parameters
        ----------
        id_order : int
            ID of the order.
        id_product : int
            ID of the product to remove.
        quantity : int, optional
            Number of units to remove (default is 1).

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if id_order <= 0 or id_product <= 0 or quantity <= 0:
            return False
        return self.orderdao.remove_product(id_order, id_product, quantity)

    @log
    def mark_as_delivered(self, id_order: int) -> bool:
        """Mark an order as delivered.

        Parameters
        ----------
        id_order : int
            ID of the order to update.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if id_order <= 0:
            return False
        return self.orderdao.mark_as_delivered(id_order)

    @log
    def mark_as_on_the_way(self, id_order: int) -> bool:
        """Mark an order as on the way.

        Parameters
        ----------
        id_order : int
            ID of the order to update.

        Returns
        -------
        bool
            True if successful, False otherwise.
        """
        if id_order <= 0:
            return False
        return self.orderdao.mark_as_on_the_way(id_order)

    @log
    def get_order_products(self, id_order: int) -> List[Dict[str, Any]]:
        """Retrieve the products associated with a specific order.

        Parameters
        ----------
        id_order : int
            ID of the order.

        Returns
        -------
        list of dict
            List of products in the order.
        """
        if id_order <= 0:
            return []
        return self.orderdao.get_order_products(id_order)

    @log
    def get_by_id(self, id_order: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific order with its products and address.

        Parameters
        ----------
        id_order : int
            ID of the order to retrieve.

        Returns
        -------
        dict or None
            The order details if found, otherwise None.
        """
        if id_order <= 0:
            return None
        return self.orderdao.get_by_id(id_order)["order"]

    @log
    def list_all_orders(self) -> List[Dict[str, Any]]:
        """List all orders with customer, driver, address, and product details.

        Returns
        -------
        list of dict
            List of all orders with detailed information.
        """
        customerdao = CustomerDAO(self.orderdao.db_connector)
        customerservice = CustomerService(customerdao)
        driverdao = DriverDAO(self.orderdao.db_connector)

        raw_orders = self.orderdao.list_all_orders()
        orders = []

        for order_dict in raw_orders:
            order_d = {}
            raw_order = order_dict["order"]
            if raw_order is not None:
                raw_address = order_dict["address"]
                order_d["id_order"] = raw_order.id_order
                order_d["status"] = raw_order.status
                order_d["total_amount"] = raw_order.total_amount
                order_d["nb_items"] = raw_order.nb_items
                order_d["date"] = raw_order.date
                order_d["id_customer"] = raw_order.id_customer

                customer = customerservice.get_by_id(raw_order.id_customer)
                order_d["username_customer"] = customer.user_name

                order_d["address"] = f"{raw_address.address} {raw_address.city} {raw_address.postal_code}"

                order_d["id_driver"] = raw_order.id_driver
                if order_d["id_driver"] is None:
                    order_d["username_driver"] = None
                else:
                    driver = driverdao.get_by_id(raw_order.id_driver)
                    order_d["username_driver"] = driver.user_name

                order_d["products_name"] = []
                order_d["products_quantity"] = []
                for raw_product in order_dict["products"]:
                    order_d["products_name"].append(raw_product["name"])
                    order_d["products_quantity"].append(raw_product["quantity"])

                orders.append(order_d)

        return orders

    @log
    def list_all_orders_ready(self) -> List[Dict[str, Any]]:
        """Retrieve all orders that are ready with full address and product details.

        Returns
        -------
        list of dict
            List of ready orders.
        """
        return self.orderdao.list_all_orders_ready()

    @log
    def get_assigned_orders(self, id_driver: int) -> List[Dict[str, Any]]:
        """Retrieve all orders assigned to a specific driver.

        Parameters
        ----------
        id_driver : int
            ID of the driver.

        Returns
        -------
        list of dict
            Orders assigned to the driver. Empty list if invalid ID.
        """
        if id_driver <= 0:
            return []
        return self.orderdao.get_assigned_orders(id_driver)

    @log
    def assign_order(self, id_driver: int, id_order: int) -> bool:
        """Assign an order to a driver.

        Parameters
        ----------
        id_driver : int
            ID of the driver.
        id_order : int
            ID of the order.

        Returns
        -------
        bool
            True if assignment succeeded, otherwise False.
        """
        if id_driver <= 0 or id_order <= 0:
            return False
        return self.orderdao.assign_order(id_driver, id_order)

    @log
    def get_all_orders_by_id_customer(self, id_customer: int) -> List[Dict[str, Any]]:
        """Retrieve all orders placed by a specific customer.

        Parameters
        ----------
        id_customer : int
            ID of the customer.

        Returns
        -------
        list of dict
            Orders placed by the customer.
        """
        return self.orderdao.get_orders_by_id_user(id_customer)
