import logging
from typing import List, Optional

from utils.log_decorator import log
from src.DAO.DBConnector import DBConnector
from src.Model.Driver import Driver


class DriverDAO:
    """DAO pour gérer les drivers dans la base de données"""

    def __init__(self):
        self.db_connector = DBConnector()

    @log
    def create(self, driver: Driver) -> bool:
        """Créer un driver dans la DB"""
        try:
            user_res = self.db_connector.sql_query(
                """
                INSERT INTO users (user_name, password, first_name, last_name, email)
                VALUES (%(user_name)s, %(password)s, %(first_name)s, %(last_name)s, %(email)s)
                RETURNING id_user;
                """,
                {
                    "user_name": driver.user_name,
                    "password": driver.password,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
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
                {"id_user": id_user, "mean_of_transport": driver.mean_of_transport},
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

            return Driver(
                id=res["id_driver"],
                user_name=res["user_name"],
                password=res["password"],
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
                    drivers.append(
                        Driver(
                            id=row["id_driver"],
                            user_name=row["user_name"],
                            password=row["password"],
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
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE driver
                SET mean_of_transport = %(mean_of_transport)s
                WHERE id_driver = %(id_driver)s
                RETURNING id_driver;
                """,
                {"mean_of_transport": driver.mean_of_transport, "id_driver": driver.id},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.info(e)
            return False

    @log
    def delete(self, driver_id: int) -> bool:
        try:
            res = self.db_connector.sql_query(
                """
                DELETE FROM driver
                WHERE id_driver = %(id_driver)s
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
    def login(self, user_name: str, password: str) -> Optional[Driver]:
        try:
            res = self.db_connector.sql_query(
                """
                SELECT d.id_driver, d.mean_of_transport,
                       u.user_name, u.password, u.first_name, u.last_name, u.email
                FROM driver d
                JOIN users u ON d.id_user = u.id_user
                WHERE u.user_name = %(user_name)s AND u.password = %(password)s;
                """,
                {"user_name": user_name, "password": password},
                "one",
            )

            if not res:
                return None

            return Driver(
                id=res["id_driver"],
                user_name=res["user_name"],
                password=res["password"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"],
                mean_of_transport=res["mean_of_transport"],
            )

        except Exception as e:
            logging.info(e)
            return None
