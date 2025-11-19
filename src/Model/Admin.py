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
