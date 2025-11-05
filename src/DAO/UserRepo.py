from typing import Optional
import logging
from utils.log_decorator import log
from src.Model.User import User
from .DBConnector import DBConnector


class UserRepo:
    """DAO User"""

    def __init__(self, db_connector):
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
                    "last_name": user.last_name,
                    "first_name": user.first_name,
                    "user_name": user.user_name,
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

    def get_by_id(self, user_id: int) -> Optional[User]:
        raw_user = self.db_connector.sql_query(
            "SELECT * from users WHERE id_user=%s", [user_id], "one"
        )
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def get_by_username(self, user_name: str) -> Optional[User]:
        raw_user = self.db_connector.sql_query(
            "SELECT * from users WHERE user_name=%s", [user_name], "one"
        )
        if raw_user is None:
            return None
        # pyrefly: ignore
        return User(**raw_user)

    def get_all_users(self, include_password=False) -> list[User]:
        """List all the users, optionally including the password."""
        raw_list = self.db_connector.sql_query("SELECT * FROM users")
        if raw_list is None:
            return []
        print(raw_list)

        list_users = []
        for line in raw_list:
            # line doit être un tuple : (id_user, first_name, last_name, user_name, password, email)
            #if not isinstance(line, tuple) or len(line) < 6:
            #    continue  # ignore invalid rows

            user = User(
                id=int(line['id_user']),  # assure l'entier
                first_name=str(line['first_name']),
                last_name=str(line['last_name']),
                user_name=str(line['user_name']),
                password=str(line['password']) if include_password else None,
                email=str(line['email']),
            )
            list_users.append(user)

        return list_users
