from typing import Any, List

from pos.core.models.campaigns import BuyNGetN, Combo, DiscountItem, DiscountPrice
from pos.core.models.receipt import Receipt
from pos.core.models.repositories import CampaignRepository
from pos.infra.database import Database


class CampaignSQLiteRepository(CampaignRepository):
    def __init__(self, db: Database):
        self.db = db

    def create_discount_item(self, campaign: DiscountItem) -> DiscountItem:
        self.db.execute(
            "INSERT INTO discount_items (id, product_id, discount) VALUES (?, ?, ?)",
            (campaign.id, campaign.product_id, campaign.discount),
        )
        return campaign

    def create_discount_price(self, campaign: DiscountPrice) -> DiscountPrice:
        self.db.execute(
            "INSERT INTO discount_prices (id, price, discount) VALUES (?, ?, ?)",
            (campaign.id, campaign.price, campaign.discount),
        )
        return campaign

    def create_buy_n_get_n(self, campaign: BuyNGetN) -> BuyNGetN:
        self.db.execute(
            "INSERT INTO buyNgetN (id, product_id,"
            " product_amount, gift_id, gift_amount) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                campaign.id,
                campaign.product_id,
                campaign.product_amount,
                campaign.gift_id,
                campaign.gift_amount,
            ),
        )
        return campaign

    def create_combo(self, campaign: Combo) -> Combo:
        self.db.execute(
            "INSERT INTO combo (id, products_id, discount) VALUES (?, ?, ?)",
            (campaign.id, ",".join(campaign.products), campaign.discount),
        )
        return campaign

    def delete(self, campaign_id: str) -> None:
        self.db.execute("DELETE FROM discount_items WHERE id = ?", (campaign_id,))
        self.db.execute("DELETE FROM discount_prices WHERE id = ?", (campaign_id,))
        self.db.execute("DELETE FROM buyNgetN WHERE id = ?", (campaign_id,))
        self.db.execute("DELETE FROM combo WHERE id = ?", (campaign_id,))

    def list(self) -> List[Any]:
        campaigns: List[Any] = []

        discount_items = self.db.fetchall("SELECT * FROM discount_items")

        if discount_items:
            for campaign in discount_items:
                campaigns.append(
                    DiscountItem(
                        id=campaign[0], product_id=campaign[1], discount=campaign[2]
                    )
                )

        discount_prices = self.db.fetchall("SELECT * FROM discount_prices")

        if discount_prices:
            for campaign in discount_prices:
                campaigns.append(
                    DiscountPrice(
                        id=campaign[0], price=campaign[1], discount=campaign[2]
                    )
                )

        but_n_get_n = self.db.fetchall("SELECT * FROM buyNgetN")

        if but_n_get_n:
            for campaign in but_n_get_n:
                campaigns.append(
                    BuyNGetN(
                        id=campaign[0],
                        product_id=campaign[1],
                        product_amount=campaign[2],
                        gift_id=campaign[3],
                        gift_amount=campaign[4],
                    )
                )

        combos = self.db.fetchall("SELECT * FROM combo")

        if combos:
            for campaign in combos:
                campaigns.append(
                    Combo(
                        id=campaign[0],
                        products=campaign[1].split(","),
                        discount=campaign[2],
                    )
                )

        return campaigns

    def campaign_check(self, receipt: Receipt) -> None:
        receipt.discount_price = receipt.total_price
        self.__check_discount_item(receipt)
        self.__check_combo(receipt)
        self.__check_discount_price(receipt)
        self.__check_buy_n_get_n(receipt)

    def __check_discount_price(self, receipt: Receipt) -> None:
        rows = self.db.fetchall("SELECT price, discount FROM discount_prices")

        if rows:
            final_discount = 0
            campaign_price = 0
            for row in rows:
                if receipt.discount_price >= row[0] > campaign_price:
                    final_discount = row[1]
                    campaign_price = row[0]
            receipt.discount_price -= final_discount

    def __check_combo(self, receipt: Receipt) -> None:
        products = receipt.products
        product_ids = list(products.keys())

        rows = self.db.fetchall("SELECT products_id, discount FROM combo")
        if rows:
            for row in rows:
                combo_products = row[0].split(",")
                print(combo_products)
                if set(combo_products).issubset(set(product_ids)):
                    receipt.discount_price -= row[1]

    def __check_buy_n_get_n(self, receipt: Receipt) -> None:
        products = receipt.products
        for product_id, quantity in products.items():
            rows = self.db.fetchall(
                "SELECT product_amount, gift_id, gift_amount "
                "FROM buyNgetN WHERE product_id = ?",
                (product_id,),
            )
            if rows:
                for row in rows:
                    if quantity >= row[0]:
                        receipt.gift_products[row[1]] = row[2]

    def __check_discount_item(self, receipt: Receipt) -> None:
        products = receipt.products
        for product_id, quantity in products.items():
            row = self.db.fetchone(
                "SELECT discount FROM discount_items WHERE product_id = ?",
                (product_id,),
            )
            if row:
                total_discount = quantity * row[0]
                receipt.discount_price -= total_discount
