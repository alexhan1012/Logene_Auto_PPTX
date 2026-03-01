import type { Template } from '../api/client'

interface TemplateGalleryProps {
  templates: Template[]
}

const ICONS: Record<string, string> = {
  title_slide: '🎯',
  agenda: '📋',
  section_divider: '📌',
  content_bullets: '📝',
  key_metrics: '📊',
  timeline: '⏱️',
  process_flow: '🔄',
  comparison: '⚖️',
  pyramid: '🔺',
  matrix_2x2: '🧮',
  conclusion: '✅',
  thank_you: '🙏',
}

export default function TemplateGallery({ templates }: TemplateGalleryProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {templates.map((tpl) => (
        <div
          key={tpl.id}
          className="border border-gray-200 rounded-xl p-3 bg-white hover:shadow-md
            transition-shadow cursor-default"
        >
          <div className="text-2xl mb-1">{ICONS[tpl.id] ?? '📄'}</div>
          <p className="text-xs font-semibold text-gray-800 leading-tight">{tpl.name}</p>
          <p className="text-xs text-gray-500 mt-1 line-clamp-2">{tpl.description}</p>
        </div>
      ))}
    </div>
  )
}
