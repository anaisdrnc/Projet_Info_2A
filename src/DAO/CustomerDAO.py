import logging
from typing import Optional, List

from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer


class CustomerDAO:
    """DAO pour gérer les clients."""

    def __init__(self, db_connector: DBConnector = None):
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    def add_customer(self, customer: Customer) -> bool:
        """Créer un client dans la DB (users + customer)."""
        try:
            # Ajouter l'utilisateur via UserRepo
            id_user = self.user_repo.add_user(customer)
            if not id_user:
                return False

            # Insérer dans customer
            customer_res = self.db_connector.sql_query(
                f"""
                INSERT INTO {self.db_connector.schema}.customer (id_user)
                VALUES (%(id_user)s)
                RETURNING id_customer;
                """,
                {"id_user": id_user},
                "one",
            )

            if customer_res and "id_customer" in customer_res:
                customer.id_customer = customer_res["id_customer"]
                return True

        except Exception as e:
            logging.info(e)
        return False


    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Récupérer un client par son ID customer."""
        try:
            res = self.db_connector.sql_query(
                """
                SELECT c.id_customer, u.id_user, u.user_name, u.password, u.salt,
                       u.first_name, u.last_name, u.email
                FROM customer c
                JOIN users u ON c.id_user = u.id_user
                WHERE c.id_customer = %(id_customer)s;
                """,
                {"id_customer": customer_id},
                "one",
            )
            if not res:
                return None

            return Customer(
                id=res["id_user"],
                id_customer=res["id_customer"],
                user_name=res["user_name"],
                password=res["password"],
                salt=res["salt"],
                first_name=res["first_name"],
                last_name=res["last_name"],
                email=res["email"]
            )
        except Exception as e:
            logging.info(e)
            return None


    def update_customer(self, customer: Customer) -> bool:
        """Permet au client de mettre à jour ses informations."""
        try:
            # On met à jour les infos dans users
            return self.user_repo.update_user(customer)
        except Exception as e:
            logging.info(e)
            return False

    def delete_customer(self, id_customer: int) -> bool:
        """Supprime un client et son user associé."""
        customer = self.get_by_id(id_customer)
        if not customer:
            return False

        try:
            # Supprimer le client avec RETURNING
            res = self.db_connector.sql_query(
                """
                DELETE FROM customer
                WHERE id_customer = %(id_customer)s
                RETURNING id_customer;
                """,
                {"id_customer": id_customer},
                "one",
            )

            if not res or "id_customer" not in res:
                return False

            # Supprimer aussi l'utilisateur lié
            self.user_repo.delete_user(customer.id)
            return True

        except Exception as e:
            logging.info(e)
            return False

