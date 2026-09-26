from decimal import Decimal

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    category: str
    image_url: str | None = None
    rating: float = 0.0
    stock_quantity: int

class StockReduceRequest(BaseModel):
    quantity: int = Field(gt=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    sku: str
    category: str
    image_url: str | None
    rating: float
    stock_quantity: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }