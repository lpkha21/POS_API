import unittest

from pos.core.models.campaigns import BuyNGetN, Combo, DiscountItem, DiscountPrice
from pos.core.models.receipt import Receipt
from pos.infra.database import Database
from pos.infra.sqlite_repositories.campaign_sqlite_repository import (
    CampaignSQLiteRepository,
)


class TestReportRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.repo = CampaignSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS discount_items")
        self.db.execute("DROP TABLE IF EXISTS discount_prices")
        self.db.execute("DROP TABLE IF EXISTS combo")
        self.db.execute("DROP TABLE IF EXISTS buyNgetN")

    def test_create_discount_item(self) -> None:
        campaign = DiscountItem(id="1", product_id="A1", discount=10)
        created_campaign = self.repo.create_discount_item(campaign)
        self.assertEqual(created_campaign.id, "1")
        self.assertEqual(created_campaign.product_id, "A1")
        self.assertEqual(created_campaign.discount, 10)

    def test_create_discount_price(self) -> None:
        campaign = DiscountPrice(id="1", price=100, discount=15)
        created_campaign = self.repo.create_discount_price(campaign)
        self.assertEqual(created_campaign.id, "1")
        self.assertEqual(created_campaign.price, 100)
        self.assertEqual(created_campaign.discount, 15)

    def test_create_buy_n_get_n(self) -> None:
        campaign = BuyNGetN(
            id="1", product_id="A1", product_amount=2, gift_id="B1", gift_amount=1
        )
        created_campaign = self.repo.create_buy_n_get_n(campaign)
        self.assertEqual(created_campaign.id, "1")
        self.assertEqual(created_campaign.product_id, "A1")
        self.assertEqual(created_campaign.product_amount, 2)
        self.assertEqual(created_campaign.gift_id, "B1")
        self.assertEqual(created_campaign.gift_amount, 1)

    def test_create_combo(self) -> None:
        campaign = Combo(id="1", products=["A1", "B1"], discount=20)
        created_campaign = self.repo.create_combo(campaign)
        self.assertEqual(created_campaign.id, "1")
        self.assertEqual(created_campaign.products, ["A1", "B1"])
        self.assertEqual(created_campaign.discount, 20)

    def test_list_campaigns(self) -> None:
        campaign1 = DiscountItem(id="1", product_id="A1", discount=10)
        campaign2 = DiscountPrice(id="2", price=100, discount=15)
        campaign3 = BuyNGetN(
            id="3", product_id="A1", product_amount=2, gift_id="B1", gift_amount=1
        )
        self.repo.create_discount_item(campaign1)
        self.repo.create_discount_price(campaign2)
        self.repo.create_buy_n_get_n(campaign3)
        campaigns = self.repo.list()
        self.assertEqual(len(campaigns), 3)

    def test_delete_campaign(self) -> None:
        campaign_disc: DiscountItem = DiscountItem(id="1", product_id="A1", discount=10)
        self.repo.create_discount_item(campaign_disc)
        self.repo.delete("1")
        campaigns = self.repo.list()
        self.assertEqual(len(campaigns), 0)

        campaign_disc = DiscountItem(id="1", product_id="A1", discount=10)
        self.repo.create_discount_item(campaign_disc)
        campaign_combo: Combo = Combo(id="2", products=["A1", "B1"], discount=20)
        self.repo.create_combo(campaign_combo)
        self.repo.delete("2")
        campaigns = self.repo.list()
        self.assertEqual(len(campaigns), 1)

    def test_campaign_check(self) -> None:
        receipt = Receipt(id="1", shift_id="22")
        receipt.products["A1"] = 2
        receipt.products["2"] = 3
        receipt.total_price = 31

        combo = Combo(id="1", products=["A1", "2"], discount=2)
        self.repo.create_combo(combo)

        discount_price_campaign = DiscountPrice(id="1", price=10, discount=2)
        self.repo.create_discount_price(discount_price_campaign)

        discount_item_campaign = DiscountItem(id="2", product_id="A1", discount=3)
        self.repo.create_discount_item(discount_item_campaign)

        self.repo.campaign_check(receipt)

        self.assertEqual(receipt.discount_price, 21)
