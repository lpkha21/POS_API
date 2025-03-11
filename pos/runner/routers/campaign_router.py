import uuid
from typing import Any, List

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from pydantic import BaseModel

from pos.core.models.campaigns import BuyNGetN, Combo, DiscountItem, DiscountPrice
from pos.core.services.campaign_service import CampaignService
from pos.runner.routers.infra import _Infra

router = APIRouter()


def create_campaign_service(request: Request) -> CampaignService:
    infra: _Infra = request.app.state.infra
    return CampaignService(infra.campaign_repo())


class DiscountItemRequest(BaseModel):
    product_id: str
    discount: int


class DiscountPriceRequest(BaseModel):
    price: int
    discount: int


class BuyNGetNRequest(BaseModel):
    product_id: str
    product_amount: int
    gift_id: str
    gift_amount: int


class ComboRequest(BaseModel):
    products: List[str]
    discount: int


@router.post("/discount/item", status_code=201, response_model=DiscountItem)
def create_discount_item_campaign(
    request: DiscountItemRequest,
    service: CampaignService = Depends(create_campaign_service),
) -> DiscountItem:
    campaign_id = str(uuid.uuid4())
    return service.create_discount_item_campaign(
        campaign_id, request.product_id, request.discount
    )


@router.post("/discount/price", status_code=201, response_model=DiscountPrice)
def create_discount_price_campaign(
    request: DiscountPriceRequest,
    service: CampaignService = Depends(create_campaign_service),
) -> DiscountPrice:
    campaign_id = str(uuid.uuid4())
    return service.create_discount_price_campaign(
        campaign_id, request.price, request.discount
    )


@router.post("/nbyn", status_code=201, response_model=BuyNGetN)
def create_buy_n_get_n_campaign(
    request: BuyNGetNRequest,
    service: CampaignService = Depends(create_campaign_service),
) -> BuyNGetN:
    campaign_id = str(uuid.uuid4())
    return service.create_buy_n_get_n_campaign(
        campaign_id,
        request.product_id,
        request.product_amount,
        request.gift_id,
        request.gift_amount,
    )


@router.post("/combo", status_code=201, response_model=Combo)
def create_combo_campaign(
    request: ComboRequest,
    service: CampaignService = Depends(create_campaign_service),
) -> Combo:
    campaign_id = str(uuid.uuid4())
    return service.create_combo_campaign(
        campaign_id, request.products, request.discount
    )


@router.delete("/{campaign_id}", status_code=204)
def deactivate_campaign(
    campaign_id: str,
    service: CampaignService = Depends(create_campaign_service),
) -> None:
    service.delete_discount_campaign(campaign_id)


@router.get("", status_code=200, response_model=List[Any])
def list_campaigns(
    service: CampaignService = Depends(create_campaign_service),
) -> List[Any]:
    return service.list_campaigns()
