import sys
import os

import logging
from typing import Optional

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
from Model.User import User
from utils.log_decorator import log

from .DBConnector import DBConnector


class UserRepo:
    """Class providing access to the User table of the database"""

    def __init__(self, db_connector=None):
        """Initialize UserDAO with a DB connector."""
        self.db_connector = db_connector if db_connector is not None else DBConnector()

    @log
    def add_user(self, user):
        """Add a user to the database and return their user ID.

        Parameters
        ----------
        user : User

        Returns
        -------
        Optional[int]
            The generated id_user if the insertion succeeded, otherwise None.
        """
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
        """Delete a user from the database by their user ID.

        Parameters
        ----------
        user_id : int
            The unique identifier of the user to delete.

        Returns
        -------
        bool
            True if the user was successfully deleted.
            False if the user does not exist or if a database error occurred.
        """
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
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE id_user=%s", [user_id], "one")
        if raw_user is None:
            return None
        return User(**raw_user)

    @log
    def get_by_username(self, user_name: str) -> Optional[User]:
        """Retrieve a user from the database by their username.

        Parameters
        ----------
        user_name : str
            The username of the user to retrieve.

        Returns
        -------
        Optional[User]
            A User object if a matching user is found, otherwise None.
        """
        raw_user = self.db_connector.sql_query("SELECT * from users WHERE user_name=%s", [user_name], "one")
        if raw_user is None:
            return None
        id_user = raw_user["id_user"]
        user_name = raw_user["user_name"]
        first_name = raw_user["first_name"]
        last_name = raw_user["last_name"]
        email = raw_user["email"]
        password = raw_user["password"]
        salt = raw_user["salt"]
        return User(
            id=id_user,
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            salt=salt,
        )

    @log
    def get_password(self, username):
        """Retrieve the password hash for a given username.

        Parameters
        ----------
        username : str
            The username of the user whose password is being retrieved.

        Returns
        -------
        Optional[str]
            The password hash as stored in the database, or None if no user is found."""

        raw_password = self.db_connector.sql_query("SELECT password from users WHERE user_name=%s", [username], "one")
        if raw_password is None:
            return None
        if raw_password:
            password = raw_password["password"]
            return password

    @log
    def is_username_taken(self, username):
        """Check if a username already exists in the database.

        Parameters
        ----------
        username : str
            The username to check for existence.

        Returns
        -------
        bool
            True if the username exists in the database, False otherwise.
        """
        raw_answer = self.db_connector.sql_query("SELECT * FROM users WHERE user_name = %s;", [username], "one")
        if raw_answer is None:
            return False
        return True

    @log
    def update_user(self, user: User) -> bool:
        """Update an existing user's information in the database.

        Parameters
        ----------
        user : User

        Returns
        -------
        bool
            True if the user was successfully updated, False otherwise.

        """
        if not user.id:
            #print(user.id)
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
