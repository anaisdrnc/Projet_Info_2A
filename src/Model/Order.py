from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Order(BaseModel):
    """
    Class representing a customer's Order entity.

    Attributes
    ----------
    id_order : Optional[int]
                The unique identifier for the order in the database. Optional for creation.
    id_customer : int
                The ID of the customer who placed the order.
    id_driver : Optional[int]
                The ID of the driver assigned to the order. Optional until assigned.
    id_address : int
                The ID of the delivery address.
    date : datetime
                The timestamp when the order was created. Defaults to the current time.
    status : Literal["Delivered", "Preparing", "Ready", "En route", "Cancelled"] #modifier en route
                The current status of the order. Defaults to "Preparing".
    nb_items : int
                The total number of items included in the order. Must be greater than or equal to 0.
    total_amount : float
                The final monetary amount of the order. Defaults to 0.0, must be greater than or equal to 0.
    payment_method : Literal["Card", "Cash"]
                The payment method selected by the customer. Defaults to "Card".
    """

    id_order: Optional[int] = None
    id_customer: int
    id_driver: Optional[int] = None
    id_address: int
    date: datetime = Field(default_factory=datetime.now)
    status: Literal["Delivered", "Preparing", "Ready", "En route", "Cancelled"] = "Preparing"  # Modifier en route
    nb_items: int = Field(..., ge=0)
    total_amount: float = Field(default=0.0, ge=0)
    payment_method: Literal["Card", "Cash"] = "Card"
