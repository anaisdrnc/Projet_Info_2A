from typing import Literal

from src.Model.User import User


class Driver(User):
    transport_mean: Literal["bicycling", "driving"]
