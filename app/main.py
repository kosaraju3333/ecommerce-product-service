from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models.product import Product
from app.routers.products import router as product_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="E-Commerce Product Service",
    description="Product microservice for the E-Commerce platform",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(product_router)


@app.get("/")
def root():

    return {
        "service": "product-service",
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "service": "product-service",
        "status": "UP"
    }