import unittest

from pos.core.services.campaign_service import CampaignService
from pos.infra.database import Database
from pos.infra.sqlite_repositories.campaign_sqlite_repository import (
    CampaignSQLiteRepository,
)


class TestCampaignService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.campaign_repository = CampaignSQLiteRepository(self.db)
        self.campaign_service = CampaignService(self.campaign_repository)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS buyNgetN")
        self.db.execute("DROP TABLE IF EXISTS combo")
        self.db.execute("DROP TABLE IF EXISTS discount_items")
        self.db.execute("DROP TABLE IF EXISTS discount_prices")

    def test_create_discount_item_campaign(self) -> None:
        campaign = self.campaign_service.create_discount_item_campaign(
            campaign_id="1", product_id="123", discount=5
        )
        self.assertEqual(campaign.id, "1")
        self.assertEqual(campaign.product_id, "123")
        self.assertEqual(campaign.discount, 5)

    def test_create_discount_price_campaign(self) -> None:
        campaign = self.campaign_service.create_discount_price_campaign(
            campaign_id="2", price=500, discount=50
        )
        self.assertEqual(campaign.id, "2")
        self.assertEqual(campaign.price, 500)
        self.assertEqual(campaign.discount, 50)

    def test_create_buy_n_get_n_campaign(self) -> None:
        campaign = self.campaign_service.create_buy_n_get_n_campaign(
            campaign_id="3",
            product_id="101",
            product_amount=2,
            gift_id="102",
            gift_amount=1,
        )
        self.assertEqual(campaign.id, "3")
        self.assertEqual(campaign.product_id, "101")
        self.assertEqual(campaign.product_amount, 2)
        self.assertEqual(campaign.gift_id, "102")
        self.assertEqual(campaign.gift_amount, 1)

    def test_create_combo_campaign(self) -> None:
        campaign = self.campaign_service.create_combo_campaign(
            campaign_id="4", products=["103", "104"], discount=20
        )
        self.assertEqual(campaign.id, "4")
        self.assertEqual(campaign.products, ["103", "104"])
        self.assertEqual(campaign.discount, 20)

    def test_list_campaigns(self) -> None:
        self.campaign_service.create_discount_item_campaign(
            campaign_id="1", product_id="123", discount=5
        )
        self.campaign_service.create_discount_price_campaign(
            campaign_id="2", price=500, discount=50
        )
        self.campaign_service.create_discount_item_campaign(
            campaign_id="3", product_id="90", discount=10
        )
        self.campaign_service.create_combo_campaign(
            campaign_id="4", products=["103", "104"], discount=20
        )

        self.assertEqual(len(self.campaign_service.list_campaigns()), 4)

    def test_delete_discount_campaign(self) -> None:
        self.campaign_service.create_discount_item_campaign(
            campaign_id="1", product_id="123", discount=5
        )
        self.campaign_service.create_discount_price_campaign(
            campaign_id="2", price=500, discount=50
        )
        self.assertEqual(len(self.campaign_service.list_campaigns()), 2)

        self.campaign_service.delete_discount_campaign(campaign_id="1")
        self.assertEqual(len(self.campaign_service.list_campaigns()), 1)

        self.campaign_service.delete_discount_campaign(campaign_id="2")
        self.assertEqual(len(self.campaign_service.list_campaigns()), 0)
