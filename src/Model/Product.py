from typing import Literal

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str
    price: float = Field(..., gt=0, description="The selling price must be strictly positive")
    production_cost: float = Field(..., gt=0, description="The production cost must be strictly positive")
    product_type: Literal["drink", "lunch", "dessert"]
    description: str
    stock_quantity: int = Field(..., ge=0, description="The stock quantity must be strictly positive or equals to zero")
