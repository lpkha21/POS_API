import uuid
from typing import Tuple

import httpx
import pytest
from fastapi.testclient import TestClient

from pos.infra.database import Database
from pos.runner.__main__ import app  # Import FastAPI app

db = Database()

# Initialize FastAPI test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db() -> None:
    db.execute("DELETE FROM receipts;")
    db.execute("DELETE FROM products;")


def test_create_receipt() -> None:
    request_data = {"shift_id": str(uuid.uuid4())}
    response = client.post("/receipts/", json=request_data)
    assert response.status_code == 201
    response_data = response.json()
    assert "receipt" in response_data
    assert response_data["receipt"]["shift_id"] == request_data["shift_id"]


def test_get_receipt_success() -> None:
    request_data = {"shift_id": str(uuid.uuid4())}
    create_response = client.post("/receipts/", json=request_data)
    receipt_id = create_response.json()["receipt"]["id"]

    response = client.get(f"/receipts/{receipt_id}")
    assert response.status_code == 200
    assert response.json()["receipt"]["id"] == receipt_id


def test_get_receipt_not_found() -> None:
    response = client.get("/receipts/non_existing_id")
    assert response.status_code == 404


def __add_product_to_receipt() -> Tuple[int, httpx.Response, httpx.Response]:
    request_data = {"shift_id": str(uuid.uuid4())}
    create_response = client.post("/receipts/", json=request_data)

    receipt_id = create_response.json()["receipt"]["id"]

    product_create_data = {"name": "apple", "barcode": "111", "price": 100}

    product_response = client.post("/products/", json=product_create_data)

    product_data = {"id": product_response.json()["product"]["id"], "quantity": 1}

    response = client.post(f"/receipts/{receipt_id}/products", json=product_data)

    return receipt_id, product_response, response


def test_add_product_to_receipt() -> None:
    [_, _, receipt_response] = __add_product_to_receipt()

    assert receipt_response.status_code == 201


def test_calculate_payment() -> None:
    [receipt_id, _, _] = __add_product_to_receipt()

    response = client.post(f"/receipts/{receipt_id}/quotes")
    print("\n", response.json(), "\n")
    assert response.status_code == 201
    assert "total_price" in response.json()
    assert response.json()["total_price"] == 100


def test_add_payment_to_receipt() -> None:
    request_data = {"shift_id": str(uuid.uuid4())}
    create_response = client.post("/receipts/", json=request_data)
    receipt_id = create_response.json()["receipt"]["id"]

    response = client.post(f"/receipts/{receipt_id}/payments")
    assert response.status_code == 201
