import logging
from abc import ABC, abstractmethod


class AbstractView(ABC):
    """Base model for a View"""

    def __init__(self, message=""):
        self.message = message
        logging.info(type(self).__name__)

    def clear_console(self):
        """Insert empty lines to simulate clearing the console"""
        for _ in range(30):
            print("")

    def display(self) -> None:
        """Add a large space in the terminal to simulate
        a page change in the application"""
        self.clear_console()
        print(self.message)
        print()

    @abstractmethod
    def choose_menu(self):
        """Prompt the user to choose the next menu"""
        pass
