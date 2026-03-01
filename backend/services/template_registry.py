"""
Template registry – defines every available slide template, including
the description used in the AI system-prompt and the content schema.
"""
from __future__ import annotations

TEMPLATES: list[dict] = [
    {
        "id": "title_slide",
        "name": "封面页 (Title Slide)",
        "description": (
            "演示文稿的第一页封面，包含大标题和副标题/日期。"
            "每个演示文稿只使用一次，放在最开头。"
        ),
        "content_schema": {
            "title": "string – 主标题",
            "subtitle": "string – 副标题或日期，可选",
        },
    },
    {
        "id": "agenda",
        "name": "目录/议程页 (Agenda)",
        "description": (
            "列出演示文稿的主要章节或议题，通常紧跟封面页。"
            "每个演示文稿只使用一次。"
        ),
        "content_schema": {
            "title": "string – 如 '议程' 或 '目录'",
            "items": "array of string – 各章节标题，3-6 项",
        },
    },
    {
        "id": "section_divider",
        "name": "章节分隔页 (Section Divider)",
        "description": (
            "章节过渡页，用于宣告新章节的开始，背景为纯色，"
            "突出显示章节标题。"
        ),
        "content_schema": {
            "section_number": "string – 如 '01' / '02'",
            "section_title": "string – 章节大标题",
            "section_subtitle": "string – 简短描述，可选",
        },
    },
    {
        "id": "content_bullets",
        "name": "文字要点页 (Content / Bullets)",
        "description": (
            "标准内容页：左上角有幻灯片标题，下方是 4-6 条要点。"
            "适合描述、背景介绍、观点陈述等纯文字内容。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "bullets": "array of string – 要点，4-6 条",
        },
    },
    {
        "id": "key_metrics",
        "name": "关键指标页 (Key Metrics)",
        "description": (
            "突出展示 3-6 个重要数字/指标，每个指标包含数值和说明标签。"
            "适合财务摘要、KPI 展示、统计数据亮点等。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "metrics": "array of {value: string, label: string, trend: '↑'|'↓'|'' optional}",
        },
    },
    {
        "id": "timeline",
        "name": "时间轴页 (Timeline)",
        "description": (
            "水平时间轴，按时间顺序排列事件/里程碑。"
            "适合历史回顾、项目路线图、公司发展历程等。"
            "每条事件包含时间标签和简短描述（建议 3-6 个事件）。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "events": "array of {date: string, title: string, description: string optional}",
        },
    },
    {
        "id": "process_flow",
        "name": "流程图页 (Process Flow)",
        "description": (
            "水平流程图，显示步骤之间的顺序关系，适合工作流程、方法论、"
            "执行计划等。建议 3-6 个步骤，每步有编号、标题和简短说明。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "steps": "array of {title: string, description: string}",
        },
    },
    {
        "id": "comparison",
        "name": "对比页 (Comparison)",
        "description": (
            "并排比较 2-3 个选项/方案/对象，每列有标题和多条要点。"
            "适合产品对比、方案评估、竞品分析等。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "columns": "array of {header: string, points: array of string} – 2 或 3 列",
        },
    },
    {
        "id": "pyramid",
        "name": "金字塔页 (Pyramid)",
        "description": (
            "三角形金字塔结构，从上到下（或从下到上）展示层级关系，"
            "适合优先级排序、需求层次、战略层级、价值主张等。"
            "建议 3-5 层，每层有标签和简短描述。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "levels": "array of {label: string, description: string optional} – 从顶层到底层",
        },
    },
    {
        "id": "matrix_2x2",
        "name": "四象限矩阵页 (2×2 Matrix)",
        "description": (
            "经典四象限矩阵（如 BCG 矩阵、艾森豪威尔矩阵），"
            "X 轴和 Y 轴各有两个极值，四个象限各有标题和要点。"
            "适合战略分析、优先级排序、机会评估等。"
        ),
        "content_schema": {
            "title": "string – 幻灯片标题",
            "x_axis_label": "string – X 轴标签",
            "y_axis_label": "string – Y 轴标签",
            "x_low": "string",
            "x_high": "string",
            "y_low": "string",
            "y_high": "string",
            "quadrants": "{top_left, top_right, bottom_left, bottom_right}: {title: string, items: array of string}",
        },
    },
    {
        "id": "conclusion",
        "name": "总结/结论页 (Conclusion)",
        "description": (
            "演示文稿结尾，列出 3-5 条关键结论或行动建议。"
            "每个演示文稿只使用一次，放在最后（感谢页之前）。"
        ),
        "content_schema": {
            "title": "string – 如 '核心结论' 或 '下一步行动'",
            "takeaways": "array of {headline: string, detail: string optional} – 3-5 条",
        },
    },
    {
        "id": "thank_you",
        "name": "感谢页 (Thank You)",
        "description": (
            "演示文稿最后一页，包含感谢语和联系方式。"
            "每个演示文稿只使用一次，放在最后。"
        ),
        "content_schema": {
            "message": "string – 如 'Thank You' 或 '谢谢'",
            "contact": "string – 联系信息，可选",
        },
    },
]

TEMPLATE_MAP: dict[str, dict] = {t["id"]: t for t in TEMPLATES}
