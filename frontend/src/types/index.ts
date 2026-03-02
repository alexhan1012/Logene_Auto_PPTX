export type GenerationStatus = 'idle' | 'uploading' | 'generating' | 'done' | 'error'

export interface GenerationState {
  status: GenerationStatus
  message: string
  downloadUrl: string | null
  filename: string | null
}

export interface CustomTemplate {
  id: string
  name: string
  category: string
  description: string
  filename: string
  slide_count: number
  created_at: string
}
