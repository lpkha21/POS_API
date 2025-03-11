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
    db.execute("DELETE FROM shifts;")


def test_create_shift() -> None:
    shift_data = {"cashier": "John Doe"}
    response = client.post("/shift", json=shift_data)

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["cashier"] == "John Doe"


def test_close_shift() -> None:
    shift_data = {"cashier": "John Doe"}
    response = client.post("/shift", json=shift_data)
    assert response.status_code == 201
    shift_id = response.json()["id"]

    close_response = client.post("/shift/close", json={"shift_id": shift_id})
    assert close_response.status_code == 204

    get_response = client.get(f"/shift/{shift_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == shift_id
    assert get_response.json()["cashier"] == "John Doe"
    assert not get_response.json()["is_open"]


def test_read_shift() -> None:
    shift_data = {"cashier": "John Doe"}
    response = client.post("/shift", json=shift_data)
    assert response.status_code == 201
    shift_id = response.json()["id"]

    get_response = client.get(f"/shift/{shift_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == shift_id
    assert get_response.json()["cashier"] == "John Doe"
