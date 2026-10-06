from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.routers.products import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
    reduce_stock,
)
from app.schemas.product import ProductCreate, StockReduceRequest


# ============================================================
# Helpers
# ============================================================

def sample_product_create():
    return ProductCreate(
        name="iPhone 17",
        description="Apple smartphone",
        price=Decimal("79999.00"),
        sku="IPHONE17-001",
        category="Smartphones",
        image_url="/images/iphone-17.jpg",
        rating=4.5,
        stock_quantity=25,
    )


def sample_db_product():
    product = MagicMock()

    product.id = 1
    product.name = "iPhone 17"
    product.description = "Apple smartphone"
    product.price = Decimal("79999.00")
    product.sku = "IPHONE17-001"
    product.category = "Smartphones"
    product.image_url = "/images/iphone-17.jpg"
    product.rating = 4.5
    product.stock_quantity = 25
    product.is_active = True

    return product


# ============================================================
# CREATE PRODUCT
# ============================================================

def test_create_product_success():
    db = MagicMock()

    # SKU does not already exist
    db.query.return_value.filter.return_value.first.return_value = None

    product_data = sample_product_create()

    result = create_product(
        product=product_data,
        db=db,
        current_user={"id": 1, "role": "ADMIN"},
    )

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

    created_product = db.add.call_args[0][0]

    assert created_product.name == "iPhone 17"
    assert created_product.sku == "IPHONE17-001"
    assert created_product.stock_quantity == 25

    assert result is created_product


def test_create_product_duplicate_sku():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = (
        sample_db_product()
    )

    with pytest.raises(HTTPException) as exc:
        create_product(
            product=sample_product_create(),
            db=db,
            current_user={"id": 1, "role": "ADMIN"},
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Product with this SKU already exists"

    db.add.assert_not_called()
    db.commit.assert_not_called()


# ============================================================
# GET PRODUCTS
# ============================================================

def test_get_products_success():
    db = MagicMock()

    products = [
        sample_db_product(),
        sample_db_product(),
    ]

    db.query.return_value.filter.return_value.all.return_value = products

    result = get_products(db=db)

    assert result == products
    assert len(result) == 2


# ============================================================
# GET PRODUCT
# ============================================================

def test_get_product_success():
    db = MagicMock()

    product = sample_db_product()

    db.query.return_value.filter.return_value.first.return_value = product

    result = get_product(
        product_id=1,
        db=db,
    )

    assert result == product
    assert result.id == 1


def test_get_product_not_found():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        get_product(
            product_id=999,
            db=db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"


# ============================================================
# UPDATE PRODUCT
# ============================================================

def test_update_product_success():
    db = MagicMock()

    existing_product = sample_db_product()

    # update_product() calls .first() twice:
    # 1. existing product
    # 2. duplicate SKU check
    db.query.return_value.filter.return_value.first.side_effect = [
        existing_product,
        None,
    ]

    updated_data = ProductCreate(
        name="iPhone 17 Pro",
        description="Updated Apple smartphone",
        price=Decimal("99999.00"),
        sku="IPHONE17PRO-001",
        category="Smartphones",
        image_url="/images/iphone-17-pro.jpg",
        rating=4.8,
        stock_quantity=30,
    )

    result = update_product(
        product_id=1,
        product=updated_data,
        db=db,
        current_user={"id": 1, "role": "ADMIN"},
    )

    assert result.name == "iPhone 17 Pro"
    assert result.price == Decimal("99999.00")
    assert result.sku == "IPHONE17PRO-001"
    assert result.stock_quantity == 30

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing_product)


def test_update_product_not_found():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        update_product(
            product_id=999,
            product=sample_product_create(),
            db=db,
            current_user={"id": 1, "role": "ADMIN"},
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"

    db.commit.assert_not_called()


def test_update_product_duplicate_sku():
    db = MagicMock()

    existing_product = sample_db_product()
    duplicate_product = sample_db_product()
    duplicate_product.id = 2

    db.query.return_value.filter.return_value.first.side_effect = [
        existing_product,
        duplicate_product,
    ]

    with pytest.raises(HTTPException) as exc:
        update_product(
            product_id=1,
            product=sample_product_create(),
            db=db,
            current_user={"id": 1, "role": "ADMIN"},
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Product with this SKU already exists"

    db.commit.assert_not_called()


# ============================================================
# DELETE PRODUCT
# ============================================================

def test_delete_product_success():
    db = MagicMock()

    product = sample_db_product()

    db.query.return_value.filter.return_value.first.return_value = product

    result = delete_product(
        product_id=1,
        db=db,
        current_user={"id": 1, "role": "ADMIN"},
    )

    assert product.is_active is False

    assert result == {
        "message": "Product deleted successfully",
        "product_id": 1,
    }

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(product)


def test_delete_product_not_found():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc:
        delete_product(
            product_id=999,
            db=db,
            current_user={"id": 1, "role": "ADMIN"},
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"

    db.commit.assert_not_called()


# ============================================================
# REDUCE STOCK
# ============================================================

def test_reduce_stock_success():
    db = MagicMock()

    product = sample_db_product()
    product.stock_quantity = 25

    db.query.return_value.filter.return_value.first.return_value = product

    request = StockReduceRequest(quantity=5)

    result = reduce_stock(
        product_id=1,
        request=request,
        db=db,
    )

    assert product.stock_quantity == 20

    assert result == {
        "message": "Stock reduced successfully",
        "product_id": 1,
        "quantity_reduced": 5,
        "remaining_stock": 20,
    }

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(product)


def test_reduce_stock_product_not_found():
    db = MagicMock()

    db.query.return_value.filter.return_value.first.return_value = None

    request = StockReduceRequest(quantity=5)

    with pytest.raises(HTTPException) as exc:
        reduce_stock(
            product_id=999,
            request=request,
            db=db,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Product not found"

    db.commit.assert_not_called()


def test_reduce_stock_inactive_product():
    db = MagicMock()

    product = sample_db_product()
    product.is_active = False

    db.query.return_value.filter.return_value.first.return_value = product

    request = StockReduceRequest(quantity=5)

    with pytest.raises(HTTPException) as exc:
        reduce_stock(
            product_id=1,
            request=request,
            db=db,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Product is not available"

    db.commit.assert_not_called()


def test_reduce_stock_insufficient_stock():
    db = MagicMock()

    product = sample_db_product()
    product.stock_quantity = 2

    db.query.return_value.filter.return_value.first.return_value = product

    request = StockReduceRequest(quantity=5)

    with pytest.raises(HTTPException) as exc:
        reduce_stock(
            product_id=1,
            request=request,
            db=db,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Insufficient stock"

    assert product.stock_quantity == 2
    db.commit.assert_not_called()