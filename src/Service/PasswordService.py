import secrets
from typing import Optional

from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from utils.securite import hash_password


def create_salt() -> str:
    return secrets.token_hex(128)


def check_password_strength(password: str):
    """Vérifie que le mot de passe est suffisamment fort"""
    if len(password) < 8:
        raise Exception("Password length must be at least 8 characters")
    if not any(c.isupper() for c in password):
        raise Exception("Password must contain at least one uppercase letter")
    if not any(c.islower() for c in password):
        raise Exception("Password must contain at least one lowercase letter")
    if not any(c.isdigit() for c in password):
        raise Exception("Password must contain at least one number")


def validate_username_password(
    username: str, password: str, user_repo: UserRepo
) -> User:
    user_with_username: Optional[User] = user_repo.get_by_username(username=username)
    if user_with_username is None:
        raise Exception("User not found")

    # On récupère le salt et le hash enregistré
    salt = user_with_username.salt
    stored_hash = user_with_username.password

    # On re-hashe le mot de passe fourni
    computed_hash = hash_password(password, salt)

    if computed_hash != stored_hash:
        raise Exception("Invalid password")

    return user_with_username
