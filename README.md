# 🌊 Plastic Pollution Report 2026 — Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)

A backend service for collecting and processing global plastic pollution statistics. It operates as an ETL pipeline: fetching data from OECD, processing it, and serving it via API.

## ⚙️ Tech Stack
* **FastAPI** — Main framework for high-performance API.
* **Python** — Core programming language.
* **Pandas** — Data processing and filtration.
* **Docker** — Containerization for seamless deployment.
* **Render** — Cloud hosting platform.

## 🚀 Features
* **Data Fetching**: Automates CSV data retrieval directly from OECD databases.
* **Fast API**: Provides `/stats/plastic` for charts and `/stats/cards` for summary data.
* **Memory Cache**: Stores processed data in RAM for near-instant response times.
