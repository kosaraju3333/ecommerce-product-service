# ============================================================
# ROOT / HEALTH
# ============================================================


def test_root(client):

    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "service": "product-service",
        "status": "running",
    }


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "UP"


# ============================================================
# GET PRODUCTS
# ============================================================


def test_get_products(client, product):

    response = client.get("/api/products/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "iPhone Test"
    assert data[0]["sku"] == "IPHONE-TEST-001"
    assert data[0]["stock_quantity"] == 25
    assert data[0]["is_active"] is True


def test_get_product_by_id(client, product):

    response = client.get(
        f"/api/products/{product.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product.id
    assert data["name"] == "iPhone Test"
    assert data["sku"] == "IPHONE-TEST-001"


def test_get_nonexistent_product(client):

    response = client.get(
        "/api/products/99999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_inactive_product_not_in_product_list(
    client,
    product,
    db,
):

    product.is_active = False

    db.commit()

    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# CREATE PRODUCT
# ============================================================


def test_admin_can_create_product(
    client,
    admin_headers,
):

    payload = {
        "name": "Samsung Test",
        "description": "Samsung test phone",
        "price": "45999.00",
        "sku": "SAMSUNG-TEST-001",
        "category": "Smartphones",
        "image_url": "/images/samsung-test.jpg",
        "rating": 4.5,
        "stock_quantity": 15,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Samsung Test"
    assert data["sku"] == "SAMSUNG-TEST-001"
    assert data["stock_quantity"] == 15
    assert data["is_active"] is True


def test_customer_cannot_create_product(
    client,
    customer_headers,
):

    payload = {
        "name": "Unauthorized Product",
        "description": "Should not be created",
        "price": "1000.00",
        "sku": "UNAUTH-001",
        "category": "Test",
        "rating": 1.0,
        "stock_quantity": 5,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=customer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_create_product_without_token(client):

    payload = {
        "name": "No Token Product",
        "price": "1000.00",
        "sku": "NO-TOKEN-001",
        "category": "Test",
        "stock_quantity": 5,
    }

    response = client.post(
        "/api/products/",
        json=payload,
    )

    # HTTPBearer rejects missing credentials.
    assert response.status_code in (401, 403)


def test_create_product_with_invalid_token(client):

    response = client.post(
        "/api/products/",
        json={
            "name": "Invalid Token",
            "price": "1000.00",
            "sku": "INVALID-TOKEN-001",
            "category": "Test",
            "stock_quantity": 5,
        },
        headers={
            "Authorization": "Bearer invalid.jwt.token"
        },
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Invalid or expired token"
    )


def test_duplicate_sku_on_create(
    client,
    admin_headers,
    product,
):

    payload = {
        "name": "Another Phone",
        "description": "Duplicate SKU test",
        "price": "50000.00",
        "sku": "IPHONE-TEST-001",
        "category": "Smartphones",
        "rating": 4.0,
        "stock_quantity": 10,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Product with this SKU already exists"
    )


def test_create_product_missing_required_field(
    client,
    admin_headers,
):

    payload = {
        "name": "Missing Category",
        "price": "1000.00",
        "sku": "MISSING-001",
        "stock_quantity": 5,
    }

    response = client.post(
        "/api/products/",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 422


# ============================================================
# UPDATE PRODUCT
# ============================================================


def test_admin_can_update_product(
    client,
    admin_headers,
    product,
):

    payload = {
        "name": "Updated iPhone",
        "description": "Updated description",
        "price": "85000.00",
        "sku": "IPHONE-TEST-001",
        "category": "Smartphones",
        "image_url": "/images/updated.jpg",
        "rating": 4.8,
        "stock_quantity": 30,
    }

    response = client.put(
        f"/api/products/{product.id}",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated iPhone"
    assert data["stock_quantity"] == 30
    assert data["rating"] == 4.8


def test_customer_cannot_update_product(
    client,
    customer_headers,
    product,
):

    payload = {
        "name": "Customer Update",
        "price": "100.00",
        "sku": "IPHONE-TEST-001",
        "category": "Test",
        "stock_quantity": 1,
    }

    response = client.put(
        f"/api/products/{product.id}",
        json=payload,
        headers=customer_headers,
    )

    assert response.status_code == 403


def test_update_nonexistent_product(
    client,
    admin_headers,
):

    payload = {
        "name": "Does Not Exist",
        "price": "1000.00",
        "sku": "NOT-FOUND-001",
        "category": "Test",
        "stock_quantity": 1,
    }

    response = client.put(
        "/api/products/99999",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_update_product_duplicate_sku(
    client,
    admin_headers,
    product,
    second_product,
):

    payload = {
        "name": "Updated iPhone",
        "description": "Duplicate SKU",
        "price": "85000.00",
        "sku": second_product.sku,
        "category": "Smartphones",
        "rating": 4.8,
        "stock_quantity": 20,
    }

    response = client.put(
        f"/api/products/{product.id}",
        json=payload,
        headers=admin_headers,
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Product with this SKU already exists"
    )


# ============================================================
# DELETE / SOFT DELETE
# ============================================================


def test_admin_can_delete_product(
    client,
    admin_headers,
    product,
    db,
):

    response = client.delete(
        f"/api/products/{product.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    assert (
        response.json()["message"]
        == "Product deleted successfully"
    )

    db.refresh(product)

    # Verify actual soft-delete behavior
    assert product.is_active is False


def test_customer_cannot_delete_product(
    client,
    customer_headers,
    product,
):

    response = client.delete(
        f"/api/products/{product.id}",
        headers=customer_headers,
    )

    assert response.status_code == 403


def test_delete_nonexistent_product(
    client,
    admin_headers,
):

    response = client.delete(
        "/api/products/99999",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_soft_deleted_product_not_in_list(
    client,
    admin_headers,
    product,
):

    delete_response = client.delete(
        f"/api/products/{product.id}",
        headers=admin_headers,
    )

    assert delete_response.status_code == 200

    response = client.get("/api/products/")

    assert response.status_code == 200
    assert response.json() == []


# ============================================================
# STOCK
# ============================================================


def test_reduce_stock(client, product):

    response = client.put(
        f"/api/products/{product.id}/stock/reduce",
        json={
            "quantity": 5
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity_reduced"] == 5
    assert data["remaining_stock"] == 20


def test_reduce_stock_insufficient_stock(
    client,
    product,
):

    response = client.put(
        f"/api/products/{product.id}/stock/reduce",
        json={
            "quantity": 100
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"


def test_reduce_stock_nonexistent_product(client):

    response = client.put(
        "/api/products/99999/stock/reduce",
        json={
            "quantity": 1
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_cannot_reduce_stock_for_inactive_product(
    client,
    product,
    db,
):

    product.is_active = False
    db.commit()

    response = client.put(
        f"/api/products/{product.id}/stock/reduce",
        json={
            "quantity": 1
        },
    )

    assert response.status_code == 400

    assert (
        response.json()["detail"]
        == "Product is not available"
    )


def test_reduce_stock_zero_quantity(
    client,
    product,
):

    response = client.put(
        f"/api/products/{product.id}/stock/reduce",
        json={
            "quantity": 0
        },
    )

    # Field(gt=0)
    assert response.status_code == 422


def test_reduce_stock_negative_quantity(
    client,
    product,
):

    response = client.put(
        f"/api/products/{product.id}/stock/reduce",
        json={
            "quantity": -5
        },
    )

    assert response.status_code == 422