import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from pydantic import BaseModel

from pos.core.models.receipt import Receipt
from pos.core.services.receipt_service import ReceiptService
from pos.runner.routers.infra import _Infra

router = APIRouter()


def create_receipt_service(request: Request) -> ReceiptService:
    infra: _Infra = request.app.state.infra
    return ReceiptService(
        infra.receipt_repo(), infra.product_repo(), infra.campaign_repo()
    )


class CreateReceiptRequest(BaseModel):
    shift_id: str


class ReceiptResponse(BaseModel):
    receipt: Receipt


@router.post("/", status_code=201, response_model=ReceiptResponse)
def create_receipt(
    request: CreateReceiptRequest,
    service: ReceiptService = Depends(create_receipt_service),
) -> ReceiptResponse:
    try:
        receipt_id = str(uuid.uuid4())
        receipt = service.create_receipt(receipt_id, request.shift_id)
        return ReceiptResponse(receipt=receipt)
    except ValueError as e:
        raise HTTPException(status_code=409, detail={"error": {"message": str(e)}})


@router.get("/{receipt_id}", status_code=200, response_model=ReceiptResponse)
def get_receipt(
    receipt_id: str,
    service: ReceiptService = Depends(create_receipt_service),
) -> ReceiptResponse:
    try:
        receipt = service.get_receipt(receipt_id)
        return ReceiptResponse(receipt=receipt)
    except Exception:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {"message": f"Receipt with id <{receipt_id}> does not exists."}
            },
        )


class AddProductRequest(BaseModel):
    id: str
    quantity: int


class EmptyResponse(BaseModel):
    class Config:
        orm_mode = True


@router.post("/{receipt_id}/products", status_code=201, response_model=EmptyResponse)
def add_product_to_receipt(
    receipt_id: str,
    request: AddProductRequest,
    service: ReceiptService = Depends(create_receipt_service),
) -> EmptyResponse:
    try:
        service.add_product_to_receipt(receipt_id, request.id, request.quantity)
        return EmptyResponse()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


class PaymentResponse(BaseModel):
    total_price: float


@router.post("/{receipt_id}/quotes", status_code=201, response_model=PaymentResponse)
def calculate_payment(
    receipt_id: str,
    service: ReceiptService = Depends(create_receipt_service),
) -> PaymentResponse:
    try:
        price: float = service.get_receipt_total_price(receipt_id)
        response: PaymentResponse = PaymentResponse(total_price=price)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{receipt_id}/payments", status_code=201, response_model=EmptyResponse)
def add_payment_to_receipt(
    receipt_id: str, service: ReceiptService = Depends(create_receipt_service)
) -> EmptyResponse:
    try:
        service.close_receipt(receipt_id)
        return EmptyResponse()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
