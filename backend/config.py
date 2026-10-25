"""
Конфігурація домашньої енергосистеми Deye
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Завантаження змінних середовища з .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # Загальні налаштування сервера
    HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # База даних
    DATABASE_PATH: Path = BASE_DIR / "energy_system.db"
    DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_NOTIFICATIONS_ENABLED: bool = os.getenv("TELEGRAM_NOTIFICATIONS_ENABLED", "True").lower() in ("true", "1", "t")

    # ДТЕК налаштування
    DTEK_REGION: str = os.getenv("DTEK_REGION", "kiev") # kiev, kiev_region, dnipro, odesa
    DTEK_GROUP: str = os.getenv("DTEK_GROUP", "3")      # Черга/Група 1..6

    # Параметри акумулятора (LiFePO4)
    BATTERY_CAPACITY_WH: float = float(os.getenv("BATTERY_CAPACITY_WH", "5120"))  # 5.12 kWh
    BATTERY_MIN_SOC: float = float(os.getenv("BATTERY_MIN_SOC", "15"))            # Буфер розряду %
    LOW_BATTERY_ALERT_SOC: float = float(os.getenv("LOW_BATTERY_ALERT_SOC", "20")) # Сповіщення %

    # Режим симуляції (Demo Mode) за відсутності фізичного заліза
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "True").lower() in ("true", "1", "t")

    # Modbus налаштування (Інвертор Deye)
    MODBUS_ENABLED: bool = os.getenv("MODBUS_ENABLED", "False").lower() in ("true", "1", "t")
    MODBUS_TYPE: str = os.getenv("MODBUS_TYPE", "rtu").lower() # rtu або tcp
    MODBUS_PORT: str = os.getenv("MODBUS_PORT", "COM3")        # Для RTU (наприклад /dev/ttyUSB0 або COM3)
    MODBUS_BAUDRATE: int = int(os.getenv("MODBUS_BAUDRATE", "9600"))
    MODBUS_HOST: str = os.getenv("MODBUS_HOST", "192.168.1.100") # Для TCP
    MODBUS_TCP_PORT: int = int(os.getenv("MODBUS_TCP_PORT", "502"))
    MODBUS_SLAVE_ID: int = int(os.getenv("MODBUS_SLAVE_ID", "1"))

    # Опитування
    POLL_INTERVAL: float = float(os.getenv("POLL_INTERVAL", "2.0"))
    GRID_VOLTAGE_THRESHOLD: float = float(os.getenv("GRID_VOLTAGE_THRESHOLD", "150.0"))

    # Статичні файли фронтенду
    STATIC_DIR: Path = BASE_DIR


config = Config()
