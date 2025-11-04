from typing import Literal

from src.Model.User import User


class Driver(User):
    mean_of_transport: Literal["Bike", "Car"]
