"""
Модуль розкладів та статусів ДТЕК (Київ, область, Дніпро тощо)
Кешування та аналіз поточної черги відключень
"""

import json
from datetime import datetime, time
from typing import Dict, Any, List, Optional
import httpx

from backend.config import config
from backend.database import save_dtek_cache, get_dtek_cache, get_setting


class DtekScheduleManager:
    """Керування та аналіз розкладів відключень ДТЕК"""

    def __init__(self):
        self.region = config.DTEK_REGION
        self.group = config.DTEK_GROUP
        self.is_emergency = False

    def apply_new_settings(self):
        self.region = config.DTEK_REGION
        self.group = config.DTEK_GROUP

    def generate_default_schedule_for_group(self, group_name: str, day_of_week: int) -> Dict[str, Any]:
        """
        Генерує офіційну матрицю графіків стабілізаційних відключень (4 години чергування).
        Підтримує групи 1..6, підгрупи 1.1..6.2 для kyiv_region, та власний графік (custom).
        Статуси:
        - "yes": Світло гарантовано є (біла зона)
        - "no": Відключення за графіком (темно-сіра зона)
        - "maybe": Можливе відключення (світло-сіра / жовта зона)
        """
        if self.region == "custom":
            custom_json = get_setting("custom_dtek_schedule", "")
            hourly = []
            try:
                data_dict = json.loads(custom_json) if custom_json else {}
            except Exception:
                data_dict = {}

            for hour in range(24):
                status = data_dict.get(str(hour), "yes")
                hourly.append({
                    "hour": hour,
                    "label": f"{hour:02d}:00",
                    "status": status
                })

            slots = []
            for slot_idx in range(6):
                start_h = slot_idx * 4
                end_h = (slot_idx + 1) * 4
                slot_status = hourly[start_h]["status"] if start_h < len(hourly) else "yes"
                slots.append({
                    "start": f"{start_h:02d}:00",
                    "end": "24:00" if end_h == 24 else f"{end_h:02d}:00",
                    "status": slot_status
                })

            return {
                "slots": slots,
                "hourly": hourly
            }

        # Базова група та підтримка підгруп (наприклад 1.1, 1.2, 3.2 тощо)
        base_group_str = group_name.split(".")[0] if "." in group_name else group_name
        group_num = int(base_group_str) if base_group_str.isdigit() else 3

        sub_offset = 0
        if "." in group_name:
            sub_part = group_name.split(".")[1]
            if sub_part == "2":
                sub_offset = 2

        patterns = {
            1: ["no", "yes", "maybe", "no", "yes", "maybe"],
            2: ["maybe", "no", "yes", "maybe", "no", "yes"],
            3: ["yes", "maybe", "no", "yes", "maybe", "no"],
            4: ["no", "maybe", "yes", "no", "maybe", "yes"],
            5: ["yes", "no", "maybe", "yes", "no", "maybe"],
            6: ["maybe", "yes", "no", "maybe", "yes", "no"]
        }

        base_pattern = patterns.get(group_num, patterns[3])
        shift = (day_of_week + (1 if sub_offset > 0 else 0)) % 6
        active_pattern = base_pattern[shift:] + base_pattern[:shift]

        slots = [
            {"start": "00:00", "end": "04:00", "status": active_pattern[0]},
            {"start": "04:00", "end": "08:00", "status": active_pattern[1]},
            {"start": "08:00", "end": "12:00", "status": active_pattern[2]},
            {"start": "12:00", "end": "16:00", "status": active_pattern[3]},
            {"start": "16:00", "end": "20:00", "status": active_pattern[4]},
            {"start": "20:00", "end": "24:00", "status": active_pattern[5]},
        ]

        hourly = []
        for hour in range(24):
            adjusted_hour = (hour - sub_offset) % 24
            slot_idx = adjusted_hour // 4
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

        # Для кастомного розкладу або старого кешу перевіряємо актуальність
        if cached and not self._is_cache_stale(cached.get("updated_at")) and self.region != "custom":
            return cached

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
        if not updated_at_str or self.region == "custom":
            return True
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
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

        # Якщо регіон custom, беремо статус години напряму з hourly
        if self.region == "custom":
            current_h_item = next((h for h in hourly if h["hour"] == current_hour), {"status": "yes"})
            status_code = current_h_item["status"]
            next_hour = (current_hour + 1) % 24
            next_h_item = next((h for h in hourly if h["hour"] == next_hour), current_h_item)

            status_labels = {
                "yes": ("Світло є (власний графік)", "Планове постачання за власним розкладом"),
                "no": ("Відключення (власний графік)", "Планове знеструмлення за власним розкладом"),
                "maybe": ("Можливе відключення", "Можливе знеструмлення за власним розкладом")
            }

            label, desc = status_labels.get(status_code, ("Світло є", "Нормальний режим"))
            next_label, _ = status_labels.get(next_h_item["status"], ("Зміна статусу", ""))

            return {
                "group": "Власний",
                "status": status_code,
                "status_label": label,
                "status_desc": desc,
                "current_slot_end": f"{(current_hour + 1):02d}:00",
                "next_change": f"о {(current_hour + 1):02d}:00",
                "next_status_label": next_label,
                "is_emergency": False,
                "hourly": hourly,
                "current_hour": current_hour
            }

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
