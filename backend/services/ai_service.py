"""
AI Service – calls OpenAI or Aliyun Bailian to turn the user prompt + document text
into a structured presentation plan (list of slides with template IDs
and content fields).
"""
from __future__ import annotations

import json
import os
import re

from openai import AsyncOpenAI

from services.template_registry import TEMPLATES

# ── Configure API provider ──────────────────────────────────────────
_PROVIDER = os.getenv("AI_PROVIDER", "aliyun").lower()
_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

if _PROVIDER == "aliyun":
    _BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    _MODEL = os.getenv("OPENAI_MODEL", "qwen-long")
else:
    _BASE_URL = "https://api.openai.com/v1"
    _MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

_client = AsyncOpenAI(
    api_key=_API_KEY,
    base_url=_BASE_URL,
)

# ── Build the template catalogue description once ───────────────────────────
_TEMPLATE_CATALOGUE = "\n\n".join(
    f"### {t['id']}\n"
    f"**名称**: {t['name']}\n"
    f"**用途**: {t['description']}\n"
    f"**内容字段 (JSON schema)**:\n```\n{json.dumps(t['content_schema'], ensure_ascii=False, indent=2)}\n```"
    for t in TEMPLATES
)

_SYSTEM_PROMPT = f"""
你是一名专业的商业演示文稿设计师和内容策略师。
你的任务是根据用户需求和参考资料，规划并生成一份高质量 PowerPoint 演示文稿的结构和内容。

## 可用幻灯片模板

以下是所有可用的幻灯片模板，每份演示文稿仅从这些模板中选择：

{_TEMPLATE_CATALOGUE}

## 输出要求

请输出**严格合法的 JSON**，格式如下（不要包含任何注释或多余文字）：

```json
{{
  "title": "演示文稿标题",
  "slides": [
    {{
      "template": "<template_id>",
      "content": {{ ... }}  // 字段必须与该模板的 content_schema 完全对应
    }}
  ]
}}
```

## 设计原则

1. **每份演示文稿必须以 title_slide 开头，以 thank_you 结尾**。
2. 根据内容复杂度，合理安排 6-16 张幻灯片。
3. 尽量选择最贴合内容形式的模板（数据→key_metrics，流程→process_flow，对比→comparison，等）。
4. 内容语言与用户输入语言保持一致（中文输入则用中文，英文输入则用英文）。
5. 每张幻灯片内容务必充实、具体，避免使用"请参考资料"等占位文字。
6. **只输出 JSON，不输出任何额外文字或 markdown 代码块标记**。
"""


async def generate_presentation_plan(
    user_prompt: str,
    document_text: str,
) -> dict:
    """
    Call OpenAI and return the parsed presentation plan dict.
    Raises ValueError if the response cannot be parsed.
    """
    user_message = f"## 用户需求\n{user_prompt}"
    if document_text.strip():
        # Truncate to avoid hitting context limits
        truncated = document_text[:12000]
        user_message += f"\n\n## 参考资料\n{truncated}"

    response = await _client.chat.completions.create(
        model=_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    raw_json = response.choices[0].message.content or ""
    try:
        plan = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        # Attempt to extract JSON block if model wrapped it in markdown
        match = re.search(r"\{.*\}", raw_json, re.DOTALL)
        if match:
            plan = json.loads(match.group())
        else:
            raise ValueError(f"AI 返回内容无法解析为 JSON: {exc}\n原始内容: {raw_json[:500]}")

    _validate_plan(plan)
    return plan


def _validate_plan(plan: dict) -> None:
    """Basic structural validation – raises ValueError on failure."""
    valid_ids = {t["id"] for t in TEMPLATES}
    if not isinstance(plan, dict):
        raise ValueError("顶层结构必须是对象")
    if "slides" not in plan or not isinstance(plan["slides"], list):
        raise ValueError("缺少 'slides' 列表")
    for i, slide in enumerate(plan["slides"]):
        if slide.get("template") not in valid_ids:
            raise ValueError(
                f"第 {i+1} 张幻灯片使用了未知模板: '{slide.get('template')}'"
            )
