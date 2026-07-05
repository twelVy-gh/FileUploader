/**
 * Корневой компонент приложения.
 * Определяет маршрутизацию между страницами.
 */

import { Routes, Route, Link, useLocation } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import SearchPage from './pages/SearchPage'
import './styles/App.css'

function App() {
  const location = useLocation()

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">📄 Интеллектуальный поиск по документам</h1>
        <nav className="app-nav">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Загрузка документов
          </Link>
          <Link
            to="/search"
            className={`nav-link ${location.pathname === '/search' ? 'active' : ''}`}
          >
            Поиск
          </Link>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/search" element={<SearchPage />} />
        </Routes>
      </main>

      <footer className="app-footer">
        <p>© 2026 Document Search System</p>
      </footer>
    </div>
  )
}

export default App