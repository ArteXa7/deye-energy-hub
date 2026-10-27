"""
Фоновий колектор даних інвертора Deye (Modbus RTU / TCP / симуляція)
Моніторинг напруги мережі 230V, визначення блэкаутів та безпечний режим
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any

from backend.config import config
from backend.database import start_blackout, end_blackout, get_active_blackout, load_config_from_db
from backend.telegram_notifier import telegram_notifier


class DeyeCollector:
    """Збирач даних інвертора з підтримкою реального Modbus або безпечного відключення"""

    def __init__(self):
        load_config_from_db()
        self.grid_online = False
        self.hardware_connected = False
        self.battery_soc = 0.0
        self.battery_volts = 0.0
        self.battery_temp = 0.0
        self.base_load = 0.0
        self.extra_load = 0.0
        self.grid_volts = 0.0
        self.grid_freq = 0.0
        self.energy_grid_today = 0.0
        self.energy_bat_today = 0.0
        self.peak_load = 0.0
        self.low_battery_notified = False
        self.running = False
        self.modbus_client = None

        if config.DEMO_MODE:
            self._init_demo_defaults()
        elif config.MODBUS_ENABLED:
            self._init_modbus_client()

    def _init_demo_defaults(self):
        """Початкові значення для режиму демонстрації"""
        self.grid_online = True
        self.hardware_connected = True
        self.battery_soc = 87.0
        self.battery_volts = 51.8
        self.battery_temp = 24.2
        self.base_load = 520.0
        self.grid_volts = 228.4
        self.grid_freq = 50.0
        self.energy_grid_today = 4.82
        self.energy_bat_today = 1.45
        self.peak_load = 2840.0

    def _init_modbus_client(self):
        """Ініціалізація клієнта Modbus без блокування потоку"""
        try:
            if config.MODBUS_TYPE == "tcp":
                from pymodbus.client import ModbusTcpClient
                self.modbus_client = ModbusTcpClient(config.MODBUS_HOST, port=config.MODBUS_TCP_PORT, timeout=3)
            else:
                from pymodbus.client import ModbusSerialClient
                self.modbus_client = ModbusSerialClient(
                    port=config.MODBUS_PORT,
                    baudrate=config.MODBUS_BAUDRATE,
                    stopbits=1,
                    bytesize=8,
                    parity='N',
                    timeout=3
                )
            connected = self.modbus_client.connect()
            self.hardware_connected = bool(connected)
            if connected:
                print(f"[Modbus] Успішно підключено до інвертора ({config.MODBUS_TYPE})")
            else:
                print(f"[Modbus] Не вдалося з'єднатися з інвертором ({config.MODBUS_TYPE})")
        except Exception as e:
            print(f"[Modbus Error] Помилка ініціалізації: {e}")
            self.modbus_client = None
            self.hardware_connected = False

    def apply_new_settings(self):
        """Оновлює конфігурацію та перепідключає Modbus клієнт без перезапуску"""
        load_config_from_db()

        if self.modbus_client:
            try:
                self.modbus_client.close()
            except Exception:
                pass
            self.modbus_client = None

        if config.DEMO_MODE:
            self._init_demo_defaults()
            print("[Collector] Увімкнено DEMO_MODE: активовано симуляцію.")
        else:
            self.hardware_connected = False
            self.grid_volts = 0.0
            self.grid_online = False
            self.base_load = 0.0
            self.extra_load = 0.0
            if config.MODBUS_ENABLED:
                self._init_modbus_client()
            else:
                print("[Collector] Modbus та симуляція вимкнені: статус ОФЛАЙН.")

    def calculate_runtime(self, soc: float, load_w: float) -> str:
        if not self.hardware_connected and not config.DEMO_MODE:
            return "Немає зв'язку"
        if load_w <= 10:
            return "> 24 год"
        usable_soc = max(0.0, soc - config.BATTERY_MIN_SOC)
        usable_wh = (usable_soc / 100.0) * config.BATTERY_CAPACITY_WH
        effective_hours = (usable_wh * 0.96) / load_w

        if effective_hours <= 0:
            return "АКБ розряджено"
        hours = int(effective_hours)
        minutes = int((effective_hours - hours) * 60)
        if hours > 24:
            return "> 24 год"
        if hours == 0:
            return f"~{minutes} хв"
        return f"~{hours} год {minutes:02d} хв"

    async def read_hardware_registers(self) -> bool:
        """Безпечне читання регістрів (read-only)"""
        if config.DEMO_MODE or not config.MODBUS_ENABLED or not self.modbus_client:
            self.hardware_connected = False
            return False

        try:
            # Читання регістрів у окремому потоці, щоб не блокувати async event loop
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.modbus_client.read_holding_registers(
                    address=630,
                    count=10,
                    slave=config.MODBUS_SLAVE_ID
                )
            )

            if result and not result.isError():
                regs = result.registers
                self.grid_volts = regs[0] / 10.0
                self.battery_soc = regs[3] / 10.0
                self.battery_volts = regs[4] / 10.0
                new_online = self.grid_volts > config.GRID_VOLTAGE_THRESHOLD
                await self.check_grid_state_change(new_online)
                self.hardware_connected = True
                return True
            else:
                self.hardware_connected = False
                return False
        except Exception:
            self.hardware_connected = False
            return False

    def simulate_step(self):
        """Крок симуляції (працює ТІЛЬКИ коли увімкнено DEMO_MODE)"""
        if not config.DEMO_MODE:
            return

        self.hardware_connected = True
        delta = (random.random() - 0.48) * 30
        self.base_load = max(350, min(680, self.base_load + delta))
        current_load = round(self.base_load + self.extra_load)

        if current_load > self.peak_load:
            self.peak_load = current_load

        if self.grid_online:
            self.grid_volts = 226 + (random.random() * 5.0)
            self.grid_freq = 49.96 + (random.random() * 0.08)
            self.energy_grid_today += (current_load * (config.POLL_INTERVAL / 3600.0)) / 1000.0
            if self.battery_soc < 92.0:
                self.battery_soc = min(100.0, self.battery_soc + 0.02)
                self.low_battery_notified = False
        else:
            drain = (current_load * (config.POLL_INTERVAL / 3600.0)) / config.BATTERY_CAPACITY_WH * 100.0
            self.battery_soc = max(10.0, self.battery_soc - drain)
            self.battery_volts = 49.2 + (self.battery_soc / 100.0) * 4.4
            self.battery_temp = min(34.0, self.battery_temp + 0.01)

            if self.battery_soc <= config.LOW_BATTERY_ALERT_SOC and not self.low_battery_notified:
                self.low_battery_notified = True
                asyncio.create_task(telegram_notifier.notify_low_battery(self.battery_soc, self.battery_volts))

    async def check_grid_state_change(self, new_online_state: bool):
        if self.grid_online == new_online_state:
            return

        current_load = int(self.base_load + self.extra_load)

        if self.grid_online and not new_online_state:
            self.grid_online = False
            start_blackout(start_soc=self.battery_soc)
            runtime_str = self.calculate_runtime(self.battery_soc, current_load)
            print(f"[Blackout] Мережу знеструмлено! Перехід на АКБ. SoC: {self.battery_soc:.1f}%")
            await telegram_notifier.notify_blackout_started(
                soc=self.battery_soc,
                volts=self.battery_volts,
                load=current_load,
                runtime=runtime_str
            )
        elif not self.grid_online and new_online_state:
            self.grid_online = True
            ended_event = end_blackout(end_soc=self.battery_soc, avg_load_w=current_load)
            duration_str = ended_event.duration if ended_event else "—"
            bat_used = ended_event.bat_used if ended_event else "0.5 кВт·ч"

            print(f"[Blackout] Електропостачання відновлено! Тривалість: {duration_str}")
            await telegram_notifier.notify_blackout_ended(
                duration=duration_str,
                end_soc=self.battery_soc,
                bat_used=bat_used
            )
            self.low_battery_notified = False

    async def manual_toggle_grid(self) -> bool:
        target = not self.grid_online
        await self.check_grid_state_change(target)
        return self.grid_online

    def get_current_metrics(self) -> Dict[str, Any]:
        """Формує словник метрик з обов'язковим статусом зв'язку"""
        current_load = int(self.base_load + self.extra_load) if (self.hardware_connected or config.DEMO_MODE) else 0
        runtime_str = self.calculate_runtime(self.battery_soc, current_load)
        active_blackout = get_active_blackout()

        if self.hardware_connected or config.DEMO_MODE:
            battery_power = current_load if not self.grid_online else -35.0
            battery_current = round(battery_power / max(1.0, self.battery_volts), 1)
        else:
            battery_power = 0
            battery_current = 0.0

        return {
            "demo_mode": config.DEMO_MODE,
            "connected": self.hardware_connected,
            "grid_online": self.grid_online,
            "grid_volts": round(self.grid_volts, 1),
            "grid_freq": round(self.grid_freq, 2),
            "battery_soc": round(self.battery_soc, 1),
            "battery_volts": round(self.battery_volts, 2),
            "battery_temp": round(self.battery_temp, 1),
            "battery_power": int(battery_power),
            "battery_current": battery_current,
            "current_load": current_load,
            "peak_load": int(self.peak_load),
            "runtime": runtime_str,
            "energy_grid_today": round(self.energy_grid_today, 2),
            "energy_bat_today": round(self.energy_bat_today, 2),
            "energy_total_today": round(self.energy_grid_today + self.energy_bat_today, 2),
            "active_outage": active_blackout,
            "timestamp": datetime.now().isoformat()
        }

    async def start_background_loop(self):
        self.running = True
        print("[Collector] Фоновий збирач даних запущено.")
        while self.running:
            try:
                if config.DEMO_MODE:
                    self.simulate_step()
                else:
                    success = await self.read_hardware_registers()
                    if not success:
                        self.hardware_connected = False
                        self.grid_volts = 0.0
                        self.grid_freq = 0.0
            except Exception as e:
                print(f"[Collector Error] Помилка в циклі: {e}")

            await asyncio.sleep(config.POLL_INTERVAL)


collector = DeyeCollector()