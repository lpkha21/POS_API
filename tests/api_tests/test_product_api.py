import uuid

from fastapi.testclient import TestClient

from pos.infra.database import Database
from pos.runner.__main__ import app  # FastAPI app

db = Database()

# Initialize FastAPI test client
client = TestClient(app)


def reset_db() -> None:
    db.execute("DELETE FROM products;")


def test_create_product() -> None:
    reset_db()
    # Unique product data for each test run
    barcode: str = str(uuid.uuid4().int)[:10]
    product_data = {
        "name": "laptop",  # Ensure unique name
        "barcode": barcode,  # Ensure unique barcode
        "price": 1000.0,
    }

    response = client.post("/products", json=product_data)
    assert response.status_code == 201

    response_data = response.json()
    assert "product" in response_data
    assert response_data["product"]["name"] == "laptop"
    assert response_data["product"]["barcode"] == barcode


def test_create_product_duplicate_barcode() -> None:
    reset_db()

    # Create a product first
    product_data = {
        "unit_id": "unit_1",
        "name": "Laptop",
        "barcode": "12345",
        "price": 1000.0,
    }
    client.post("/products", json=product_data)

    # Try to create another product with the same barcode
    response = client.post("/products", json=product_data)

    # Check that the response status code is 409 Conflict (duplicate barcode)
    assert response.status_code == 409


def test_read_product_endpoint_existing() -> None:
    reset_db()

    # First, create a product to test the read operation
    product_data = {
        "unit_id": "unit_1",
        "name": "Laptop",
        "barcode": "12345",
        "price": 1000.0,
    }
    create_response = client.post("/products", json=product_data)
    print(create_response.json())
    product_id = create_response.json()["product"]["id"]

    # Now test reading the product
    response = client.get(f"/products/{product_id}")

    assert (
        response.status_code == 200
    )  # Assert that status code is 200 OK for existing product
    response_data = response.json()
    assert response_data["product"]["name"] == "Laptop"
    assert response_data["product"]["barcode"] == "12345"


def test_read_product_endpoint_not_found() -> None:
    reset_db()

    # Test the read endpoint with a non-existing product ID
    response = client.get("/products/non_existing_id")

    assert response.status_code == 404


def test_list_products_endpoint() -> None:
    reset_db()

    # Create a couple of products to test the list endpoint
    product_data_1 = {
        "unit_id": "unit_1",
        "name": "Laptop",
        "barcode": "12345",
        "price": 1000.0,
    }
    product_data_2 = {
        "unit_id": "unit_2",
        "name": "Phone",
        "barcode": "67890",
        "price": 500.0,
    }

    client.post("/products", json=product_data_1)
    client.post("/products", json=product_data_2)

    # Test listing products
    response = client.get("/products")

    assert (
        response.status_code == 200
    )  # Assert that status code is 200 OK for list endpoint
    response_data = response.json()
    assert "products" in response_data
    assert len(response_data["products"]) > 0  # Check that products are returned
    assert any(product["name"] == "Laptop" for product in response_data["products"])
    assert any(product["name"] == "Phone" for product in response_data["products"])


def test_update_product_success() -> None:
    reset_db()

    # Create a product first
    product_data = {
        "unit_id": "unit_1",
        "name": "Laptop",
        "barcode": "12345",
        "price": 1000.0,
    }
    create_response = client.post("/products", json=product_data)
    product_id = create_response.json()["product"]["id"]

    # Update the product's price
    updated_data = {"price": 1200.0}
    response = client.patch(f"/products/{product_id}", json=updated_data)

    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200

    # Check if the product's price was updated correctly
    read_response = client.get(f"/products/{product_id}")
    read_response_data = read_response.json()
    assert read_response_data["product"]["price"] == 1200.0
