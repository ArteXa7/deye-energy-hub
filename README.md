# ⚡ Deye Inverter & DTEK Power Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Open%20Source-orange?style=for-the-badge)

A production-grade real-time web monitoring and automation system for **Deye Hybrid Inverters** (SUN-5K-SG03LP1-EU and compatible) combined with **DTEK Power Outage Schedules** (Ukraine) and automated **Telegram alerts**.

[Features](#-key-features) • [Architecture](#-system-architecture) • [Quick Start](#-quick-start) • [Docker Deployment](#-docker-deployment) • [Demo Mode](#-demo-mode) • [Configuration](#-configuration)

</div>

---

## 🌟 Key Features

- **Hybrid Inverter Telemetry (Deye Sun series):** Real-time monitoring of grid voltage (230V phase), grid frequency, battery SoC (State of Charge), voltage, temperature, current, and household power consumption.
- **Modbus RTU / TCP & Smart Simulation Mode:** Connects directly to physical Deye inverters via RS485/USB or Modbus TCP. Includes an intelligent **Demo Mode (`DEMO_MODE=True`)** that generates realistic telemetry and allows full UI testing without hardware.
- **DTEK Power Outage Schedules:** Integrates regional blackout schedules (Kyiv, Kyiv Region, Dnipro, Odesa) with hourly status breakdown (Power ON / Planned Outage / Gray Zone).
- **Automated Telegram Bot Alerts:** Instant Ukrainian-language notifications when mains power fails, when power is restored, and when battery SoC drops below critical thresholds (`<20%`).
- **Interactive Energy Dashboard:** Premium glassmorphism UI with live power-flow animation, battery runtime calculator, historical blackout logs, and load test controls (fridge, electric kettle).
- **Persistent SQLite Storage:** Automatically logs blackout durations, energy usage, and cached DTEK schedules.

---

## 🏗️ System Architecture

```
┌─────────────────────────┐         ┌──────────────────────────┐
│  Deye Inverter Hardware │         │ DTEK Outage Schedule API │
│  (Modbus RTU / TCP)     │         │ (Regional Schedules)     │
└────────────┬────────────┘         └─────────────┬────────────┘
             │ (RS485 / TCP)                      │ (HTTP GET)
             ▼                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Python 3.11)               │
│  ┌───────────────────────┐          ┌─────────────────────┐  │
│  │ DeyeCollector         │          │ DtekScheduleManager │  │
│  │ (Hardware / Simulator)│          │ (Schedule Parser)   │  │
│  └───────────┬───────────┘          └──────────┬──────────┘  │
│              └─────────────────┬───────────────┘             │
│                                ▼                             │
│                     SQLite Database (Local)                  │
└────────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼ (WebSockets / REST API)
┌──────────────────────────────────────────────────────────────┐
│                 Frontend Dashboard (HTML/CSS/JS)             │
│   • Live Power Flow Animation • Battery SOC Gauge • DTEK Grid│
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, PyModbus, PySerial, HTTPX.
- **Frontend:** HTML5, Vanilla CSS (with modern CSS variables, glassmorphism, responsive grid), Modern JavaScript (ES6+).
- **Database:** SQLite (lightweight, zero-config file database).
- **Containerization:** Docker & Docker Compose.

---

## 🚀 Quick Start

### Local Startup on Windows (PowerShell)
Use the provided `run.ps1` script for automated virtual environment setup, dependency installation, and server startup:

```powershell
.\run.ps1
```

### Manual Local Startup (Linux / macOS / Windows)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/invertorweb.git
   cd invertorweb
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and adjust settings:
   ```bash
   cp .env.example .env
   ```

5. **Run the server:**
   ```bash
   python -m backend.main
   ```

6. **Open in browser:**
   👉 `http://localhost:8000`

---

## 🐳 Docker Deployment

Deploy the entire application with a single command using Docker Compose:

```bash
docker compose up -d --build
```

To view logs:
```bash
docker compose logs -f
```

To stop:
```bash
docker compose down
```

---

## 🎮 Demo Mode

If you don't have a physical Deye inverter connected, the application runs out-of-the-box in **Demo Mode**:
- Set `DEMO_MODE=True` in `.env`.
- The background collector automatically simulates realistic fluctuations (household load 350–680W, battery charging/discharging, grid voltage 226–231V).
- You can manually click the **"⚡ Мережа"** toggle button in the header to simulate power outages and observe real-time UI transitions, alert sounds, and database logging!

---

## ⚙️ Configuration (`.env`)

All parameters are fully configurable via environment variables in `.env`:

```env
# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# Demo / Simulation Mode (True = test without physical inverter)
DEMO_MODE=True

# Telegram Bot Notifications (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_NOTIFICATIONS_ENABLED=True

# DTEK Power Outage Schedule Settings
DTEK_REGION=kyiv          # Options: kyiv, kyiv_region, dnipro, odesa
DTEK_GROUP=3              # Queue group: 1 to 6

# Battery Parameters (LiFePO4)
BATTERY_CAPACITY_WH=5120
BATTERY_MIN_SOC=15
LOW_BATTERY_ALERT_SOC=20

# Modbus Hardware Integration (Deye Inverter via RS485/USB or TCP)
MODBUS_ENABLED=False
MODBUS_TYPE=rtu
MODBUS_PORT=COM3
MODBUS_BAUDRATE=9600
MODBUS_HOST=192.168.1.100
MODBUS_TCP_PORT=502
MODBUS_SLAVE_ID=1
```

---

## 🛡️ Security Audit

- No hardcoded API keys, Telegram tokens, passwords, or IP addresses exist in the source code.
- All secrets are loaded strictly from environment variables via `python-dotenv`.
- `.env` is ignored in `.gitignore` to prevent accidental credential leakage.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
