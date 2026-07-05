/**
 * Страница полнотекстового поиска.
 * Содержит строку поиска, карточки результатов с подсветкой
 * и пагинацию.
 */

import { useState, useCallback, FormEvent } from 'react'
import { searchDocuments } from '../api/client'
import type { SearchResultItem } from '../types'
import SearchResults from '../components/SearchResults'
import '../styles/SearchPage.css'

const PAGE_SIZE = 10

function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResultItem[]>([])
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  // Выполнение поиска
  const performSearch = useCallback(async (searchQuery: string, from: number) => {
    if (!searchQuery.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await searchDocuments(searchQuery.trim(), from, PAGE_SIZE)
      setResults(response.results)
      setTotal(response.total)
      setHasSearched(true)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Ошибка поиска'
      setError(errorMsg)
      setResults([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  // Обработка отправки формы
  const handleSubmit = useCallback((e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!query.trim()) return
    setCurrentPage(0)
    performSearch(query, 0)
  }, [query, performSearch])

  // Обработка изменения строки поиска
  const handleQueryChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value)
  }, [])

  // Пагинация — следующая страница
  const handleNextPage = useCallback(() => {
    const nextPage = currentPage + 1
    const from = nextPage * PAGE_SIZE
    if (from < total) {
      setCurrentPage(nextPage)
      performSearch(query, from)
    }
  }, [currentPage, total, query, performSearch])

  // Пагинация — предыдущая страница
  const handlePrevPage = useCallback(() => {
    if (currentPage > 0) {
      const prevPage = currentPage - 1
      const from = prevPage * PAGE_SIZE
      setCurrentPage(prevPage)
      performSearch(query, from)
    }
  }, [currentPage, query, performSearch])

  // Обработка поиска по Enter
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      if (!query.trim()) return
      setCurrentPage(0)
      performSearch(query, 0)
    }
  }, [query, performSearch])

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const showPagination = total > PAGE_SIZE

  return (
    <div className="search-page">
      <section className="search-section">
        <h2>Поиск по документам</h2>
        <p className="search-hint">
          Введите запрос для поиска по проиндексированным документам
        </p>

        <form className="search-form" onSubmit={handleSubmit}>
          <div className="search-input-wrapper">
            <input
              type="text"
              className="search-input"
              value={query}
              onChange={handleQueryChange}
              onKeyDown={handleKeyDown}
              placeholder="Введите поисковый запрос..."
              disabled={loading}
              autoFocus
            />
            <button
              type="submit"
              className="search-btn"
              disabled={loading || !query.trim()}
            >
              {loading ? '⏳ Поиск...' : '🔍 Найти'}
            </button>
          </div>
        </form>

        {error && (
          <div className="search-error">
            <p>❌ {error}</p>
          </div>
        )}

        {loading && (
          <div className="search-loading">
            <p>Выполняется поиск...</p>
          </div>
        )}

        {!loading && hasSearched && results.length === 0 && !error && (
          <div className="no-results">
            <p>😕 По вашему запросу ничего не найдено...</p>
            <p className="no-results-hint">
              Попробуйте изменить запрос или загрузить новые документы
            </p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <>
            <div className="results-info">
              <p>
                Найдено результатов: <strong>{total}</strong>
                {totalPages > 1 && (
                  <span> • Страница {currentPage + 1} из {totalPages}</span>
                )}
              </p>
            </div>

            <SearchResults results={results} query={query} />

            {showPagination && (
              <div className="pagination">
                <button
                  className="pagination-btn prev"
                  onClick={handlePrevPage}
                  disabled={currentPage === 0}
                >
                  ← Назад
                </button>
                <span className="pagination-info">
                  {currentPage + 1} / {totalPages}
                </span>
                <button
                  className="pagination-btn next"
                  onClick={handleNextPage}
                  disabled={(currentPage + 1) * PAGE_SIZE >= total}
                >
                  Вперёд →
                </button>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  )
}

export default SearchPage