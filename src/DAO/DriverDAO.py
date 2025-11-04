import logging
from typing import List, Optional

from utils.log_decorator import log
from src.DAO.DBConnector import DBConnector
from src.Model.Driver import Driver


class DriverDAO:
    """
    DAO for managing drivers in the database.

    Provides methods to create, read, update, delete, and authenticate driver records.
    """

    def __init__(self):
        """Initialize a new DriverDAO instance with a database connector."""
        self.db_connector = DBConnector()

    @log
    def create(self, driver: Driver) -> bool:
        """Create a new driver record in the database."""
        try:
            user_res = self.db_connector.sql_query(
                """
                INSERT INTO users (user_name, password, first_name, last_name, email)
                VALUES (%(username)s, %(password)s, %(firstname)s, %(lastname)s, %(email)s)
                RETURNING id_user;
                """,
                {
                    "username": driver.username,
                    "password": driver.password,
                    "firstname": driver.firstname,
                    "lastname": driver.lastname,
                    "email": driver.email,
                },
                "one",
            )

            if not user_res or "id_user" not in user_res:
                return False

            id_user = user_res["id_user"]

            driver_res = self.db_connector.sql_query(
                """
                INSERT INTO driver (id_user, mean_of_transport)
                VALUES (%(id_user)s, %(mean_of_transport)s)
                RETURNING id_driver;
                """,
                {"id_user": id_user, "mean_of_transport": driver.transport_mean},
                "one",
            )

            if driver_res and "id_driver" in driver_res:
                driver.id = driver_res["id_driver"]
                return True

        except Exception as e:
            logging.info(e)

        return False

    @log
    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        """Retrieve a driver by their unique ID."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, 
                       u.user_name, u.password, u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE d.id_driver = %(id_driver)s;
                """,
                {"id_driver": driver_id},
                "one",
            )

            if not res:
                return None

            driver = Driver(
                id=res["id_driver"],
                username=res["user_name"],
                password=res["password"],
                firstname=res["first_name"],
                lastname=res["last_name"],
                email=res["email"],
                transport_mean=res["mean_of_transport"],
            )
            return driver

        except Exception as e:
            logging.info(e)
            return None

    @log
    def list_all(self) -> List[Driver]:
        """Retrieve all drivers from the database."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, 
                       u.user_name, u.password, u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user;
                """,
                None,
                "all",
            )

            drivers = []
            if res:
                for row in res:
                    driver = Driver(
                        id=row["id_driver"],
                        username=row["user_name"],
                        password=row["password"],
                        firstname=row["first_name"],
                        lastname=row["last_name"],
                        email=row["email"],
                        transport_mean=row["mean_of_transport"],
                    )
                    drivers.append(driver)

            return drivers

        except Exception as e:
            logging.info(e)
            return []

    @log
    def update(self, driver: Driver) -> bool:
        """Update a driver's transport information."""
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE driver
                SET mean_of_transport = %(mean_of_transport)s
                WHERE id_driver = %(id_driver)s
                RETURNING id_driver;
                """,
                {"mean_of_transport": driver.transport_mean, "id_driver": driver.id},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def delete(self, driver_id: int) -> bool:
        """Delete a driver record from the database."""
        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM driver WHERE id_driver = %(id_driver)s
                RETURNING id_driver;
                """,
                {"id_driver": driver_id},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def login(self, username: str, password: str) -> Optional[Driver]:
        """Authenticate a driver using their username and password."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport,
                       u.user_name, u.password, u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE u.user_name = %(username)s AND u.password = %(password)s;
                """,
                {"username": username, "password": password},
                "one",
            )

            if not res:
                return None

            driver = Driver(
                id=res["id_driver"],
                username=res["user_name"],
                password=res["password"],
                firstname=res["first_name"],
                lastname=res["last_name"],
                email=res["email"],
                transport_mean=res["mean_of_transport"],
            )
            return driver

        except Exception as e:
            logging.info(e)
            return None
