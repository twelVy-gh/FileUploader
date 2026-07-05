/**
 * Компонент списка загруженных документов.
 * Отображает таблицу с метаданными: имя файла, дата, статус.
 */

import type { Document } from '../types'
import '../styles/DocumentList.css'

interface DocumentListProps {
  documents: Document[]
  onRefresh: () => void
}

/**
 * Форматирование даты в читаемый вид.
 */
function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

/**
 * Получение текстового описания статуса.
 */
function getStatusLabel(status: string): string {
  switch (status) {
    case 'uploading': return '📤 Загрузка'
    case 'indexing': return '⚙️ Индексация'
    case 'ready': return '✅ Готов'
    case 'error': return '❌ Ошибка'
    default: return status
  }
}

function DocumentList({ documents, onRefresh }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="document-list-empty">
        <p>Документы ещё не загружены</p>
        <p className="empty-hint">Загрузите первый документ с помощью зоны выше</p>
      </div>
    )
  }

  return (
    <div className="document-list">
      <div className="document-list-header">
        <span className="doc-count">Всего документов: {documents.length}</span>
        <button className="refresh-btn" onClick={onRefresh} title="Обновить список">
          🔄 Обновить
        </button>
      </div>
      
      <table className="documents-table">
        <thead>
          <tr>
            <th>Название файла</th>
            <th>Дата загрузки</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id} className={`doc-row status-${doc.status}`}>
              <td className="doc-name" title={doc.file_name}>
                <span className="doc-icon">
                  {doc.file_name.toLowerCase().endsWith('.pdf') ? '📕' : '📘'}
                </span>
                {doc.file_name}
              </td>
              <td className="doc-date">{formatDate(doc.upload_date)}</td>
              <td className="doc-status">
                <span className={`status-badge status-${doc.status}`}>
                  {getStatusLabel(doc.status)}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default DocumentList