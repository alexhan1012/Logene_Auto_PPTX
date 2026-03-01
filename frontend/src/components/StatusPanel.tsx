import { CheckCircle, XCircle, Download, Loader2 } from 'lucide-react'
import type { GenerationState } from '../types'

interface StatusPanelProps {
  state: GenerationState
  onDownload: () => void
  onReset: () => void
}

const STEP_LABELS = [
  { key: 'uploading', label: '上传资料' },
  { key: 'generating', label: 'AI 分析与生成内容' },
  { key: 'done', label: '渲染 PPTX 文件' },
]

export default function StatusPanel({ state, onDownload, onReset }: StatusPanelProps) {
  if (state.status === 'idle') return null

  const currentIdx =
    state.status === 'uploading'
      ? 0
      : state.status === 'generating'
        ? 1
        : state.status === 'done' || state.status === 'error'
          ? 2
          : 0

  return (
    <div className="mt-6 rounded-xl border border-gray-200 bg-white shadow-sm p-5 space-y-4">
      {/* Step indicators */}
      <div className="flex items-center gap-2">
        {STEP_LABELS.map((step, i) => {
          const isDone = state.status === 'done' || (state.status !== 'error' && i < currentIdx)
          const isCurrent = i === currentIdx && state.status !== 'done' && state.status !== 'error'
          const isError = state.status === 'error' && i === currentIdx

          return (
            <div key={step.key} className="flex items-center gap-1 flex-1">
              <div className="flex items-center gap-1.5">
                {isDone ? (
                  <CheckCircle size={16} className="text-green-500 shrink-0" />
                ) : isError ? (
                  <XCircle size={16} className="text-red-500 shrink-0" />
                ) : isCurrent ? (
                  <Loader2 size={16} className="animate-spin text-blue-500 shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-gray-300 shrink-0" />
                )}
                <span
                  className={`text-xs font-medium ${
                    isDone
                      ? 'text-green-600'
                      : isError
                        ? 'text-red-600'
                        : isCurrent
                          ? 'text-blue-600'
                          : 'text-gray-400'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {i < STEP_LABELS.length - 1 && (
                <div className={`flex-1 h-0.5 mx-1 ${isDone ? 'bg-green-400' : 'bg-gray-200'}`} />
              )}
            </div>
          )
        })}
      </div>

      {/* Message */}
      <p
        className={`text-sm ${
          state.status === 'error' ? 'text-red-600' : 'text-gray-600'
        }`}
      >
        {state.message}
      </p>

      {/* Action buttons */}
      {state.status === 'done' && (
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onDownload}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white
              rounded-lg hover:bg-green-700 transition-colors font-medium text-sm"
          >
            <Download size={16} />
            下载 PPTX
          </button>
          <button
            type="button"
            onClick={onReset}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg
              hover:bg-gray-50 transition-colors text-sm"
          >
            重新生成
          </button>
        </div>
      )}

      {state.status === 'error' && (
        <button
          type="button"
          onClick={onReset}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg
            hover:bg-gray-50 transition-colors text-sm"
        >
          返回重试
        </button>
      )}
    </div>
  )
}
