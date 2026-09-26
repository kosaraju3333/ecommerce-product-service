from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Float

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    price = Column(Numeric(10, 2), nullable=False)

    sku = Column(String(100), unique=True, nullable=False, index=True)

    category = Column(String(100), nullable=False)

    image_url = Column(String(500), nullable=True)

    rating = Column(Float, nullable=False, default=0.0)

    stock_quantity = Column(Integer, nullable=False, default=0)

    is_active = Column(Boolean, nullable=False, default=True)