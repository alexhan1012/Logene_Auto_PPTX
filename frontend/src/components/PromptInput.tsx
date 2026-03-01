interface PromptInputProps {
  value: string
  onChange: (val: string) => void
}

const EXAMPLES = [
  '制作一份关于公司2024年年度总结的PPT，包括业绩回顾、团队亮点和2025年规划',
  '为新产品发布会制作演示文稿，突出产品特性、市场定位和竞品对比',
  '制作一份项目可行性分析报告PPT，包含市场分析、财务预测和风险评估',
]

export default function PromptInput({ value, onChange }: PromptInputProps) {
  return (
    <div className="space-y-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        placeholder="描述你想要的演示文稿内容和风格，AI 将自动选择合适的模板并填充内容…"
        className="w-full border border-gray-300 rounded-xl px-4 py-3 text-sm text-gray-800
          placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500
          focus:border-transparent resize-none transition-shadow"
      />
      <div>
        <p className="text-xs text-gray-500 mb-1">示例提示词：</p>
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => onChange(ex)}
              className="text-xs text-blue-600 bg-blue-50 hover:bg-blue-100 px-2 py-1
                rounded-lg border border-blue-200 transition-colors text-left"
            >
              {ex.slice(0, 28)}…
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
