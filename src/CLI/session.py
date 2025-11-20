from datetime import datetime

from src.utils.log_decorator import log
from src.utils.singleton import Singleton


class Session(metaclass=Singleton):
    """Stores session-related data.
    This allows, for example, to know the currently logged-in user
    from any class.
    Without this, the user would need to be passed between views.
    """

    def __init__(self):
        """Create a new session"""
        self.username = None
        self.id_role = None
        self.login_start = None

    @log
    def login(self, user, id_role):
        """Store user data in the session"""
        self.username = user.user_name
        self.id_role = id_role
        self.login_start = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @log
    def logout(self):
        """Clear the session data"""
        self.username = None
        self.id_role = None
        self.login_start = None

    @log
    def get_id_role(self):
        """Return the id of the connected user"""
        return self.id_role
