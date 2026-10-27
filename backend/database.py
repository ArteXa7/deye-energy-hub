"""
Модуль бази даних SQLite (SQLAlchemy)
Збереження історії відключень та розкладів ДТЕК
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Text, desc
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backend.config import config

Base = declarative_base()


class SystemSetting(Base):
    __tablename__ = "settings"

    key = Column(String(50), primary_key=True, index=True)
    value = Column(Text, nullable=True)


class BlackoutEvent(Base):
    __tablename__ = "blackout_events"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    battery_start_soc = Column(Float, nullable=False, default=100.0)
    battery_end_soc = Column(Float, nullable=True)
    battery_used_kwh = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True, index=True)
    notes = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        duration_str = format_duration(self.duration_seconds)
        date_str = format_date_ua(self.started_at)
        time_down = self.started_at.strftime("%H:%M")
        time_up = self.ended_at.strftime("%H:%M") if self.ended_at else "Триває..."

        return {
            "id": self.id,
            "status": "active" if self.is_active else "restored",
            "date": date_str,
            "time_down": time_down,
            "time_up": time_up,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "duration": duration_str,
            "battery_start_soc": round(self.battery_start_soc, 1),
            "battery_end_soc": round(self.battery_end_soc, 1) if self.battery_end_soc is not None else None,
            "bat_used": f"{round(self.battery_used_kwh, 2)} кВт·ч" if self.battery_used_kwh else "—"
        }


class DtekSchedule(Base):
    __tablename__ = "dtek_schedule"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    group_name = Column(String(20), nullable=False, index=True) # "3"
    intervals_json = Column(Text, nullable=False) # JSON з інтервалами
    is_emergency = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.now)

    def get_intervals(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.intervals_json)
        except Exception:
            return []


# Налаштування engine та сесій
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Допоміжні функції форматування українською мовою ---
def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "0 хв"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours} год {minutes:02d} хв"
    elif minutes > 0:
        return f"{minutes} хв {secs:02d} с"
    else:
        return f"{secs} с"


def format_date_ua(dt: datetime) -> str:
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    event_date = dt.date()

    if event_date == today:
        return "Сьогодні"
    elif event_date == yesterday:
        return "Вчора"

    months_ua = [
        "", "січ", "лют", "бер", "квіт", "трав", "черв",
        "лип", "серп", "вер", "жовт", "лист", "груд"
    ]
    return f"{dt.day} {months_ua[dt.month]}"


# --- Керування подіями відключень ---
def start_blackout(start_soc: float) -> BlackoutEvent:
    """Фіксує аварійне знеструмлення мережі"""
    with SessionLocal() as db:
        # Перевірка чи вже є активне
        active = db.query(BlackoutEvent).filter(BlackoutEvent.is_active == True).first()
        if active:
            return active

        new_event = BlackoutEvent(
            started_at=datetime.now(),
            battery_start_soc=start_soc,
            is_active=True
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event


def end_blackout(end_soc: float, avg_load_w: float = 500) -> Optional[BlackoutEvent]:
    """Фіксує відновлення живлення мережі 230V"""
    with SessionLocal() as db:
        active = db.query(BlackoutEvent).filter(BlackoutEvent.is_active == True).first()
        if not active:
            return None

        now = datetime.now()
        active.ended_at = now
        active.is_active = False
        active.battery_end_soc = end_soc

        duration_sec = int((now - active.started_at).total_seconds())
        active.duration_seconds = max(1, duration_sec)

        # Розрахунок використаної енергії АКБ:
        # delta_soc * capacity або інтеграл навантаження
        delta_soc = max(0.0, active.battery_start_soc - end_soc)
        kwh_from_soc = (delta_soc / 100.0) * (config.BATTERY_CAPACITY_WH / 1000.0)
        kwh_from_load = (avg_load_w * (duration_sec / 3600.0)) / 1000.0
        active.battery_used_kwh = max(kwh_from_soc, kwh_from_load, 0.05)

        db.commit()
        db.refresh(active)
        return active


def get_active_blackout() -> Optional[Dict[str, Any]]:
    """Повертає поточне активне відключення"""
    with SessionLocal() as db:
        active = db.query(BlackoutEvent).filter(BlackoutEvent.is_active == True).first()
        if not active:
            return None

        # Оновлюємо тривалість на льоту
        elapsed = int((datetime.now() - active.started_at).total_seconds())
        active.duration_seconds = elapsed
        return active.to_dict()


def get_blackout_history(days: int = 30) -> List[Dict[str, Any]]:
    """Повертає історію знеструмлень за останні N днів"""
    with SessionLocal() as db:
        cutoff = datetime.now() - timedelta(days=days)
        events = db.query(BlackoutEvent)\
                   .filter(BlackoutEvent.started_at >= cutoff)\
                   .order_by(desc(BlackoutEvent.started_at))\
                   .all()

        return [e.to_dict() for e in events]


# --- Кешування розкладу ДТЕК ---
def save_dtek_cache(date_str: str, group_name: str, intervals: list, is_emergency: bool = False):
    with SessionLocal() as db:
        existing = db.query(DtekSchedule)\
                     .filter(DtekSchedule.date == date_str, DtekSchedule.group_name == group_name)\
                     .first()
        if existing:
            existing.intervals_json = json.dumps(intervals, ensure_ascii=False)
            existing.is_emergency = is_emergency
            existing.updated_at = datetime.now()
        else:
            sched = DtekSchedule(
                date=date_str,
                group_name=group_name,
                intervals_json=json.dumps(intervals, ensure_ascii=False),
                is_emergency=is_emergency,
                updated_at=datetime.now()
            )
            db.add(sched)
        db.commit()


def get_dtek_cache(date_str: str, group_name: str) -> Optional[Dict[str, Any]]:
    with SessionLocal() as db:
        entry = db.query(DtekSchedule)\
                  .filter(DtekSchedule.date == date_str, DtekSchedule.group_name == group_name)\
                  .first()
        if not entry:
            return None
        return {
            "date": entry.date,
            "group_name": entry.group_name,
            "intervals": entry.get_intervals(),
            "is_emergency": entry.is_emergency,
            "updated_at": entry.updated_at.isoformat()
        }


# --- Керування налаштуваннями системи ---
def get_setting(key: str, default: str = "") -> str:
    with SessionLocal() as db:
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        return setting.value if setting and setting.value is not None else default


def set_setting(key: str, value: Any):
    with SessionLocal() as db:
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = SystemSetting(key=key, value=str(value))
            db.add(setting)
        db.commit()


def get_all_settings() -> Dict[str, str]:
    with SessionLocal() as db:
        settings = db.query(SystemSetting).all()
        return {s.key: s.value for s in settings}


def init_default_settings():
    defaults = {
        "modbus_enabled": str(config.MODBUS_ENABLED),
        "modbus_type": config.MODBUS_TYPE,
        "modbus_host": config.MODBUS_HOST,
        "modbus_port": str(config.MODBUS_PORT),
        "modbus_tcp_port": str(config.MODBUS_TCP_PORT),
        "modbus_slave_id": str(config.MODBUS_SLAVE_ID),
        "dtek_region": config.DTEK_REGION,
        "dtek_group": config.DTEK_GROUP,
        "custom_dtek_schedule": json.dumps({str(h): "yes" for h in range(24)}),
        "telegram_bot_token": config.TELEGRAM_BOT_TOKEN,
        "telegram_chat_id": config.TELEGRAM_CHAT_ID,
        "telegram_notifications_enabled": str(config.TELEGRAM_NOTIFICATIONS_ENABLED),
        "demo_mode": str(config.DEMO_MODE),
        "admin_password": os.getenv("ADMIN_PASSWORD", "admin")
    }
    with SessionLocal() as db:
        for k, v in defaults.items():
            existing = db.query(SystemSetting).filter(SystemSetting.key == k).first()
            if not existing:
                db.add(SystemSetting(key=k, value=str(v)))
        db.commit()


def load_config_from_db():
    try:
        all_s = get_all_settings()
        if not all_s:
            return
        if "modbus_enabled" in all_s:
            config.MODBUS_ENABLED = all_s["modbus_enabled"].lower() in ("true", "1", "t")
        if "modbus_type" in all_s:
            config.MODBUS_TYPE = all_s["modbus_type"]
        if "modbus_host" in all_s:
            config.MODBUS_HOST = all_s["modbus_host"]
        if "modbus_port" in all_s:
            config.MODBUS_PORT = all_s["modbus_port"]
        if "modbus_tcp_port" in all_s:
            config.MODBUS_TCP_PORT = int(all_s["modbus_tcp_port"])
        if "modbus_slave_id" in all_s:
            config.MODBUS_SLAVE_ID = int(all_s["modbus_slave_id"])
        if "dtek_region" in all_s:
            config.DTEK_REGION = all_s["dtek_region"]
        if "dtek_group" in all_s:
            config.DTEK_GROUP = all_s["dtek_group"]
        if "telegram_bot_token" in all_s:
            config.TELEGRAM_BOT_TOKEN = all_s["telegram_bot_token"]
        if "telegram_chat_id" in all_s:
            config.TELEGRAM_CHAT_ID = all_s["telegram_chat_id"]
        if "telegram_notifications_enabled" in all_s:
            config.TELEGRAM_NOTIFICATIONS_ENABLED = all_s["telegram_notifications_enabled"].lower() in ("true", "1", "t")
        if "demo_mode" in all_s:
            config.DEMO_MODE = all_s["demo_mode"].lower() in ("true", "1", "t")
    except Exception:
        pass


# --- Початкова ініціалізація та демо-дані ---
def init_db():
    Base.metadata.create_all(bind=engine)
    init_default_settings()
    load_config_from_db()

    with SessionLocal() as db:
        count = db.query(BlackoutEvent).count()
        if count == 0:
            now = datetime.now()
            # Додаємо кілька реалістичних подій за останні дні
            demo_events = [
                BlackoutEvent(
                    started_at=now - timedelta(days=1, hours=8, minutes=10),
                    ended_at=now - timedelta(days=1, hours=4, minutes=20),
                    duration_seconds=3 * 3600 + 50 * 60,
                    battery_start_soc=96.0,
                    battery_end_soc=62.0,
                    battery_used_kwh=1.92,
                    is_active=False
                ),
                BlackoutEvent(
                    started_at=now - timedelta(days=2, hours=15, minutes=0),
                    ended_at=now - timedelta(days=2, hours=12, minutes=40),
                    duration_seconds=2 * 3600 + 20 * 60,
                    battery_start_soc=92.0,
                    battery_end_soc=71.0,
                    battery_used_kwh=1.18,
                    is_active=False
                ),
                BlackoutEvent(
                    started_at=now - timedelta(days=4, hours=22, minutes=10),
                    ended_at=now - timedelta(days=4, hours=17, minutes=40),
                    duration_seconds=4 * 3600 + 30 * 60,
                    battery_start_soc=98.0,
                    battery_end_soc=56.0,
                    battery_used_kwh=2.34,
                    is_active=False
                ),
                BlackoutEvent(
                    started_at=now - timedelta(days=7, hours=6, minutes=30),
                    ended_at=now - timedelta(days=7, hours=5, minutes=15),
                    duration_seconds=1 * 3600 + 15 * 60,
                    battery_start_soc=88.0,
                    battery_end_soc=76.0,
                    battery_used_kwh=0.65,
                    is_active=False
                ),
            ]
            db.add_all(demo_events)
            db.commit()
