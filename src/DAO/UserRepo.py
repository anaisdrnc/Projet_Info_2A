from typing import Optional
import logging
from typing import List, Optional
from utils.log_decorator import log
from src.Model.User import User
from .DBConnector import DBConnector


class UserRepo():
    """DAO User"""

    def __init__(self):
        """Initialize a new UserDAO instance with a database connector."""
        self.db_connector = DBConnector()

    def add_user(self, user):
        """add user to the database and return id_user, in order to add the user to the
        proprer table (customer, driver or admin) with another method"""
        res = None
        try:
            res = self.db_connector.sql_query(
                "INSERT INTO users (first_name, last_name, user_name, password, email)"
                "VALUES "
                "(%(first_name)s, %(last_name)s, %(user_name)s, %(password)s, %(email)s)"
                "RETURNING id_user;",
                {
                    "last_name": user.lastname,
                    "first_name": user.firstname,
                    "user_name": user.username,
                    "password": user.password,
                    "email": user.email,
                },
            )
        except Exception as e:
            logging.info(e)
        if res:
            user.id = res["id_user"]
            return user.id
        return None

    def get_by_id(self, user_id: int) -> Optional[User]:
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE id=%s", [user_id], "one")
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def get_by_username(self, username: str) -> Optional[User]:
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE username=%s", [username], "one")
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def get_all_users(self):
        "list all the users (used in the reset_database)"
        raw_list = self.db_connector.sqd_query("SELECT * FROM users")
        if raw_list is None:
            return None
        list_users = []
        for line in raw_list:
            user = User(
                id=line["id_user"],
                firstname=line["firstname"],
                lastname=line["lastname"],
                username=line["username"],
                password=line["password"],
                email=line["email"],
            )
            list_users.append(user)
        return list_users
