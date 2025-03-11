from typing import Any, List

from pos.core.models.campaigns import BuyNGetN, Combo, DiscountItem, DiscountPrice
from pos.core.models.repositories import CampaignRepository


class CampaignService:
    def __init__(self, campaign_repository: CampaignRepository):
        self.campaign_repository = campaign_repository

    def create_discount_item_campaign(
        self, campaign_id: str, product_id: str, discount: int
    ) -> DiscountItem:
        campaign = DiscountItem(
            id=campaign_id, product_id=product_id, discount=discount
        )
        return self.campaign_repository.create_discount_item(campaign)

    def create_discount_price_campaign(
        self, campaign_id: str, price: int, discount: int
    ) -> DiscountPrice:
        campaign = DiscountPrice(id=campaign_id, price=price, discount=discount)
        return self.campaign_repository.create_discount_price(campaign)

    def create_buy_n_get_n_campaign(
        self,
        campaign_id: str,
        product_id: str,
        product_amount: int,
        gift_id: str,
        gift_amount: int,
    ) -> BuyNGetN:
        campaign = BuyNGetN(
            id=campaign_id,
            product_id=product_id,
            product_amount=product_amount,
            gift_id=gift_id,
            gift_amount=gift_amount,
        )
        return self.campaign_repository.create_buy_n_get_n(campaign)

    def create_combo_campaign(
        self, campaign_id: str, products: List[str], discount: int
    ) -> Combo:
        campaign = Combo(id=campaign_id, products=products, discount=discount)
        return self.campaign_repository.create_combo(campaign)

    def delete_discount_campaign(self, campaign_id: str) -> None:
        self.campaign_repository.delete(campaign_id)

    def list_campaigns(self) -> List[Any]:
        return self.campaign_repository.list()
