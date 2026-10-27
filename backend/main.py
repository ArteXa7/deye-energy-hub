"""
Головний FastAPI сервер (backend/main.py)
Повний захист дашборду та налаштувань через сесійні Cookie (Логін + Пароль)
"""

import asyncio
import os
import secrets
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Body, Depends, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from backend.config import config
from backend.database import init_db, get_blackout_history, get_setting, set_setting, get_all_settings
from backend.collector import collector
from backend.dtek_parser import dtek_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("[Server] База даних ініціалізована успішно.")
    collector_task = asyncio.create_task(collector.start_background_loop())
    yield
    collector.running = False
    collector_task.cancel()
    print("[Server] Сервер зупинено.")


app = FastAPI(
    title="Deye Home Energy System API",
    version="3.0 PRO",
    lifespan=lifespan
)

# Активні сесії користувачів
active_sessions = set()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoadControlRequest(BaseModel):
    device: str  # "fridge", "kettle", "reset"
    action: bool


def is_authenticated(request: Request) -> bool:
    token = request.cookies.get("deye_session")
    return bool(token and token in active_sessions)


async def require_auth_api(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Необхідна авторизація")
    return True


# --- Авторизація ---

@app.post("/api/auth/login")
async def api_login(req: LoginRequest, response: Response):
    expected_user = get_setting("admin_username", os.getenv("ADMIN_USERNAME", "admin"))
    expected_pass = get_setting("admin_password", os.getenv("ADMIN_PASSWORD", "admin"))

    if req.username == expected_user and req.password == expected_pass:
        token = secrets.token_hex(24)
        active_sessions.add(token)
        response.set_cookie(
            key="deye_session",
            value=token,
            httponly=True,
            max_age=86400 * 30,  # 30 днів
            samesite="lax"
        )
        return {"success": True}

    raise HTTPException(status_code=401, detail="Невірний логін або пароль")


@app.post("/api/auth/logout")
async def api_logout(request: Request, response: Response):
    token = request.cookies.get("deye_session")
    if token in active_sessions:
        active_sessions.remove(token)
    response.delete_cookie("deye_session")
    return {"success": True}


# --- Захищені API Ендпоінти ---

@app.get("/api/status", dependencies=[Depends(require_auth_api)])
async def api_get_status():
    try:
        metrics = collector.get_current_metrics()
        schedule_data = await dtek_manager.fetch_or_get_schedule()
        dtek_status = dtek_manager.get_current_status(schedule_data)
        return {**metrics, "dtek": dtek_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", dependencies=[Depends(require_auth_api)])
async def api_get_history(days: int = 30):
    try:
        history = get_blackout_history(days=days)
        return {"count": len(history), "days": days, "events": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/toggle-grid", dependencies=[Depends(require_auth_api)])
async def api_toggle_grid():
    try:
        new_state = await collector.manual_toggle_grid()
        return {
            "success": True,
            "grid_online": new_state,
            "message": "Мережа в нормі" if new_state else "Мережа відключена (автономний режим)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control-load", dependencies=[Depends(require_auth_api)])
async def api_control_load(req: LoadControlRequest):
    if req.device == "fridge":
        collector.extra_load = collector.extra_load + 150 if req.action else max(0.0, collector.extra_load - 150)
    elif req.device == "kettle":
        collector.extra_load = collector.extra_load + 1800 if req.action else max(0.0, collector.extra_load - 1800)
    elif req.device == "reset":
        collector.extra_load = 0.0

    return {
        "success": True,
        "extra_load": collector.extra_load,
        "current_load": int(collector.base_load + collector.extra_load)
    }


@app.get("/api/admin/settings", dependencies=[Depends(require_auth_api)])
async def api_get_settings():
    try:
        return get_all_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/settings", dependencies=[Depends(require_auth_api)])
async def api_save_settings(settings: Dict[str, Any] = Body(...)):
    try:
        for k, v in settings.items():
            if k in ("admin_password", "admin_username") and not str(v).strip():
                continue
            set_setting(k, v)

        collector.apply_new_settings()
        dtek_manager.apply_new_settings()
        return {"success": True, "message": "Налаштування успішно збережено та застосовано"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/admin/test-modbus", dependencies=[Depends(require_auth_api)])
async def api_test_modbus(data: Dict[str, Any] = Body(...)):
    host = data.get("modbus_host", config.MODBUS_HOST)
    port = int(data.get("modbus_tcp_port", config.MODBUS_TCP_PORT))
    m_type = data.get("modbus_type", config.MODBUS_TYPE)

    if m_type == "tcp":
        try:
            from pymodbus.client import ModbusTcpClient
            client = ModbusTcpClient(host, port=port, timeout=3)
            connected = client.connect()
            if connected:
                res = client.read_holding_registers(address=630, count=2, slave=1)
                client.close()
                if not res.isError():
                    return {"success": True, "message": f"Успішно підключено до {host}:{port}! Дані прочитано."}
                return {"success": True, "message": f"З'єднання з {host}:{port} встановлено, але регістри не відповідають."}
            return {"success": False, "message": f"Не вдалося встановити TCP з'єднання з {host}:{port}"}
        except Exception as e:
            return {"success": False, "message": f"Помилка тесту Modbus TCP: {str(e)}"}
    else:
        serial_port = data.get("modbus_port", config.MODBUS_PORT)
        try:
            from pymodbus.client import ModbusSerialClient
            client = ModbusSerialClient(port=serial_port, baudrate=9600, timeout=3)
            connected = client.connect()
            if connected:
                client.close()
                return {"success": True, "message": f"Послідовний порт {serial_port} успішно відкритий."}
            return {"success": False, "message": f"Не вдалося відкрити послідовний порт {serial_port}"}
        except Exception as e:
            return {"success": False, "message": f"Помилка тесту Modbus RTU: {str(e)}"}


# --- Сторінки та статика ---

@app.get("/login")
async def serve_login(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/", status_code=302)
    return FileResponse(config.STATIC_DIR / "login.html")


@app.get("/")
async def serve_index(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/settings")
async def serve_settings(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=302)
    return FileResponse(config.STATIC_DIR / "settings.html")


@app.get("/styles.css")
async def serve_css():
    return FileResponse(config.STATIC_DIR / "styles.css")


@app.get("/app.js")
async def serve_js():
    return FileResponse(config.STATIC_DIR / "app.js")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)