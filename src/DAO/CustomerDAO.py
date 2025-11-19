import logging
from typing import Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer
from utils.log_decorator import log


class CustomerDAO:
    """Class providing access to the Customer table of the database"""

    def __init__(self, db_connector: DBConnector = None):
        """Initialize CustomerDAO with a DB connector."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    @log
    def add_customer(self, customer: Customer) -> Optional[Customer]:
        """Create a new customer in the database (users + customer).

        This method:
            1) Creates the user in the users table.
            2) Creates the corresponding entry in the customer table.

        Parameters
        ----------
        customer : Customer
            The Customer object to insert.

        Returns
        -------
        Customer or None
            The Customer object with its id_customer set if creation succeeds.
            None if the creation fails at any step.
        """
        try:
            # Ajouter l'utilisateur via UserRepo
            id_user = self.user_repo.add_user(customer)
            if not id_user:
                return None

            # Insérer dans customer
            customer_res = self.db_connector.sql_query(
                f"""
                INSERT INTO {self.db_connector.schema}.customer (id_user)
                VALUES (%(id_user)s)
                RETURNING id_customer;
                """,
                {"id_user": id_user},
                "one",
            )

            if customer_res and "id_customer" in customer_res:
                customer.id_customer = customer_res["id_customer"]
                return customer

        except Exception as e:
            logging.info(e)
        return None

    @log
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Retrieve an customer from the database using their customer ID.

        Parameters
        ----------
        customer_id : int
            The id of the customer to retrieve.

        Returns
        -------
        Customer or None
            The corresponding Customer object if found,
            or None if no customer exists with this ID or if an error occurs."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT c.id_customer, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM customer c
                JOIN users u ON c.id_user = u.id_user
                WHERE c.id_customer = %(id_customer)s;
                """,
                {"id_customer": customer_id},
                "one",
            )
            if not res:
                return None

            return Customer(
                id=res["id_user"],
                id_customer=res["id_customer"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )
        except Exception as e:
            logging.info(e)
            return None

    @log
    def update_customer(self, customer: Customer) -> bool:
        """Update an customer's user information.

        Parameters
        ----------
        customer : Customer

        Returns
        -------
        bool :
            True if the update succeeds, False otherwise.
        """
        try:
            return self.user_repo.update_user(customer)
        except Exception as e:
            logging.info(e)
            return False

    @log
    def delete_customer(self, id_customer: int) -> bool:
        """Delete a customer and their associated user from the database.

        Parameters
        ----------
        id_customer : int
            The ID of the customer to delete.

        Returns
        -------
        bool
            True if the customer (and associated user) was successfully deleted.
            False if the customer does not exist or if the deletion fails.
        """
        customer = self.get_by_id(id_customer)
        if not customer:
            return False

        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM customer
                WHERE id_customer = %(id_customer)s
                RETURNING id_customer;
                """,
                {"id_customer": id_customer},
                "one",
            )

            if not res or "id_customer" not in res:
                return False

            self.user_repo.delete_user(customer.id)
            return True

        except Exception as e:
            logging.info(e)
            return False

    @log
    def get_id_customer_by_id_user(self, id_user) -> Optional[int]:
        """Retrieve the customer ID associated with a given user ID.

        Parameters
        ----------
        id_user : int
            The ID of the user whose customer ID is to be retrieved.

        Returns
        -------
        int or None
            The corresponding customer ID if found.
            None if no customer exists for the given user ID.
        """
        raw_customer = self.db_connector.sql_query("SELECT * from customer WHERE id_user =%s", [id_user], "one")
        if raw_customer is None:
            return None
        return raw_customer["id_customer"]

