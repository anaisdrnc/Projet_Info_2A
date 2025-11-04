from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt
from utils.securite import hash_password

class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def create_user(self, username: str, password: str) -> User:
        """
        Crée un nouvel utilisateur :
        - Vérifie la force du mot de passe
        - Génère un sel
        - Hache le mot de passe
        - Sauvegarde l'utilisateur via UserRepo
        """
        check_password_strength(password)
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)
        user = User(username=username, password=hashed_password, salt=salt)
        created_user = self.user_repo.create(user)

        return created_user

    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)
