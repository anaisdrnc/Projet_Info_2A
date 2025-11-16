from typing import Literal, Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    """
    Class representing a Product entity.

    Attributes
    ----------
    id_product : Optional[int]
                The unique identifier for the product in the database. Optional for creation.
    name : str
                The name of the product.
    price : float
                The selling price of the product. Must be strictly greater than 0.
    production_cost : float
             The cost associated with producing the product. Must be strictly greater than 0.
    product_type : Literal["drink", "lunch", "dessert"]
             The category of the product. Limited to 'drink', 'lunch', or 'dessert'.
    description : str
                A brief description of the product.
    stock : int
                The current quantity of the product available in inventory. Must be greater than or equal to 0.
    """

    id_product: Optional[int] = None
    name: str
    price: float = Field(..., gt=0, description="The selling price must be strictly positive")
    production_cost: float = Field(..., gt=0, description="The production cost must be strictly positive")
    product_type: Literal["drink", "lunch", "dessert"]
    description: str
    stock: int = Field(
        ...,
        ge=0,
        description="The stock quantity must be strictly positive or equals to zero",
    )
