import { useState, useEffect } from 'react'
import { Upload, Trash2, Pencil, X, Check, FolderOpen, FileText, Plus } from 'lucide-react'
import type { CustomTemplate } from '../types'
import {
  fetchCustomTemplates,
  fetchCustomTemplateCategories,
  uploadCustomTemplate,
  updateCustomTemplate,
  deleteCustomTemplate,
} from '../api/client'

// ── Upload Modal ──────────────────────────────────────────────────────────────

interface UploadModalProps {
  onClose: () => void
  onUploaded: (t: CustomTemplate) => void
  existingCategories: string[]
}

function UploadModal({ onClose, onUploaded, existingCategories }: UploadModalProps) {
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !name.trim() || !category.trim()) return
    setLoading(true)
    setError('')
    try {
      const record = await uploadCustomTemplate(file, name.trim(), category.trim(), description.trim())
      onUploaded(record)
      onClose()
    } catch {
      setError('上传失败，请检查文件格式或重试。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-800">上传 PPT 模板</h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-100 text-gray-500"
            aria-label="关闭"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* File picker */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              PPTX 文件 <span className="text-red-500">*</span>
            </label>
            <label className="flex items-center gap-2 border-2 border-dashed border-gray-300 rounded-xl p-4 cursor-pointer hover:border-blue-400 transition-colors">
              <Upload size={20} className="text-gray-400 shrink-0" />
              <span className="text-sm text-gray-500 truncate">
                {file ? file.name : '点击选择 .pptx 文件'}
              </span>
              <input
                type="file"
                accept=".pptx"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0] ?? null
                  setFile(f)
                  if (f && !name) setName(f.name.replace(/\.pptx$/i, ''))
                }}
              />
            </label>
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              模板名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例如：科技公司介绍 - 单标题版"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              分类 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              list="category-suggestions"
              placeholder="例如：商业报告、产品发布、教育培训"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-400"
              required
            />
            {existingCategories.length > 0 && (
              <datalist id="category-suggestions">
                {existingCategories.map((c) => (
                  <option key={c} value={c} />
                ))}
              </datalist>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              描述（帮助 AI 选择合适的模板）
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="例如：适用于科技类产品发布，单标题设计，简洁现代风格"
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm
                text-gray-700 hover:bg-gray-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading || !file || !name.trim() || !category.trim()}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium
                hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? '上传中…' : '上传'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Inline Edit Row ───────────────────────────────────────────────────────────

interface EditState {
  name: string
  category: string
  description: string
}

interface TemplateCardProps {
  template: CustomTemplate
  onDelete: (id: string) => void
  onUpdated: (t: CustomTemplate) => void
}

function TemplateCard({ template, onDelete, onUpdated }: TemplateCardProps) {
  const [editing, setEditing] = useState(false)
  const [editState, setEditState] = useState<EditState>({
    name: template.name,
    category: template.category,
    description: template.description,
  })
  const [saving, setSaving] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      const updated = await updateCustomTemplate(template.id, editState)
      onUpdated(updated)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirmDelete) { setConfirmDelete(true); return }
    await deleteCustomTemplate(template.id)
    onDelete(template.id)
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow">
      {editing ? (
        <div className="space-y-2">
          <input
            className="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            value={editState.name}
            onChange={(e) => setEditState((s) => ({ ...s, name: e.target.value }))}
            placeholder="名称"
          />
          <input
            className="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
            value={editState.category}
            onChange={(e) => setEditState((s) => ({ ...s, category: e.target.value }))}
            placeholder="分类"
          />
          <textarea
            className="w-full border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            value={editState.description}
            onChange={(e) => setEditState((s) => ({ ...s, description: e.target.value }))}
            placeholder="描述"
            rows={2}
          />
          <div className="flex gap-2 justify-end">
            <button
              onClick={() => setEditing(false)}
              className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100"
              aria-label="取消"
            >
              <X size={16} />
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="p-1.5 rounded-lg text-green-600 hover:bg-green-50 disabled:opacity-50"
              aria-label="保存"
            >
              <Check size={16} />
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2 min-w-0">
              <FileText size={18} className="text-blue-500 shrink-0" />
              <p className="text-sm font-semibold text-gray-800 truncate">{template.name}</p>
            </div>
            <div className="flex gap-1 shrink-0">
              <button
                onClick={() => setEditing(true)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                aria-label="编辑"
              >
                <Pencil size={14} />
              </button>
              <button
                onClick={handleDelete}
                className={`p-1.5 rounded-lg transition-colors ${
                  confirmDelete
                    ? 'text-white bg-red-500 hover:bg-red-600'
                    : 'text-gray-400 hover:text-red-600 hover:bg-red-50'
                }`}
                aria-label={confirmDelete ? '确认删除' : '删除'}
                onBlur={() => setConfirmDelete(false)}
              >
                <Trash2 size={14} />
              </button>
            </div>
          </div>
          <span className="inline-block text-xs bg-blue-100 text-blue-700 rounded-full px-2 py-0.5 mb-1">
            {template.category}
          </span>
          <p className="text-xs text-gray-500 line-clamp-2">{template.description || '暂无描述'}</p>
          <p className="text-xs text-gray-400 mt-2">
            {template.slide_count} 张幻灯片 · {template.filename}
          </p>
          {confirmDelete && (
            <p className="text-xs text-red-600 mt-1">再次点击删除按钮以确认删除</p>
          )}
        </>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function TemplateManagerPage() {
  const [templates, setTemplates] = useState<CustomTemplate[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [showUpload, setShowUpload] = useState(false)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [tmpl, cats] = await Promise.all([
        fetchCustomTemplates(),
        fetchCustomTemplateCategories(),
      ])
      setTemplates(tmpl)
      setCategories(cats)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const filtered = activeCategory
    ? templates.filter((t) => t.category === activeCategory)
    : templates

  const handleUploaded = (t: CustomTemplate) => {
    setTemplates((prev) => [...prev, t])
    if (!categories.includes(t.category)) {
      setCategories((prev) => [...prev, t.category].sort())
    }
  }

  const handleDelete = (id: string) => {
    setTemplates((prev) => {
      const next = prev.filter((t) => t.id !== id)
      const remaining = new Set(next.map((t) => t.category))
      setCategories([...remaining].sort())
      if (activeCategory && !remaining.has(activeCategory)) {
        setActiveCategory(null)
      }
      return next
    })
  }

  const handleUpdated = (updated: CustomTemplate) => {
    setTemplates((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
    const allCats = new Set(
      templates.map((t) => (t.id === updated.id ? updated.category : t.category)),
    )
    setCategories([...allCats].sort())
  }

  return (
    <div className="space-y-6">
      {/* Header row */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-gray-800">PPT 模板库</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            上传自定义 PPT 模板，AI 生成时将自动从中选择最合适的视觉风格。
          </p>
        </div>
        <button
          onClick={() => setShowUpload(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl
            text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm"
        >
          <Plus size={16} />
          上传模板
        </button>
      </div>

      {/* Category filter tabs */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setActiveCategory(null)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              activeCategory === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            全部（{templates.length}）
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat === activeCategory ? null : cat)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                activeCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <FolderOpen size={13} />
              {cat}（{templates.filter((t) => t.category === cat).length}）
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="text-center py-16 text-gray-400">加载中…</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-gray-300">
          <Upload size={36} className="mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500 font-medium">
            {templates.length === 0 ? '还没有自定义模板' : '该分类暂无模板'}
          </p>
          <p className="text-sm text-gray-400 mt-1">
            点击右上角"上传模板"按钮，添加你的 PPT 模板文件
          </p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((t) => (
            <TemplateCard
              key={t.id}
              template={t}
              onDelete={handleDelete}
              onUpdated={handleUpdated}
            />
          ))}
        </div>
      )}

      {/* Upload modal */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUploaded={handleUploaded}
          existingCategories={categories}
        />
      )}
    </div>
  )
}
