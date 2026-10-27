# ⚡ Deye Inverter & DTEK Power Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Open%20Source-orange?style=for-the-badge)

A production-grade real-time web monitoring and automation system for **Deye Hybrid Inverters** (SUN-5K/6K-SG03LP1-EU and compatible) combined with **DTEK Power Outage Schedules** (Ukraine), dynamic BMS capacity detection, cookie-based session security, and automated **Telegram alerts**.

[Features](#-key-features) • [Architecture](#%EF%B8%8F-system-architecture) • [Security & Auth](#-security--authentication) • [Quick Start](#-quick-start) • [Docker Deployment](#-docker-deployment) • [Configuration](#%EF%B8%8F-configuration-env)

</div>

---

## 🌟 Key Features

- **Dynamic Inverter & Battery Telemetry:** Real-time extraction of inverter model name, serial identification, battery State of Health (SOH), and capacity (Ah / kWh) via Modbus/BMS with zero hardcoded placeholders.
- **Safe Read-Only Modbus Polling:** Interacts with physical Deye inverters safely over RS485/USB or Modbus TCP using strict read-only register requests (`read_holding_registers`). Transparent offline handling prevents silent fallback errors when hardware is disconnected.
- **DTEK Outage Schedules & Subgroups:** Supports official schedules for Kyiv, Kyiv Region (including detailed subgroups 1.1–6.2), Dnipro, Odesa, and a configurable **Custom Schedule** mode for non-standard regional timetables.
- **Smart Simulation Mode (`DEMO_MODE=True`):** Full-fledged software emulation of household load variations (350–680 W), battery discharge curves, and grid outages for UI/UX testing and development without physical hardware.
- **Automated Telegram Bot Alerts:** Push notifications in Ukrainian triggered instantly on mains disconnection, utility restoration, and critical low-battery thresholds (<20%).
- **Interactive Dashboard & Admin Panel:** Glassmorphism dark UI featuring live animated power flows, real-time battery runtime projections, 30-day blackout history logs, appliance load test controls, and an in-app system settings panel (`/settings`).
- **Persistent SQLite Storage:** Local, zero-maintenance database tracking historical outage records, user preferences, and cached outage schedules.

---

## 🏗️ System Architecture

```text
  ┌──────────────────────────────┐  ┌──────────────────────────────┐
  │    Deye Inverter Hardware    │  │   DTEK Outage Schedule API   │
  │      (Modbus RTU / TCP)      │  │     (Regional Schedules)     │
  └──────────────┬───────────────┘  └──────────────┬───────────────┘
                 │                                 │
                 │ (RS485 / TCP - Read-Only)       │ (HTTP GET)
                 ▼                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python 3.11)                    │
│                                                                    │
│   ┌──────────────────────────┐      ┌──────────────────────────┐   │
│   │      DeyeCollector       │      │   DtekScheduleManager    │   │
│   │  (Hardware / Simulator)  │      │    (Schedule Parser)     │   │
│   └────────────┬─────────────┘      └────────────┬─────────────┘   │
│                │                                 │                 │
│                └────────────────┬────────────────┘                 │
│                                 ▼                                  │
│                      SQLite Database (Local)                       │
│                                                                    │
└─────────────────────────────────┬──────────────────────────────────┘
                                  │
                                  ▼ (WebSockets / REST API)
┌────────────────────────────────────────────────────────────────────┐
│                  Frontend Dashboard (HTML/CSS/JS)                  │
│         • Live Power Flow Animation   • Battery SOC Gauge          │
│                        • DTEK Grid Timeline                        │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Security & Authentication

- **Cookie-Based Session Protection:** The entire dashboard (`/`) and administrative configuration panel (`/settings`) are guarded behind a dedicated login route (`/login`).
- **HTTP-Only Session Cookies:** Uses secure `deye_session` HTTP-only cookies to eliminate risks associated with client-side token storage (XSS protection).
- **In-App Credential Management:** Modify admin username and password directly within the settings view without manual `.env` file editing.
- **Zero Exposed Secrets:** Telegram credentials, local secrets, and databases are strictly excluded from version control via `.gitignore`.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, FastAPI, Uvicorn, SQLite, PyModbus, PySerial, HTTPX, Pydantic v2.
- **Frontend:** HTML5, Modern CSS (Glassmorphism styling, CSS custom properties, responsive flex/grid layouts), Vanilla JavaScript (ES6+).
- **Storage:** SQLite3 local database.
- **Deployment:** Docker & Docker Compose, Windows PowerShell automation scripts (`run.ps1`).

---

## 🚀 Quick Start

### Local Startup on Windows (PowerShell)

Run the automated environment bootstrap and server startup script:

```powershell
.\run.ps1
```

### Manual Local Startup (Linux / macOS / Windows)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/invertorweb.git
   cd invertorweb
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv

   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1

   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install project dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare environment configuration:**

   ```bash
   cp .env.example .env
   ```

5. **Launch the application:**

   ```bash
   python -m backend.main
   ```

6. **Access the dashboard:**

   Open <http://localhost:8000> in your browser. Default login credentials:

   - **Username:** `admin`
   - **Password:** `admin`

   > ⚠️ Change the default credentials right after the first login (via `/settings` or `.env`).

---

## 🐳 Docker Deployment

Run the complete stack in a detached container via Docker Compose:

```bash
docker compose up -d --build
```

View live server logs:

```bash
docker compose logs -f
```

Shut down containers:

```bash
docker compose down
```

---

## 🎮 Demo & Simulation Mode

When physical hardware is not linked, run the system in simulated mode:

- Set `DEMO_MODE=True` via `.env` or enable it inside `/settings`.
- The background telemetry engine models fluctuating consumption, battery charge/discharge dynamics, and grid stability.
- Use the **"⚡ Мережа"** toggle switch in the dashboard header or appliance buttons (Fridge / Kettle) to simulate power failure scenarios, trigger alarm sounds, and generate outage log entries in real time.

---

## ⚙️ Configuration (`.env`)

Default variables defined in `.env`:

```env
# Server bind address
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# Authentication defaults
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Simulation Mode (Set False for real Modbus connection)
DEMO_MODE=True

# Telegram Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_NOTIFICATIONS_ENABLED=True

# DTEK Outage Schedule Settings
DTEK_REGION=kyiv          # Options: kyiv, kyiv_region, dnipro, odesa, custom
DTEK_GROUP=3              # Groups: 1-6 (or subgroups 1.1-6.2 for kyiv_region)

# Battery Parameters (LiFePO4 Fallback)
BATTERY_CAPACITY_WH=5120
BATTERY_MIN_SOC=15
LOW_BATTERY_ALERT_SOC=20

# Deye Modbus Hardware Interface (Read-Only)
MODBUS_ENABLED=False
MODBUS_TYPE=tcp           # Options: tcp, rtu
MODBUS_HOST=192.168.1.150
MODBUS_TCP_PORT=502
MODBUS_PORT=COM3          # Serial interface (e.g., COM3 or /dev/ttyUSB0)
MODBUS_BAUDRATE=9600
MODBUS_SLAVE_ID=1
```

---

## 🛡️ Security Audit & Repository Hygiene

- No hardcoded access tokens, external endpoints, or credentials exist in tracked files.
- Real `.env` configuration files and runtime SQLite databases (`*.db`, `*.sqlite3`) are isolated via `.gitignore`.
- Modbus commands are strictly restricted to reading registers to eliminate any hardware write hazard.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
