from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_setting, set_setting, get_all_settings

client = TestClient(app)

def test_database_settings():
    init_db()
    set_setting("test_key", "test_val")
    assert get_setting("test_key") == "test_val"
    all_s = get_all_settings()
    assert "test_key" in all_s
    assert all_s["test_key"] == "test_val"

def test_admin_login_and_settings_api():
    init_db()
    # Wrong password
    response = client.post("/api/admin/login", json={"password": "wrongpassword"})
    assert response.status_code == 401

    # Default password (admin)
    response = client.post("/api/admin/login", json={"password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    token = data["token"]

    # Get settings with token
    response = client.get("/api/admin/settings", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    settings = response.json()
    assert "modbus_host" in settings

    # Save settings with token
    response = client.post("/api/admin/settings", json={"modbus_host": "192.168.1.150"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert get_setting("modbus_host") == "192.168.1.150"
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_database_settings()
    test_admin_login_and_settings_api()
    print("All assertions passed!")

