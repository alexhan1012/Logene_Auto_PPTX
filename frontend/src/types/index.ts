export type GenerationStatus = 'idle' | 'uploading' | 'generating' | 'done' | 'error'

export interface GenerationState {
  status: GenerationStatus
  message: string
  downloadUrl: string | null
  filename: string | null
}
