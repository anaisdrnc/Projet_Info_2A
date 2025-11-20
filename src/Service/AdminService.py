import logging

from fastapi import HTTPException

from src.DAO.AdminDAO import AdminDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Admin import Admin
from src.Service.PasswordService import check_password_strength, create_salt
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class AdminService:
    """Service class providing business logic related to administrators."""

    def __init__(self, admindao=None):
        """Initialize the AdminService with a DAO for administrators.

        Parameters
        ----------
        admindao : AdminDAO, optional
            The DAO responsible for persistence of admin data.
            If None, a default AdminDAO with DBConnector is created.
        """
        self.admindao = admindao or AdminDAO(DBConnector())

    @log
    def create_admin(
        self,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        email: str,
    ) -> Admin:
        """Create a new administrator.

        This method:
        1) Verifies the password strength
        2) Generates a salt
        3) Hashes the password
        4) Creates and stores the administrator via AdminDAO

        Parameters
        ----------
        username : str
            Administrator's username.
        password : str
            Raw password to validate and hash.
        first_name : str
            Administrator's first name.
        last_name : str
            Administrator's last name.
        email : str
            Administrator's email.

        Returns
        -------
        Admin or None
            The created Admin object if successful,
            None if creation failed.
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
        """Update administrator information.

        Parameters
        ----------
        admin : Admin
            The admin object containing the updated fields.

        Returns
        -------
        bool
            True if the update was successful.

        Raises
        ------
        HTTPException
            If update fails or a database error occurs.
        """
        try:
            updated = self.admindao.update_admin(admin)
            if not updated:
                raise HTTPException(status_code=500, detail="Failed to update admin")
            return True

        except HTTPException:
            raise

        except Exception as e:
            logging.error(
                f"[AdminService] Erreur lors de la mise à jour de l'admin {admin.id}: {e}"
            )
            raise HTTPException(status_code=500, detail=str(e)) from e

    def get_by_username(self, username: str) -> Admin | None:
        """Retrieve an administrator using their username.

        Parameters
        ----------
        username : str
            The username to search for.

        Returns
        -------
        Admin or None
            The corresponding Admin object if found, otherwise None.
        """
        try:
            return self.admindao.get_by_username(username)
        except Exception as e:
            logging.error(
                f"[AdminService] Erreur lors de la récupération de l'admin {username}: {e}"
            )
            return None

    def get_by_id(self, admin_id: int) -> Admin | None:
        """Retrieve an administrator using their admin ID.

        Parameters
        ----------
        admin_id : int
            Administrator ID.

        Returns
        -------
        Admin or None
            The associated Admin object if found, otherwise None.
        """
        try:
            return self.admindao.get_by_id(admin_id)
        except Exception as e:
            logging.error(
                f"[AdminService] Erreur lors de la récupération de l'admin id={admin_id}: {e}"
            )
            return None

    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        """Verify if a provided password matches the stored hash.

        Parameters
        ----------
        plain_password : str
            Raw password to validate.
        hashed_password : str
            Stored password hash.
        salt : str
            Salt used to hash the stored password.

        Returns
        -------
        bool
            True if the password matches, False otherwise.
        """
        return hash_password(plain_password, salt) == hashed_password
