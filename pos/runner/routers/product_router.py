import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from pydantic import BaseModel

from pos.core.models.product import Product
from pos.core.services.product_service import ProductService
from pos.runner.routers.infra import _Infra

router = APIRouter()


def create_product_service(request: Request) -> ProductService:
    infra: _Infra = request.app.state.infra
    return ProductService(infra.product_repo())


class CreateProductRequest(BaseModel):
    name: str
    barcode: str
    price: float


class ProductResponse(BaseModel):
    product: Product


@router.post("/", status_code=201, response_model=ProductResponse)
def create_product(
    request: CreateProductRequest,
    service: ProductService = Depends(create_product_service),
) -> ProductResponse:
    try:
        product_id = str(uuid.uuid4())
        product = service.create_product(
            product_id, request.name, request.barcode, request.price
        )
        return ProductResponse(product=product)
    except ValueError as e:
        raise HTTPException(status_code=409, detail={"error": {"message": str(e)}})


@router.get("/{product_id}", status_code=200, response_model=ProductResponse)
def get_product(
    product_id: str,
    service: ProductService = Depends(create_product_service),
) -> ProductResponse:
    product: Optional[Product] = service.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {"message": f"Product with id <{product_id}> does not exist."}
            },
        )
    return ProductResponse(product=product)


class ProductListResponse(BaseModel):
    products: List[Product]


@router.get("/", status_code=200, response_model=ProductListResponse)
def list_products(
    service: ProductService = Depends(create_product_service),
) -> ProductListResponse:
    return ProductListResponse(products=service.list_products())


class UpdateProductRequest(BaseModel):
    price: float


@router.patch("/{product_id}", status_code=200)
def update_product_price(
    product_id: str,
    request: UpdateProductRequest,
    service: ProductService = Depends(create_product_service),
) -> None:
    try:
        service.update_product_price(product_id, int(request.price))
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": {"message": str(e)}})
