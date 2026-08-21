import ReportsPage from './pages/ReportsPage'

export default function App() {
  return (
    <div className="page">
      <header className="page-header">
        <h1>Interview Prep Lab</h1>
        <p className="subtitle">
          Phase 0 — scaffold and harness. The number in the badge below is read from the
          backend&rsquo;s <code>X-Query-Count</code> header; it is the instrument the rest of the lab
          is measured with.
        </p>
      </header>
      <ReportsPage />
      <footer className="page-footer">
        {/* Phase 8 replaces this with a /lab index of the React failure modes. */}
        <p>
          Next up: <code>/lab</code> arrives in Phase 8 with one page per React failure mode.
        </p>
      </footer>
    </div>
  )
}
