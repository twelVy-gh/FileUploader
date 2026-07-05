/**
 * API клиент для взаимодействия с бэкендом.
 * Использует axios для HTTP запросов.
 */

import axios, { AxiosError } from 'axios'

// Типы данных
export interface Document {
  id: string
  file_name: string
  upload_date: string
  status: 'uploading' | 'indexing' | 'ready' | 'error'
}

export interface DocumentUploadResponse {
  message: string
  document_id: string
  file_name: string
  status: string
}

export interface DocumentListResponse {
  documents: Document[]
  total: number
}

export interface SearchResultItem {
  chunk_id: string
  file_name: string
  page: number | null
  text: string
  score: number
}

export interface SearchResponse {
  results: SearchResultItem[]
  total: number
  from_item: number
  size: number
}

export interface ErrorResponse {
  error: string
  detail: string
}

// Создание экземпляра axios
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Обработка ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response) {
      const message = error.response.data?.detail || 'Произошла ошибка'
      console.error('API Error:', message)
      return Promise.reject(new Error(message))
    }
    return Promise.reject(error)
  }
)

/**
 * Загрузка документов на сервер.
 * 
 * @param files - Список файлов для загрузки
 * @returns Promise с ответом от сервера
 */
export const uploadDocuments = async (
  files: File[]
): Promise<DocumentUploadResponse[]> => {
  const formData = new FormData()
  
  files.forEach((file) => {
    formData.append('files', file)
  })

  const response = await apiClient.post<DocumentUploadResponse[]>(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )

  return response.data
}

/**
 * Получение списка всех загруженных документов.
 * 
 * @returns Promise со списком документов
 */
export const getDocuments = async (): Promise<DocumentListResponse> => {
  const response = await apiClient.get<DocumentListResponse>('/documents')
  return response.data
}

/**
 * Полнотекстовый поиск по документам.
 * 
 * @param query - Поисковый запрос
 * @param from - Начальный индекс для пагинации
 * @param size - Количество результатов на странице
 * @returns Promise с результатами поиска
 */
export const searchDocuments = async (
  query: string,
  from: number = 0,
  size: number = 10
): Promise<SearchResponse> => {
  const response = await apiClient.get<SearchResponse>('/search', {
    params: {
      q: query,
      from_item: from,
      size: size,
    },
  })
  return response.data
}

export default apiClient