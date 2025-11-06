import logging

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Admin import Admin

# from src.Model.User import User


class AdminDAO:
    """Connect with the customer table
    add customer,"""

    def __init__(self, db_connector):
        """Initialize a new AdminDAO instance with a database connector."""
        self.db_connector = DBConnector()

    def add_admin(self, admin: Admin):
        """Add a admin to the database (from a user, creating the users in the user table
        and then putting the admin in the admins database with the id_user)"""
        user_repo = UserRepo(self.db_connector)
        id_user = user_repo.add_user(admin)
        try:
            res = self.db_connector.sql_query(
                "INSERT INTO administrator (id_user)VALUES (%(id_user)s)RETURNING id_administrator;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)

        if res and "id_admin" in res:
            admin.id = res["id_admin"]
            return True
        return False
