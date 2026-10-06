import pytest

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.product import Product
from app.config import settings


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture()
def db():

    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# --------------------------------------------------
# JWT HELPERS
# --------------------------------------------------

def create_test_token(
    user_id: int,
    username: str,
    role: str,
):

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


@pytest.fixture()
def admin_token():

    return create_test_token(
        user_id=1,
        username="admin_test",
        role="ADMIN",
    )


@pytest.fixture()
def customer_token():

    return create_test_token(
        user_id=2,
        username="customer_test",
        role="CUSTOMER",
    )


@pytest.fixture()
def admin_headers(admin_token):

    return {
        "Authorization": f"Bearer {admin_token}"
    }


@pytest.fixture()
def customer_headers(customer_token):

    return {
        "Authorization": f"Bearer {customer_token}"
    }


# --------------------------------------------------
# PRODUCT FIXTURES
# --------------------------------------------------

@pytest.fixture()
def product(db):

    product = Product(
        name="iPhone Test",
        description="Test smartphone",
        price=79999.00,
        sku="IPHONE-TEST-001",
        category="Smartphones",
        image_url="/images/iphone-test.jpg",
        rating=4.5,
        stock_quantity=25,
        is_active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@pytest.fixture()
def second_product(db):

    product = Product(
        name="MacBook Test",
        description="Test laptop",
        price=150000.00,
        sku="MAC-TEST-001",
        category="Laptops",
        image_url="/images/mac-test.jpg",
        rating=4.7,
        stock_quantity=10,
        is_active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product