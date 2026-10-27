# ⚡ Deye Inverter & DTEK Power Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Open%20Source-orange?style=for-the-badge)

A production-grade real-time web monitoring and automation system for **Deye Hybrid Inverters** (SUN-5K/6K-SG03LP1-EU and compatible) combined with **DTEK Power Outage Schedules** (Ukraine), dynamic BMS capacity detection, cookie-based session security, and automated **Telegram alerts**.

[Features](#-key-features) • [Architecture](#-system-architecture) • [Security & Auth](#-security--authentication) • [Quick Start](#-quick-start) • [Docker Deployment](#-docker-deployment) • [Configuration](#-configuration)

</div>

---

## 🌟 Key Features

- **Dynamic Inverter & Battery Telemetry:** Real-time extraction of inverter model name, serial identification, battery State of Health (SOH), and capacity (Ah / kWh) via Modbus/BMS with zero hardcoded placeholders.
- **Safe Read-Only Modbus Polling:** Interacts with physical Deye inverters safely over RS485/USB or Modbus TCP using strict read-only register requests (`read_holding_registers`). Transparent offline handling prevents silent fallback errors when hardware is disconnected.
- **DTEK Outage Schedules & Subgroups:** Supports official schedules for Kyiv, Kyiv Region (including detailed subgroups `1.1`–`6.2`), Dnipro, Odesa, and a configurable **Custom Schedule** mode for non-standard regional timetables.
- **Smart Simulation Mode (`DEMO_MODE=True`):** Full-fledged software emulation of household load variations (350–680W), battery discharge curves, and grid outages for UI/UX testing and development without physical hardware.
- **Automated Telegram Bot Alerts:** Push notifications in Ukrainian triggered instantly on mains disconnection, utility restoration, and critical low-battery thresholds (`<20%`).
- **Interactive Dashboard & Admin Panel:** Glassmorphism dark UI featuring live animated power flows, real-time battery runtime projections, 30-day blackout history logs, appliance load test controls, and an in-app system settings panel (`/settings`).
- **Persistent SQLite Storage:** Local, zero-maintenance database tracking historical outage records, user preferences, and cached outage schedules.

---

## 🏗️ System Architecture