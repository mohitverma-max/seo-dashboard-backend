"""
SEO Dashboard Backend — entry point.

Start with:  uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import health, monitor, optimizer, feedback, approval

app = FastAPI(
    title="SEO Dashboard Backend",
    description="Central controller between the Claude Dashboard and SEO agents.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow the Claude Artifact Dashboard (any origin during development).
# Lock this down to specific origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (PDFs) ───────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router, tags=["Health"])
app.include_router(monitor.router, tags=["SEO Monitor"])
app.include_router(optimizer.router, tags=["Content Optimizer"])
app.include_router(feedback.router, tags=["Feedback"])
app.include_router(approval.router, tags=["Approval Workflow"])
