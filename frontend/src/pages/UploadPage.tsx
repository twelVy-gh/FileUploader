/**
 * Страница загрузки документов.
 * Содержит Drag-and-Drop зону, список загружаемых файлов
 * и таблицу ранее загруженных документов.
 */

import { useState, useEffect, useCallback } from 'react'
import { uploadDocuments, getDocuments } from '../api/client'
import type { Document, UploadingFile } from '../types'
import FileUpload from '../components/FileUpload'
import DocumentList from '../components/DocumentList'
import '../styles/UploadPage.css'

function UploadPage() {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Загрузка списка документов при монтировании
  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await getDocuments()
      setDocuments(response.documents)
    } catch (err) {
      setError('Не удалось загрузить список документов')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  // Обработка выбранных файлов
  const handleFilesSelected = useCallback(async (files: File[]) => {
    // Валидация
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    const maxSize = 20 * 1024 * 1024 // 20 MB

    const validFiles: File[] = []
    const newUploading: UploadingFile[] = []

    for (const file of files) {
      const id = crypto.randomUUID()
      
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx)$/i)) {
        newUploading.push({
          id,
          file,
          progress: 0,
          status: 'error',
          message: 'Неподдерживаемый формат. Разрешены только PDF и DOCX.'
        })
        continue
      }

      if (file.size > maxSize) {
        newUploading.push({
          id,
          file,
          progress: 0,
          status: 'error',
          message: 'Файл превышает 20 МБ'
        })
        continue
      }

      validFiles.push(file)
      newUploading.push({
        id,
        file,
        progress: 0,
        status: 'pending'
      })
    }

    setUploadingFiles(prev => [...newUploading, ...prev])

    if (validFiles.length === 0) return

    // Обновляем статус на "загрузка"
    setUploadingFiles(prev =>
      prev.map(f => 
        validFiles.some(vf => vf.name === f.file.name) && f.status === 'pending'
          ? { ...f, status: 'uploading', progress: 30 }
          : f
      )
    )

    try {
      // Загружаем файлы
      const response = await uploadDocuments(validFiles)
      
      // Обновляем статус на "индексация"
      setUploadingFiles(prev =>
        prev.map(f => {
          const match = response.find(r => r.file_name === f.file.name)
          if (match) {
            return { ...f, status: 'indexing', progress: 70, documentId: match.document_id }
          }
          return f
        })
      )

      // Имитация прогресса индексации
      setTimeout(() => {
        setUploadingFiles(prev =>
          prev.map(f => 
            f.status === 'indexing' ? { ...f, status: 'ready', progress: 100 } : f
          )
        )
        // Обновляем список документов
        fetchDocuments()
      }, 2000)

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Ошибка загрузки'
      setUploadingFiles(prev =>
        prev.map(f => 
          f.status === 'uploading' 
            ? { ...f, status: 'error', message: errorMsg }
            : f
        )
      )
    }
  }, [])

  // Удаление элемента из списка загрузки
  const handleRemoveFile = useCallback((id: string) => {
    setUploadingFiles(prev => prev.filter(f => f.id !== id))
  }, [])

  return (
    <div className="upload-page">
      <section className="upload-section">
        <h2>Загрузка документов</h2>
        <p className="upload-hint">
          Поддерживаемые форматы: PDF, DOCX. Максимальный размер: 20 МБ.
        </p>
        
        <FileUpload onFilesSelected={handleFilesSelected} />

        {uploadingFiles.length > 0 && (
          <div className="uploading-list">
            <h3>Загружаемые файлы</h3>
            {uploadingFiles.map(file => (
              <div key={file.id} className={`upload-item status-${file.status}`}>
                <div className="upload-item-info">
                  <span className="file-name">{file.file.name}</span>
                  <span className="file-size">
                    {(file.file.size / 1024).toFixed(1)} КБ
                  </span>
                  <span className={`status-badge status-${file.status}`}>
                    {file.status === 'pending' && 'Ожидание...'}
                    {file.status === 'uploading' && 'Загрузка...'}
                    {file.status === 'indexing' && 'Индексация...'}
                    {file.status === 'ready' && '✓ Готово'}
                    {file.status === 'error' && '✗ Ошибка'}
                  </span>
                  <button 
                    className="remove-btn"
                    onClick={() => handleRemoveFile(file.id)}
                    title="Удалить из списка"
                  >
                    ×
                  </button>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${file.progress}%` }}
                  />
                </div>
                {file.message && (
                  <div className="error-message">{file.message}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="documents-section">
        <h2>Загруженные документы</h2>
        {loading ? (
          <p className="loading-text">Загрузка...</p>
        ) : error ? (
          <p className="error-text">{error}</p>
        ) : (
          <DocumentList documents={documents} onRefresh={fetchDocuments} />
        )}
      </section>
    </div>
  )
}

export default UploadPage