/** 由 frontend/.env 或 .env.local 設定 VITE_API_BASE_URL，見 .env.example */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.trim() || ''

interface RequestOptions extends RequestInit {
  token?: string
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export function hasBackendApi(): boolean {
  return API_BASE_URL.length > 0
}

/** 開發用：目前資料來源為 Mock 或 API（DB），便於辨識。 */
export function getDataSourceLabel(): 'Mock' | 'API' {
  return hasBackendApi() ? 'API' : 'Mock'
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('Content-Type', 'application/json')
  if (options.token) {
    headers.set('Authorization', `Bearer ${options.token}`)
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const data = await response.json() as { detail?: string }
      if (data.detail) {
        message = data.detail
      }
    }
    catch {
      // ignore json parse errors
    }
    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }
  return await response.json() as T
}
