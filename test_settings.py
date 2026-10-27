from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, get_setting, set_setting, get_all_settings
from backend.dtek_parser import dtek_manager
from backend.collector import collector
import json

client = TestClient(app)

def test_database_settings():
    init_db()
    set_setting("test_key", "test_val")
    assert get_setting("test_key") == "test_val"
    all_s = get_all_settings()
    assert "test_key" in all_s
    assert all_s["test_key"] == "test_val"

def test_collector_telemetry():
    metrics = collector.get_current_metrics()
    assert "inverter_model" in metrics
    assert "battery_capacity_ah" in metrics
    assert "battery_soh" in metrics
    assert metrics["battery_capacity_wh"] > 0

def test_dtek_parser_subgroups_and_custom():
    init_db()
    # Test kyiv subgroup
    dtek_manager.region = "kyiv_region"
    dtek_manager.group = "1.1"
    sched1 = dtek_manager.generate_default_schedule_for_group("1.1", 0)
    assert "hourly" in sched1
    assert len(sched1["hourly"]) == 24

    # Test custom schedule
    dtek_manager.region = "custom"
    custom_sched = {str(h): "maybe" for h in range(24)}
    custom_sched["12"] = "no"
    set_setting("custom_dtek_schedule", json.dumps(custom_sched))
    
    sched_custom = dtek_manager.generate_default_schedule_for_group("custom", 0)
    assert sched_custom["hourly"][12]["status"] == "no"
    assert sched_custom["hourly"][0]["status"] == "maybe"

    status = dtek_manager.get_current_status(sched_custom)
    assert status["group"] == "Власний"

def test_admin_login_and_settings_api():
    init_db()
    # Wrong password
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert response.status_code == 401

    # Correct password
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Get settings (cookie is stored in client session)
    response = client.get("/api/admin/settings")
    assert response.status_code == 200
    settings = response.json()
    assert "modbus_host" in settings

    # Save settings
    response = client.post("/api/admin/settings", json={"modbus_host": "192.168.1.150"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert get_setting("modbus_host") == "192.168.1.150"
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_database_settings()
    test_collector_telemetry()
    test_dtek_parser_subgroups_and_custom()
    test_admin_login_and_settings_api()
    print("All assertions passed!")
