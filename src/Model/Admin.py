import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from Model.User import User


class Admin(User):
    """
    Class representing an Administrator user.

    This class extends the base User model, inheriting all core
    user attributes (username, password, name, etc.) and adding
    an attribute specific to the administrator role.

    Attributes
    ----------
    id_admin : Optional[int]
                The unique identifier for the administrator role in the database.
                It is optional for creation.
    """

    id_admin: int | None = None
