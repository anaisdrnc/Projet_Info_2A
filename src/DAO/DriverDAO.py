import logging
from typing import List, Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Driver import Driver
from utils.log_decorator import log
from utils.securite import hash_password


class DriverDAO:
    """Class providing access to the Driver table of the database"""

    @log
    def __init__(self, db_connector=None):
        """Initialize DriverDAO with a DB connector."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    @log
    def create(self, driver: Driver) -> bool:
        """Create a driver in the database (users + driver).

        This method:
            1) Creates the user in the users table via user_repo.
            2) Creates the corresponding entry in the driver table.

        Parameters
        ----------
        driver : Driver
            The Driver object to insert.

        Returns
        -------
        bool
            True if the driver was successfully created and the id_driver set.
            False if the creation fails at any step or an error occurs.
        """
        try:
            id_user = self.user_repo.add_user(driver)
            if not id_user:
                return False

            driver_res = self.db_connector.sql_query(
                f"""
                INSERT INTO {self.db_connector.schema}.driver (id_user, mean_of_transport)
                VALUES (%(id_user)s, %(mean_of_transport)s)
                RETURNING id_driver;
                """,
                {"id_user": id_user, "mean_of_transport": driver.mean_of_transport},
                "one",
            )

            if driver_res and "id_driver" in driver_res:
                driver.id_driver = driver_res["id_driver"]
                return True

        except Exception as e:
            logging.info(e)
        return False

    @log
    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        """Retrieve a driver from the database using their driver ID.

        Parameters
        ----------
        driver_id : int
            The ID of the driver to retrieve.

        Returns
        -------
        Driver or None
            The corresponding Driver object if found,
            or None if no driver exists with this ID or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE d.id_driver = %(id_driver)s;
                """,
                {"id_driver": driver_id},
                "one",
            )
            if not res:
                return None

            return Driver(
                id=res["id_user"],
                id_driver=res["id_driver"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
                mean_of_transport=res["mean_of_transport"],
            )
        except Exception as e:
            logging.info(e)
            return None

    @log
    def list_all(self) -> List[Driver]:
        """Retrieve all drivers from the database.

        Returns
        -------
        List[Driver]
            A list of Driver objects representing all drivers in the database.
            Returns an empty list if no drivers are found or an error occurs.
        """
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user;
                """,
                None,
                "all",
            )
            drivers = []
            if res:
                for row in res:
                    drivers.append(
                        Driver(
                            id=row["id_user"],
                            id_driver=row["id_driver"],
                            user_name=row["user_name"],
                            password=row["password"],
                            salt=row["salt"],
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                            email=row["email"],
                            mean_of_transport=row["mean_of_transport"],
                        )
                    )
            return drivers
        except Exception as e:
            logging.info(e)
            return []

    @log
    def update(self, driver: Driver) -> bool:
        """Update a driver's information in the database.
        Only updates driver-specific fields (e.g., mean_of_transport).
        Does not update user information.

        Parameters
        ----------
        driver : Driver
            The Driver object containing updated data.

        Returns
        -------
        bool
            True if the update succeeded, False if it failed or an error occurred.
        """
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE driver
                SET mean_of_transport = %(mean_of_transport)s
                WHERE id_driver = %(id_driver)s
                RETURNING id_driver;
                """,
                {
                    "mean_of_transport": driver.mean_of_transport,
                    "id_driver": driver.id_driver,
                },
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def delete(self, driver_id: int) -> bool:
        """Delete a driver and their associated user from the database.

        Parameters
        ----------
        driver_id : int
            The ID of the driver to delete.

        Returns
        -------
        bool
            True if both the driver and the associated user were successfully deleted.
            False if the driver does not exist, the deletion fails, or an error occurs.
        """
        try:
            driver = self.get_by_id(driver_id)
            if not driver:
                return False
            res_driver = self.db_connector.sql_query(
                """
                DELETE FROM driver
                WHERE id_driver = %(id_driver)s
                RETURNING id_driver;
                """,
                {"id_driver": driver_id},
                "one",
            )
            if not res_driver:
                return False

            return self.user_repo.delete_user(driver.id)
        except Exception as e:
            logging.info(e)
            return False

    @log
    def login(self, username, password):
        """Authenticate a driver using their username and password.

        Parameters
        ----------
        username : str
            The username of the driver attempting to log in.
        password : str
            The password provided by the driver.

        Returns
        -------
        Driver or None
            A Driver object if authentication succeeds.
            None if the username does not exist or the password is incorrect.
        """
        query = """
        SELECT u.id_user, u.user_name, u.password, u.salt, u.first_name, u.last_name, u.email,
            d.id_driver, d.mean_of_transport
        FROM users u
        JOIN driver d ON u.id_user = d.id_user
        WHERE u.user_name = %(username)s
        """
        res = self.db_connector.sql_query(query, {"username": username}, "one")
        if not res:
            return None

        hashed_input = hash_password(password, res["salt"])
        if hashed_input != res["password"]:
            return None

        driver = Driver(
            id=res["id_user"],
            id_driver=res["id_driver"],
            user_name=res["user_name"],
            password=res["password"],
            salt=res["salt"],
            first_name=res["first_name"],
            last_name=res["last_name"],
            email=res["email"],
            mean_of_transport=res["mean_of_transport"],
        )
        return driver

    @log
    def get_id_driver_by_id_user(self, id_user) -> Optional[int]:
        """Retrieve the driver ID associated with a given user ID.

        Parameters
        ----------
        id_user : int
            The ID of the user whose driver ID is to be retrieved.

        Returns
        -------
        int or None
            The corresponding driver ID if found.
            None if no driver exists for the given user ID.
        """
        raw_driver = self.db_connector.sql_query("SELECT * from driver WHERE id_user =%s", [id_user], "one")
        if raw_driver is None:
            return None
        # pyrefly: ignore
        return raw_driver["id_driver"]
