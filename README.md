# Logene Auto PPTX

> AI 驱动的专业演示文稿生成器 — 上传资料 + 描述需求，自动生成风格统一的 .pptx 文件。

## 功能特性

- �� **GPT-4o 驱动**：AI 分析内容，自动选择最合适的幻灯片模板
- 📄 **多格式资料支持**：PDF、DOCX、TXT、XLSX
- 🗂️ **12 种专业模板**：封面、议程、时间轴、金字塔、四象限矩阵、流程图、对比分析、关键指标、文字要点、章节分隔、结论、感谢页
- 🎨 **品牌统一**：所有幻灯片共享一套配色方案，下限高
- ⚡ **渐进式披露**：模板设计借鉴 ThinkCell 思路，内容结构化展示

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 19 + TypeScript + Vite + Tailwind CSS v4 |
| 后端 | Python 3.12 + FastAPI + Uvicorn |
| AI | OpenAI GPT-4o (JSON mode) |
| PPT 生成 | python-pptx |
| 文档解析 | pdfplumber · python-docx · openpyxl |

## 快速开始

### 1. 克隆与配置

```bash
git clone https://github.com/alexhan1012/Logene_Auto_PPTX.git
cd Logene_Auto_PPTX
```

### 2. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 配置 OpenAI API Key
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 启动后端（默认端口 8000）
uvicorn main:app --reload
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev     # 开发模式（含热重载，默认端口 5173）
```

访问 [http://localhost:5173](http://localhost:5173) 即可使用。

> **提示**：Vite 开发服务器已配置 `/api` 代理，会自动转发到后端 8000 端口。

### 4. 生产构建

```bash
cd frontend && npm run build   # 输出到 frontend/dist/
# 可将 dist/ 通过 FastAPI StaticFiles 或 Nginx 对外提供
```

## 项目结构

```
Logene_Auto_PPTX/
├── backend/
│   ├── main.py                    # FastAPI 应用入口
│   ├── requirements.txt
│   ├── .env.example
│   └── services/
│       ├── ai_service.py          # OpenAI 调用 & 演示文稿结构规划
│       ├── document_parser.py     # 多格式文档文字提取
│       ├── pptx_generator.py      # python-pptx 渲染各模板
│       └── template_registry.py   # 12 种模板定义 & AI 提示词描述
└── frontend/
    └── src/
        ├── App.tsx                # 主界面
        ├── api/client.ts          # API 请求封装
        ├── components/
        │   ├── FileUpload.tsx     # 拖拽上传组件
        │   ├── PromptInput.tsx    # 提示词输入 & 示例
        │   ├── GenerateButton.tsx # 生成按钮
        │   ├── StatusPanel.tsx    # 进度 & 下载面板
        │   └── TemplateGallery.tsx# 模板展示
        └── types/index.ts         # TypeScript 类型
```

## API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/templates` | 获取所有可用模板列表 |
| POST | `/api/generate` | 生成 PPTX（`multipart/form-data`：`prompt` + 可选 `files[]`） |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OPENAI_API_KEY` | — | **必填**，OpenAI API 密钥 |
| `OPENAI_MODEL` | `gpt-4o` | 使用的模型，也支持 `gpt-4-turbo` |
| `MAX_UPLOAD_MB` | `20` | 单文件最大上传大小（MB） |
| `CORS_ORIGINS` | `http://localhost:5173,...` | 允许的前端来源 |

## 许可

MIT
