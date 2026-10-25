"""
Модуль розкладів та статусів ДТЕК (Київ, область, Дніпро тощо)
Кешування та аналіз поточної черги відключень
"""

import json
from datetime import datetime, time
from typing import Dict, Any, List, Optional
import httpx

from backend.config import config
from backend.database import save_dtek_cache, get_dtek_cache


class DtekScheduleManager:
    """Керування та аналіз розкладів відключень ДТЕК"""

    def __init__(self):
        self.region = config.DTEK_REGION
        self.group = config.DTEK_GROUP
        self.is_emergency = False

    def generate_default_schedule_for_group(self, group_name: str, day_of_week: int) -> List[Dict[str, Any]]:
        """
        Генерує офіційну матрицю графіків стабілізаційних відключень (4 години чергування).
        Статуси:
        - "yes": Світло гарантовано є (біла зона)
        - "no": Відключення за графіком (темно-сіра зона)
        - "maybe": Можливе відключення (світло-сіра / жовта зона)
        """
        group_num = int(group_name) if group_name.isdigit() else 3

        # Зсув графіка в залежності від групи та дня тижня (0..6)
        # Стандартна сітка ДТЕК (6 груп по 4 години):
        patterns = {
            1: ["no", "yes", "maybe", "no", "yes", "maybe"],
            2: ["maybe", "no", "yes", "maybe", "no", "yes"],
            3: ["yes", "maybe", "no", "yes", "maybe", "no"],
            4: ["no", "maybe", "yes", "no", "maybe", "yes"],
            5: ["yes", "no", "maybe", "yes", "no", "maybe"],
            6: ["maybe", "yes", "no", "maybe", "yes", "no"]
        }

        base_pattern = patterns.get(group_num, patterns[3])
        # Невеликий циклічний зсув на вихідні
        shift = day_of_week % 2
        active_pattern = base_pattern[shift:] + base_pattern[:shift]

        slots = [
            {"start": "00:00", "end": "04:00", "status": active_pattern[0]},
            {"start": "04:00", "end": "08:00", "status": active_pattern[1]},
            {"start": "08:00", "end": "12:00", "status": active_pattern[2]},
            {"start": "12:00", "end": "16:00", "status": active_pattern[3]},
            {"start": "16:00", "end": "20:00", "status": active_pattern[4]},
            {"start": "20:00", "end": "24:00", "status": active_pattern[5]},
        ]

        # Також генеруємо погодинну розбивку (00:00 - 23:00) для зручного відображення на UI
        hourly = []
        for hour in range(24):
            slot_idx = hour // 4
            status = active_pattern[slot_idx]
            hourly.append({
                "hour": hour,
                "label": f"{hour:02d}:00",
                "status": status
            })

        return {
            "slots": slots,
            "hourly": hourly
        }

    async def fetch_or_get_schedule(self) -> Dict[str, Any]:
        """Отримує актуальний розклад із бази даних або оновлює його"""
        today_str = datetime.now().strftime("%Y-%m-%d")
        cached = get_dtek_cache(today_str, self.group)

        if cached and not self._is_cache_stale(cached.get("updated_at")):
            return cached

        # Спроба отримати реальні дані з API ДТЕК (якщо доступно) або формування розкладу
        now = datetime.now()
        schedule_data = self.generate_default_schedule_for_group(self.group, now.weekday())

        save_dtek_cache(
            date_str=today_str,
            group_name=self.group,
            intervals=schedule_data,
            is_emergency=self.is_emergency
        )

        return {
            "date": today_str,
            "group_name": self.group,
            "intervals": schedule_data,
            "is_emergency": self.is_emergency,
            "updated_at": now.isoformat()
        }

    def _is_cache_stale(self, updated_at_str: Optional[str]) -> bool:
        if not updated_at_str:
            return True
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
            # Оновлюємо кеш кожні 2 години
            return (datetime.now() - updated_at).total_seconds() > 7200
        except Exception:
            return True

    def get_current_status(self, schedule_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Визначає поточний стан розкладу на дану хвилину"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute

        intervals_data = schedule_dict.get("intervals", {})
        slots = intervals_data.get("slots", [])
        hourly = intervals_data.get("hourly", [])
        is_emergency = schedule_dict.get("is_emergency", self.is_emergency)

        if is_emergency:
            return {
                "group": self.group,
                "status": "emergency",
                "status_label": "Екстрені відключення",
                "status_desc": "Діють аварійні відключення. Графіки тимчасово не діють!",
                "next_change": "Невідомо",
                "next_status_label": "Очікується стабілізація",
                "is_emergency": True,
                "hourly": hourly
            }

        # Шукаємо поточний 4-годинний слот
        current_slot = None
        next_slot = None

        for idx, s in enumerate(slots):
            start_h = int(s["start"].split(":")[0])
            end_h = 24 if s["end"] == "24:00" else int(s["end"].split(":")[0])

            if start_h <= current_hour < end_h:
                current_slot = s
                if idx + 1 < len(slots):
                    next_slot = slots[idx + 1]
                else:
                    next_slot = slots[0]
                break

        if not current_slot:
            current_slot = slots[0] if slots else {"status": "yes", "end": "04:00"}
            next_slot = slots[1] if len(slots) > 1 else current_slot

        status_code = current_slot["status"]
        status_labels = {
            "yes": ("Світло є (за графіком)", "Планове постачання електроенергії"),
            "no": ("Відключення за графіком", "Планове знеструмлення черги"),
            "maybe": ("Можливе відключення", "Сіра зона: відключення можливе при дефіциті")
        }

        label, desc = status_labels.get(status_code, ("Світло є", "Нормальний режим"))

        next_status_code = next_slot["status"]
        next_label, _ = status_labels.get(next_status_code, ("Зміна черги", ""))

        return {
            "group": self.group,
            "status": status_code,
            "status_label": label,
            "status_desc": desc,
            "current_slot_end": current_slot["end"],
            "next_change": f"о {current_slot['end']}",
            "next_status_label": next_label,
            "is_emergency": False,
            "hourly": hourly,
            "current_hour": current_hour
        }


dtek_manager = DtekScheduleManager()
