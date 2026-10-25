"""
Головний FastAPI сервер (backend/main.py)
Роздача статичних файлів фронтенду, API статусів, історії та симуляції
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.config import config
from backend.database import init_db, get_blackout_history
from backend.collector import collector
from backend.dtek_parser import dtek_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ініціалізація бази даних
    init_db()
    print("[Server] База даних ініціалізована успішно.")

    # Запуск фонового колектора
    collector_task = asyncio.create_task(collector.start_background_loop())
    yield
    # Зупинка
    collector.running = False
    collector_task.cancel()
    print("[Server] Сервер зупинено.")


app = FastAPI(
    title="Deye Home Energy System API",
    version="3.0 PRO",
    lifespan=lifespan
)


# Модель для запиту керування навантаженням
class LoadControlRequest(BaseModel):
    device: str  # "fridge", "kettle", "reset"
    action: bool


# --- API Ендпоінти ---

@app.get("/api/status")
async def api_get_status():
    """Повертає поточний стан інвертора, мережі, батареї та ДТЕК"""
    try:
        metrics = collector.get_current_metrics()
        schedule_data = await dtek_manager.fetch_or_get_schedule()
        dtek_status = dtek_manager.get_current_status(schedule_data)

        return {
            **metrics,
            "dtek": dtek_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history")
async def api_get_history(days: int = 30):
    """Повертає історію знеструмлень за останні N днів"""
    try:
        history = get_blackout_history(days=days)
        return {
            "count": len(history),
            "days": days,
            "events": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/toggle-grid")
async def api_toggle_grid():
    """Симуляція / ручне перемикання стану мережі"""
    try:
        new_state = await collector.manual_toggle_grid()
        return {
            "success": True,
            "grid_online": new_state,
            "message": "Мережа в нормі" if new_state else "Мережа відключена (автономний режим)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/control-load")
async def api_control_load(req: LoadControlRequest):
    """Керування тестовими електроприладами"""
    if req.device == "fridge":
        if req.action:
            collector.extra_load += 150
        else:
            collector.extra_load = max(0.0, collector.extra_load - 150)
    elif req.device == "kettle":
        if req.action:
            collector.extra_load += 1800
        else:
            collector.extra_load = max(0.0, collector.extra_load - 1800)
    elif req.device == "reset":
        collector.extra_load = 0.0

    return {
        "success": True,
        "extra_load": collector.extra_load,
        "current_load": int(collector.base_load + collector.extra_load)
    }


# --- Роздача статичних файлів фронтенду ---

@app.get("/")
async def serve_index():
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/styles.css")
async def serve_css():
    return FileResponse(config.STATIC_DIR / "styles.css")


@app.get("/app.js")
async def serve_js():
    return FileResponse(config.STATIC_DIR / "app.js")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)
