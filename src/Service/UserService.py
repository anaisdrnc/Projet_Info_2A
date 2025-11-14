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
    ) -> User:
        """
        Crée un nouvel utilisateur :
        - Vérifie la force du mot de passe
        - Génère un sel
        - Hache le mot de passe
        - Sauvegarde l'utilisateur via UserRepo
        """
        user_repo = self.user_repo
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
        new_user_added = user_repo.add_user(new_user)
        return new_user_added

    @log
    def get_user(self, user_id: int) -> User | None:
        return self.user_repo.get_by_id(user_id)

    @log
    def get_all_users(self, include_password=False):
        user_repo = self.user_repo
        users = user_repo.get_all_users()
        if not include_password:
            for user in users:
                user.password = None
        return users

    @log
    def is_username_taken(self, user_name):
        user_repo = self.user_repo
        answer = user_repo.is_username_taken(username=user_name)
        return answer
    
    @log
    def change_password(self, user_name, old_password, new_password):
        """change the password
        check the old password is correct
        take all the info of the user
        update the user with all the info + the new password"""
        user_repo = self.user_repo
        old_password_correct = validate_username_password(username= user_name, password=old_password, user_repo= user_repo)
        if not old_password_correct:
            return False
        user = user_repo.get_by_username(user_name= user_name)
        new_user  = User(
            first_name = user.first_name,
            last_name = user.last_name,
            user_name = user.user_name, 
            password = new_password,
            email = user.email,
            salt = user.salt,
            id = user.id)
        return user_repo.update_user(new_user)
