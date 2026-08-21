import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchReports } from '../api'

const LIMITS = [5, 25, 100, 200]

export default function ReportsPage() {
  const [limit, setLimit] = useState(25)

  const { data, isPending, isFetching, error } = useQuery({
    queryKey: ['reports', limit],
    queryFn: () => fetchReports(limit),
  })

  return (
    <section>
      <div className="toolbar">
        <label htmlFor="limit">Rows</label>
        <select
          id="limit"
          value={limit}
          onChange={(event) => setLimit(Number(event.target.value))}
        >
          {LIMITS.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>

        {data && (
          <>
            {/* The lesson in one badge: with selectinload the query count stays
                at 2 no matter which row limit you pick. Phase 1 adds the
                endpoint where it does not. */}
            <span className="badge" title="X-Query-Count response header">
              queries: <strong>{data.queryCount ?? '—'}</strong>
            </span>
            <span className="badge">
              round trip: <strong>{data.elapsedMs}ms</strong>
            </span>
          </>
        )}
        {isFetching && <span className="badge muted">fetching…</span>}
      </div>

      {isPending && <p>Loading reports…</p>}
      {error && <p className="error">{(error as Error).message}</p>}

      {data && (
        <table className="reports">
          <thead>
            <tr>
              <th>Title</th>
              <th>Author</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {data.data.map((report) => (
              <tr key={report.id}>
                <td>{report.title}</td>
                <td>{report.author_email}</td>
                <td>
                  <span className={`status status-${report.status}`}>{report.status}</span>
                </td>
                <td>{new Date(report.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {data?.data.length === 0 && (
        <p>
          No reports. Run <code>uv run python -m app.seed</code> in <code>backend/</code>.
        </p>
      )}
    </section>
  )
}
