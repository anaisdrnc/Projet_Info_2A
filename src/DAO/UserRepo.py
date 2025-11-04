from typing import Optional
import logging
from typing import List, Optional
from utils.log_decorator import log
from utils.singleton import Singleton
from src.Model.User import User
from .DBConnector import DBConnector

class UserRepo(metaclass = Singleton):
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

# def insert_into_db(self, username: str, salt: str, hashed_password: str) -> User:
#raw_created_user = self.db_connector.sql_query(
# """
# " INSERT INTO users (id, username, salt, password) "
# " VALUES (DEFAULT, %(username)s, %(salt)s, %(password)s)"
#" RETURNING *; "
# """,
#{"username": username, "salt": salt, "password": hashed_password},
#"one",
# )
## pyrefly: ignore
# return User(**raw_created_user)"""
