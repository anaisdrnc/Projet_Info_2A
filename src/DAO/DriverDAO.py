import logging
from typing import List, Optional

from utils.log_decorator import log

from src.DAO.DBConnector import DBConnector

from src.Model.Driver import Driver


class DriverDAO():
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
        res = None
        try:
            res = self.db_connector.sql_query(
                """
                INSERT INTO driver (id_user, mean_of_transport)
                VALUES (%(id_user)s, %(mean_of_transport)s)
                RETURNING id_driver;
                """,
                {"id_user": driver.id, "mean_of_transport": driver.transport_mean},
                "one",
            )
        except Exception as e:
            logging.info(e)

        created = False
        if res:
            driver.id = res["id_driver"]
            created = True

        return created

    @log
    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        """Retrieve a driver by their unique ID."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, u.username, u.password,
                       u.firstname, u.lastname, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE d.id_driver = %(id_driver)s;
                """,
                {"id_driver": driver_id},
                "one",
            )
        except Exception as e:
            logging.info(e)
            raise

        driver = None
        if res:
            driver = Driver(
                id=res["id_driver"],
                username=res["username"],
                password=res["password"],
                firstname=res["firstname"],
                lastname=res["lastname"],
                email=res["email"],
                transport_mean=res["mean_of_transport"],
            )
        return driver

    @log
    def list_all(self) -> List[Driver]:
        """Retrieve all drivers from the database."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, u.username, u.password,
                       u.firstname, u.lastname, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user;
                """,
                None,
                "all",
            )
        except Exception as e:
            logging.info(e)
            raise

        drivers = []
        if res:
            for row in res:
                driver = Driver(
                    id=row["id_driver"],
                    username=row["username"],
                    password=row["password"],
                    firstname=row["firstname"],
                    lastname=row["lastname"],
                    email=row["email"],
                    transport_mean=row["mean_of_transport"],
                )
                drivers.append(driver)
        return drivers

    @log
    def update(self, driver: Driver) -> bool:
        """Update a driver's transport information."""
        res = None
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE driver
                SET mean_of_transport = %(mean_of_transport)s
                WHERE id_driver = %(id_driver)s;
                """,
                {"mean_of_transport": driver.transport_mean, "id_driver": driver.id},
                "one",
            )
        except Exception as e:
            logging.info(e)

        return res is not None

    @log
    def delete(self, driver_id: int) -> bool:
        """Delete a driver record from the database."""
        res = None
        try:
            res = self.db_connector.sql_query(
                "DELETE FROM driver WHERE id_driver = %(id_driver)s;",
                {"id_driver": driver_id},
                "one",
            )
        except Exception as e:
            logging.info(e)
            raise

        return res is not None

    @log
    def login(self, username: str, password: str) -> Optional[Driver]:
        """Authenticate a driver using their username and password."""
        res = None
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport, u.username, u.password,
                       u.firstname, u.lastname, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE u.username = %(username)s AND u.password = %(password)s;
                """,
                {"username": username, "password": password},
                "one",
            )
        except Exception as e:
            logging.info(e)

        driver = None
        if res:
            driver = Driver(
                id=res["id_driver"],
                username=res["username"],
                password=res["password"],
                firstname=res["firstname"],
                lastname=res["lastname"],
                email=res["email"],
                transport_mean=res["mean_of_transport"],
            )
        return driver
