from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
# from app.schemas.product import ProductCreate, ProductResponse
from app.utils.dependencies import require_admin
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    StockReduceRequest
)

router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


# ============================================================
# CREATE PRODUCT - ADMIN ONLY
# ============================================================

@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    existing_product = (
        db.query(Product)
        .filter(Product.sku == product.sku)
        .first()
    )

    if existing_product:

        raise HTTPException(
            status_code=400,
            detail="Product with this SKU already exists"
        )

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        sku=product.sku,
        category=product.category,
        image_url=product.image_url,
        rating=product.rating,
        stock_quantity=product.stock_quantity
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ============================================================
# GET ALL PRODUCTS - PUBLIC
# ============================================================

@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db)
):

    return (
        db.query(Product)
        .filter(Product.is_active == True)
        .all()
    )


# @router.get("/", response_model=list[ProductResponse])
# def get_products(
#     db: Session = Depends(get_db)
# ):

#     return db.query(Product).all()


# ============================================================
# GET PRODUCT - PUBLIC
# ============================================================

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# ============================================================
# UPDATE PRODUCT - ADMIN ONLY
# ============================================================

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    existing_product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not existing_product:

        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    duplicate_sku = (
        db.query(Product)
        .filter(
            Product.sku == product.sku,
            Product.id != product_id
        )
        .first()
    )

    if duplicate_sku:

        raise HTTPException(
            status_code=400,
            detail="Product with this SKU already exists"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.sku = product.sku
    existing_product.category = product.category
    existing_product.image_url = product.image_url
    existing_product.rating = product.rating
    existing_product.stock_quantity = product.stock_quantity

    db.commit()
    db.refresh(existing_product)

    return existing_product


# ============================================================
# DELETE PRODUCT - ADMIN ONLY
# ============================================================

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Soft delete
    product.is_active = False

    db.commit()
    db.refresh(product)

    return {
        "message": "Product deleted successfully",
        "product_id": product.id
    }

@router.put("/{product_id}/stock/reduce")
def reduce_stock(
    product_id: int,
    request: StockReduceRequest,
    db: Session = Depends(get_db)
):

    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=400,
            detail="Product is not available"
        )

    if product.stock_quantity < request.quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    product.stock_quantity -= request.quantity

    db.commit()
    db.refresh(product)

    return {
        "message": "Stock reduced successfully",
        "product_id": product.id,
        "quantity_reduced": request.quantity,
        "remaining_stock": product.stock_quantity
    }


# @router.delete("/{product_id}")
# def delete_product(
#     product_id: int,
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_admin)
# ):

#     product = (
#         db.query(Product)
#         .filter(Product.id == product_id)
#         .first()
#     )

#     if not product:

#         raise HTTPException(
#             status_code=404,
#             detail="Product not found"
#         )

#     db.delete(product)
#     db.commit()

#     return {
#         "message": "Product deleted successfully",
#         "product_id": product_id
#     }