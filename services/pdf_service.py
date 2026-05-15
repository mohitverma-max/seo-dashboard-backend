"""PDF generation and serving utilities."""

import os
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from fastapi.responses import FileResponse

PDF_DIR = Path(os.getenv("PDF_DIR", "static/pdfs"))


def get_pdf_response(filename: str) -> FileResponse:
    """Return a FileResponse for an existing PDF, or raise 404."""
    path = PDF_DIR / filename
    if not path.exists() or path.suffix != ".pdf":
        raise HTTPException(status_code=404, detail=f"PDF '{filename}' not found.")
    return FileResponse(path=str(path), media_type="application/pdf", filename=filename)


def save_report_pdf(task_id: str, content: dict) -> str:
    """
    Generate a simple PDF report from a task result dict.
    Returns the filename so the caller can expose a download URL.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        raise RuntimeError("reportlab is not installed. Run: pip install reportlab")

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"report-{task_id}.pdf"
    filepath = PDF_DIR / filename

    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 60, "SEO Dashboard Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Task ID: {task_id}")

    y = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Results:")
    y -= 20

    c.setFont("Helvetica", 10)
    for key, value in content.items():
        if y < 60:
            c.showPage()
            y = height - 60
        text = f"  {key}: {value}"
        # Truncate very long values so they fit on one line
        if len(text) > 100:
            text = text[:97] + "..."
        c.drawString(50, y, text)
        y -= 18

    c.save()
    return filename
