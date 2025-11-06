from typing import Optional
import logging
from utils.log_decorator import log
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt
from utils.securite import hash_password
from src.DAO.DBConnector import DBConnector


class UserService:
    def __init__(self, user_repo = UserRepo(DBConnector)):
        self.user_repo = user_repo
    
    @log
    def create_user(
        self, username: str, password: str, firstname: str, lastname: str, email: str
    ) -> User:
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
        new_user = User(
            username=username,
            password=hashed_password,
            firstname=firstname,
            lastname=lastname,
            email=email,
            salt = salt
        )
        if UserRepo.add_user(new_user) is not None:
            return new_user
        return None
    
    @log
    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)
    
    @log
    def get_all_users(self, include_password=False):
        users = UserRepo.get_all_users()
        if not include_password:
            for user in users:
                user.password = None
        return users
    
    @log
    def is_username_taken(self, user_name):
        answer = UserRepo.is_username_taken(username = user_name)
        return answer

