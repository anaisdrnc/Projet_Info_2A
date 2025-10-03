from User import User
from Address import Address


class Customer(User):
    address: Address = None
