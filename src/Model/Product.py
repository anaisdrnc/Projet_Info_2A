from pydantic import BaseModel, Field 
from typing import Literal 

class Product(BaseModel):
    id: int
    name: str
    selling_price: float = Field(..., gt=0, description="The selling price must be strictly positive") 
    purchase_price: float = Field(..., gt=0, description="The purchase price must be strictly positive") 
    product_type: Literal["drink", "lunch","dessert"]
    stock_quantity : int

