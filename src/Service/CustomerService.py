from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector

# from src.DAO.UserRepo import UserRepo
from src.Model.Customer import Customer
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt
from utils.log_decorator import log
from utils.securite import hash_password


class CustomerService:
    """Class containing customers service methods"""

    def __init__(self, customerdao=CustomerDAO(DBConnector)):
        self.customerdao = customerdao

    @log
    def create_customer(
        self, username: str, password: str, firstname: str, lastname: str, email: str
    ) -> Customer:
        """
        Crée un nouveau client :
        - Vérifie la force du mot de passe
        - Génère un sel
        - Hache le mot de passe
        - Sauvegarde le client via CustomerDAO
        """
        customerdao = self.customerdao
        check_password_strength(password)
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