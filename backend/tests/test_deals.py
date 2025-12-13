"""Test deal endpoints"""


def test_create_deal(client):
    """Test creating a deal"""
    deal_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": 2022,
        "vehicle_mileage": 15000,
        "asking_price": 25000.00,
        "status": "pending"
    }
    
    response = client.post("/api/v1/deals/", json=deal_data)
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == deal_data["customer_name"]
    assert data["customer_email"] == deal_data["customer_email"]
    assert "id" in data


def test_get_deals(client):
    """Test getting all deals"""
    response = client.get("/api/v1/deals/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_deal(client):
    """Test getting a specific deal"""
    # First create a deal
    deal_data = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "vehicle_make": "Honda",
        "vehicle_model": "Accord",
        "vehicle_year": 2021,
        "vehicle_mileage": 20000,
        "asking_price": 23000.00,
        "status": "pending"
    }
    
    create_response = client.post("/api/v1/deals/", json=deal_data)
    assert create_response.status_code == 201
    deal_id = create_response.json()["id"]
    
    # Now get the deal
    response = client.get(f"/api/v1/deals/{deal_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == deal_id
    assert data["customer_name"] == deal_data["customer_name"]


def test_get_nonexistent_deal(client):
    """Test getting a non-existent deal"""
    response = client.get("/api/v1/deals/99999")
    assert response.status_code == 404
