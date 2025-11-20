from InquirerPy import inquirer

from src.CLI.session import Session
from src.CLI.view_abstract import AbstractView
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DriverDAO import DriverDAO
from src.DAO.UserRepo import UserRepo
from src.Service.PasswordService import validate_username_password


class LoginView(AbstractView):
    """Login View (prompt for username and password)"""

    def choose_menu(self):
        """
        Prompt the user to log in and route to the appropriate menu
        based on user type (Customer or Driver).

        Returns
        -------
        VueAbstraite or subclass
            The next view to display based on login success.
        """

        user_repo = UserRepo(DBConnector(test=False))
        customerdao = CustomerDAO(DBConnector(test=False))
        driverdao = DriverDAO(DBConnector(test=False))

        # Ask the user to enter username and password
        username = inquirer.text(message="Enter your username: ").execute()
        password = inquirer.secret(message="Enter your password: ").execute()

        # Call the service to validate credentials
        user = validate_username_password(
            username=username, password=password, user_repo=user_repo
        )

        # Retrieve associated customer or driver IDs
        id_customer = customerdao.get_id_customer_by_id_user(user.id) if user else None
        id_driver = driverdao.get_id_driver_by_id_user(user.id) if user else None

        # If the user exists and credentials are valid
        if user:
            if id_driver is None and id_customer is not None:
                # Customer account
                message = f"You are logged in to the customer account {user.user_name}"
                Session().login(user, id_customer)

                from CLI.customer.menu_customer import MenuView
                return MenuView(message)

            elif id_customer is None and id_driver is not None:
                # Driver account
                message = f"You are logged in to the driver account {user.user_name}"
                Session().login(user, id_driver)

                from CLI.driver.menu_driver import MenuDriver
                return MenuDriver(message)

        # Login failed
        message = "Login error (invalid username or password)"
        from CLI.opening.openingview import OpeningView

        return OpeningView(message)
