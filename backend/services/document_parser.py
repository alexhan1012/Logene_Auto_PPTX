"""
Document parser – extracts plain text from uploaded files.
Supports: .pdf, .docx, .txt, .xlsx, .xls
"""
from __future__ import annotations

import io


def parse_document(raw_bytes: bytes, suffix: str) -> str:
    """Return the best-effort plain-text extraction of the document."""
    suffix = suffix.lower()
    if suffix == ".txt":
        return _parse_txt(raw_bytes)
    if suffix == ".pdf":
        return _parse_pdf(raw_bytes)
    if suffix == ".docx":
        return _parse_docx(raw_bytes)
    if suffix in (".xlsx", ".xls"):
        return _parse_excel(raw_bytes)
    return ""


def _parse_txt(raw: bytes) -> str:
    for enc in ("utf-8", "utf-16", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def _parse_pdf(raw: bytes) -> str:
    try:
        import pdfplumber

        text_parts: list[str] = []
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:
        return f"[PDF 解析失败: {exc}]"


def _parse_docx(raw: bytes) -> str:
    try:
        from docx import Document

        doc = Document(io.BytesIO(raw))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as exc:
        return f"[DOCX 解析失败: {exc}]"


def _parse_excel(raw: bytes) -> str:
    try:
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
        lines: list[str] = []
        for sheet in wb.worksheets:
            lines.append(f"[工作表: {sheet.title}]")
            for row in sheet.iter_rows(values_only=True):
                row_text = "\t".join(
                    str(cell) if cell is not None else "" for cell in row
                )
                if row_text.strip():
                    lines.append(row_text)
        return "\n".join(lines)
    except Exception as exc:
        return f"[Excel 解析失败: {exc}]"
