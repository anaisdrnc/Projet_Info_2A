import regex
from InquirerPy import inquirer
from InquirerPy.validator import PasswordValidator
from prompt_toolkit.validation import ValidationError, Validator

from src.CLI.view_abstract import AbstractView
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.UserRepo import UserRepo
from src.Service.CustomerService import CustomerService
from src.Service.PasswordService import check_password_strength
from src.Service.UserService import UserService


class InscriptionView(AbstractView):
    """Customer account registration view"""

    def choose_menu(self):
        """Prompt the user to enter registration details"""

        # Ask user to enter username
        username = inquirer.text(message="Enter your username: ").execute()

        user_repo = UserRepo(DBConnector(test=False))
        customerdao = CustomerDAO(DBConnector(test=False))

        user_service = UserService(user_repo)
        customer_service = CustomerService(customerdao=customerdao)

        if user_service.is_username_taken(user_name=username):
            from CLI.opening.openingview import OpeningView
            return OpeningView(f"The username {username} is already taken.")

        # Ask user to enter password
        password = inquirer.secret(
            message="Enter your password: ",
            validate=PasswordValidator(
                length=8,
                cap=True,
                number=True,
                message="At least 8 characters including uppercase, lowercase, and a number",
            ),
        ).execute()

        try:
            check_password_strength(password)
        except Exception as e:
            message = str(e)
            from CLI.opening.openingview import OpeningView
            return OpeningView(message)

        # Ask for first and last name
        first_name = inquirer.text(message="Enter your first name: ").execute()
        last_name = inquirer.text(message="Enter your last name: ").execute()

        # Ask for email with validation
        email = inquirer.text(message="Enter your email: ", validate=MailValidator()).execute()

        # Create the customer account
        customer = customer_service.create_customer(
            username=username,
            password=password,
            firstname=first_name,
            lastname=last_name,
            email=email,
        )

        # Display success or error message
        if customer:
            message = f"Your account {customer.user_name} was successfully created. You can now log in."
        else:
            message = "Connection error (invalid username or password)"

        from CLI.opening.openingview import OpeningView
        return OpeningView(message)


class MailValidator(Validator):
    """MailValidator checks if the entered string matches a valid email format"""

    def validate(self, document) -> None:
        ok = regex.match(r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$", document.text)
        if not ok:
            raise ValidationError(
                message="Please enter a valid email",
                cursor_position=len(document.text),
            )
