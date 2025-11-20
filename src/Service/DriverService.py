from src.DAO.DriverDAO import DriverDAO
from src.Model.Driver import Driver
from src.Service.PasswordService import check_password_strength, create_salt
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class DriverService:
    """Service class providing business logic related to drivers."""

    def __init__(self, driverdao=None):
        """Initialize the DriverService with its DAO.

        Parameters
        ----------
        driverdao : DriverDAO, optional
            The DAO responsible for persistence of driver data.
            If None, a default DriverDAO is created.
        """
        self.driverdao = driverdao if driverdao else DriverDAO()

    @log
    def create_driver(self, username: str, password: str, firstname: str, lastname: str, email: str,
    mean_of_transport: str) -> Driver:
        """Create a new driver.

        This method:
        1) Validates password strength
        2) Generates a salt
        3) Hashes the password
        4) Creates and stores the driver via DriverDAO

        Parameters
        ----------
        username : str
            Driver's username.
        password : str
            Raw password to validate and hash.
        firstname : str
            Driver's first name.
        lastname : str
            Driver's last name.
        email : str
            Driver's email.
        mean_of_transport : str
            Type of transportation used by the driver (e.g., "Car", "Bike").

        Returns
        -------
        Driver or None
            The created Driver object if successful, otherwise None.
        """
        driverdao = self.driverdao

        # Vérifie la force du mot de passe
        check_password_strength(password)

        # Génère sel + hash
        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)

        # Création du Driver
        driver = Driver(
            user_name=username,
            password=hashed_password,
            salt=salt,
            first_name=firstname,
            last_name=lastname,
            email=email,
            mean_of_transport=mean_of_transport
        )

        if driverdao.create(driver) is not None:
            return driver
        return None

    @log
    def get_by_username(self, username: str) -> Driver | None:
        """Retrieve a driver using their username.

        Parameters
        ----------
        username : str
            Username of the driver to retrieve.

        Returns
        -------
        Driver or None
            The corresponding Driver object if found, otherwise None.
        """
        drivers = self.driverdao.list_all()
        for driver in drivers:
            if driver.user_name == username:
                return driver
        return None

    @log
    def login(self, username: str, password: str) -> Driver | None:
        """Authenticate a driver using username and password.

        Password is hashed with the driver's stored salt and compared
        to the stored password hash.

        Parameters
        ----------
        username : str
            Driver's username.
        password : str
            Raw password provided for authentication.

        Returns
        -------
        Driver or None
            The authenticated driver if successful, otherwise None.
        """
        driver = self.get_by_username(username)
        if not driver:
            return None

        hashed_input = hash_password(password, driver.salt)
        if hashed_input != driver.password:
            return None

        return driver

    @log
    def update_driver(self, username: str, locomotion: str) -> bool:
        """Update a driver's information.

        Only the mean of transport is updated.

        Parameters
        ----------
        username : str
            Username of the driver to modify.
        locomotion : str
            New mean of transport ("Bike" or "Car").

        Returns
        -------
        bool
            True if update succeeded, otherwise False.
        """
        assert locomotion in ["Bike", "Car"]

        driver = self.get_by_username(username)
        new_driver = Driver(
            first_name=driver.first_name,
            last_name=driver.last_name,
            user_name=username,
            email=driver.email,
            password=driver.password,
            mean_of_transport=locomotion,
            id=driver.id,
            id_driver=driver.id_driver
        )
        return self.driverdao.update(new_driver)

    @log
    def delete_driver(self, driver_id: int) -> bool:
        """Delete a driver and their associated user.

        Parameters
        ----------
        driver_id : int
            ID of the driver to delete.

        Returns
        -------
        bool
            True if deletion succeeded, otherwise False.
        """
        return self.driverdao.delete(driver_id)
