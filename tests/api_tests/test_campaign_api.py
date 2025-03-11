import pytest
from fastapi.testclient import TestClient

from pos.infra.database import Database
from pos.runner.__main__ import app  # Import FastAPI app

# Initialize FastAPI test client
client = TestClient(app)
db = Database()


@pytest.fixture(autouse=True)
def reset_db() -> None:
    db.execute("DELETE FROM buyNgetN;")
    db.execute("DELETE FROM combo;")
    db.execute("DELETE FROM discount_items;")
    db.execute("DELETE FROM discount_prices;")
    db.execute("DELETE FROM products;")


def test_create_discount_item_campaign() -> None:
    product_data = {"name": "apple", "barcode": "123", "price": 150}
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 201
    product_id = product_response.json()["product"]["id"]

    discount_data = {"product_id": product_id, "discount": 10}
    response = client.post("/campaign/discount/item", json=discount_data)

    assert response.status_code == 201
    assert response.json()["product_id"] == product_id
    assert response.json()["discount"] == 10


def test_create_discount_price_campaign() -> None:
    discount_data = {"price": 500, "discount": 50}
    response = client.post("/campaign/discount/price", json=discount_data)

    assert response.status_code == 201
    assert response.json()["price"] == 500
    assert response.json()["discount"] == 50


def test_create_buy_n_get_n_campaign() -> None:
    product_data = {"name": "orange", "barcode": "789", "price": 300}
    product_response = client.post("/products/", json=product_data)
    assert product_response.status_code == 201
    product_id = product_response.json()["product"]["id"]

    gift_data = {"name": "grape", "barcode": "456", "price": 200}
    gift_response = client.post("/products/", json=gift_data)
    assert gift_response.status_code == 201
    gift_id = gift_response.json()["product"]["id"]

    campaign_data = {
        "product_id": product_id,
        "product_amount": 2,
        "gift_id": gift_id,
        "gift_amount": 1,
    }
    response = client.post("/campaign/nbyn", json=campaign_data)

    assert response.status_code == 201
    assert response.json()["product_id"] == product_id
    assert response.json()["gift_id"] == gift_id


def test_create_combo_campaign() -> None:
    product1_data = {"name": "milk", "barcode": "111", "price": 250}
    product2_data = {"name": "bread", "barcode": "222", "price": 100}

    product1_response = client.post("/products/", json=product1_data)
    product2_response = client.post("/products/", json=product2_data)

    assert product1_response.status_code == 201
    assert product2_response.status_code == 201

    product1_id = product1_response.json()["product"]["id"]
    product2_id = product2_response.json()["product"]["id"]

    campaign_data = {"products": [product1_id, product2_id], "discount": 20}
    response = client.post("/campaign/combo", json=campaign_data)

    assert response.status_code == 201
    assert set(response.json()["products"]) == {product1_id, product2_id}
    assert response.json()["discount"] == 20


def test_list_campaigns() -> None:
    response = client.get("/campaign")
    print("\n", response.json(), "\n")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_deactivate_campaign() -> None:
    discount_data = {"price": 1000, "discount": 100}
    response = client.post("/campaign/discount/price", json=discount_data)
    assert response.status_code == 201
    campaign_id = response.json()["id"]

    delete_response = client.delete(f"/campaign/{campaign_id}")
    assert delete_response.status_code == 204
