import logging

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.Model.Customer import Customer
from src.Service.PasswordService import check_password_strength, create_salt
from src.utils.log_decorator import log
from src.utils.securite import hash_password


class CustomerService:
    """Service class providing business logic related to customers."""

    def __init__(self, customerdao=None):
        """Initialize the CustomerService with its DAO.

        Parameters
        ----------
        customerdao : CustomerDAO, optional
            The DAO responsible for persistence of customer data.
            If None, a default CustomerDAO with DBConnector is created.
        """
        self.customerdao = customerdao or CustomerDAO(DBConnector())

    @log
    def create_customer(self, username: str, password: str, firstname: str, lastname: str, email: str, ) -> Customer:
        """Create a new customer.

        This method:
        1) Validates password strength
        2) Generates a salt
        3) Hashes the password
        4) Creates and stores the customer via CustomerDAO

        Parameters
        ----------
        username : str
            Customer's username.
        password : str
            Raw password to validate and hash.
        firstname : str
            Customer's first name.
        lastname : str
            Customer's last name.
        email : str
            Customer's email.

        Returns
        -------
        Customer
            The created Customer object if successful.
        """
        customerdao = self.customerdao

        check_password_strength(password)

        salt = create_salt()
        hashed_password = hash_password(password, sel=salt)

        new_customer = Customer(
            user_name=username,
            password=hashed_password,
            first_name=firstname,
            last_name=lastname,
            email=email,
            salt=salt,
        )

        return customerdao.add_customer(new_customer)

    def get_by_id(self, customer_id: int) -> Customer | None:
        """Retrieve a customer using their customer ID.

        Parameters
        ----------
        customer_id : int
            ID of the customer to retrieve.

        Returns
        -------
        Customer or None
            The corresponding Customer object if found, otherwise None.
        """
        try:
            return self.customerdao.get_by_id(customer_id)
        except Exception as e:
            logging.error(f"[CustomerService] Erreur get_by_id({customer_id}) : {e}")
            return None

    def update_customer(self, customer: Customer) -> bool:
        """Update customer information.

        If a **new password is provided**, this method:
        1) Validates its strength
        2) Generates a new salt
        3) Hashes the updated password

        Parameters
        ----------
        customer : Customer
            Customer object containing updated fields.

        Returns
        -------
        bool
            True if update succeeded, False otherwise.
        """
        try:
            if customer.password and len(customer.password) < 50:
                check_password_strength(customer.password)
                customer.salt = create_salt()
                customer.password = hash_password(customer.password, sel=customer.salt)

            return self.customerdao.update_customer(customer)

        except Exception as e:
            logging.error(
                f"[CustomerService] Erreur update_customer({customer.id_customer}) : {e}"
            )
            return False

    def verify_password(self, plain_password: str, hashed_password: str, salt: str) -> bool:
        """Verify whether a raw password matches a stored salted hash.

        Parameters
        ----------
        plain_password : str
            Raw password entered by the user.
        hashed_password : str
            Stored hashed password.
        salt : str
            Salt used for hashing.

        Returns
        -------
        bool
            True if the password matches, otherwise False.
        """
        return hash_password(plain_password, sel=salt) == hashed_password
