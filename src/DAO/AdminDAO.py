import logging
from typing import Optional

from DAO.DBConnector import DBConnector
from DAO.UserRepo import UserRepo
from Model.Admin import Admin
from utils.log_decorator import log
from utils.securite import hash_password


class AdminDAO:
    """Class providing access to the Administrator table of the database"""

    def __init__(self, db_connector=None):
        """Initialize AdminDAO with a DB connector."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    @log
    def add_admin(self, admin: Admin):
        """Add an administrator to the database.

        1) Creates the user in the users table.
        2) Adds the admin to the administrator table.


        Parameters
        ----------
        admin : Admin

        Returns
        -------
        bool :
        - True if the administrator was successfully created, otherwise False.
        """
        id_user = self.user_repo.add_user(admin)
        if not id_user:
            return False

        try:
            res = self.db_connector.sql_query(
                "INSERT INTO administrator (id_user) VALUES (%(id_user)s) RETURNING id_administrator;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)
            return False

        if res and "id_administrator" in res:
            admin.id_admin = res["id_administrator"]
            return True

        return False

    @log
    def login(self, username: str, password: str):
        """Authenticates an admin based on username and password.

        Parameters
        ----------
        username : str
            the administrator's username
        password : str
            the administrator's password

        Returns
        -------
        Admin or None :
            Admin if authentication was successful, otherwise None
        """
        try:
            query = """
            SELECT u.id_user, u.user_name, u.password, u.salt, u.first_name, u.last_name, u.email
            FROM users u
            JOIN administrator a ON a.id_user = u.id_user
            WHERE u.user_name = %(username)s
            """
            res = self.db_connector.sql_query(query, {"username": username})
            if not res:
                return None

            hashed_input = hash_password(password, res["salt"])
            if hashed_input != res["password"]:
                return None

            admin = Admin(
                id=res["id_user"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )
            admin.id_admin = res.get("id_administrator")
            return admin
        except Exception as e:
            logging.info(e)
            return None

    @log
    def update_admin(self, admin: Admin) -> bool:
        """Update an administrator's user information.

        Parameters
        ----------
        admin : Admin

        Returns
        -------
        bool :
            True if the update succeeds, False otherwise.
        """
        try:
            return self.user_repo.update_user(admin)
        except Exception as e:
            logging.info(e)
            return False

    @log
    def get_by_username(self, username: str) -> Optional[Admin]:
        """Retrieve an administrator from the database using their username.

        Parameters
        ----------
        username : str
            The username of the administrator to look up.

        Returns
        -------
        Admin or None
            An Admin object if a matching administrator is found.
            None if no result is found or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                """
                SELECT a.id_administrator AS id_admin, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM administrator a
                JOIN users u ON a.id_user = u.id_user
                WHERE u.user_name = %(username)s;
                """,
                {"username": username},
                "one",
            )

            if not res:
                return None

            return Admin(
                id_admin=res["id_admin"],
                id_user=res["id_user"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )

        except Exception as e:
            logging.error(f"[AdminDAO] Erreur lors de la récupération de l'admin '{username}': {e}")
            return None

    @log
    def get_by_id(self, admin_id: int) -> Optional[Admin]:
        """Retrieve an administrator from the database using their administrator ID.

        Parameters
        ----------
        admin_id : int
            The id of the administrator to retrieve.

        Returns
        -------
        Admin or None
            The corresponding Admin object if found,
            or None if no administrator exists with this ID or if an error occurs."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT a.id_administrator AS id_admin, u.id_user, u.user_name, u.password, u.salt,
                    u.first_name, u.last_name, u.email
                FROM administrator a
                JOIN users u ON a.id_user = u.id_user
                WHERE a.id_administrator = %(admin_id)s;
                """,
                {"admin_id": admin_id},
                "one",
            )

            if not res:
                return None

            return Admin(
                id_admin=res["id_admin"],
                id_user=res["id_user"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
            )

        except Exception as e:
            logging.error(f"[AdminDAO] Erreur lors de la récupération de l'admin id={admin_id}: {e}")
            return None
