import axios from 'axios'

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
): Promise<Blob> {
  const form = new FormData()
  form.append('prompt', prompt)
  for (const f of files) {
    form.append('files', f)
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
