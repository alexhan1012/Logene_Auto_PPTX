import { useState, useEffect, useRef } from 'react'
import { Presentation, ChevronDown, ChevronUp, Info } from 'lucide-react'
import FileUpload from './components/FileUpload'
import PromptInput from './components/PromptInput'
import GenerateButton from './components/GenerateButton'
import StatusPanel from './components/StatusPanel'
import TemplateGallery from './components/TemplateGallery'
import { fetchTemplates, generatePresentation, type Template } from './api/client'
import type { GenerationState } from './types'

const INITIAL_STATE: GenerationState = {
  status: 'idle',
  message: '',
  downloadUrl: null,
  filename: null,
}

export default function App() {
  const [prompt, setPrompt] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [templates, setTemplates] = useState<Template[]>([])
  const [showTemplates, setShowTemplates] = useState(false)
  const [genState, setGenState] = useState<GenerationState>(INITIAL_STATE)
  const downloadRef = useRef<HTMLAnchorElement>(null)

  useEffect(() => {
    fetchTemplates()
      .then(setTemplates)
      .catch(() => {/* templates are informational only */})
  }, [])

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    if (genState.downloadUrl) {
      URL.revokeObjectURL(genState.downloadUrl)
    }

    setGenState({ status: 'uploading', message: '正在上传资料…', downloadUrl: null, filename: null })

    try {
      const blob = await generatePresentation(prompt, files, (msg) => {
        setGenState((prev) => ({
          ...prev,
          status: msg.startsWith('上传中') ? 'uploading' : 'generating',
          message: msg,
        }))
      })

      setGenState((prev) => ({ ...prev, status: 'generating', message: 'AI 正在规划演示文稿结构…' }))

      const url = URL.createObjectURL(blob)
      const filename = 'presentation.pptx'

      setGenState({
        status: 'done',
        message: '演示文稿已生成！点击下方按钮下载。',
        downloadUrl: url,
        filename,
      })
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : typeof err === 'object' && err !== null && 'response' in err
            ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ?? '生成失败，请检查 API Key 配置'
            : '生成失败，请稍后重试'
      setGenState({
        status: 'error',
        message: msg,
        downloadUrl: null,
        filename: null,
      })
    }
  }

  const handleDownload = () => {
    if (!genState.downloadUrl || !downloadRef.current) return
    downloadRef.current.href = genState.downloadUrl
    downloadRef.current.download = genState.filename ?? 'presentation.pptx'
    downloadRef.current.click()
  }

  const handleReset = () => {
    if (genState.downloadUrl) URL.revokeObjectURL(genState.downloadUrl)
    setGenState(INITIAL_STATE)
  }

  const isGenerating = genState.status === 'uploading' || genState.status === 'generating'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <header className="bg-gradient-to-r from-[#1F3864] to-[#2E75B6] text-white shadow-lg">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <Presentation size={28} className="shrink-0" />
          <div>
            <h1 className="text-xl font-bold leading-tight">Logene Auto PPTX</h1>
            <p className="text-xs text-blue-200">AI 驱动的专业演示文稿生成器</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        <div className="flex items-start gap-3 bg-blue-50 border border-blue-200 rounded-xl p-4">
          <Info size={18} className="shrink-0 text-blue-600 mt-0.5" />
          <p className="text-sm text-blue-800">
            <strong>使用方式：</strong>输入你的需求，可选择上传参考资料（PDF、Word、Excel 等），
            AI 将自动分析内容、选择合适的幻灯片模板，生成一份结构清晰、风格统一的 PowerPoint 文件。
          </p>
        </div>

        <div className="grid lg:grid-cols-5 gap-6">
          <div className="lg:col-span-3 space-y-5">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-3">
              <h2 className="font-semibold text-gray-800 text-base">📝 描述你的需求</h2>
              <PromptInput value={prompt} onChange={setPrompt} />
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-3">
              <h2 className="font-semibold text-gray-800 text-base">📎 上传参考资料（可选）</h2>
              <FileUpload files={files} onChange={setFiles} />
            </div>

            <GenerateButton
              onClick={handleGenerate}
              loading={isGenerating}
              disabled={!prompt.trim()}
            />

            <StatusPanel state={genState} onDownload={handleDownload} onReset={handleReset} />
          </div>

          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <button
                type="button"
                onClick={() => setShowTemplates((v) => !v)}
                className="w-full flex items-center justify-between text-base font-semibold
                  text-gray-800 hover:text-blue-700 transition-colors"
              >
                <span>🗂️ 可用幻灯片模板（{templates.length} 种）</span>
                {showTemplates ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>

              {showTemplates && templates.length > 0 && (
                <div className="mt-4">
                  <TemplateGallery templates={templates} />
                </div>
              )}

              {!showTemplates && (
                <p className="mt-2 text-xs text-gray-500">
                  AI 会自动从这 {templates.length} 种模板中选择最适合的组合，包括：
                  时间轴、金字塔、四象限矩阵、流程图、对比分析、关键指标等。
                </p>
              )}
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl border border-indigo-100 p-5">
              <h3 className="font-semibold text-indigo-800 mb-3 text-sm">⚡ 工作原理</h3>
              <ol className="space-y-2 text-xs text-indigo-700">
                <li className="flex gap-2">
                  <span className="font-bold shrink-0">1.</span>
                  <span>解析上传的资料，提取文字内容</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold shrink-0">2.</span>
                  <span>GPT-4o 分析需求，规划最优幻灯片结构与内容</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold shrink-0">3.</span>
                  <span>自动选择模板并填充内容，渲染为标准 .pptx 文件</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold shrink-0">4.</span>
                  <span>下载后可在 PowerPoint / WPS 中直接编辑</span>
                </li>
              </ol>
            </div>
          </div>
        </div>
      </main>

      {/* eslint-disable-next-line jsx-a11y/anchor-has-content */}
      <a ref={downloadRef} className="hidden" aria-hidden="true" />
    </div>
  )
}
