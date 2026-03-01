"""
PPTX Generator – renders a presentation plan (dict) into a binary .pptx file
using python-pptx.  Each template function creates exactly one slide.
"""
from __future__ import annotations

import io
from typing import Any

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt, Emu

# ── Brand colours ────────────────────────────────────────────────────────────
C_DARK_BLUE = RGBColor(0x1F, 0x38, 0x64)
C_MID_BLUE = RGBColor(0x2E, 0x75, 0xB6)
C_LIGHT_BLUE = RGBColor(0xBD, 0xD7, 0xEE)
C_ORANGE = RGBColor(0xED, 0x7D, 0x31)
C_TEAL = RGBColor(0x00, 0x70, 0xC0)
C_DARK_GRAY = RGBColor(0x40, 0x40, 0x40)
C_MID_GRAY = RGBColor(0x80, 0x80, 0x80)
C_LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK = RGBColor(0x00, 0x00, 0x00)

ACCENT_COLORS = [
    RGBColor(0x2E, 0x75, 0xB6),
    RGBColor(0xED, 0x7D, 0x31),
    RGBColor(0x00, 0x70, 0xC0),
    RGBColor(0x70, 0xAD, 0x47),
    RGBColor(0xFF, 0xC0, 0x00),
    RGBColor(0x7B, 0x0F, 0xA0),
]

# Slide size: Widescreen 13.33" × 7.5"
SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

FONT_BODY = "Calibri"
FONT_TITLE = "Calibri Light"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _new_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def _blank_slide(prs: Presentation):
    """Add a completely blank slide (no placeholders)."""
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def _fill_bg(slide, color: RGBColor):
    from pptx.oxml.ns import qn
    from lxml import etree

    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def _add_rect(slide, left, top, width, height, fill_color: RGBColor | None = None,
              line_color: RGBColor | None = None, line_width_pt: float = 0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height,
    )
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width_pt)
    else:
        shape.line.fill.background()
    return shape


def _add_textbox(slide, left, top, width, height, text: str,
                 font_size: int = 18, bold: bool = False,
                 color: RGBColor = C_DARK_GRAY, align=PP_ALIGN.LEFT,
                 font_name: str = FONT_BODY, wrap: bool = True) -> Any:
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.name = font_name
    run.font.color.rgb = color
    return txb


def _set_para(para, text: str, font_size: int, bold: bool = False,
              color: RGBColor = C_DARK_GRAY, align=PP_ALIGN.LEFT,
              font_name: str = FONT_BODY):
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.name = font_name
    run.font.color.rgb = color


def _safe(val, default=""):
    if val is None:
        return default
    return str(val)


# ── Header bar shared across content slides ───────────────────────────────────

def _add_header_bar(slide, title: str):
    """Dark-blue top bar (0.8") with white title text."""
    bar_h = Inches(0.85)
    _add_rect(slide, 0, 0, SLIDE_W, bar_h, fill_color=C_DARK_BLUE)
    _add_textbox(
        slide, Inches(0.4), Inches(0.05), Inches(12.5), bar_h,
        text=title, font_size=24, bold=True,
        color=C_WHITE, align=PP_ALIGN.LEFT, font_name=FONT_TITLE,
    )


def _add_footer(slide, text: str = "Confidential"):
    """Light footer line at bottom."""
    _add_rect(slide, 0, SLIDE_H - Inches(0.3), SLIDE_W, Inches(0.3),
              fill_color=C_DARK_BLUE)
    _add_textbox(
        slide, Inches(0.4), SLIDE_H - Inches(0.28), Inches(12.5), Inches(0.28),
        text=text, font_size=8, color=C_WHITE, align=PP_ALIGN.LEFT,
    )


# ── Template renderers ────────────────────────────────────────────────────────

def _render_title_slide(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_DARK_BLUE)

    # Left accent stripe
    _add_rect(slide, 0, 0, Inches(0.5), SLIDE_H, fill_color=C_ORANGE)

    # Decorative circles (geometric pattern)
    for i, (cx, cy, r, alpha) in enumerate([
        (Inches(11.5), Inches(1.0), Inches(2.5), C_MID_BLUE),
        (Inches(12.5), Inches(5.5), Inches(1.5), C_TEAL),
    ]):
        circle = slide.shapes.add_shape(9, cx - r, cy - r, r * 2, r * 2)
        circle.fill.solid()
        circle.fill.fore_color.rgb = alpha
        circle.line.fill.background()

    # Title text
    _add_textbox(
        slide, Inches(1.0), Inches(2.2), Inches(9.5), Inches(1.8),
        text=_safe(content.get("title"), "Presentation Title"),
        font_size=40, bold=True, color=C_WHITE, align=PP_ALIGN.LEFT,
        font_name=FONT_TITLE,
    )
    # Subtitle / date
    subtitle = _safe(content.get("subtitle"))
    if subtitle:
        _add_textbox(
            slide, Inches(1.0), Inches(4.2), Inches(9.5), Inches(0.8),
            text=subtitle, font_size=22, bold=False,
            color=C_LIGHT_BLUE, align=PP_ALIGN.LEFT,
        )
    # Bottom bar
    _add_rect(slide, Inches(0.5), SLIDE_H - Inches(0.8),
              SLIDE_W - Inches(0.5), Inches(0.8), fill_color=C_ORANGE)
    _add_textbox(
        slide, Inches(1.0), SLIDE_H - Inches(0.8), Inches(8), Inches(0.8),
        text="Powered by Logene Auto PPTX", font_size=12,
        color=C_WHITE, align=PP_ALIGN.LEFT,
    )


def _render_agenda(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "议程"))
    _add_footer(slide)

    items: list = content.get("items") or []
    col_w = Inches(5.8)
    start_y = Inches(1.1)
    item_h = Inches(0.7)
    gap = Inches(0.12)

    for i, item in enumerate(items[:6]):
        y = start_y + i * (item_h + gap)
        # Number badge
        badge_color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        _add_rect(slide, Inches(0.8), y, Inches(0.55), item_h, fill_color=badge_color)
        _add_textbox(
            slide, Inches(0.8), y + Inches(0.05), Inches(0.55), item_h - Inches(0.05),
            text=str(i + 1), font_size=20, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Item text
        _add_rect(slide, Inches(1.45), y, Inches(11.0), item_h,
                  fill_color=C_LIGHT_GRAY)
        _add_textbox(
            slide, Inches(1.65), y + Inches(0.1), Inches(10.6), item_h,
            text=_safe(item), font_size=18, bold=False,
            color=C_DARK_GRAY, align=PP_ALIGN.LEFT,
        )


def _render_section_divider(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_DARK_BLUE)

    _add_rect(slide, 0, 0, Inches(0.6), SLIDE_H, fill_color=C_ORANGE)

    number = _safe(content.get("section_number"), "")
    if number:
        _add_textbox(
            slide, Inches(1.2), Inches(1.8), Inches(3), Inches(1.5),
            text=number, font_size=72, bold=True,
            color=C_ORANGE, font_name=FONT_TITLE,
        )

    _add_textbox(
        slide, Inches(1.2), Inches(3.1), Inches(9), Inches(1.5),
        text=_safe(content.get("section_title"), "Section"),
        font_size=36, bold=True, color=C_WHITE, font_name=FONT_TITLE,
    )

    subtitle = _safe(content.get("section_subtitle"))
    if subtitle:
        _add_textbox(
            slide, Inches(1.2), Inches(4.7), Inches(9), Inches(0.9),
            text=subtitle, font_size=20, color=C_LIGHT_BLUE,
        )


def _render_content_bullets(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "内容"))
    _add_footer(slide)

    bullets: list = content.get("bullets") or []
    y = Inches(1.05)
    bullet_h = Inches(0.72)
    gap = Inches(0.08)

    for i, bullet in enumerate(bullets[:7]):
        row_y = y + i * (bullet_h + gap)
        # Accent dot
        dot_size = Inches(0.12)
        _add_rect(
            slide, Inches(0.5), row_y + (bullet_h - dot_size) / 2,
            dot_size, dot_size,
            fill_color=ACCENT_COLORS[i % len(ACCENT_COLORS)],
        )
        _add_textbox(
            slide, Inches(0.85), row_y, Inches(11.9), bullet_h,
            text=_safe(bullet), font_size=18, color=C_DARK_GRAY,
        )


def _render_key_metrics(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "关键指标"))
    _add_footer(slide)

    metrics: list = content.get("metrics") or []
    metrics = metrics[:6]
    n = len(metrics)
    if n == 0:
        return

    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    box_w = Inches(3.8)
    box_h = Inches(2.3)
    total_w = cols * box_w + (cols - 1) * Inches(0.25)
    start_x = (SLIDE_W - total_w) / 2
    start_y = Inches(1.2)

    for idx, metric in enumerate(metrics):
        row = idx // cols
        col = idx % cols
        x = start_x + col * (box_w + Inches(0.25))
        y = start_y + row * (box_h + Inches(0.2))
        color = ACCENT_COLORS[idx % len(ACCENT_COLORS)]

        _add_rect(slide, x, y, box_w, box_h, fill_color=color)

        value = _safe(metric.get("value") if isinstance(metric, dict) else metric)
        label = _safe(metric.get("label") if isinstance(metric, dict) else "")
        trend = _safe(metric.get("trend") if isinstance(metric, dict) else "")

        # Big value
        _add_textbox(
            slide, x + Inches(0.1), y + Inches(0.25),
            box_w - Inches(0.2), Inches(1.2),
            text=value + ("  " + trend if trend else ""),
            font_size=36, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Label
        _add_textbox(
            slide, x + Inches(0.1), y + Inches(1.5),
            box_w - Inches(0.2), Inches(0.65),
            text=label, font_size=14, color=C_WHITE, align=PP_ALIGN.CENTER,
        )


def _render_timeline(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "时间轴"))
    _add_footer(slide)

    events: list = content.get("events") or []
    events = events[:7]
    n = len(events)
    if n == 0:
        return

    # Horizontal line
    line_y = Inches(4.0)
    line_x_start = Inches(0.8)
    line_x_end = SLIDE_W - Inches(0.8)
    line_len = line_x_end - line_x_start
    _add_rect(slide, line_x_start, line_y - Inches(0.03),
              line_len, Inches(0.06), fill_color=C_MID_BLUE)

    spacing = line_len / (n - 1) if n > 1 else line_len / 2

    for i, event in enumerate(events):
        x = line_x_start + i * spacing if n > 1 else (line_x_start + line_x_end) / 2
        date = _safe(event.get("date") if isinstance(event, dict) else event)
        title = _safe(event.get("title") if isinstance(event, dict) else "")
        desc = _safe(event.get("description") if isinstance(event, dict) else "")
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]

        # Dot on the line
        dot_r = Inches(0.15)
        _add_rect(slide, x - dot_r, line_y - dot_r, dot_r * 2, dot_r * 2,
                  fill_color=color)

        above = i % 2 == 0  # Alternate above/below

        if above:
            # Date above line
            _add_textbox(
                slide, x - Inches(0.9), line_y - Inches(2.7), Inches(1.8), Inches(0.4),
                text=date, font_size=11, bold=True, color=color,
                align=PP_ALIGN.CENTER,
            )
            # Title
            _add_textbox(
                slide, x - Inches(0.9), line_y - Inches(2.3), Inches(1.8), Inches(0.5),
                text=title, font_size=12, bold=True, color=C_DARK_GRAY,
                align=PP_ALIGN.CENTER,
            )
            # Description
            if desc:
                _add_textbox(
                    slide, x - Inches(0.9), line_y - Inches(1.8), Inches(1.8), Inches(1.5),
                    text=desc, font_size=10, color=C_MID_GRAY,
                    align=PP_ALIGN.CENTER,
                )
            # Connector line up
            _add_rect(slide, x - Inches(0.015), line_y - Inches(0.5),
                      Inches(0.03), Inches(0.5), fill_color=color)
        else:
            # Date below line
            _add_textbox(
                slide, x - Inches(0.9), line_y + Inches(0.6), Inches(1.8), Inches(0.4),
                text=date, font_size=11, bold=True, color=color,
                align=PP_ALIGN.CENTER,
            )
            # Title
            _add_textbox(
                slide, x - Inches(0.9), line_y + Inches(1.05), Inches(1.8), Inches(0.5),
                text=title, font_size=12, bold=True, color=C_DARK_GRAY,
                align=PP_ALIGN.CENTER,
            )
            # Description
            if desc:
                _add_textbox(
                    slide, x - Inches(0.9), line_y + Inches(1.6), Inches(1.8), Inches(1.5),
                    text=desc, font_size=10, color=C_MID_GRAY,
                    align=PP_ALIGN.CENTER,
                )
            # Connector line down
            _add_rect(slide, x - Inches(0.015), line_y + Inches(0.15),
                      Inches(0.03), Inches(0.45), fill_color=color)


def _render_process_flow(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "流程"))
    _add_footer(slide)

    steps: list = content.get("steps") or []
    steps = steps[:6]
    n = len(steps)
    if n == 0:
        return

    box_w = Inches(1.9)
    arrow_w = Inches(0.35)
    total_w = n * box_w + (n - 1) * arrow_w
    start_x = (SLIDE_W - total_w) / 2
    box_y = Inches(1.5)
    box_h = Inches(3.8)

    for i, step in enumerate(steps):
        x = start_x + i * (box_w + arrow_w)
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]

        _add_rect(slide, x, box_y, box_w, box_h, fill_color=color)

        # Step number
        _add_textbox(
            slide, x, box_y + Inches(0.2), box_w, Inches(0.6),
            text=str(i + 1), font_size=28, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Separator line
        _add_rect(
            slide, x + Inches(0.2), box_y + Inches(0.9),
            box_w - Inches(0.4), Inches(0.04),
            fill_color=RGBColor(0xFF, 0xFF, 0xFF),
        )
        # Title
        step_title = _safe(step.get("title") if isinstance(step, dict) else step)
        _add_textbox(
            slide, x + Inches(0.1), box_y + Inches(1.05),
            box_w - Inches(0.2), Inches(0.9),
            text=step_title, font_size=14, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Description
        step_desc = _safe(step.get("description") if isinstance(step, dict) else "")
        if step_desc:
            _add_textbox(
                slide, x + Inches(0.1), box_y + Inches(2.05),
                box_w - Inches(0.2), Inches(1.6),
                text=step_desc, font_size=11,
                color=C_WHITE, align=PP_ALIGN.CENTER,
            )

        # Arrow between steps
        if i < n - 1:
            arrow_x = x + box_w
            _add_textbox(
                slide, arrow_x, box_y + box_h / 2 - Inches(0.25),
                arrow_w, Inches(0.5),
                text="▶", font_size=20, color=C_MID_BLUE, align=PP_ALIGN.CENTER,
            )


def _render_comparison(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "对比"))
    _add_footer(slide)

    columns: list = content.get("columns") or []
    columns = columns[:3]
    n = len(columns)
    if n == 0:
        return

    gap = Inches(0.2)
    total_gap = (n + 1) * gap
    col_w = (SLIDE_W - total_gap) / n
    start_y = Inches(1.05)
    col_h = SLIDE_H - start_y - Inches(0.35)

    for i, col in enumerate(columns):
        x = gap + i * (col_w + gap)
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        header = _safe(col.get("header") if isinstance(col, dict) else col)
        points: list = col.get("points", []) if isinstance(col, dict) else []

        # Header bar
        _add_rect(slide, x, start_y, col_w, Inches(0.55), fill_color=color)
        _add_textbox(
            slide, x + Inches(0.1), start_y + Inches(0.04),
            col_w - Inches(0.2), Inches(0.5),
            text=header, font_size=16, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Body
        _add_rect(slide, x, start_y + Inches(0.55), col_w,
                  col_h - Inches(0.55), fill_color=C_LIGHT_GRAY)
        for j, point in enumerate(points[:8]):
            py = start_y + Inches(0.65) + j * Inches(0.68)
            _add_textbox(
                slide, x + Inches(0.15), py,
                col_w - Inches(0.3), Inches(0.65),
                text=f"• {_safe(point)}", font_size=12, color=C_DARK_GRAY,
            )


def _render_pyramid(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "金字塔"))
    _add_footer(slide)

    levels: list = content.get("levels") or []
    levels = levels[:5]
    n = len(levels)
    if n == 0:
        return

    # Draw pyramid as stacked trapezoids
    pyr_top_y = Inches(1.2)
    pyr_h = Inches(5.8)
    pyr_max_w = Inches(7.0)
    pyr_center_x = Inches(5.0)
    level_h = pyr_h / n

    for i, level in enumerate(levels):
        # Width proportional to position (top = narrowest)
        frac = (i + 1) / n
        w = pyr_max_w * frac
        x = pyr_center_x - w / 2
        y = pyr_top_y + i * level_h
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]

        _add_rect(slide, x, y, w, level_h - Inches(0.04), fill_color=color)

        label = _safe(level.get("label") if isinstance(level, dict) else level)
        desc = _safe(level.get("description") if isinstance(level, dict) else "")

        # Label inside pyramid
        _add_textbox(
            slide, x + Inches(0.1), y + (level_h - Inches(0.35)) / 2,
            w - Inches(0.2), Inches(0.35),
            text=label, font_size=14, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Description on right side
        if desc:
            _add_textbox(
                slide, pyr_center_x + pyr_max_w / 2 + Inches(0.3),
                y + (level_h - Inches(0.6)) / 2,
                Inches(4.5), Inches(0.6),
                text=desc, font_size=12, color=C_DARK_GRAY,
            )


def _render_matrix_2x2(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "四象限矩阵"))
    _add_footer(slide)

    quadrants = content.get("quadrants") or {}
    x_label = _safe(content.get("x_axis_label"), "X 轴")
    y_label = _safe(content.get("y_axis_label"), "Y 轴")
    x_low = _safe(content.get("x_low"), "低")
    x_high = _safe(content.get("x_high"), "高")
    y_low = _safe(content.get("y_low"), "低")
    y_high = _safe(content.get("y_high"), "高")

    mat_x = Inches(1.5)
    mat_y = Inches(1.1)
    mat_w = Inches(9.5)
    mat_h = Inches(5.9)
    half_w = mat_w / 2
    half_h = mat_h / 2

    quad_data = [
        ("top_left", mat_x, mat_y, ACCENT_COLORS[2]),
        ("top_right", mat_x + half_w, mat_y, ACCENT_COLORS[0]),
        ("bottom_left", mat_x, mat_y + half_h, ACCENT_COLORS[3]),
        ("bottom_right", mat_x + half_w, mat_y + half_h, ACCENT_COLORS[1]),
    ]

    for key, qx, qy, color in quad_data:
        q = quadrants.get(key) or {}
        q_title = _safe(q.get("title") if isinstance(q, dict) else q)
        q_items = q.get("items", []) if isinstance(q, dict) else []

        _add_rect(slide, qx + Inches(0.02), qy + Inches(0.02),
                  half_w - Inches(0.04), half_h - Inches(0.04), fill_color=color)
        _add_textbox(
            slide, qx + Inches(0.15), qy + Inches(0.1),
            half_w - Inches(0.3), Inches(0.45),
            text=q_title, font_size=14, bold=True,
            color=C_WHITE, align=PP_ALIGN.LEFT,
        )
        for j, item in enumerate(q_items[:4]):
            _add_textbox(
                slide, qx + Inches(0.2), qy + Inches(0.65) + j * Inches(0.5),
                half_w - Inches(0.4), Inches(0.48),
                text=f"• {_safe(item)}", font_size=11, color=C_WHITE,
            )

    # Axis labels
    _add_textbox(
        slide, mat_x, mat_y + mat_h + Inches(0.1), mat_w, Inches(0.35),
        text=f"← {x_low}  {x_label}  {x_high} →",
        font_size=12, color=C_DARK_GRAY, align=PP_ALIGN.CENTER,
    )
    _add_textbox(
        slide, Inches(0.05), mat_y, Inches(1.3), mat_h,
        text=f"↑ {y_high}\n\n{y_label}\n\n{y_low} ↓",
        font_size=11, color=C_DARK_GRAY, align=PP_ALIGN.CENTER,
    )


def _render_conclusion(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_WHITE)
    _add_header_bar(slide, _safe(content.get("title"), "核心结论"))
    _add_footer(slide)

    takeaways: list = content.get("takeaways") or []
    takeaways = takeaways[:5]

    for i, item in enumerate(takeaways):
        y = Inches(1.15) + i * Inches(1.1)
        color = ACCENT_COLORS[i % len(ACCENT_COLORS)]

        headline = _safe(item.get("headline") if isinstance(item, dict) else item)
        detail = _safe(item.get("detail") if isinstance(item, dict) else "")

        # Number box
        _add_rect(slide, Inches(0.5), y, Inches(0.55), Inches(0.55), fill_color=color)
        _add_textbox(
            slide, Inches(0.5), y + Inches(0.02), Inches(0.55), Inches(0.5),
            text=str(i + 1), font_size=18, bold=True,
            color=C_WHITE, align=PP_ALIGN.CENTER,
        )
        # Headline
        _add_textbox(
            slide, Inches(1.2), y, Inches(11.2), Inches(0.5),
            text=headline, font_size=18, bold=True, color=C_DARK_BLUE,
        )
        # Detail
        if detail:
            _add_textbox(
                slide, Inches(1.2), y + Inches(0.5), Inches(11.2), Inches(0.5),
                text=detail, font_size=13, color=C_DARK_GRAY,
            )


def _render_thank_you(prs: Presentation, content: dict):
    slide = _blank_slide(prs)
    _fill_bg(slide, C_DARK_BLUE)

    _add_rect(slide, 0, 0, Inches(0.5), SLIDE_H, fill_color=C_ORANGE)
    _add_rect(slide, 0, SLIDE_H - Inches(0.8), SLIDE_W, Inches(0.8), fill_color=C_ORANGE)

    message = _safe(content.get("message"), "Thank You")
    _add_textbox(
        slide, Inches(1.0), Inches(2.5), Inches(11.0), Inches(1.5),
        text=message, font_size=48, bold=True,
        color=C_WHITE, align=PP_ALIGN.CENTER, font_name=FONT_TITLE,
    )

    contact = _safe(content.get("contact"))
    if contact:
        _add_textbox(
            slide, Inches(1.0), Inches(4.2), Inches(11.0), Inches(0.8),
            text=contact, font_size=18, color=C_LIGHT_BLUE,
            align=PP_ALIGN.CENTER,
        )


# ── Renderer map ──────────────────────────────────────────────────────────────

_RENDERERS = {
    "title_slide": _render_title_slide,
    "agenda": _render_agenda,
    "section_divider": _render_section_divider,
    "content_bullets": _render_content_bullets,
    "key_metrics": _render_key_metrics,
    "timeline": _render_timeline,
    "process_flow": _render_process_flow,
    "comparison": _render_comparison,
    "pyramid": _render_pyramid,
    "matrix_2x2": _render_matrix_2x2,
    "conclusion": _render_conclusion,
    "thank_you": _render_thank_you,
}


# ── Public entry-point ────────────────────────────────────────────────────────

def build_pptx(plan: dict) -> bytes:
    """
    Render all slides defined in *plan* and return the raw .pptx bytes.
    Unknown template IDs fall back to a content_bullets slide.
    """
    prs = _new_prs()

    for slide_def in plan.get("slides", []):
        template_id: str = slide_def.get("template", "content_bullets")
        slide_content: dict = slide_def.get("content") or {}
        renderer = _RENDERERS.get(template_id, _render_content_bullets)
        renderer(prs, slide_content)

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.read()
