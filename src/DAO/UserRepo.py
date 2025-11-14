from typing import Optional
import logging
from src.Model.User import User
from .DBConnector import DBConnector
from utils.log_decorator import log


class UserRepo:
    """DAO User"""

    def __init__(self, db_connector=None):
        """Initialize a new UserDAO instance with a database connector."""
        self.db_connector = db_connector if db_connector is not None else DBConnector()

    @log
    def add_user(self, user):
        """add user to the database and return id_user, in order to add the user to the
        proprer table (customer, driver or admin) with another method"""
        res = None
        try:
            res = self.db_connector.sql_query(
                "INSERT INTO users (first_name, last_name, user_name, password, email, salt)"
                "VALUES "
                "(%(first_name)s, %(last_name)s, %(user_name)s, %(password)s, %(email)s, %(salt)s)"
                "RETURNING id_user;",
                {
                    "last_name": user.last_name,
                    "first_name": user.first_name,
                    "user_name": user.user_name,
                    "password": user.password,
                    "email": user.email,
                    "salt": user.salt,
                },
            )
        except Exception as e:
            logging.info(e)
        if res:
            user.id = res["id_user"]
            return user.id
        return None

    @log
    def delete_user(self, user_id):
        """delete user with their id from the user table"""
        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM users
                WHERE id_user = %(user_id)s
                RETURNING id_user;
                """,
                {"user_id": user_id},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def get_by_id(self, user_id: int) -> Optional[User]:
        raw_user = self.db_connector.sql_query(
            "SELECT * from users WHERE id_user=%s", [user_id], "one"
        )
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    @log
    def get_by_username(self, user_name: str) -> Optional[User]:
        raw_user = self.db_connector.sql_query(
            "SELECT * from users WHERE user_name=%s", [user_name], "one"
        )
        if raw_user is None:
            return None
        # pyrefly: ignore
        id_user = raw_user["id_user"]
        user_name = raw_user["user_name"]
        first_name = raw_user["first_name"]
        last_name = raw_user["last_name"]
        email = raw_user["email"]
        password = raw_user["password"]
        salt = raw_user["salt"]
        return User(
            id = id_user, 
            user_name = user_name, 
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
            salt = salt)


    @log
    def get_password(self, username):
        raw_password = self.db_connector.sql_query(
            "SELECT password from users WHERE user_name=%s", [username], "one"
        )
        if raw_password is None:
            return None
        if raw_password:
            password = raw_password["password"]
            return password

    @log
    def is_username_taken(self, username):
        raw_answer = self.db_connector.sql_query(
            "SELECT * FROM users WHERE user_name = %s;", [username], "one"
        )
        if raw_answer is None:
            return False
        return True

    @log
    def update_user(self, user: User) -> bool:
        """
        Met à jour les informations d'un utilisateur existant dans la table users.
        Retourne True si la mise à jour a réussi, False sinon.
        """
        if not user.id:
            logging.info("update_user: user.id is missing")
            return False

        try:
            res = self.db_connector.sql_query(
                """
                UPDATE users
                SET first_name = %(first_name)s,
                    last_name = %(last_name)s,
                    email = %(email)s,
                    user_name = %(user_name)s,
                    password = %(password)s,
                    salt = %(salt)s
                WHERE id_user = %(id_user)s
                RETURNING id_user;
                """,
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "user_name": user.user_name,
                    "password": user.password,
                    "salt": user.salt,
                    "id_user": user.id,
                },
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False
