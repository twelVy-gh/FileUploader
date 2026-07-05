/**
 * Компонент отображения результатов поиска.
 * Отображает карточки с подсветкой совпадений.
 */

import type { SearchResultItem } from '../types'
import '../styles/SearchResults.css'

interface SearchResultsProps {
  results: SearchResultItem[]
  query: string
}

/**
 * Подсветка слов из запроса в тексте.
 * Оборачивает совпадения в <mark> тег.
 */
function highlightText(text: string, query: string): string {
  if (!query.trim()) return text
  
  // Если текст уже содержит HTML теги (подсветка от бэкенда), используем его как есть
  if (text.includes('<mark>') || text.includes('</mark>')) {
    return text
  }
  
  // Разбиваем запрос на слова и экранируем специальные regex символы
  const words = query
    .trim()
    .split(/\s+/)
    .filter(w => w.length > 0)
    .map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  
  if (words.length === 0) return text
  
  // Создаём regex для поиска всех слов (без учёта регистра)
  const regex = new RegExp(`(${words.join('|')})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function SearchResults({ results, query }: SearchResultsProps) {
  return (
    <div className="search-results">
      {results.map((result, index) => (
        <div key={result.chunk_id || index} className="result-card">
          <div className="result-header">
            <div className="result-file-info">
              <span className="result-file-icon">
                {result.file_name.toLowerCase().endsWith('.pdf') ? '📕' : '📘'}
              </span>
              <span className="result-file-name" title={result.file_name}>
                {result.file_name}
              </span>
            </div>
            {result.page && (
              <span className="result-page">
                Страница: {result.page}
              </span>
            )}
            <span className="result-score" title="Релевантность">
              Score: {result.score.toFixed(2)}
            </span>
          </div>
          
          <div 
            className="result-text"
            dangerouslySetInnerHTML={{ 
              __html: highlightText(result.text, query) 
            }}
          />
        </div>
      ))}
    </div>
  )
}

export default SearchResults