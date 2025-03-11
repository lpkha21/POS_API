import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from pydantic import BaseModel

from pos.core.models.shift import Shift
from pos.core.services.shift_service import ShiftService
from pos.runner.routers.infra import _Infra

router = APIRouter()


def create_shift_service(request: Request) -> ShiftService:
    infra: _Infra = request.app.state.infra
    return ShiftService(infra.shift_repo())


class ShiftRequest(BaseModel):
    cashier: str


class ShiftCloseRequest(BaseModel):
    shift_id: str


@router.post("/", status_code=201, response_model=Shift)
def create_shift(
    request: ShiftRequest,
    service: ShiftService = Depends(create_shift_service),
) -> Shift:
    shift_id = str(uuid.uuid4())
    shift = service.create_shift(shift_id, request.cashier)
    return Shift(id=shift.id, cashier=shift.cashier)


@router.post("/close", status_code=204)
def close_shift(
    request: ShiftCloseRequest,
    service: ShiftService = Depends(create_shift_service),
) -> None:
    service.close_shift(request.shift_id)


@router.get("/{shift_id}", status_code=200, response_model=Shift)
def read_shift(
    shift_id: str,
    service: ShiftService = Depends(create_shift_service),
) -> Shift:
    try:
        shift = service.get_shift(shift_id)
        return shift
    except ValueError:
        raise HTTPException(status_code=404, detail="Shift not found")
