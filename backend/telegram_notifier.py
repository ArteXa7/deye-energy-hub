"""
Модуль сповіщень Telegram українською мовою
Повідомлення про зникнення світла, відновлення та низький заряд АКБ
"""

import httpx
from backend.config import config


class TelegramNotifier:
    """Керування надсиланням сповіщень у Telegram"""

    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.enabled = config.TELEGRAM_NOTIFICATIONS_ENABLED and bool(self.token) and bool(self.chat_id)

    async def send_message(self, text: str) -> bool:
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                return response.status_code == 200
        except Exception as e:
            print(f"[Telegram Error] Помилка надсилання сповіщення: {e}")
            return False

    async def notify_blackout_started(self, soc: float, volts: float, load: float, runtime: str):
        text = (
            f"🔴 <b>СВІТЛО ЗНИКЛО!</b>\n\n"
            f"🔋 Батарея: <b>{soc:.1f}%</b> ({volts:.1f}V)\n"
            f"🏠 Навантаження: <b>{load} W</b>\n"
            f"⏳ Орієнтовно вистачить на: ~{runtime}\n\n"
            f"<i>Інвертор перейшов на автономний режим (UPS).</i>"
        )
        await self.send_message(text)

    async def notify_blackout_ended(self, duration: str, end_soc: float, bat_used: str):
        text = (
            f"🟢 <b>СВІТЛО З'ЯВИЛОСЯ!</b>\n\n"
            f"⏱ Відключення тривало: <b>{duration}</b>\n"
            f"🔋 Залишок батареї: <b>{end_soc:.1f}%</b>\n"
            f"⚡ Використано з АКБ: {bat_used}\n\n"
            f"<i>Інвертор синхронізовано з мережею (Bypass).</i>"
        )
        await self.send_message(text)

    async def notify_low_battery(self, soc: float, volts: float):
        text = (
            f"⚠️ <b>УВАГА: НИЗЬКИЙ ЗАЯД АКБ!</b>\n\n"
            f"🔋 Рівень заряду впав до: <b>{soc:.1f}%</b> ({volts:.1f}V)\n"
            f"<i>Рекомендується вимкнути потужні електроприлади!</i>"
        )
        await self.send_message(text)


telegram_notifier = TelegramNotifier()
