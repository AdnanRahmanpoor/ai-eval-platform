# 🤖 AI Evaluation & Operations Platform

![Python](https://img.shields.io/badge/Python-3.14.2-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.127-009688?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek_API-000000)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade SaaS platform for automated LLM evaluation, prompt versioning, and regression detection. Built to act as a CI/CD pipeline for AI, ensuring that prompt updates are mathematically verified against Golden Datasets before reaching production.

🌐 **Live Demo:** [eval.adnanrp.com](https://eval.adnanrp.com/dashboard) *(Note: Dashboard is publicly accessible, API requires valid dataset/prompt IDs)*

---

## 🌟 Key Features

- **🔄 Asynchronous Batch Engine:** Utilizes FastAPI `BackgroundTasks` and Gunicorn to process thousands of dataset rows concurrently without blocking HTTP threads.
- **🛡️ Anti-Sycophancy LLM-as-a-Judge:** Engineered a specialized evaluation prompt utilizing **Context Isolation** to grade *business accuracy* rather than *instruction-following*, preventing LLMs from being tricked by formatting hallucinations.
- **📉 Automated Regression Detection:** Mathematically compares new prompt experiments against historical baselines, automatically flagging performance drops.
- **🗄️ Zero-Downtime Migrations:** Integrated **Alembic** for safe, version-controlled database schema migrations.
- **📊 Real-Time Visual Dashboard:** A beautiful, dark-mode SaaS UI built with Jinja2, Tailwind CSS, and Chart.js to visualize experiment performance and regressions.
- **📱 Proactive Alerting:** Closed-loop integration with the Telegram Bot API to instantly page engineering teams the millisecond a regression is detected.

---

## 🏗️ System Architecture

```text
[ Client / Swagger UI ] 
       │
       ▼
┌─────────────────────────────────────────┐
│           FastAPI (Gunicorn)            │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  REST API   │  │  Jinja2 Dashboard│  │
│  │  /api/v1/*  │  │  /dashboard      │  │
│  └──────┬──────┘  └──────────────────┘  │
│         │                               │
│  ┌──────▼──────────────────────────┐    │
│  │   Background Task Queue         │    │
│  │   (Async Eval Engine)           │    │
│  └──────┬──────────────┬───────────┘    │
└─────────┼──────────────┼────────────────┘
          │              │
          ▼              ▼
┌──────────────┐  ┌──────────────┐
│ DeepSeek API │  │ Telegram API │
│ (Generation  │  │ (Regression  │
│  & Judging)  │  │  Alerts)     │
└──────────────┘  └──────────────┘
          │
          ▼
┌──────────────────────┐
│ SQLite + Alembic     │
│ (Persisted via Docker│
│  Volume Mounts)      │
└──────────────────────┘
```

---

## 🖼️ Screenshots

### 📊 Visual Dashboard & Regression Tracking
![Dashboard Screenshot](dashboard.png)

### 📱 Automated Telegram Alerts
![Telegram Alert](telegram.png)

---

## 🛠️ Tech Stack

| Category | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI, Uvicorn, Gunicorn |
| **Database & ORM** | SQLite, SQLModel, Alembic |
| **AI / LLM** | DeepSeek API (OpenAI SDK compatible) |
| **Frontend / UI** | Jinja2, Tailwind CSS, Chart.js |
| **DevOps / Infra** | Docker, Dokploy, Traefik (SSL/Reverse Proxy) |
| **Alerting** | Telegram Bot API (via `httpx`) |

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.14+
- A DeepSeek API Key

### 1. Clone and Install
```bash
git clone https://github.com/AdnanRahmanpoor/ai-eval-platform.git
cd ai-eval-platform
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
APP_NAME="AI Eval Platform"
DATABASE_URL="sqlite:///./eval_platform.db"
DEEPSEEK_API_KEY="sk-your-key-here"
DEEPSEEK_BASE_URL="https://api.deepseek.com"
DEEPSEEK_MODEL="deepseek-v4-flash"
TELEGRAM_BOT_TOKEN="telegram-bot-token"
TELEGRAM_CHAT_ID="telegram-chat-id"
```

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Start the Server
```bash
uvicorn app.main:app --reload
```
Visit **http://127.0.0.1:8000/docs** for the interactive Swagger API, or **http://127.0.0.1:8000/dashboard** for the visual UI.

---

## 🐳 Production Deployment (Docker)

This project is fully containerized and designed for zero-downtime deployments via platforms like Dokploy, Coolify, or AWS ECS.

**Build and run locally via Docker:**
```bash
docker build -t ai-eval-platform .
docker run -d -p 8000:8000 --env-file .env -v sqlite_data:/app/data ai-eval-platform
```
*Note: Ensure your `DATABASE_URL` in production points to a persistent volume path (e.g., `sqlite:////app/data/eval_platform.db`).*

---

## 🧠 Engineering Highlights & Decisions

1. **Why Context Isolation in the Judge?** 
   Early testing revealed "Instruction Sycophancy," where the LLM Judge would give perfect scores to bad prompts simply because the LLM followed formatting tricks. By feeding *only* the raw input data and the output to the Judge (isolating it from the system prompt), we force it to evaluate pure business accuracy.
2. **Why SQLite + Docker Volumes?**
   For a single-VPS SaaS, PostgreSQL is often overkill. By utilizing Docker Volume mounts, we achieve persistent, crash-resilient SQLite storage without the overhead of managing a separate database container, while keeping the Docker image incredibly lightweight.
3. **Why `httpx` for Telegram?**
   Instead of pulling in a massive bot framework, we use `httpx` for a single, asynchronous POST request. This keeps the Docker image small and prevents blocking the Gunicorn event loop.

---

