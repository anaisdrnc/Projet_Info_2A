from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from src.Model.Address import Address


class Order(BaseModel):
    id_order: Optional[int] = None
    id_customer: int
    id_driver: int
    id_address: int
    date: datetime = Field(default_factory=datetime.now)
    status: Literal["Delivered", "Preparing"] = "Preparing"
    nb_items: int = Field(..., ge=0)
    total_amount: float = Field(..., gt=0)
    payment_method: Literal["card", "cash"]
