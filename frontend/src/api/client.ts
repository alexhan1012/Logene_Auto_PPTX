import axios from 'axios'
import type { CustomTemplate } from '../types'

export interface Template {
  id: string
  name: string
  description: string
  content_schema: Record<string, string>
}

export async function fetchTemplates(): Promise<Template[]> {
  const { data } = await axios.get('/api/templates')
  return data.templates as Template[]
}

export async function generatePresentation(
  prompt: string,
  files: File[],
  onProgress?: (msg: string) => void,
  customTemplateId?: string | null,
): Promise<Blob> {
  const form = new FormData()
  form.append('prompt', prompt)
  for (const f of files) {
    form.append('files', f)
  }
  if (customTemplateId) {
    form.append('custom_template_id', customTemplateId)
  }
  onProgress?.('正在发送请求…')
  const response = await axios.post('/api/generate', form, {
    responseType: 'blob',
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && e.total > 0) {
        const pct = Math.round((e.loaded / e.total) * 100)
        onProgress?.(`上传中 ${pct}%…`)
      }
    },
  })
  return response.data as Blob
}

// ── Custom Template API ───────────────────────────────────────────────────────

export async function fetchCustomTemplates(category?: string): Promise<CustomTemplate[]> {
  const params = category ? { category } : {}
  const { data } = await axios.get('/api/custom-templates', { params })
  return data.templates as CustomTemplate[]
}

export async function fetchCustomTemplateCategories(): Promise<string[]> {
  const { data } = await axios.get('/api/custom-templates/categories')
  return data.categories as string[]
}

export async function uploadCustomTemplate(
  file: File,
  name: string,
  category: string,
  description: string,
): Promise<CustomTemplate> {
  const form = new FormData()
  form.append('file', file)
  form.append('name', name)
  form.append('category', category)
  form.append('description', description)
  const { data } = await axios.post('/api/custom-templates', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data as CustomTemplate
}

export async function updateCustomTemplate(
  id: string,
  updates: { name?: string; category?: string; description?: string },
): Promise<CustomTemplate> {
  const form = new FormData()
  if (updates.name !== undefined) form.append('name', updates.name)
  if (updates.category !== undefined) form.append('category', updates.category)
  if (updates.description !== undefined) form.append('description', updates.description)
  const { data } = await axios.put(`/api/custom-templates/${id}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data as CustomTemplate
}

export async function deleteCustomTemplate(id: string): Promise<void> {
  await axios.delete(`/api/custom-templates/${id}`)
}

