"""
Logene Auto PPTX – FastAPI backend
"""
from __future__ import annotations

import io
import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

from services.document_parser import parse_document
from services.ai_service import generate_presentation_plan
from services.pptx_generator import build_pptx
from services import custom_template_store as cts

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


# ── Custom Template CRUD ──────────────────────────────────────────────────────

@app.get("/api/custom-templates/categories")
def list_custom_categories():
    """Return the list of distinct custom template categories."""
    return {"categories": cts.list_categories()}


@app.get("/api/custom-templates")
def list_custom_templates(category: Optional[str] = None):
    """Return all custom templates, optionally filtered by category."""
    return {"templates": cts.list_templates(category)}


@app.post("/api/custom-templates", status_code=201)
async def create_custom_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    category: str = Form(...),
    description: str = Form(default=""),
):
    """Upload a new PPTX template with its metadata."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".pptx":
        raise HTTPException(
            status_code=415,
            detail="只支持 .pptx 格式的模板文件",
        )
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"文件超过 {os.getenv('MAX_UPLOAD_MB', 20)} MB 限制",
        )
    record = cts.save_template(
        pptx_bytes=raw,
        original_filename=file.filename or "template.pptx",
        name=name,
        category=category,
        description=description,
    )
    return record


@app.put("/api/custom-templates/{template_id}")
def update_custom_template(
    template_id: str,
    name: Optional[str] = Form(default=None),
    category: Optional[str] = Form(default=None),
    description: Optional[str] = Form(default=None),
):
    """Update mutable metadata of an existing custom template."""
    record = cts.update_template(template_id, name=name, category=category, description=description)
    if record is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    return record


@app.delete("/api/custom-templates/{template_id}", status_code=204)
def delete_custom_template(template_id: str):
    """Delete a custom template and its file."""
    if not cts.delete_template(template_id):
        raise HTTPException(status_code=404, detail="模板不存在")


@app.post("/api/generate")
async def generate(
    prompt: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    custom_template_id: Optional[str] = Form(default=None),
):
    """
    Main endpoint: receive user prompt + optional uploaded files,
    call OpenAI to build a presentation plan, then render the PPTX.
    Optionally uses a custom uploaded PPTX template as the visual base.
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
    # Optionally pass custom template catalogue for progressive disclosure
    custom_templates = cts.list_templates()
    try:
        plan = await generate_presentation_plan(prompt, combined_text, custom_templates)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # ── 3. Render PPTX ────────────────────────────────────────────────
    # If a custom template ID was specified, use that PPTX as the base
    base_template_path: Optional[str] = None
    if custom_template_id:
        record = cts.get_template(custom_template_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"自定义模板 '{custom_template_id}' 不存在")
        base_template_path = record["file_path"]

    pptx_bytes: bytes = build_pptx(plan, base_template_path=base_template_path)

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
