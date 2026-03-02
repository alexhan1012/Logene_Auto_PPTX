import { useState, useEffect, useRef } from 'react'
import { Presentation, ChevronDown, ChevronUp, Info, LayoutTemplate, Wand2 } from 'lucide-react'
import FileUpload from './components/FileUpload'
import PromptInput from './components/PromptInput'
import GenerateButton from './components/GenerateButton'
import StatusPanel from './components/StatusPanel'
import TemplateGallery from './components/TemplateGallery'
import TemplateManagerPage from './pages/TemplateManagerPage'
import { fetchTemplates, generatePresentation, fetchCustomTemplates, type Template } from './api/client'
import type { GenerationState, CustomTemplate } from './types'

const INITIAL_STATE: GenerationState = {
  status: 'idle',
  message: '',
  downloadUrl: null,
  filename: null,
}

type ActiveTab = 'generate' | 'templates'

export default function App() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('generate')
  const [prompt, setPrompt] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [templates, setTemplates] = useState<Template[]>([])
  const [customTemplates, setCustomTemplates] = useState<CustomTemplate[]>([])
  const [selectedCustomTemplateId, setSelectedCustomTemplateId] = useState<string | null>(null)
  const [showTemplates, setShowTemplates] = useState(false)
  const [genState, setGenState] = useState<GenerationState>(INITIAL_STATE)
  const downloadRef = useRef<HTMLAnchorElement>(null)

  useEffect(() => {
    fetchTemplates()
      .then(setTemplates)
      .catch(() => {/* templates are informational only */})
    fetchCustomTemplates()
      .then(setCustomTemplates)
      .catch(() => {/* non-critical */})
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
      }, selectedCustomTemplateId)

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
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Presentation size={28} className="shrink-0" />
            <div>
              <h1 className="text-xl font-bold leading-tight">Logene Auto PPTX</h1>
              <p className="text-xs text-blue-200">AI 驱动的专业演示文稿生成器</p>
            </div>
          </div>
          {/* Navigation tabs */}
          <nav className="flex gap-1 bg-white/10 rounded-xl p-1">
            <button
              onClick={() => setActiveTab('generate')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-white text-blue-800'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              <Wand2 size={16} />
              生成 PPT
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'templates'
                  ? 'bg-white text-blue-800'
                  : 'text-white/80 hover:text-white hover:bg-white/10'
              }`}
            >
              <LayoutTemplate size={16} />
              模板管理
            </button>
          </nav>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {activeTab === 'templates' ? (
          <TemplateManagerPage />
        ) : (
          <div className="space-y-8">
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

                {/* Custom template selector */}
                {customTemplates.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 space-y-3">
                    <h2 className="font-semibold text-gray-800 text-base">🎨 选择视觉模板（可选）</h2>
                    <p className="text-xs text-gray-500">
                      选择一个自定义模板作为视觉风格基础，AI 将使用其设计主题生成演示文稿。
                    </p>
                    <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
                      <button
                        type="button"
                        onClick={() => setSelectedCustomTemplateId(null)}
                        className={`text-left p-3 rounded-xl border text-sm transition-colors ${
                          selectedCustomTemplateId === null
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300 text-gray-600'
                        }`}
                      >
                        <span className="font-medium">默认风格</span>
                        <p className="text-xs text-gray-400 mt-0.5">使用内置模板</p>
                      </button>
                      {customTemplates.map((t) => (
                        <button
                          key={t.id}
                          type="button"
                          onClick={() =>
                            setSelectedCustomTemplateId(
                              selectedCustomTemplateId === t.id ? null : t.id,
                            )
                          }
                          className={`text-left p-3 rounded-xl border text-sm transition-colors ${
                            selectedCustomTemplateId === t.id
                              ? 'border-blue-500 bg-blue-50 text-blue-700'
                              : 'border-gray-200 hover:border-gray-300 text-gray-600'
                          }`}
                        >
                          <span className="font-medium truncate block">{t.name}</span>
                          <p className="text-xs text-gray-400 mt-0.5 truncate">{t.category}</p>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

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
          </div>
        )}
      </main>

      {/* eslint-disable-next-line jsx-a11y/anchor-has-content */}
      <a ref={downloadRef} className="hidden" aria-hidden="true" />
    </div>
  )
}

