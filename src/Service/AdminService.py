from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
import logging

# from src.DAO.UserRepo import UserRepo
from src.Model.Admin import Admin
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt
from utils.log_decorator import log
from utils.securite import hash_password


class AdminService:
    """Class containing administrators service methods"""

    def __init__(self, admindao=AdminDAO(DBConnector)):
        self.admindao = admindao

    @log
    def create_admin(
        self, username: str, password: str, firstname: str, lastname: str, email: str
    ) -> Admin:
        """
        Crée un nouveau admin :
        - Vérifie la force du mot de passe
        - Génère un sel
        - Hache le mot de passe
        - Sauvegarde le client via CustomerDAO
        """
        admindao = self.admindao
        check_password_strength(password)
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)
        new_user = User(
            user_name=username,
            password=hashed_password,
            first_name=firstname,
            last_name=lastname,
            email=email,
            salt=salt,
        )

        if admindao.add_admin(new_user) is not None:
            return new_user
        return None

    def get_by_username(self, username: str) -> Admin | None:
        """Récupère un administrateur à partir de son nom d'utilisateur."""
        try:
            return self.admindao.get_by_username(username)
        except Exception as e:
            logging.error(
                f"[AdminService] Erreur lors de la récupération de l'admin {username}: {e}"
            )
            return None
