/**
 * Thin fetch layer.
 *
 * It returns the parsed body *and* the X-Query-Count header, because half the
 * point of this lab is watching that number change on screen when you switch
 * between a broken and a fixed endpoint.
 */

export type Report = {
  id: string
  org_id: string
  author_id: string
  title: string
  body: string
  status: 'draft' | 'submitted' | 'approved'
  created_at: string
  author_email: string
}

export type Measured<T> = {
  data: T
  queryCount: number | null
  elapsedMs: number
}

export async function measuredGet<T>(path: string): Promise<Measured<T>> {
  const started = performance.now()
  const response = await fetch(`/api${path}`)
  const elapsedMs = Math.round(performance.now() - started)

  if (!response.ok) {
    throw new Error(`GET ${path} failed: ${response.status} ${response.statusText}`)
  }

  const header = response.headers.get('X-Query-Count')
  return {
    data: (await response.json()) as T,
    queryCount: header === null ? null : Number(header),
    elapsedMs,
  }
}

export const fetchReports = (limit = 25) => measuredGet<Report[]>(`/reports?limit=${limit}`)
