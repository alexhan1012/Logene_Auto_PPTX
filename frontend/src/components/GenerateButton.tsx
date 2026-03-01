import { Loader2, Sparkles } from 'lucide-react'

interface GenerateButtonProps {
  onClick: () => void
  loading: boolean
  disabled: boolean
}

export default function GenerateButton({ onClick, loading, disabled }: GenerateButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className="w-full flex items-center justify-center gap-2 px-6 py-3
        bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold
        rounded-xl shadow-md hover:from-blue-700 hover:to-indigo-700 transition-all
        disabled:opacity-50 disabled:cursor-not-allowed text-base"
    >
      {loading ? (
        <Loader2 size={20} className="animate-spin" />
      ) : (
        <Sparkles size={20} />
      )}
      {loading ? '正在生成…' : '生成 PPT'}
    </button>
  )
}
