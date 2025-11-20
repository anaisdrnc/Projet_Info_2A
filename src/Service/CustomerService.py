import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import logging

from DAO.CustomerDAO import CustomerDAO
from DAO.DBConnector import DBConnector
from Model.Customer import Customer
from Service.PasswordService import check_password_strength, create_salt
from utils.log_decorator import log
from utils.securite import hash_password


class CustomerService:
    """Class containing customers service methods"""

    def __init__(self, customerdao=None):
        self.customerdao = customerdao or CustomerDAO(DBConnector())

    @log
    def create_customer(
        self, username: str, password: str, firstname: str, lastname: str, email: str
    ) -> Customer:
        """Crée un nouveau client."""
        customerdao = self.customerdao

        # Vérifie force du password
        check_password_strength(password)

        # Génère sel + hash
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)

        new_customer = Customer(
            user_name=username,
            password=hashed_password,
            first_name=firstname,
            last_name=lastname,
            email=email,
            salt=salt,
        )

        return customerdao.add_customer(new_customer)

    def get_by_id(self, customer_id: int) -> Customer | None:
        """Récupère un customer depuis son id_customer."""
        try:
            return self.customerdao.get_by_id(customer_id)
        except Exception as e:
            logging.error(f"[CustomerService] Erreur get_by_id({customer_id}) : {e}")
            return None

    def update_customer(self, customer: Customer) -> bool:
        """
        Met à jour un customer.
        Si un nouveau mot de passe est fourni, il est contrôlé + hashé.
        """
        try:
            if customer.password and len(customer.password) < 50:  # si update inclut un mot de passe
                check_password_strength(customer.password)
                customer.salt = create_salt()
                customer.password = hash_password(customer.password, sel=customer.salt)

            return self.customerdao.update_customer(customer)

        except Exception as e:
            logging.error(f"[CustomerService] Erreur update_customer({customer.id_customer}) : {e}")
            return False

    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        """
        Vérifie si un mot de passe correspond au hash + sel.
        """
        return hash_password(plain_password, sel=salt) == hashed_password
