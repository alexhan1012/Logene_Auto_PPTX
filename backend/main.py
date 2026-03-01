"""
Logene Auto PPTX – FastAPI backend
"""
from __future__ import annotations

import io
import os
import uuid
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

from services.document_parser import parse_document
from services.ai_service import generate_presentation_plan
from services.pptx_generator import build_pptx

app = FastAPI(title="Logene Auto PPTX API", version="1.0.0")

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "20")) * 1024 * 1024

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/templates")
def list_templates():
    """Return the list of available slide templates."""
    from services.template_registry import TEMPLATES
    return {"templates": TEMPLATES}


@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    files: List[UploadFile] = File(default=[]),
):
    """
    Main endpoint: receive user prompt + optional uploaded files,
    call OpenAI to build a presentation plan, then render the PPTX.
    """
    # ── 1. Parse uploaded documents ──────────────────────────────────
    combined_text: str = ""
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type: {suffix}. "
                       f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}",
            )
        raw = await upload.read()
        if len(raw) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File '{upload.filename}' exceeds the "
                       f"{os.getenv('MAX_UPLOAD_MB', 20)} MB limit.",
            )
        combined_text += f"\n\n--- 文件: {upload.filename} ---\n"
        combined_text += parse_document(raw, suffix)

    # ── 2. Ask AI to produce a structured presentation plan ───────────
    plan = await generate_presentation_plan(prompt, combined_text)

    # ── 3. Render PPTX ────────────────────────────────────────────────
    pptx_bytes: bytes = build_pptx(plan)

    # ── 4. Stream the file back to the client ─────────────────────────
    safe_title = "".join(
        c for c in plan.get("title", "presentation") if c.isalnum() or c in " _-"
    ).strip() or "presentation"
    filename = f"{safe_title[:60]}.pptx"

    return StreamingResponse(
        io.BytesIO(pptx_bytes),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
