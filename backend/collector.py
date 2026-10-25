"""
Фоновий колектор даних інвертора Deye (Modbus RTU / TCP / симуляція)
Моніторинг напруги мережі 230V, визначення блэкаутів та запуск сповіщень
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, Any

from backend.config import config
from backend.database import start_blackout, end_blackout, get_active_blackout
from backend.telegram_notifier import telegram_notifier


class DeyeCollector:
    """Збирач даних інвертора з підтримкою реального Modbus або розумної симуляції"""

    def __init__(self):
        self.grid_online = True
        self.battery_soc = 87.0
        self.battery_volts = 51.8
        self.battery_temp = 24.2
        self.base_load = 520.0
        self.extra_load = 0.0
        self.grid_volts = 228.4
        self.grid_freq = 50.0
        self.energy_grid_today = 4.82
        self.energy_bat_today = 1.45
        self.peak_load = 2840.0
        self.low_battery_notified = False
        self.running = False

        # Спроба підключення бібліотеки pymodbus якщо увімкнено
        self.modbus_client = None
        if config.MODBUS_ENABLED:
            try:
                if config.MODBUS_TYPE == "tcp":
                    from pymodbus.client import ModbusTcpClient
                    self.modbus_client = ModbusTcpClient(config.MODBUS_HOST, port=config.MODBUS_TCP_PORT)
                else:
                    from pymodbus.client import ModbusSerialClient
                    self.modbus_client = ModbusSerialClient(
                        port=config.MODBUS_PORT,
                        baudrate=config.MODBUS_BAUDRATE,
                        stopbits=1,
                        bytesize=8,
                        parity='N'
                    )
                self.modbus_client.connect()
                print(f"[Modbus] Успішно підключено до інвертора Deye ({config.MODBUS_TYPE})")
            except Exception as e:
                print(f"[Modbus Warning] Не вдалося ініціалізувати Modbus клієнт: {e}. Переходимо на симуляцію.")
                self.modbus_client = None

    def calculate_runtime(self, soc: float, load_w: float) -> str:
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
        """Читання регістрів через Modbus (якщо налаштовано та не активовано DEMO_MODE)"""
        if config.DEMO_MODE:
            return False
        if not self.modbus_client or not self.modbus_client.is_socket_open():
            return False
        try:
            # Читання базових регістрів Deye (наприклад Holding Registers 600+)
            result = self.modbus_client.read_holding_registers(address=630, count=10, slave=config.MODBUS_SLAVE_ID)
            if not result.isError():
                regs = result.registers
                self.grid_volts = regs[0] / 10.0
                self.battery_soc = regs[3] / 10.0
                self.battery_volts = regs[4] / 10.0
                self.grid_online = self.grid_volts > config.GRID_VOLTAGE_THRESHOLD
                return True
        except Exception:
            pass
        return False

    def simulate_step(self):
        """Реалістичний крок симуляції параметрів"""
        # Коливання навантаження
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
            # Розряд АКБ
            drain = (current_load * (config.POLL_INTERVAL / 3600.0)) / config.BATTERY_CAPACITY_WH * 100.0
            self.battery_soc = max(10.0, self.battery_soc - drain)
            self.battery_volts = 49.2 + (self.battery_soc / 100.0) * 4.4
            self.battery_temp = min(34.0, self.battery_temp + 0.01)

            # Перевірка низького заряду
            if self.battery_soc <= config.LOW_BATTERY_ALERT_SOC and not self.low_battery_notified:
                self.low_battery_notified = True
                asyncio.create_task(telegram_notifier.notify_low_battery(self.battery_soc, self.battery_volts))

    async def check_grid_state_change(self, new_online_state: bool):
        """Детектор зникнення або появи мережі з фіксацією в БД та Telegram"""
        if self.grid_online == new_online_state:
            return

        current_load = int(self.base_load + self.extra_load)

        if self.grid_online and not new_online_state:
            # Світло зникло
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
            # Світло з'явилося
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
        """Ручне перемикання мережі через UI (для демонстрації/симуляції)"""
        target = not self.grid_online
        await self.check_grid_state_change(target)
        return self.grid_online

    def get_current_metrics(self) -> Dict[str, Any]:
        """Формує повний словник поточних метрик для фронтенду"""
        current_load = int(self.base_load + self.extra_load)
        runtime_str = self.calculate_runtime(self.battery_soc, current_load)
        active_blackout = get_active_blackout()

        battery_power = current_load if not self.grid_online else -35.0
        battery_current = round(battery_power / self.battery_volts, 1)

        return {
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
        """Основний фоновий цикл опитування"""
        self.running = True
        print("[Collector] Фоновий збирач даних запущено.")
        while self.running:
            try:
                success = await self.read_hardware_registers()
                if not success:
                    self.simulate_step()
            except Exception as e:
                print(f"[Collector Error] Помилка в циклі: {e}")

            await asyncio.sleep(config.POLL_INTERVAL)


collector = DeyeCollector()
