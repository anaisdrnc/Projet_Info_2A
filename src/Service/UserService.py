from typing import Optional
import logging
from utils.log_decorator import log
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt, validate_username_password
from utils.securite import hash_password
from src.DAO.DBConnector import DBConnector


class UserService:
    def __init__(self, user_repo=UserRepo(DBConnector)):
        self.user_repo = user_repo

    @log
    def create_user(
        self, username: str, password: str, firstname: str, lastname: str, email: str
    ) -> int:
        """
        Crée un nouvel utilisateur et retourne son ID (int).
        """
        user_repo = self.user_repo
        check_password_strength(password)
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)

        # Crée l'objet User
        new_user = User(
            id=None,
            user_name=username,
            password=hashed_password,
            first_name=firstname,
            last_name=lastname,
            email=email,
            salt=salt,
        )

        # Insert en base → retourne un ID
        new_user_id = user_repo.add_user(new_user)

        return new_user_id


    @log
    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)

    @log
    def is_username_taken(self, user_name):
        user_repo = self.user_repo
        answer = user_repo.is_username_taken(username=user_name)
        return answer

    @log
    def change_password(self, user_name, old_password, new_password):
        user_repo = self.user_repo

        # Vérifie l'ancien mot de passe
        old_password_correct = validate_username_password(
            username=user_name, password=old_password, user_repo=user_repo
        )
        if not old_password_correct:
            return False

        # Vérifie la force du nouveau mot de passe
        check_password_strength(new_password)

        # Récupère l'utilisateur actuel
        user = user_repo.get_by_username(user_name=user_name)

        # Génère un nouveau sel et hash le nouveau mot de passe
        new_salt = create_salt()
        hashed_password = hash_password(new_password, new_salt)

        # Crée un nouvel objet User
        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            user_name=user.user_name,
            password=hashed_password,
            salt=new_salt,
            email=user.email,
            id=user.id
        )

        # Met à jour l'utilisateur
        return user_repo.update_user(new_user)

