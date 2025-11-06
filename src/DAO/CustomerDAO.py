from src.DAO.DBConnector import DBConnector
import logging
from src.Model.User import User
from src.Model.Customer import Customer
from src.DAO.UserRepo import UserRepo


class CustomerDAO:
    """Connect with the customer table
    add customer,"""

    def __init__(self, db_connector):
        """Initialize a new CustomerDAO instance with a database connector."""
        self.db_connector = DBConnector()

    def add_customer(self, user: User):
        """Add a customer to the database (from a user, creating the users in the user table
        and then putting the customer in the customers database with the id_user)"""
        user_repo = UserRepo(self.db_connector)
        id_user = user_repo.add_user(user)
        try:
            res = self.db_connector.sql_query(
                "INSERT INTO customer (id_user)"
                "VALUES (%(id_user)s)"
                "RETURNING id_customer;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)
        if res is not None:
            id_customer = res["id_customer"]
            return id_customer
        return None
