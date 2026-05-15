# SEO Dashboard Backend

Central FastAPI controller between the Claude Artifact Dashboard and all SEO agents.

## Architecture

```
Claude Artifact Dashboard
        │
        ▼
SEO Dashboard Backend  (this repo — port 8000)
        │
        ├──▶  SEO Monitor Agent         (port 8001)
        └──▶  Content Optimizer Agent   (port 8002)

        (future)
        ├──▶  Content Writer Agent      (port 8003)
        ├──▶  Keyword Research Agent    (port 8004)
        └──▶  Technical SEO Agent       (port 8005)
```

## Folder Structure

```
seo-dashboard-backend/
├── main.py                    ← FastAPI app + CORS + static files
├── requirements.txt
├── .env.example               ← Copy to .env
├── routers/
│   ├── health.py              ← GET  /health
│   ├── monitor.py             ← POST /run-monitor
│   ├── optimizer.py           ← POST /optimize
│   ├── feedback.py            ← POST /apply-feedback
│   └── approval.py            ← POST /approve  /reject  /tasks
├── agents/
│   ├── seo_monitor.py         ← HTTP client → SEO Monitor Agent
│   └── content_optimizer.py   ← HTTP client → Content Optimizer Agent
├── models/
│   ├── requests.py            ← Pydantic input models
│   └── responses.py           ← Pydantic output models + WorkflowStatus enum
├── services/
│   ├── workflow.py            ← In-memory task state machine
│   └── pdf_service.py         ← PDF generation & serving
├── utils/
│   └── logger.py
└── static/
    └── pdfs/                  ← Generated PDF reports land here
```

## Quick Start

### 1. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env if your agents run on different ports
```

### 4. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

The API is now available at:
- **Swagger UI:**  http://localhost:8000/docs
- **ReDoc:**       http://localhost:8000/redoc
- **Health:**      http://localhost:8000/health

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Backend + agent status |
| `POST` | `/run-monitor` | Start an SEO audit |
| `POST` | `/optimize` | Start content optimization |
| `POST` | `/apply-feedback` | Record human feedback on a task |
| `POST` | `/approve` | Approve a pending task (generates PDF) |
| `POST` | `/reject` | Reject a pending task |
| `GET`  | `/tasks` | List all tasks |
| `GET`  | `/tasks/{task_id}` | Get a single task state |
| `GET`  | `/tasks/{task_id}/pdf` | Download the approved task PDF |

---

## Workflow State Machine

```
idle ──▶ running ──▶ pending_approval ──▶ approved
                  ╲                    ╲
                   ▶ error              ▶ rejected
```

1. Call `/run-monitor` or `/optimize` → get back a `task_id`, `status: running`.
2. Poll `GET /tasks/{task_id}` until `status: pending_approval`.
3. Call `/apply-feedback` (optional) to send reviewer notes before approving.
4. Call `/approve` → PDF report is generated and URL is returned.
5. Call `/reject` → re-run `/optimize` with the same `task_id` to pick up feedback.

---

## Adding a New Agent

1. Add the agent URL to `.env.example` and `.env`.
2. Create `agents/my_new_agent.py` with a single async function that calls the agent.
3. Add a new router in `routers/my_new_router.py`.
4. Include the router in `main.py`.
5. Add the agent URL to the `_AGENTS` dict in `routers/health.py`.

---

## Notes

- **Agent offline?** The connectors fall back to mock results so the rest of the backend keeps working during development.
- **Production:** Replace the in-memory `WorkflowManager` (`services/workflow.py`) with Redis or a database for persistence across restarts.
- **PDF reports** are saved to `static/pdfs/` and served at `/static/pdfs/<filename>`.
