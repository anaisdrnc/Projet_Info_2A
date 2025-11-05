from DBConnector import DBConnector
import logging
from src.Model.User import User
from UserRepo import UserRepo


class AdminDAO:
    """Connect with the customer table
    add customer,"""

    def __init__(self, db_connector):
        """Initialize a new AdminDAO instance with a database connector."""
        self.db_connector = DBConnector()

    def add_admin(self, user: User):
        """Add a admin to the database (from a user, creating the users in the user table
        and then putting the admin in the admins database with the id_user)"""
        id_user = UserRepo.add_user(user)
        try:
            res = self.db_connector.sql_query(
                "INSERT INTO administrator (id_user)"
                "VALUES (%(id_user)s)"
                "RETURNING id_administrator;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)
        if res is not None:
            id_admin = res["id_administrator"]
            return id_admin
        return None
