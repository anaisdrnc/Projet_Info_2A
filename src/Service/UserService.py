from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt, validate_username_password
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class UserService:
    """Class containing service methods for managing users."""

    def __init__(self, user_repo: UserRepo | None = None):
        """
        Initialize UserService with a UserRepo.

        Parameters
        ----------
        user_repo : UserRepo, optional
            The repository to use for database operations. If None, a default UserRepo is created.
        """
        self.user_repo = user_repo or UserRepo(DBConnector)

    @log
    def create_user(self, username: str, password: str, firstname: str, lastname: str, email: str) -> int:
        """
        Create a new user and return its ID.

        Parameters
        ----------
        username : str
            The username of the new user.
        password : str
            The password of the new user (will be hashed and salted).
        firstname : str
            First name of the user.
        lastname : str
            Last name of the user.
        email : str
            Email of the user.

        Returns
        -------
        int
            The ID of the newly created user in the database.
        """
        check_password_strength(password)
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)

        new_user = User(
            id=None,
            user_name=username,
            password=hashed_password,
            first_name=firstname,
            last_name=lastname,
            email=email,
            salt=salt,
        )

        return self.user_repo.add_user(new_user)

    @log
    def get_user(self, user_id: int) -> User | None:
        """
        Retrieve a user by its ID.

        Parameters
        ----------
        user_id : int
            The ID of the user.

        Returns
        -------
        User or None
            The User object if found, else None.
        """
        return self.user_repo.get_by_id(user_id)

    @log
    def is_username_taken(self, user_name: str) -> bool:
        """
        Check if a username is already taken.

        Parameters
        ----------
        user_name : str
            The username to check.

        Returns
        -------
        bool
            True if the username is taken, False otherwise.
        """
        return self.user_repo.is_username_taken(username=user_name)

    @log
    def change_password(self, user_name: str, old_password: str, new_password: str) -> bool:
        """
        Change the password of a user after verifying the old password.

        Parameters
        ----------
        user_name : str
            The username of the user.
        old_password : str
            The current password of the user.
        new_password : str
            The new password to set (will be hashed and salted).

        Returns
        -------
        bool
            True if the password was successfully changed, False otherwise.
        """
        old_password_correct = validate_username_password(
            username=user_name, password=old_password, user_repo=self.user_repo
        )
        if not old_password_correct:
            return False

        check_password_strength(new_password)

        user = self.user_repo.get_by_username(user_name=user_name)

        new_salt = create_salt()
        hashed_password = hash_password(new_password, new_salt)

        new_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            user_name=user.user_name,
            password=hashed_password,
            salt=new_salt,
            email=user.email,
            id=user.id
        )

        return self.user_repo.update_user(new_user)
