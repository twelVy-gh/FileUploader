/**
 * Общие типы для фронтенд приложения.
 */

/** Статус обработки документа */
export type DocumentStatus = 'uploading' | 'indexing' | 'ready' | 'error'

/** Документ (метаданные) */
export interface Document {
  id: string
  file_name: string
  upload_date: string
  status: DocumentStatus
}

/** Ответ при загрузке файла */
export interface DocumentUploadResponse {
  message: string
  document_id: string
  file_name: string
  status: string
}

/** Ответ со списком документов */
export interface DocumentListResponse {
  documents: Document[]
  total: number
}

/** Один элемент результата поиска */
export interface SearchResultItem {
  chunk_id: string
  file_name: string
  page: number | null
  text: string
  score: number
}

/** Ответ на поисковый запрос */
export interface SearchResponse {
  results: SearchResultItem[]
  total: number
  from_item: number
  size: number
}

/** Состояние загружаемого файла (для UI) */
export interface UploadingFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'indexing' | 'ready' | 'error'
  message?: string
  documentId?: string
}