import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from pos.infra.database import Database
from pos.runner.__main__ import app  # Import FastAPI app

db = Database()

# Initialize FastAPI test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db() -> None:
    db.execute("DELETE FROM receipts;")
    db.execute("DELETE FROM products;")
    db.execute("DELETE FROM shifts;")


def test_get_sales() -> None:
    response = client.get("/sales")

    assert response.status_code == 200
    assert "sales" in response.json()
    assert isinstance(response.json()["sales"], dict)


class ShiftRequest(BaseModel):
    cashier: str


def __create_shift_with_sales() -> str:
    """Helper function to create a shift and add sales to it."""
    request = ShiftRequest(cashier="luka")

    # Convert ShiftRequest to dictionary
    shift = client.post("/shift", json=request.dict())  # Convert to dict here
    assert shift.status_code == 201

    shift_id: str = shift.json()["id"]  # Assuming 'id' is in the response JSON

    # Add sales/receipt to the shift
    receipt_data = {"shift_id": shift_id}
    create_response = client.post("/receipts/", json=receipt_data)
    receipt_id = create_response.json()["receipt"]["id"]

    product_data = {"name": "banana", "barcode": "222", "price": 200}
    product_response = client.post("/products/", json=product_data)
    product_id = product_response.json()["product"]["id"]
    data = {"id": product_id, "quantity": 1}

    client.post(f"/receipts/{receipt_id}/products", json=data)
    client.post(f"/receipts/{receipt_id}/quotes")
    client.post(f"/receipts/{receipt_id}/payments")
    return shift_id


def test_get_sales_with_data() -> None:
    __create_shift_with_sales()

    response = client.get("/sales")

    assert response.status_code == 200

    assert response.json()["sales"]["revenue_gel"] == 200


def test_get_x_report_success() -> None:
    shift_id = __create_shift_with_sales()

    response = client.get("/reports/x-report", params={"shift_id": shift_id})
    assert response.status_code == 200
    assert "report" in response.json()


def test_get_z_report_success() -> None:
    shift_id = __create_shift_with_sales()

    response = client.get("/reports/z-report", params={"shift_id": shift_id})
    assert response.status_code == 200
    assert "report" in response.json()

    response = client.get(f"/shift/{shift_id}")
    assert response.status_code == 200
    assert not response.json()["is_open"]
