import logging

from fastapi import HTTPException

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Admin import Admin
from src.Service.PasswordService import check_password_strength, create_salt
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class AdminService:
    """Class containing administrators service methods"""

    def __init__(self, admindao=None):
        self.admindao = admindao or AdminDAO(DBConnector())

    @log
    def create_admin(self, username: str, password: str, first_name: str, last_name: str, email: str) -> Admin:
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
        new_user = Admin(
            user_name=username,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            salt=salt,
        )

        if admindao.add_admin(new_user) is not None:
            return new_user
        return None

    def update_admin(self, admin: Admin) -> bool:
        """
        Met à jour un administrateur.
        La validation du mot de passe se fait AVANT hash dans le controller !
        Ici on ne fait QUE sauvegarder en base.
        """
        try:
            updated = self.admindao.update_admin(admin)
            if not updated:
                raise HTTPException(status_code=500, detail="Failed to update admin")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"[AdminService] Erreur lors de la mise à jour de l'admin {admin.id}: {e}")
            raise HTTPException(status_code=500, detail=str(e)) from e

    def get_by_username(self, username: str) -> Admin | None:
        """Récupère un administrateur à partir de son nom d'utilisateur."""
        try:
            return self.admindao.get_by_username(username)
        except Exception as e:
            logging.error(f"[AdminService] Erreur lors de la récupération de l'admin {username}: {e}")
            return None

    def get_by_id(self, admin_id: int) -> Admin | None:
        """Récupère un administrateur à partir de son id_admin."""
        try:
            return self.admindao.get_by_id(admin_id)
        except Exception as e:
            logging.error(f"[AdminService] Erreur lors de la récupération de l'admin id={admin_id}: {e}")
            return None

    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        """Vérifie si le mot de passe correspond au hash stocké."""
        return hash_password(plain_password, salt) == hashed_password
