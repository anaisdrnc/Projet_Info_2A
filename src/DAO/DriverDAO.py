import logging
from typing import List, Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Driver import Driver
from utils.log_decorator import log
from utils.securite import hash_password


class DriverDAO:
    def __init__(self, db_connector=None):
        """Initialise DriverDAO avec un connecteur DB."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    def create(self, driver: Driver) -> bool:
        """Créer un driver dans la DB"""
        try:
            # Ajouter l'utilisateur via UserRepo
            id_user = self.user_repo.add_user(driver)
            if not id_user:
                return False

            # Insérer dans driver
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
        """Récupérer un driver par son ID driver"""
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
        """Liste tous les drivers"""
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
        """Met à jour uniquement le driver (transport), pas les infos user"""
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
        """Supprime le driver et l'utilisateur associé"""
        try:
            driver = self.get_by_id(driver_id)
            if not driver:
                return False

            # Supprime le driver dans la table driver
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

            # Supprime l'utilisateur associé
            return self.user_repo.delete_user(driver.id)
        except Exception as e:
            logging.info(e)
            return False

    @log
    def login(self, username, password):
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
        raw_driver = self.db_connector.sql_query("SELECT * from driver WHERE id_user =%s", [id_user], "one")
        if raw_driver is None:
            return None
        # pyrefly: ignore
        return raw_driver["id_driver"]
