"""
Custom Template Store – JSON-file-backed CRUD for user-uploaded PPTX templates.

Each template record contains:
  id           : UUID string
  name         : display name
  category     : user-defined category (e.g. "商业报告", "产品发布")
  description  : what the template is best suited for (used by AI for selection)
  filename     : original file name of the uploaded PPTX
  file_path    : absolute path on disk
  slide_count  : number of slides in the uploaded PPTX
  created_at   : ISO-8601 timestamp
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pptx import Presentation

# ── Storage paths ─────────────────────────────────────────────────────────────

_BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = _BASE_DIR / "data"
UPLOADS_DIR = _BASE_DIR / "uploads" / "templates"
DB_FILE = DATA_DIR / "custom_templates.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_db() -> list[dict]:
    if not DB_FILE.exists():
        return []
    try:
        return json.loads(DB_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_db(records: list[dict]) -> None:
    DB_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def _count_slides(file_path: Path) -> int:
    try:
        prs = Presentation(str(file_path))
        return len(prs.slides)
    except Exception:
        return 0


# ── Public API ────────────────────────────────────────────────────────────────

def list_templates(category: Optional[str] = None) -> List[dict]:
    """Return all custom templates, optionally filtered by category."""
    records = _load_db()
    if category:
        records = [r for r in records if r.get("category") == category]
    return records


def list_categories() -> List[str]:
    """Return all distinct categories, sorted."""
    records = _load_db()
    cats = sorted({r["category"] for r in records if r.get("category")})
    return cats


def get_template(template_id: str) -> Optional[dict]:
    """Return a single template by ID, or None if not found."""
    for r in _load_db():
        if r["id"] == template_id:
            return r
    return None


def save_template(
    pptx_bytes: bytes,
    original_filename: str,
    name: str,
    category: str,
    description: str,
) -> dict:
    """Persist a new template record and its PPTX file; return the new record."""
    template_id = str(uuid.uuid4())
    safe_name = "".join(c for c in original_filename if c.isalnum() or c in "._- ").strip()
    dest_filename = f"{template_id}_{safe_name}"
    dest_path = UPLOADS_DIR / dest_filename

    dest_path.write_bytes(pptx_bytes)
    slide_count = _count_slides(dest_path)

    record = {
        "id": template_id,
        "name": name,
        "category": category,
        "description": description,
        "filename": original_filename,
        "file_path": str(dest_path),
        "slide_count": slide_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    records = _load_db()
    records.append(record)
    _save_db(records)
    return record


def update_template(
    template_id: str,
    name: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
) -> Optional[dict]:
    """Update mutable fields of an existing template; return updated record or None."""
    records = _load_db()
    for record in records:
        if record["id"] == template_id:
            if name is not None:
                record["name"] = name
            if category is not None:
                record["category"] = category
            if description is not None:
                record["description"] = description
            _save_db(records)
            return record
    return None


def delete_template(template_id: str) -> bool:
    """Delete a template record and its file. Returns True on success."""
    records = _load_db()
    for i, record in enumerate(records):
        if record["id"] == template_id:
            file_path = Path(record.get("file_path", ""))
            if file_path.exists():
                file_path.unlink()
            records.pop(i)
            _save_db(records)
            return True
    return False
