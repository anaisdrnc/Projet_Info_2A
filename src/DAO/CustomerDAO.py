import logging
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer
from utils.securite import hash_password


class CustomerDAO:
    """DAO pour gérer les admins dans la base de données."""

    def __init__(self, db_connector=None):
        """Initialise CustomerDAO avec un connecteur DB."""
        self.db_connector = db_connector or DBConnector()
        self.user_repo = UserRepo(self.db_connector)

    def add_customer(self, customer: Customer):
        """
        Ajoute un customer dans la base de données.
        1) Crée l'utilisateur dans la table users.
        2) Ajoute le customer dans la table customer.
        """
        id_user = self.user_repo.add_user(customer)
        if not id_user:
            return False

        try:
            res = self.db_connector.sql_query(
                "INSERT INTO customer (id_user) VALUES (%(id_user)s) RETURNING id_customer;",
                {"id_user": id_user},
            )
        except Exception as e:
            logging.info(e)
            return False

        if res and "id_customer" in res:
            customer.id_customer = res["id_customer"]
            return True

        return False
